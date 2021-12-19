from ccc.languages import (
    detectLanguage,
    detectLanguageFromName,
    detectLanguageFromShebang,
)


def test_fullname():
    langs, ext = detectLanguageFromName(".gitignore")
    assert ext == ".gitignore"
    assert len(langs) == 1 and langs[0] == "gitignore"


def test_ext():
    langs, ext = detectLanguageFromName("main.py")
    assert ext == "py"
    assert len(langs) == 1 and langs[0] == "Python"

    langs, ext = detectLanguageFromName("main.go")
    assert ext == "go"
    assert len(langs) == 1 and langs[0] == "Go"

    langs, ext = detectLanguageFromName("main.ts")
    assert ext == "ts"
    assert len(langs) == 1 and langs[0] == "TypeScript"

    langs, ext = detectLanguageFromName("main.d.ts")
    assert ext == "d.ts"
    assert len(langs) == 1 and langs[0] == "TypeScript Typings"

    langs, ext = detectLanguageFromName("a.b.c.d.e")
    assert ext == "c.d.e"
    assert len(langs) == 0


def test_shebang():
    lang = detectLanguageFromShebang(["#!/usr/bin/env python3"])
    assert lang == "Python"

    lang = detectLanguageFromShebang(["#!/bin/sh"])
    assert lang == "Shell"

    lang = detectLanguage("name", ["#!/usr/bin/env python3"])
    assert lang == "Python"

    lang = detectLanguage("name", ["#!/bin/sh"])
    assert lang == "Shell"
