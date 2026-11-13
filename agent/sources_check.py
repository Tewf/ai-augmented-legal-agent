#!/usr/bin/env python3
"""The legal agent's rule "every point sourced", checked by a program: list each reference and each long quotation in
the agent's output that appears in none of the texts it was given.

  python3 sources_check.py OUTPUT.md [OUTPUT.md ...] --texts DIR_OR_FILE [DIR_OR_FILE ...]
      exit 0 when every reference and quotation is found, 1 otherwise

Checked: numbers written « n° 2026-042 » (a deliberation, a decision), Légifrance's LEGIARTI, LEGITEXT and JORFTEXT
ids, EUR-Lex's CELEX ids, and every quotation between « » or " " of eight words or more. Text is compared lower-cased,
with spaces, line breaks, apostrophes and quote marks made one form.

Why: on 13 Nov. 2026 the agent called the CNIL's recommendation « n° 2026-042 » fifteen times; the number is in none of
the texts it was given, and only a person reading caught it. What a clean run guarantees: every listed kind of
reference is in a given text. What it does not: that a section number, an article number or a short phrase is right,
or that a reference found says what the agent makes it say. That stays the reader's, with rubric.md. Time O(text).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

NUMBER = re.compile(r"n°\s*\d{4}-\d{2,4}", re.I)
IDS = re.compile(r"\b(?:LEGIARTI|LEGITEXT|JORFTEXT)\d{8,}\b|\bCELEX:\s*\w+")
QUOTE = re.compile(r"«\s*([^«»]+?)\s*»|\"([^\"\n]+)\"")
MIN_WORDS = 8   # PROVISIONAL: a shorter quotation is often a term, which the text may inflect
MIN_PIECE = 4   # PROVISIONAL: a piece of a quotation around a marked cut, checked when it has this many words
EDIT = re.compile(r"\[[^\]]*\]")


def flat(text: str) -> str:
    """One form for what typography alone changes: case, spaces and line breaks, apostrophes, quote marks."""
    text = text.lower().replace("’", "'").replace("‘", "'")
    text = re.sub(r"[«»“”\"]", " ", text)
    return " ".join(text.split())


def read_texts(paths: list[Path]) -> str:
    """Every given text, one string; a folder gives each file under it."""
    files = [f for p in paths for f in ([p] if p.is_file() else sorted(p.rglob("*"))) if f.is_file()]
    return flat("\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files))


def missing(output: str, texts: str) -> list[str]:
    """The references and long quotations of `output` that `texts` does not hold, each once, in order."""
    found = [m.group(0) for m in NUMBER.finditer(output)] + [m.group(0) for m in IDS.finditer(output)]
    for m in QUOTE.finditer(output):
        quoted = m.group(1) or m.group(2)
        if len(quoted.split()) < MIN_WORDS:
            continue
        # a marked cut « [...] » or insertion « [les personnes] » is the quoter's; each piece around it must be found
        pieces = [p.strip() for p in EDIT.split(quoted) if len(p.split()) >= MIN_PIECE]
        found.extend(pieces if EDIT.search(quoted) else [quoted])
    out = []
    for item in found:
        key = flat(item).replace("n° ", "n°").replace("n°", "n° ")
        if key not in texts.replace("n° ", "n°").replace("n°", "n° ") and item not in out:
            out.append(item)
    return out


def main(argv: list[str]) -> int:
    if "--texts" not in argv:
        print(__doc__.split("\n\n")[1])
        return 2
    cut = argv.index("--texts")
    outputs, texts = [Path(a) for a in argv[:cut]], read_texts([Path(a) for a in argv[cut + 1:]])
    failed = False
    for path in outputs:
        for item in missing(path.read_text(encoding="utf-8"), texts):
            failed = True
            print(f"{path}: in no text given: {' '.join(item.split())[:160]}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
