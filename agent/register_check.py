#!/usr/bin/env python3
"""The legal agent's register, checked by a program: its columns, its states, one line per point and question, every
line traced to a unique source, the counts reconciled with the inputs, and no state only the approver may write.

  python3 register_check.py REGISTER.md [--before OLD.md] [--expect SOURCE=N ...] [--expect-issues N]

The register is the Markdown table of register.md, with English or French column names; accents are read in NFC,
curly apostrophes as straight ones, and an escaped pipe `\\|` stays inside its cell. Errors:
- no register table, no row, a row or the separator row whose cells differ in number from the header, a column named
  twice in the header, a column of register.md missing, column names of both languages in one header; every table
  whose header holds point and state is read;
- a state outside the five, or states of both languages in one register;
- a line with no source, or two lines with one source;
- two lines with the same issue, article, point and question;
- without --before: the version committed at HEAD is used when the file is tracked; when it is not, any line in
  "temporary" or "settled", which only the approver writes;
- with --before (the register before the agent's change, keyed by source): a line that became "temporary" or
  "settled", a line moved out of "settled" or "settled, to confirm", a temporary line moved anywhere but to
  "settled, to confirm" or whose approved measure or settle-by date changed, and a line of the old register missing;
- with --expect SOURCE=N: the lines whose source is SOURCE, or SOURCE followed by `#`, `:`, `/` or `,`, are not N;
- with --expect-issues N: the distinct issues the issue cells name are not N (a link and a reference to one issue
  count once, several issues in one cell each count, a draft counts none).
It prints the count of lines per source prefix, for the takeover's report. Exit 0 with no error, 1 otherwise.
A clean run guarantees the form and the counts, not that a line says the right thing. Time O(lines).
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

COLUMNS = {  # English name: French name, as register.md gives them
    "source": "source", "group": "groupe", "point": "point", "holds only if": "vaut seulement si", "article": "article",
    "link": "lien", "read on": "lu le", "grade": "niveau", "what a text attaches": "ce que le texte attache",
    "what bears on it": "ce qui l'éclaire", "what we do": "ce que nous faisons", "witness": "témoin",
    "to establish first": "à établir d'abord", "question": "question", "who answers": "qui répond",
    "asked on": "demandé le", "issue": "ticket", "when it must hold": "avant quand", "what it stops": "ce qu'il bloque",
    "answer": "réponse", "state": "état", "temporary measure": "mesure provisoire", "risk": "risque",
    "settle by": "à régler avant", "prior note": "note antérieure",
}
STATES_EN = {"open", "measure proposed", "temporary", "settled, to confirm", "settled"}
STATES_FR = {"ouvert", "mesure proposée", "provisoire", "réglé, à confirmer", "réglé"}
APPROVER_ONLY = {"temporary", "settled", "provisoire", "réglé"}
APPROVER_EXIT = {"settled", "réglé", "settled, to confirm", "réglé, à confirmer"}
TEMPORARY = {"temporary", "provisoire"}
TO_CONFIRM = {"settled, to confirm", "réglé, à confirmer"}
ISSUE = re.compile(r"github\.com/([\w.-]+)/([\w.-]+)/issues/(\d+)|([\w.-]+/[\w.-]+)#(\d+)|(?<![\w/])#(\d+)")
SHORT_ISSUE = re.compile(r"(?<![\w./-])(?:[\w-]+)?#\d+")


def norm(text: str) -> str:
    text = unicodedata.normalize("NFC", text).replace("’", "'")
    return re.sub(r"[*`_]", "", text).strip().lower()


def cells_of(line: str) -> list[str]:
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") and not body.endswith("\\|") else body
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", body)]


def read(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    """The register's lines keyed by the English column names, each with the language of its table's header, and the
    problems of reading it. Every table whose header holds point and state is read."""
    french = {fr: en for en, fr in COLUMNS.items()}
    both = set(COLUMNS) & set(COLUMNS.values())
    rows, header, language, problems = [], None, "en", []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.lstrip().startswith("|"):
            header = None
            continue
        cells = cells_of(line)
        if header is None:
            raw = [norm(c) for c in cells]
            names = [french.get(c, c) for c in raw]
            if "point" in names and "state" not in names:
                problems.append(f"line {number} of the file: a table with a point column and no state column")
            if "state" in names and "point" in names:
                header = names
                english = {c for c in raw if c in COLUMNS and c not in both}
                french_names = {c for c in raw if c in french and c not in both}
                if english and french_names:
                    problems.append(f"line {number} of the file: column names of both languages in one header")
                language = "fr" if french_names else "en"
                twice = sorted({n for n in names if names.count(n) > 1})
                if twice:
                    problems.append(f"line {number} of the file: a column named twice in the header: " + ", ".join(twice))
                missing = [c for c in COLUMNS if c not in names]
                if missing:
                    problems.append(f"line {number} of the file: a table missing the columns " + ", ".join(missing))
            continue
        if set("".join(cells)) <= set("-: "):
            if len(cells) != len(header):
                problems.append(f"line {number} of the file: the separator row has {len(cells)} cells where the header has {len(header)}")
            continue
        if len(cells) != len(header):
            problems.append(f"line {number} of the file: {len(cells)} cells where the header has {len(header)}")
            continue
        rows.append({**dict(zip(header, cells)), "__language__": language})
    if header is None and not rows:
        problems.append("no register table: no header holds both point and state")
    elif not rows:
        problems.append("the register table has no row")
    return rows, problems


def problems(rows: list[dict], before: list[dict] | None, expect: dict[str, int], issues: int | None) -> list[str]:
    out = []
    states = [norm(r.get("state", "")) for r in rows]
    if any(s in STATES_EN for s in states) and any(s in STATES_FR - STATES_EN for s in states):
        out.append("states of both languages in one register: write them all in the company's language")
    for n, (row, state) in enumerate(zip(rows, states), 1):
        if row.get("__language__") == "fr" and state in STATES_EN - STATES_FR:
            out.append(f"line {n}: an English state in a register whose columns are French")
        if row.get("__language__") == "en" and state in STATES_FR - STATES_EN:
            out.append(f"line {n}: a French state in a register whose columns are English")
    keys, sources = Counter(), Counter()
    for n, (row, state) in enumerate(zip(rows, states), 1):
        if state not in STATES_EN | STATES_FR:
            out.append(f"line {n}: state {row.get('state')!r} is not one of the five")
        source = row.get("source", "").strip()
        if not source:
            out.append(f"line {n}: no source")
        else:
            sources[source] += 1
            if sources[source] == 2:
                out.append(f"line {n}: source {source!r} is already another line's")
        key = tuple(norm(row.get(c, "")) for c in ("issue", "article", "point", "question"))
        keys[key] += 1
        if keys[key] == 2:
            out.append(f"line {n}: same issue, article, point and question as an earlier line")
        if state in TO_CONFIRM and not row.get("answer", "").strip():
            out.append(f"line {n}: settled, to confirm, with no answer recorded")
        if before is None and state in APPROVER_ONLY:
            out.append(f"line {n}: state {state!r}, which only the approver writes; give --before to show it was already there")
    if before is not None:
        old = {r.get("source", "").strip(): norm(r.get("state", "")) for r in before}
        old_rows = {r.get("source", "").strip(): r for r in before}
        now = {r.get("source", "").strip() for r in rows}
        for n, (row, state) in enumerate(zip(rows, states), 1):
            was = old.get(row.get("source", "").strip())
            if state in APPROVER_ONLY and was != state:
                out.append(f"line {n}: state became {state!r}, which only the approver writes")
            if was in APPROVER_EXIT and state != was:
                out.append(f"line {n}: moved out of {was!r}, which only the approver does")
            prior_row = old_rows.get(row.get("source", "").strip())
            if was in APPROVER_EXIT and state == was and prior_row is not None:
                changed = [c for c in COLUMNS if norm(row.get(c, "")) != norm(prior_row.get(c, ""))]
                if changed:
                    out.append(f"line {n}: a {was!r} line changed ({', '.join(changed)}), which only the approver does")
            if was in TEMPORARY and state not in TEMPORARY | TO_CONFIRM:
                out.append(f"line {n}: a temporary line leaves only to settled, to confirm, when an answer is recorded")
            prior = old_rows.get(row.get("source", "").strip())
            if was in TEMPORARY and prior is not None:
                for column in ("temporary measure", "settle by"):
                    if norm(row.get(column, "")) != norm(prior.get(column, "")):
                        out.append(f"line {n}: the approved {column} of a temporary line changed; propose a renewal beside it")
        for source in old:
            if source and source not in now:
                out.append(f"line with source {source!r} is missing from the new register")
    for prefix, n in expect.items():
        got = sum(1 for r in rows if re.match(re.escape(prefix) + r"($|[#:/,])", r.get("source", "").strip()))
        if got != n:
            out.append(f"source {prefix}: {got} lines, the input holds {n}")
    for n, row in enumerate(rows, 1):
        cell = ISSUE.sub(lambda m: "" if m.group(3) or m.group(5) else m.group(0), row.get("issue", ""))
        if SHORT_ISSUE.search(cell):
            out.append(f"line {n}: an issue reference without its owner and repository; write owner/repo#N")
    if issues is not None:
        got = len(issue_refs(rows))
        if got != issues:
            out.append(f"{got} distinct issues, the input holds {issues}")
    return out


def issue_refs(rows: list[dict]) -> set[str]:
    """Every distinct issue the issue cells name, a link and a reference counted once, drafts left out."""
    refs = set()
    for row in rows:
        for m in ISSUE.finditer(row.get("issue", "")):
            if m.group(3):
                refs.add(f"{m.group(1)}/{m.group(2)}#{m.group(3)}".lower())
            elif m.group(5):
                refs.add(f"{m.group(4)}#{m.group(5)}".lower())
            else:
                refs.add(f"#{m.group(6)}")
    return refs


def counts_by_source(rows: list[dict]) -> Counter:
    return Counter(re.split(r"[#:/,]", r.get("source", ""), maxsplit=1)[0].strip() for r in rows)


def from_git(path: Path):
    """The register as committed at HEAD, when the file is tracked: the default --before. A person commits the register; the agent never does."""
    import subprocess, tempfile
    folder = path.resolve().parent
    top = subprocess.run(["git", "-C", str(folder), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode:
        return None
    rel = path.resolve().relative_to(top.stdout.strip())
    shown = subprocess.run(["git", "-C", top.stdout.strip(), "show", f"HEAD:{rel}"], capture_output=True, text=True)
    if shown.returncode:
        return None
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as handle:
        handle.write(shown.stdout)
    return read(Path(handle.name))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("register", type=Path)
    parser.add_argument("--before", type=Path)
    parser.add_argument("--expect", nargs="*", default=[])
    parser.add_argument("--expect-issues", type=int)
    args = parser.parse_args()
    rows, found = read(args.register)
    before = None
    if args.before:
        before, old_problems = read(args.before)
        found += [f"--before: {p}" for p in old_problems]
    else:
        committed = from_git(args.register)
        if committed is not None:
            print("--before: the version committed at HEAD")
            before, old_problems = committed
            found += [f"--before (HEAD): {p}" for p in old_problems]
    try:
        expect = {k: int(v) for k, v in (e.rsplit("=", 1) for e in args.expect)}
    except ValueError:
        parser.error("--expect takes SOURCE=N, N a whole number")
    for source, n in sorted(counts_by_source(rows).items()):
        print(f"{n}\t{source}")
    found += problems(rows, before, expect, args.expect_issues)
    for p in found:
        print("error:", p)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
