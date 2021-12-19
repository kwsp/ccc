from pathlib import Path
from ccc.gitignore import GitIgnore

def test_ignore(tmp_path: Path):
    tmp = tmp_path / ".gitignore"
    ignoreRules = """
    *.pyc
    __pycache__/
    /site
    """
    tmp.write_text(ignoreRules)

    gitIgnore = GitIgnore.fromPath(tmp)

    assert not gitIgnore.match("main.py")
    assert not gitIgnore.match("a/b/c/main.py")

    assert gitIgnore.match("main.pyc")
    assert gitIgnore.match("a/b/c/main.pyc")

    assert gitIgnore.match("__pycache__/what")

    assert gitIgnore.match("site/what")
    assert not gitIgnore.match("what/site/what")

