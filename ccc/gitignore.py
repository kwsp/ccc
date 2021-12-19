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
            rules = _transform_rules(fp.read())
        return cls.fromRules(rules)

    @classmethod
    def fromRules(cls, rules: List[str]) -> GitIgnore:
        spec = PathSpec.from_lines(GitWildMatchPattern, rules)
        return cls(path=None, spec=spec)

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
