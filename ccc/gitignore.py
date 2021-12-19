from __future__ import annotations
from typing import List
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from pathlib import Path


class GitIgnore:
    def __init__(self, path: Path, spec: PathSpec):
        self.path = path.parent
        self.spec = spec

    @classmethod
    def fromPath(cls, path: Path) -> GitIgnore:
        with open(path, "r") as fp:
            lines = _transform_rules(fp.read())
        spec = PathSpec.from_lines(GitWildMatchPattern, lines)
        return cls(path=path, spec=spec)

    def match(self, fpath: Path | str) -> bool:
        return self.spec.match_file(fpath)


def _transform_rules(raw: str) -> List[str]:
    rules = []
    for l in raw.splitlines():
        if l and not l.startswith("#"):
            # rule = l[1:] if l.startswith("!") else "!" + l
            # rules.append(rule)
            rules.append(l)
    return rules
