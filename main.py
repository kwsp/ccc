from __future__ import annotations
import os
import re
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from typing import Dict, List, NamedTuple, Optional

from ccc.gitignore import GitIgnore
from ccc.languages import detectLanguage

Excludes = [".git"]


class Config:
    verbose = False


class DirectoryJob(NamedTuple):
    root: Path
    path: Path
    ignores: List[GitIgnore]

    @classmethod
    def fromPath(cls, path: Path, ignores: List[GitIgnore] = []):
        return cls(root=path, path=path, ignores=ignores)


class FileJob(NamedTuple):
    path: Path

    @classmethod
    def fromPath(cls, path: Path):
        return cls(path=path)


class FileSummary(NamedTuple):
    path: Path
    language: str
    extension: str
    bytes: int
    lines: int
    code: int
    comment: int
    blank: int

    @classmethod
    def fromPath(cls, path: Path) -> Optional[FileSummary]:
        "Process file at given path"
        stat = path.lstat()
        bytes = stat.st_size
        extension = path.suffix

        try:
            with open(path, "r") as fp:
                raw = fp.read()
        except UnicodeDecodeError:  # ignore binary files
            if Config.verbose:
                print("Ignoring binary file: ", path)
            return None
        except FileNotFoundError:
            if Config.verbose:
                print("File not found: ", path)
            return None

        content = raw.splitlines()
        language = detectLanguage(path.name, content)
        lines = len(content)
        # TODO implement code/comment/blank count
        code = 0
        comment = 0
        blank = 0

        return cls(
            path=path,
            language=language,
            extension=extension,
            bytes=bytes,
            lines=lines,
            code=code,
            comment=comment,
            blank=blank,
        )


@dataclass
class LanguageSummary:
    name: str
    bytes: int
    lines: int
    code: int
    comment: int
    blank: int
    count: int
    files: List[FileSummary]

    @classmethod
    def init(cls, name: str) -> LanguageSummary:
        return cls(
            name=name,
            bytes=0,
            lines=0,
            code=0,
            comment=0,
            blank=0,
            count=0,
            files=[],
        )

    def add(self, job: FileSummary):
        assert self.name == job.language
        self.bytes += job.bytes
        self.lines += job.lines
        self.code += job.code
        self.comment += job.comment
        self.blank += job.blank
        self.count += 1
        self.files.append(job)


FileJobQueue = Queue[FileJob]
FileSummaryQueue = Queue[FileSummary]
DirQueue = Queue[DirectoryJob]


class DirWalker:
    def __init__(self, fileListQueue: FileJobQueue):
        self.fileListQueue: FileJobQueue = fileListQueue
        self.dirJobsQueue: DirQueue = Queue()
        self.excludes: List[re.Pattern] = [re.compile(pat) for pat in Excludes]
        self.checkExclude = lambda path: any(pat.match(path) for pat in self.excludes)

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
                continue
            if any(pat.match(dirEnt) for pat in ignores):
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
        if Config.verbose:
            print("Processing ", job.path)

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
        langSummaries[lang].add(job)
        inp.task_done()
    return langSummaries


def formatResult(summaries: Dict[str, LanguageSummary]):
    langs = list(summaries.keys())
    langs.sort()
    for lang in langs:
        s = summaries[lang]
        print(lang)
        print("    Lines:", s.lines)


def main():
    entryPoint = Path(os.path.expanduser("~/code/py/imget"))
    assert entryPoint.exists(), "Dir does not exists: " + str(entryPoint)

    fileListQueue: FileJobQueue = Queue()
    fileSummaryQueue: FileSummaryQueue = Queue()

    dw = DirWalker(fileListQueue)
    dw.start(entryPoint)

    fileProcessWorker(fileListQueue, fileSummaryQueue)

    summaries = fileSummarize(fileSummaryQueue)
    formatResult(summaries)


if __name__ == "__main__":
    main()
