#!/usr/bin/env python3
"""The legal agent's rule "every point sourced", checked by a program: list each reference and each long quotation in
the agent's output that appears in none of the texts it was given.

  python3 sources_check.py OUTPUT.md [OUTPUT.md ...] --texts DIR_OR_FILE [DIR_OR_FILE ...]
      exit 0 when every reference and quotation is found, 1 otherwise

Checked: numbers written « n° 2026-042 » (a deliberation, a decision), Légifrance's LEGIARTI, LEGITEXT and JORFTEXT
ids, EUR-Lex's CELEX ids, case numbers of the Court of Justice and the General Court (« C-393/09 », « T-12/21 »),
article numbers of a code (« L. 122-6-1 », « R. 221-1 ») and article numbers (« article 13 », « art. 82 »,
« article 1er », « article 1-1 »), and every quotation between « » or " " of eight words or more. Text is compared lower-cased, with
spaces, line breaks, apostrophes, quote marks and dashes made one form.

Why: on 13 Nov. 2026 the agent called the CNIL's recommendation « n° 2026-042 » fifteen times; the number is in none of
the texts it was given, and only a person reading caught it. Case and article numbers were added on 17 Nov. 2026, when an invented « C-999/99 »
passed and pass 11 had cited GDPR articles 13 and 28 from memory. What a clean run guarantees: every listed kind of
reference is in a given text. What it does not: that a section number or a short phrase is right, that an article
number found belongs to the act the agent names (any given text holding « article 13 » clears it), or that a
reference found says what the agent makes it say. That stays the reader's, with rubric.md. Time O(text).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

NUMBER = re.compile(r"n°\s*\d{4}-\d{2,4}", re.I)
IDS = re.compile(r"\b(?:LEGIARTI|LEGITEXT|JORFTEXT)\d{8,}\b|\bCELEX:\s*\w+")
CASE = re.compile(r"\b[CT]-\d{1,4}/\d{2}\b")
CODE = re.compile(r"\b([LRD])\.?\s?(\d{1,4}(?:-\d{1,4}){1,3})\b")
ARTICLE = re.compile(r"\b(?:articles?|art\.)\s+(premier|1\s?er|\d+(?:-\d+)*)(?![\d/-])", re.I)
DASHES = str.maketrans({c: "-" for c in "\u2010\u2011\u2012\u2013\u2014\u2212"})
QUOTE = re.compile(r"«\s*([^«»]+?)\s*»|\"([^\"\n]+)\"")
MIN_WORDS = 8   # PROVISIONAL: a shorter quotation is often a term, which the text may inflect
MIN_PIECE = 4   # PROVISIONAL: a piece of a quotation around a marked cut, checked when it has this many words
EDIT = re.compile(r"\[[^\]]*\]")


def flat(text: str) -> str:
    """One form for what typography alone changes: case, spaces and line breaks, apostrophes, quote marks."""
    text = text.translate(DASHES).lower().replace("’", "'").replace("‘", "'")
    text = re.sub(r"[«»“”\"]", " ", text)
    return " ".join(text.split())


def read_texts(paths: list[Path]) -> str:
    """Every given text, one string; a folder gives each file under it."""
    files = [f for p in paths for f in ([p] if p.is_file() else sorted(p.rglob("*"))) if f.is_file()]
    return flat("\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files))


def article_key(number: str) -> str:
    """« article 1er », « article premier » and « art. 1 » are one key, « article 1 »."""
    number = number.lower().replace(" ", "")
    return "article " + ("1" if number in ("premier", "1er") else number)


def articles_in(text: str) -> set[str]:
    """The article keys a text holds: « article N » and code articles « L122-6-1 », in one form."""
    keys = {article_key(m.group(1)) for m in ARTICLE.finditer(text)}
    keys |= {(m.group(1) + m.group(2)).lower() for m in CODE.finditer(text.translate(DASHES).upper())}
    return keys


def missing(output: str, texts: str) -> list[str]:
    """The references and long quotations of `output` that `texts` does not hold, each once, in order."""
    out = []
    held = articles_in(texts)
    for m in CASE.finditer(output.translate(DASHES)):
        if m.group(0).lower() not in texts and m.group(0) not in out:
            out.append(m.group(0))
    for m in ARTICLE.finditer(output):
        key = article_key(m.group(1))
        if key not in held and key not in out:
            out.append(key)
    for m in CODE.finditer(output.translate(DASHES)):
        if (m.group(1) + m.group(2)).lower() not in held and m.group(0) not in out:
            out.append(m.group(0))
    found = [m.group(0) for m in NUMBER.finditer(output)] + [m.group(0) for m in IDS.finditer(output)]
    for m in QUOTE.finditer(output):
        quoted = m.group(1) or m.group(2)
        if len(quoted.split()) < MIN_WORDS:
            continue
        # a marked cut « [...] » or insertion « [les personnes] » is the quoter's; each piece around it must be found
        pieces = [p.strip() for p in EDIT.split(quoted) if len(p.split()) >= MIN_PIECE]
        found.extend(pieces if EDIT.search(quoted) else [quoted])
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
