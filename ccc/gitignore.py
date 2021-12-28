from __future__ import annotations
from typing import List, Optional
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from pathlib import Path


class GitIgnore:
    def __init__(self, path: Optional[Path], spec: PathSpec):
        self.path = path.parent if path else None
        self.spec = spec

    @classmethod
    def fromPath(cls, path: Path) -> GitIgnore:
        with open(path, "r") as fp:
            rules = fp.read().split("\n")
        return cls.fromRules(rules)

    @classmethod
    def fromRules(cls, rules: List[str]) -> GitIgnore:
        rules = [r.removesuffix("/") for r in rules]
        spec = PathSpec.from_lines(GitWildMatchPattern, rules)
        return cls(path=None, spec=spec)

    def match(self, fpath: Path | str) -> bool:
        return self.spec.match_file(fpath)
