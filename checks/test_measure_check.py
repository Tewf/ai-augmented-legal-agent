"""Tests of agent/measure_check.py, from the real measure cells of the five passes of work/2026-11-16_law-2 (16 Nov. 2026).
Run: python3 -m unittest discover -s checks
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

AGENT = Path(__file__).resolve().parents[1] / "agent"
spec = importlib.util.spec_from_file_location("measure_check", AGENT / "measure_check.py")
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)
rc = mc.register_check

COLS = list(rc.COLUMNS)
Q1 = "La demande « ma dépression », montrée sur deux cartes publiques, est-elle une donnée concernant la santé, selon qu'elle vient d'une personne identifiable ou qu'elle a été écrite par la maison ?"
Q2 = "Un parfum d'exemple montré en réponse à une demande qui nomme un état de santé peut-il être lu comme lui attribuant une fonction qu'il n'a pas ?"
CHANGE = "remplacer sur les deux cartes la demande « ma dépression » par une formulation ne nommant pas un état de santé, jusqu'à la réponse du juriste"


def rows(*lines):
    names = [rc.COLUMNS[c] for c in COLS]
    text = ["| " + " | ".join(names) + " |", "|" + "---|" * len(names)]
    for i, kw in enumerate(lines, 1):
        base = {"source": f"acte.md, question {i}", "state": "mesure proposée", "article": "art. 1", "issue": f"brouillon : q{i}.md"}
        base.update(kw)
        text.append("| " + " | ".join(base.get(c, "") for c in COLS) + " |")
    path = Path(tempfile.mkdtemp()) / "r.md"
    path.write_text("\n".join(text) + "\n", encoding="utf-8")
    data, problems = rc.read(path)
    return data


class Conditions(unittest.TestCase):
    def test_a_condition_on_a_fact_being_established_is_refused(self):
        r = rows({"question": Q1, "temporary measure": f"si cette provenance n'est pas établie, {CHANGE}"})
        self.assertTrue(any("tests whether a fact is established" in p for p in mc.check(r)), mc.check(r))

    def test_a_condition_on_the_value_the_fact_takes_passes(self):
        r = rows({"question": Q1, "temporary measure": f"si la demande vient d'une personne identifiable, {CHANGE}"})
        self.assertEqual(mc.check(r), [])

    def test_a_condition_on_a_fact_the_line_does_not_ask_about_is_refused(self):
        r = rows({"question": Q2, "point": "si un parfum est un produit cosmétique, alors le texte dit que l'article 20 vise le texte",
                  "temporary measure": f"si cette provenance est qu'elle vient d'une personne identifiable, {CHANGE}"})
        self.assertTrue(any("shares no word" in p for p in mc.check(r)), mc.check(r))

    def test_the_same_condition_on_the_line_that_asks_about_it_passes(self):
        r = rows({"question": Q1, "temporary measure": f"si cette provenance est qu'elle vient d'une personne identifiable, {CHANGE}"})
        self.assertEqual(mc.check(r), [])


class FirstStep(unittest.TestCase):
    def test_a_measure_that_starts_by_establishing_a_fact_needs_the_cell(self):
        r = rows({"question": Q1, "temporary measure": f"établir d'abord la provenance de la demande ; {CHANGE}"})
        self.assertTrue(any("« à établir d'abord » is empty" in p for p in mc.check(r)), mc.check(r))

    def test_with_the_cell_filled_it_passes(self):
        r = rows({"question": Q1, "to establish first": "la provenance de la demande",
                  "temporary measure": f"établir d'abord la provenance de la demande ; {CHANGE}"})
        self.assertEqual(mc.check(r), [])


class SameChange(unittest.TestCase):
    def test_one_line_conditional_and_one_free_for_the_same_change_is_refused(self):
        r = rows({"question": Q1, "temporary measure": f"si la demande vient d'une personne identifiable, {CHANGE}"},
                 {"question": Q2, "temporary measure": CHANGE})
        self.assertTrue(any("with no condition" in p for p in mc.check(r)), mc.check(r))

    def test_both_free_or_both_conditional_passes(self):
        free = rows({"question": Q1, "temporary measure": CHANGE}, {"question": Q2, "temporary measure": CHANGE})
        self.assertEqual(mc.check(free), [])

    def test_a_line_with_no_measure_is_not_read(self):
        self.assertEqual(mc.check(rows({"question": Q1})), [])


if __name__ == "__main__":
    unittest.main()
