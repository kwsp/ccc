from typing import DefaultDict, List, Tuple
import json
from importlib.resources import files

languageDB = {}
ext2lang = DefaultDict(list)
fname2lang = DefaultDict(list)
shebang2lang = {}
SHEBANG = "!#"


# Load language database
with (files("ccc") /  "languages.json").open() as fp:
    languageDB = json.load(fp)

for lang, val in languageDB.items():
    for ext in val["extensions"]:
        ext2lang[ext].append(lang)

    if "filenames" in val:
        for fname in val["filenames"]:
            fname2lang[fname].append(lang)

    if "shebangs" in val:
        for shebang in val["shebangs"]:
            shebang2lang[shebang] = lang


def detectLanguageFromName(fname: str) -> Tuple[List[str], str]:
    """
    Returns list of possible languages and extension
    """
    parts = fname.split(".", 1)
    if len(parts) == 1 or fname.startswith("."):  # no dots
        # check fullname
        if fname in fname2lang:
            return fname2lang[fname], fname
        # check shebang
        return [SHEBANG], fname

    # in case fullname matches
    if fname in ext2lang:
        return ext2lang[fname], fname

    ext = parts[-1]
    if ext in ext2lang:
        return ext2lang[ext], ext
    # check multiple extensions
    parts = ext.split(".", 1)
    ext = parts[-1]
    return ext2lang[ext], ext


def detectLanguageFromShebang(content: List[str]) -> str:
    line = content[0].strip()
    if line.startswith("#!"):
        parts = line.split()
        if len(parts) > 1:
            return shebang2lang[parts[-1]]
        return shebang2lang[parts[0].split("/")[-1]]
    return ""


def detectLanguage(langs: List[str], content: List[str]) -> str:
    if len(langs) == 1:
        if langs[0] == SHEBANG:
            return detectLanguageFromShebang(content)
        return langs[0]

    # TODO: detect language from content

    return ""
