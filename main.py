import os
import re
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from typing import List

from gitignore import GitIgnore

Excludes = [".git", ".mypy_cache"]


class Config:
    verbose = True


@dataclass
class DirectoryJob:
    root: Path
    path: Path
    ignores: List[GitIgnore]

    @classmethod
    def fromPath(cls, path: Path):
        return cls(root=path, path=path, ignores=[])


@dataclass
class FileJob:
    path: Path
    lines: int

    @classmethod
    def fromPath(cls, path: Path):
        return cls(path=path, lines=0)


FileQueue = Queue[FileJob]
DirQueue = Queue[DirectoryJob]


class DirWalker:
    def __init__(self, fileListQueue: FileQueue):
        self.fileListQueue: FileQueue = fileListQueue
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
        while not dw.dirJobsQueue.empty():
            dw.walk()

    def readDir(self, dirJob: DirectoryJob) -> List[Path]:
        # TODO: check dirjob ignores
        return [fpath for fpath in dirJob.path.glob("*")]

    def walk(self):
        "Rapidly find all files"
        dirJob = self.dirJobsQueue.get()
        dirEnts = self.readDir(dirJob)
        print("Walk ", dirJob.path)

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
                newDirJob = DirectoryJob.fromPath(dirEnt)
                newDirJob.ignores = ignores
                self.dirJobsQueue.put(newDirJob)
            else:
                self.fileListQueue.put(FileJob.fromPath(dirEnt))


def fileProcessWorker(inp: FileQueue, out: FileQueue):
    while not inp.empty():
        job = inp.get()
        print(job.path)

        try:
            with open(job.path, "r") as fp:
                raw = fp.read().split("\n")
            job.lines = len(raw)
        except:
            pass

        out.put(job)
        inp.task_done()


def fileSummarize(inp: FileQueue):
    lines = 0
    while not inp.empty():
        job = inp.get()
        lines += job.lines
    return lines


# def main():
entryPoint = Path(os.path.expanduser("~/code/py/imget"))
assert entryPoint.exists(), "Dir does not exists: " + str(entryPoint)

fileListQueue: FileQueue = Queue()
fileSummaryQueue: FileQueue = Queue()

dw = DirWalker(fileListQueue)
dw.start(entryPoint)

fileProcessWorker(fileListQueue, fileSummaryQueue)

result = fileSummarize(fileSummaryQueue)
print(result)
