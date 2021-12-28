from typing import Dict

from .datastructures import *


class DirWalker:
    def __init__(self, fileListQueue: FileJobQueue):
        self.fileListQueue: FileJobQueue = fileListQueue
        self.dirJobsQueue: DirQueue = Queue()
        self.excludes = GitIgnore.fromRules(Config.excludes)
        self.checkExclude = lambda path: self.excludes.match(path)

    def start(self, startDir: Path):
        "Start looking for files at the given directory"
        if not startDir.is_dir():
            self.fileListQueue.put(FileJob.fromPath(startDir))
            return
        self.dirJobsQueue.put(DirectoryJob.fromPath(startDir))

        # TODO: parallelize this
        while not self.dirJobsQueue.empty():
            self.walk()

    def readDir(self, dirJob: DirectoryJob) -> List[Path]:
        return [fpath for fpath in dirJob.path.glob("*")]

    def walk(self):
        "Rapidly find all files"
        dirJob = self.dirJobsQueue.get()
        if dirJob.path.name.startswith("."):  # ignore hidden directories
            return
        dirEnts = self.readDir(dirJob)
        if Config.verbose:
            print("Walking ", dirJob.path)

        # look for .gitignore
        ignores = dirJob.ignores
        for fpath in dirEnts:
            name = fpath.name
            if name == ".gitignore":
                if Config.verbose:
                    print("Found gitignore: ", fpath)
                try:
                    ignores.append(GitIgnore.fromPath(fpath))
                except Exception as e:
                    print(f"Failed to load gitignore {fpath}: {e}")

        # walk directory entries
        for dirEnt in dirEnts:
            if self.checkExclude(dirEnt.name):
                if Config.verbose:
                    print("Ignoring due to exclude: ", dirEnt)
                continue
            if any(pat.match(dirEnt) for pat in ignores):
                if Config.verbose:
                    print("Ignoring due to gitignore: ", dirEnt)
                continue

            if dirEnt.is_dir():
                newDirJob = DirectoryJob.fromPath(dirEnt, ignores=ignores)
                self.dirJobsQueue.put(newDirJob)
            else:
                self.fileListQueue.put(FileJob.fromPath(dirEnt))


def fileProcessWorker(inp: FileJobQueue, out: FileSummaryQueue):
    # TODO: parallelize
    while not inp.empty():
        job = inp.get()
        try:
            fileSummary = FileSummary.fromPath(job.path)
            if fileSummary:
                out.put(fileSummary)
        except Exception as e:
            print(f"Failed to process file {job.path}: {e}")
        finally:
            inp.task_done()


def fileSummarize(inp: FileSummaryQueue) -> Dict[str, LanguageSummary]:
    langSummaries: Dict[str, LanguageSummary] = {}
    while not inp.empty():
        job = inp.get()
        lang = job.language
        if lang not in langSummaries:
            langSummaries[lang] = LanguageSummary.init(lang)
        langSummaries[lang].add_file(job)
        inp.task_done()
    return langSummaries
