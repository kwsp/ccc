from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from queue import Queue
from typing import List, NamedTuple, Optional

from .languages import detectLanguage, detectLanguageFromName
from .gitignore import GitIgnore


class Config:
    verbose: bool = False
    excludes: List[str] = [r"\.", ".git"]


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
        language = None
        languages, _ = detectLanguageFromName(path.name)

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

        if Config.verbose:
            print("Processing ", path)

        content = raw.splitlines()
        language = detectLanguage(languages, content)
        if not language:
            print("Unable to detect language: ", path)
            return
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

    def add_file(self, job: FileSummary):
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
