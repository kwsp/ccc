from typing import Dict

from .datastructures import LanguageSummary

LINE = "───────────────────────────────────────────────────────────────────────────────"
HEADING = (
    "Language                 Files     Lines   Blanks  Comments     Code Complexity"
)
TEMPLATE = "{name:<20}{files:>10}{lines:>10}{blanks:>9}{comments:>10}{code:>10}{complexity:>10}"


def formatResult(summaries: Dict[str, LanguageSummary]):
    langs = list(summaries.keys())
    langs.sort(key=lambda lang: -len(summaries[lang].files))
    print(LINE)
    print(HEADING)
    print(LINE)
    files = 0
    lines = 0
    blanks = 0
    comments = 0
    code = 0
    complexity = 0
    for lang in langs:
        s = summaries[lang]
        print(
            TEMPLATE.format(
                name=lang,
                files=len(s.files),
                lines=s.lines,
                blanks=s.blank,
                comments=s.comment,
                code=s.code,
                complexity=0,
            )
        )
        files += len(s.files)
        lines += s.lines
        blanks += s.blank
        comments += s.comment
        code += s.code
        complexity += 0
    print(LINE)
    print(
        TEMPLATE.format(
            name="Total",
            files=files,
            lines=lines,
            blanks=blanks,
            comments=comments,
            code=code,
            complexity=0,
        )
    )
    print(LINE)
