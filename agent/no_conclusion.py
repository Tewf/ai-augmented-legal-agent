#!/usr/bin/env python3
"""The legal agent's rule "never conclude", checked by a program: list every sentence of a text that states a legal
reading as settled. Every prompt runs it on its output before returning (SKILL.md).

  python3 no_conclusion.py FILE.md [FILE.md ...]     exit 0 when no sentence concludes, 1 otherwise

A sentence concludes when it holds a phrase of no-conclusion.toml, in French or English, outside a quotation, and does
not end on a question mark. Ported from the issue verifier of the legal track of 11 Nov. 2026.

What a clean run guarantees: no listed phrase states a reading as the agent's own. What it does not: that an unlisted
phrase, a quotation used as the agent's own words, or a conclusion phrased as a question does not conclude. That is
the fresh reader's job, with rubric.md, on a sample of every run (SKILL.md). Time O(text x phrases).
"""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

PHRASES = tomllib.loads((Path(__file__).resolve().parent / "no-conclusion.toml").read_text(encoding="utf-8"))
QUOTED = re.compile(r"«[^«»|]*»|“[^“”|]*”|\"[^\"\n|]*\"|`[^`\n|]*`")


BLOCK = re.compile(r"^\s*(?:[-*+]\s|#+\s|\d+[.)]\s|\||>)")


def sentences(text: str) -> list[str]:
    """Sentences, split first at blank lines, list items, headings, table rows and quotes, then at punctuation: a
    bullet with no final stop never merges with the question after it."""
    blocks, current = [], []
    for line in QUOTED.sub(" ", text).splitlines():
        if not line.strip() or BLOCK.match(line):
            if current:
                blocks.append(" ".join(current))
            current = [line] if line.strip() else []
        else:
            current.append(line)
    if current:
        blocks.append(" ".join(current))
    out = []
    for block in blocks:
        flat = re.sub(r"\s+", " ", re.sub(r"^\s*(?:[-*+]|#+|\d+[.)]|>)\s*", "", block))
        out += [part.strip() for part in re.split(r"(?<=[.!?:;])\s+|\s?\|\s?", flat) if part.strip()]
    return out


def conclusions(text: str) -> list[tuple[str, str]]:
    """(phrase, sentence) for each sentence that states a reading as settled."""
    found = []
    for sentence in sentences(text):
        if sentence.endswith("?"):
            continue
        low = sentence.lower().replace("’", "'")
        for phrase in PHRASES["fr"] + PHRASES["en"]:
            if re.search(r"(?<!\w)" + re.escape(phrase.replace("’", "'")) + r"(?!\w)", low):
                found.append((phrase, sentence))
                break
        else:
            for pattern in PHRASES.get("patterns", []):
                if re.search(pattern, low):
                    found.append((pattern, sentence))
                    break
    return found


def main() -> int:
    bad = 0
    for name in sys.argv[1:]:
        for phrase, sentence in conclusions(Path(name).read_text(encoding="utf-8")):
            print(f"{name}: concludes ({phrase!r}): {sentence[:160]}")
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
