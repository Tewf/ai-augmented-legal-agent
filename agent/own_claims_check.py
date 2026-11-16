#!/usr/bin/env python3
"""The legal agent's statements about its own files, checked against the files, by a program.

  python3 own_claims_check.py REPORT.md --register REGISTER.md [--files F.md ...] [--texts DIR_OR_FILE ...] [--act ACTE.md]
      exit 0 when no statement is contradicted, 1 otherwise

Why: on 16 Nov. 2026 five passes of the agent on one act (work/2026-11-16_law-2) each ended with a section « Passe N » or
« Gardes » of statements about the agent's own output, and a fresh reader found some of them false by hand: « la ligne de
séparation a 25 cellules » over a 26-cell row, « le singulier ... ne reste que dans la question de l'acte » over a register
cell that still holds it, « cité ... dans la cellule article » over a cell that does not hold it, a hash cut to 39 characters,
« les trois gardes n'ont pas encore été exécutés » in a finished report. This file checks the forms below, and no others.

Checked, in the report's own words:
- a count: « la ligne de séparation / l'en-tête a N cellules », « N cellules comme les deux lignes », « N lignes dans
  register.md », against the register table;
- a presence: an item that says a quotation « ... » (five words or more) or a reference (considérant N, article N, art. N)
  is « cité / repris / figure » in `question-1.md`, in « les deux brouillons », in « la cellule X de la ligne N » or in
  « la ligne N du registre » or « ce rapport », against those files (the item's first parenthesis, its label, is not read);
- an absence: an item that says a quotation « ... » « ne reste que dans », « n'apparaît plus », « ne figure plus » or
  « est supprimé », against the register, the other files and the report outside its Passe sections; a line that holds
  a whole line of the act (--act) is the act's own question, quoted, and is let through;
- a hash: a run of 32 hexadecimal characters or more that is not 64, or a 64 that no given text writes and that is not the
  sha256 of a given file;
- the guards: a sentence saying the three guards « n'ont pas encore été exécutés » in a report that is finished.

What a clean run guarantees: none of these forms is contradicted by the files. What it does not: a statement in another
form (« la raison repose non sur la mesure ni sur la date de la ligne 1 »), a statement about meaning, or a count
the report does not give. That stays the fresh reader's. Quotations and references are compared in lower case, with
spaces, apostrophes and guillemets made one form. Time O(text x items).
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import register_check  # noqa: E402  (the one reader of the register's table)

NUMBER_WORDS = {"un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6}
QUOTE = re.compile(r"«\s*([^«»]+?)\s*»")
REFERENCE = re.compile(r"\b(considérant \d+|article \d+|art\. \d+)(?![\d-])", re.I)
FILE = re.compile(r"`?(question-[12]\.md|result\.md|register\.md|search-log\.md)`?")
CELL = re.compile(r"cellule\s+([\w'’ ]+?)\s+de la ligne\s+(\d+)")
LINE_OF_REGISTER = re.compile(r"ligne\s+(\d+)\s+du\s+registre")
SHE_CELL = re.compile(r"\bsa cellule\s+([\w'’]+)")
PRESENT = re.compile(r"\b(cité|citée|citées|cités|repris|reprise|reprises|repris|figure|figurent|écrit|écrite|écrits|écrites)\b", re.I)
ABSENT = re.compile(r"ne reste que|n'apparaît plus|n'apparaissent plus|ne figure plus|ne figurent plus|est supprimé|sont supprimés|a disparu", re.I)
NOT_RUN = re.compile(r"garde[s]?[^.\n]{0,100}n'(?:ont|a) pas (?:encore )?été (?:exécuté|lancé|passé)", re.I)
PASSE = re.compile(r"^##\s+Passe\b", re.I)
LABEL = re.compile(r"^\s*(?:\d+[.)]|[-*])\s*\([^)]*\)")   # the finding an item answers, which says what was wrong
CORRECTED = re.compile(r"\[corrigé|corrigé en passe|\bcorrigée?\b", re.I)


def flat(text: str) -> str:
    """One form for what typography alone changes: case, spaces, apostrophes, quotation marks and backticks."""
    text = text.lower().replace("’", "'").replace("‘", "'")
    text = re.sub(r"[«»“”\"`*]", " ", text)
    text = re.sub(r"\barticles?\b", "art.", text)       # « article 1 » and « art. 1 » are one reference
    return " ".join(text.split())


def sections(report: str) -> tuple[str, list[str]]:
    """The report outside its Passe sections, and the items of those sections (a numbered or bulleted line and what
    follows it up to the next item)."""
    body, items, inside = [], [], False
    for line in report.splitlines():
        if line.startswith("## "):
            inside = bool(PASSE.match(line))
            if not inside:
                body.append(line)
            continue
        if not inside:
            body.append(line)
        elif re.match(r"^\s*(?:\d+[.)]|[-*])\s", line) or not items:
            items.append(line)
        elif line.strip():
            items[-1] += " " + line.strip()
    return "\n".join(body), items


def register_facts(path: Path) -> dict:
    """Cell counts and the lines of the register, read as the register check reads them (the table with point and state)."""
    counts, rows, header = {}, [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            header = None if header and rows else header
            continue
        cells = register_check.cells_of(line)
        if header is None:
            names = [register_check.norm(c) for c in cells]
            if "point" in names:
                header, counts["header"] = names, len(cells)
            continue
        if set("".join(cells)) <= set("-: "):
            counts["separator"] = len(cells)
            continue
        rows.append(dict(zip(header, [c for c in cells])))
        counts.setdefault("rows", []).append(len(cells))
    return {"counts": counts, "rows": rows}


def number(token: str) -> int | None:
    token = token.lower()
    return int(token) if token.isdigit() else NUMBER_WORDS.get(token)


def check_counts(report_text: str, facts: dict, label: str) -> list[str]:
    out, counts = [], facts["counts"]
    for n, line in enumerate(report_text.splitlines(), 1):
        line = LABEL.sub("", line)
        for clause in re.split(r"[;:]|, et |\. ", line):
            if re.search(r"\bplus\b|avait|ancien|\bavant\b", clause, re.I):
                continue
            for subject, key in (("séparation", "separator"), ("en-tête", "header"), ("entête", "header")):
                m = re.search(rf"{subject}\D{{0,60}}?(\d+)\s+(?:cellules|colonnes)", clause, re.I)
                if m and key in counts and int(m.group(1)) != counts[key]:
                    out.append(f"{label}:{n}: says the {subject} has {m.group(1)} cells; the register's has {counts[key]}")
            m = re.search(r"(\d+)\s+(?:cellules|colonnes)\s+comme\s+les\s+(?:deux\s+)?lignes", clause, re.I)
            if m and counts.get("rows") and any(c != int(m.group(1)) for c in counts["rows"]):
                out.append(f"{label}:{n}: says the lines have {m.group(1)} cells; the register's have {counts['rows']}")
            m = re.search(r"\b(\w+)\s+lignes?\s+(?:dans|du)\s+`?register\.md", clause, re.I)
            if m and number(m.group(1)) is not None and counts.get("rows") is not None and number(m.group(1)) != len(counts["rows"]):
                out.append(f"{label}:{n}: says {m.group(1)} lines in register.md; the register has {len(counts['rows'])}")
    return out


def item_keys(item: str) -> list[str]:
    """What an item says is cited: its quotations of five words or more, then its references; its label, the first
    parenthesis after the number, is not read."""
    item = re.sub(r"^\s*(?:\d+[.)]|[-*])\s*\([^)]*\)", "", item)
    keys = [flat(q) for q in QUOTE.findall(item) if len(q.split()) >= 5]
    keys += [flat(r) for r in REFERENCE.findall(item)]
    return keys


def targets(item: str, files: dict[str, str], report_body: str, facts: dict) -> list[tuple[str, str]]:
    """The places an item names, each as (name, text)."""
    found, last_line = [], None
    for name in dict.fromkeys(FILE.findall(item)):
        if name in files:
            found.append((name, files[name]))
    if re.search(r"deux brouillons", item):
        found += [(n, files[n]) for n in ("question-1.md", "question-2.md") if n in files]
    if re.search(r"\bce rapport\b|\bla question [12] de ce rapport", item):
        found.append(("this report", report_body))
    for column, number_ in CELL.findall(item):
        last_line = int(number_)
        found.append((f"the cell {column} of line {number_}", cell_text(facts, last_line, column)))
    for column in SHE_CELL.findall(item):
        if last_line:
            found.append((f"the cell {column} of line {last_line}", cell_text(facts, last_line, column)))
    for number_ in LINE_OF_REGISTER.findall(item):
        if not CELL.search(item):
            found.append((f"line {number_} of the register", " ".join(cells_of_line(facts, int(number_)))))
    return found


def cells_of_line(facts: dict, n: int) -> list[str]:
    return list(facts["rows"][n - 1].values()) if 0 < n <= len(facts["rows"]) else []


def cell_text(facts: dict, n: int, column: str) -> str:
    if not 0 < n <= len(facts["rows"]):
        return ""
    wanted = register_check.norm(column)
    for name, value in facts["rows"][n - 1].items():
        if name == wanted or register_check.COLUMNS.get(name) == wanted or name.startswith(wanted):
            return value
    return ""


def act_lines(path: Path | None) -> list[str]:
    if path is None:
        return []
    return [flat(re.sub(r"^\s*(?:\d+[.)]|[-*#>])\s*", "", l)) for l in path.read_text(encoding="utf-8").splitlines() if len(l.split()) >= 8]


CHANGE = re.compile(r"remplac|ne dit plus|ne cite plus|n'est plus cité|supprim|retir|déplac|reformul|devient|devenu|ajout", re.I)
GONE = re.compile(r"«\s*([^«»]{8,}?)\s*»[\s,]{0,3}(?:" + ABSENT.pattern + ")", re.I)


def segments(text: str) -> list[str]:
    """A line of the text; a table row is cut into its cells, since a row holds the act's own question in one cell and
    other words in the next."""
    out = []
    for line in text.splitlines():
        out += register_check.cells_of(line) if line.lstrip().startswith("|") else [line]
    return out


def sentences_of(item: str) -> list[str]:
    item = re.sub(r"^\s*(?:\d+[.)]|[-*])\s*\([^)]*\)", "", item)
    return [s.strip() for s in re.split(r"(?<=[.;])\s+(?=[A-ZÀ-Ý«(])|;\s+", item) if s.strip()]


def check_items(items: list[str], files: dict[str, str], report_body: str, facts: dict, act: list[str], label: str) -> list[str]:
    out = []
    for item in items:
        head = item.strip()[:70]
        for sentence in sentences_of(item):
            for quote in ([] if CORRECTED.search(item) else GONE.findall(sentence)):
                key = flat(quote[0] if isinstance(quote, tuple) else quote)
                if len(key.split()) < 3:
                    continue
                for name, text in files.items():
                    for segment in segments(text):
                        flat_segment = flat(segment)
                        if key in flat_segment and not any(a in flat_segment for a in act):
                            out.append(f"{label}: «{head}…» says « {key} » is gone, and {name} still holds it: {segment.strip()[:110]}")
                            break
            if CHANGE.search(sentence) or CORRECTED.search(item) or not PRESENT.search(sentence):
                continue
            keys = [flat(q) for q in QUOTE.findall(sentence) if len(q.split()) >= 5]
            keys = keys or [flat(r) for r in REFERENCE.findall(sentence)]
            for name, text in targets(sentence, files, report_body, facts):
                for key in dict.fromkeys(keys):
                    if key not in flat(text):
                        out.append(f"{label}: «{head}…» says « {key} » is in {name}, and it is not")
    return list(dict.fromkeys(out))


def check_hashes(texts: list[Path], files: dict[str, str], report_body: str, report_items: list[str], label: str) -> list[str]:
    known = set()
    for base in texts:
        for f in [base] if base.is_file() else sorted(base.rglob("*")):
            if f.is_file():
                data = f.read_bytes()
                known.add(hashlib.sha256(data).hexdigest())
                known |= set(re.findall(r"\b[0-9a-f]{64}\b", data.decode("utf-8", "ignore").lower()))
    out = []
    for name, text in {**files, "this report": report_body + "\n" + "\n".join(report_items)}.items():
        for n, line in enumerate(text.splitlines(), 1):
            for token in re.findall(r"\b[0-9a-f]{32,}\b", line.lower()):
                if len(token) != 64:
                    out.append(f"{name}:{n}: a hash of {len(token)} characters, where a sha256 has 64: {token[:20]}…")
                elif texts and token not in known:
                    out.append(f"{name}:{n}: the hash {token[:12]}… is no given text's and no given file's")
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("report", type=Path)
    parser.add_argument("--register", type=Path, required=True)
    parser.add_argument("--files", type=Path, nargs="*", default=[], help="the other output files: question-1.md, search-log.md, ...")
    parser.add_argument("--texts", type=Path, nargs="*", default=[], help="the texts and inputs the agent was given")
    parser.add_argument("--act", type=Path)
    args = parser.parse_args(argv)
    text = args.report.read_text(encoding="utf-8")
    body, items = sections(text)
    files = {f.name: f.read_text(encoding="utf-8") for f in [args.register, *args.files]}
    files[args.report.name] = body
    facts = register_facts(args.register)
    act = act_lines(args.act)
    problems = check_counts(text, facts, args.report.name)
    problems += check_items(items, files, body, facts, act, args.report.name)
    problems += check_hashes(args.texts, files, body, items, args.report.name)
    for n, line in enumerate(body.splitlines(), 1):
        if NOT_RUN.search(line):
            problems.append(f"{args.report.name}: says the guards were not run, in a finished report: {line.strip()[:120]}")
    print("\n".join(problems) if problems else "own_claims_check: no statement contradicted")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
