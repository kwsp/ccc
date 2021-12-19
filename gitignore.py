import re
import pathspec
from re import Pattern
from pathlib import Path
from typing import List


class GitIgnorePattern:
    def __init__(self, pat: str):
        self.pat = pat

    def match(self, path: Path) -> bool:
        # TODO: Implement
        return False


class GitIgnore:
    def __init__(self, path: Path, spec: pathspec.PathSpec):
        self.path = path.parent
        self.spec = spec

    @classmethod
    def fromPath(cls, path: Path):
        with open(path, "r") as fp:
            raw = fp.read().strip()

        spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern, raw.splitlines()
        )
        return cls(path=path, spec=spec)

    def match(self, fpath: Path) -> bool:
        return self.spec.match_file(fpath)
