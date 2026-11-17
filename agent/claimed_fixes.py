#!/usr/bin/env python3
"""Check that each fix an agent's report claims is in the files it says it changed.

    python3 claimed_fixes.py OUTDIR [--report FILE]     exit 0 every checked claim holds, 1 a claimed fix is absent, 2 usage

Why: on 17 Nov. 2026 a legal agent ran to its deadline twice and ended with a « Passe 13 » list of twenty fixes, six of which were
not in its files (work/2026-11-16_law-1/reader-13/reader.md). The three programs of its skill check the form of its output, not
whether what it says it did is true. This one reads the report's numbered items, takes the words each puts between « », reads from
the words before them whether the item says the wording is gone or is there, and greps the files the item names.

own_claims_check.py reads other forms (a count, « cité dans », « ne reste que dans », a hash); this one reads the forms it
leaves: « ne dit plus « ... » », « plus de « ... » », « ni « ... » », « dit « ... » », « porte « ... » ». On pass 13's report
the first finds nothing and this one finds six absent fixes.

The report is the last section headed `## Passe N` of result.md (or `--report FILE`). The files checked are `result.md` without
that section, `register.md`, `search-log.md` and the drafts `brouillon-*.md` of OUTDIR; an item that names `brouillon-NN`, `registre`
or `result.md` narrows the check to those files, one that names none checks them all.

A claim is read only when the words before the quoted span say so (the lists below); every other span is reported as « not read »,
never as holding. What a run guarantees: a span that the report says is gone and is still in a scoped file, or says is there and is
in none, is listed and the exit code is 1. What it does not: that the fix is right, that a fix claimed without quoted words (a page
number, a re-attributed sentence) was made, nor a paraphrase: the wording is compared after lower-casing and collapsing spaces.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True       # a run's folder is sealed: importing a sibling must not write a cache into it

GONE = re.compile(r"(\bni\b|ne\s+\w+(?:\s+\w+)?\s+plus|n['’]est\s+plus|plus\s+(?:aucun|aucune|de|d['’])|\bnon\b|\bsans\b|supprim|retir|vid[ée])", re.I)
THERE = re.compile(r"(\bdits?\b|\bcite\b|\bcité|\bporte\b|\btient\b|\btiennent\b|\bécrit\b|\bremplac\w+ par\b|\bnomme\b)", re.I)
QUOTE = re.compile(r"«\s*(.+?)\s*»", re.S)
ITEM = re.compile(r"^(\d+)\.\s+(.*?)(?=^\d+\.\s|\Z)", re.S | re.M)


def norm(text: str) -> str:
    text = text.replace("’", "'").replace("…", " ").replace(" ", " ").replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip().lower()


def split_report(result: str, report: str | None) -> tuple[str, str]:
    """(the body of result.md, the report): the last `## Passe N` section is the report unless a file is given."""
    heads = list(re.finditer(r"^## Passe \d+\s*$", result, re.M))
    if report is not None:
        return result, report
    if not heads:
        return result, ""
    last = heads[-1]
    return result[: last.start()], result[last.end():]


def scope(item: str, files: dict[str, str]) -> dict[str, str]:
    named = {}
    for number in re.findall(r"brouillon-0?(\d)", item):
        for name, text in files.items():
            if re.match(rf"brouillon-0?{number}", name):
                named[name] = text
    if re.search(r"huit\s+(?:fichiers|brouillons)|\bles brouillons\b|chaque brouillon", item, re.I):
        named.update({n: t for n, t in files.items() if n.startswith("brouillon")})
    if re.search(r"\bregistre\b|register|\bligne\s+\d|\bcellule\b|\bcolonne\b", item, re.I):
        named["register.md"] = files["register.md"]
    if re.search(r"result\.md|ce rapport", item, re.I):
        named["result.md"] = files["result.md"]
    if re.search(r"search-log", item, re.I):
        named["search-log.md"] = files.get("search-log.md", "")
    return named or files


def check(outdir: Path, report_file: Path | None = None) -> tuple[list[str], list[str], int]:
    """(absent claims, spans not read, spans that hold)."""
    result = (outdir / "result.md").read_text(encoding="utf-8")
    body, report = split_report(result, report_file.read_text(encoding="utf-8") if report_file else None)
    files = {"result.md": body}
    for path in sorted(outdir.glob("*.md")):
        if path.name not in ("result.md",):
            files[path.stem if path.name.startswith("brouillon") else path.name] = path.read_text(encoding="utf-8")
    absent, unread, holds = [], [], 0
    for number, item in ITEM.findall(report):
        scoped = scope(item, files)
        for span in QUOTE.finditer(item):
            words = span.group(1)
            before = item[max(0, span.start() - 70): span.start()]
            gone, there = GONE.search(before), THERE.search(before)
            if gone is None and there is None:
                unread.append(f"item {number}: « {' '.join(words.split())[:70]} »")
                continue
            expect_gone = bool(gone) and (not there or gone.start() > there.start() or "plus" in before.lower())
            found_in = [name for name, text in scoped.items() if norm(words) in norm(text)]
            if expect_gone and found_in:
                absent.append(f"item {number}: says « {' '.join(words.split())[:70]} » is gone, still in {', '.join(found_in)}")
            elif not expect_gone and not found_in:
                absent.append(f"item {number}: says « {' '.join(words.split())[:70]} » is there, in none of {', '.join(scoped)}")
            else:
                holds += 1
    return absent, unread, holds


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("outdir", type=Path)
    parser.add_argument("--report", type=Path, help="the report, when it is not the last `## Passe N` section of result.md")
    args = parser.parse_args(argv)
    if not (args.outdir / "result.md").is_file():
        print(f"claimed_fixes: no result.md in {args.outdir}", file=sys.stderr)
        return 2
    absent, unread, holds = check(args.outdir, args.report)
    for line in absent:
        print(f"claimed_fixes: {line}")
    print(f"claimed_fixes: {holds} claim(s) hold, {len(absent)} claimed fix(es) absent, {len(unread)} span(s) not read")
    return 1 if absent else 0


if __name__ == "__main__":
    sys.exit(main())
