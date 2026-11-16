#!/usr/bin/env python3
"""The legal agent's temporary measures, checked for the conditions they name, by a program.

  python3 measure_check.py REGISTER.md          exit 0 when no measure is refused, 1 otherwise

Why: on 16 Nov. 2026 the readers of five passes of the agent (work/2026-11-16_law-2) found the same fault in the measure
cell of the register again and again: a measure whose condition does not test what it names. « si cette provenance n'est
pas établie, remplacer ... » tests whether a fact is known, where the question is what the fact is; « si cette provenance
est qu'elle vient d'une personne identifiable » on the line of a question that never speaks of provenance; a measure that
opens with « établir d'abord » over an empty « à établir d'abord » cell; the same change proposed under a condition on one
line and with none on the next. This file refuses those four forms, and no others.

Refused, per line, in the cell « mesure provisoire » (temporary measure):
- a « si » clause that tests a state of knowledge (« n'est pas établi », « est vérifié », « soit connu »): it must say
  the value the fact takes, since the measure applies to a value;
- a « si » clause none of whose words of seven letters or more is in the line's own question, point or « vaut seulement si »:
  it conditions the measure on a fact the line does not ask about;
- a measure that says « établir d'abord » (or vérifier, déterminer, identifier d'abord) while the line's « à établir d'abord »
  is empty: the fact it starts from has no cell;
- a change (« remplacer », « retirer », « suspendre » and what follows it) that two lines propose, one under a « si » clause
  and one with none.

What a clean run guarantees: none of those four forms is in the register. What it does not: that a condition is the right
one, that the words it shares with the question are the ones that matter, or that a measure is the least restrictive.
That stays with the reader and the approver. Time O(lines squared).
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import register_check  # noqa: E402  (the one reader of the register's table)

KNOWLEDGE = re.compile(r"\bsi\b[^,;]*?\b(?:n'est pas|n'a pas été|ne sont pas|est|soit|sont|a été|ont été)\s+(?:encore\s+)?"
                       r"(?:établi|vérifi|connu|trouvé|su\b|résolu|terminé|déterminé|identifié|lu)", re.I)
IF_CLAUSE = re.compile(r"\bsi\b\s+([^,;]+)", re.I)
FIRST = re.compile(r"(?:établir|vérifier|déterminer|identifier|connaître)\s+d'abord|à établir d'abord", re.I)
ACTION = re.compile(r"\b(remplacer|retirer|suspendre)\b\s+([^;,]{0,70})", re.I)


def words(text: str) -> set[str]:
    text = unicodedata.normalize("NFC", text).lower().replace("’", "'")
    return {w for w in re.findall(r"[a-zàâçéèêëîïôûùüÿœ]{7,}", text)}


def check(rows: list[dict]) -> list[str]:
    out, actions = [], {}
    for n, row in enumerate(rows, 1):
        measure = row.get("temporary measure", "")
        if not measure.strip():
            continue
        own = words(" ".join(row.get(c, "") for c in ("question", "point", "holds only if")))
        for clause in IF_CLAUSE.findall(measure):
            if KNOWLEDGE.search("si " + clause):
                out.append(f"line {n}: the condition « si {clause.strip()} » tests whether a fact is established, not what it is; "
                           f"say the value the measure applies to")
            elif words(clause) and not words(clause) & own:
                out.append(f"line {n}: the condition « si {clause.strip()} » shares no word of seven letters with the line's own "
                           f"question, point or « vaut seulement si »: it conditions the measure on a fact the line does not ask about")
        if FIRST.search(measure) and not row.get("to establish first", "").strip():
            out.append(f"line {n}: the measure starts by establishing a fact, and « à établir d'abord » is empty")
        action = ACTION.search(measure)
        if action:
            key = re.sub(r"\s+", " ", (action.group(1) + " " + action.group(2)).lower()).strip()
            actions.setdefault(key, []).append((n, bool(IF_CLAUSE.search(measure))))
    for key, lines in actions.items():
        if len({conditional for _, conditional in lines}) == 2:
            under = [n for n, c in lines if c]
            free = [n for n, c in lines if not c]
            out.append(f"lines {free} propose « {key} » with no condition, and lines {under} propose it under a « si » clause")
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.splitlines()[0], file=sys.stderr)
        return 2
    rows, problems = register_check.read(Path(argv[0]))
    found = [f"register: {p}" for p in problems] + check(rows)
    print("\n".join(found) if found else f"measure_check: {len(rows)} line(s), no measure refused")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
