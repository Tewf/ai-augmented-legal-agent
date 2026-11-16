"""Tests of agent/own_claims_check.py, from real statements of the five passes of work/2026-11-16_law-2 (16 Nov. 2026).
Run: python3 -m unittest discover -s checks
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

AGENT = Path(__file__).resolve().parents[1] / "agent"
spec = importlib.util.spec_from_file_location("own_claims_check", AGENT / "own_claims_check.py")
oc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oc)
rc = oc.register_check
COLS = list(rc.COLUMNS)
HASH = "27a2248cf0cf7c79a3ec7eae30b6e871817230d9f577632fed915181642144c2"
ACT = "1. La demande « ma dépression », montrée sur deux cartes publiques, est-elle une donnée concernant la santé au sens de l'article 9 du RGPD ?\n"


def register(separator=None, cells=None):
    names = [rc.COLUMNS[c] for c in COLS]
    lines = ["| " + " | ".join(names) + " |", "|" + "---|" * (separator or len(names))]
    for point in (cells or ["p1", "p2"]):
        row = {"source": point, "point": point, "state": "ouvert", "article": "art. 4 point 15", "issue": "o/r#1"}
        lines.append("| " + " | ".join(row.get(c, "") for c in COLS) + " |")
    return "\n".join(lines) + "\n"


def run(report, reg=None, files=None, texts=(), act=ACT, separator=None):
    d = Path(tempfile.mkdtemp())
    (d / "result.md").write_text(report, encoding="utf-8")
    (d / "register.md").write_text(reg or register(separator), encoding="utf-8")
    (d / "acte.md").write_text(act, encoding="utf-8")
    extra = []
    for name, text in (files or {}).items():
        (d / name).write_text(text, encoding="utf-8")
        extra.append(str(d / name))
    argv = [str(d / "result.md"), "--register", str(d / "register.md"), "--files", *extra, "--act", str(d / "acte.md")]
    if texts:
        for name, text in texts.items():
            (d / name).write_text(text, encoding="utf-8")
        argv += ["--texts", *[str(d / n) for n in texts]]
    import io, contextlib
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = oc.main(argv)
    return code, buffer.getvalue()


class Counts(unittest.TestCase):
    def test_a_separator_count_the_register_contradicts_is_listed(self):
        code, out = run("## Passe 4\n17. (mineur, séparation) L'en-tête n'a plus 26 colonnes : 25 colonnes, et la ligne de séparation a 25 cellules comme les deux lignes.\n", separator=26)
        self.assertEqual(code, 1)
        self.assertIn("has 25 cells; the register's has 26", out)

    def test_a_true_count_passes(self):
        code, out = run("## Passe 4\n17. (mineur, séparation) La ligne de séparation a 25 cellules comme les deux lignes.\n")
        self.assertEqual(code, 0, out)

    def test_the_finding_an_item_answers_is_not_read_as_a_claim(self):
        code, out = run("## Passe 5\n9. (mineur, ligne de séparation à 26 cellules) : corrigée à 25 cellules.\n")
        self.assertEqual(code, 0, out)


class Presence(unittest.TestCase):
    ITEM = "## Passe 2\n12. (moyen, règlement 655/2013) L'article 1 et le considérant 4 sont cités dans la question 2 de ce rapport, dans les deux brouillons et dans la ligne 2 du registre.\n"

    def test_a_reference_said_to_be_in_a_draft_that_lacks_it_is_listed(self):
        code, out = run("## Question 2\nL'article 1 et le considérant 4 : texte.\n" + self.ITEM,
                        files={"question-1.md": "rien ici\n", "question-2.md": "article 1 et considérant 4\n"})
        self.assertEqual(code, 1)
        self.assertIn("is in question-1.md, and it is not", out)

    def test_a_quotation_said_to_be_in_a_cell_that_lacks_it_is_listed(self):
        quote = "une substance ou un mélange destiné à être ingéré, inhalé, injecté ou implanté dans le corps humain"
        report = f"## Passe 5\n8. (moyen, art. 2 point 2) : il est cité — « {quote} » — dans la cellule point de la ligne 1 et dans sa cellule article.\n"
        reg = register(cells=[quote + " (point)"]).replace("art. 4 point 15", "art. 2")
        code, out = run(report, reg=reg)
        self.assertEqual(code, 1)
        self.assertIn("the cell article of line 1", out)

    def test_an_item_that_says_it_corrected_the_claim_is_not_read(self):
        code, out = run(self.ITEM.rstrip() + " [corrigé en passe 3 : seule la ligne 2 les cite]\n",
                        files={"question-1.md": "rien\n", "question-2.md": "x\n"})
        self.assertEqual(code, 0, out)


class Absence(unittest.TestCase):
    def test_a_quotation_said_to_be_gone_that_a_cell_still_holds_is_listed(self):
        report = "## Passe 3\n10. (mineur, singulier) : le singulier « une donnée concernant la santé » ne reste que dans la question de l'acte, citée telle quelle.\n"
        code, out = run(report, reg=register(cells=["est une « donnée concernant la santé » au sens de l'art. 4"]))
        self.assertEqual(code, 1)
        self.assertIn("still holds it", out)

    def test_the_act_s_own_question_quoted_is_let_through(self):
        report = "## Question 1\n1. La demande « ma dépression », montrée sur deux cartes publiques, est-elle une donnée concernant la santé au sens de l'article 9 du RGPD ?\n\n## Passe 3\n10. (mineur) : le singulier « une donnée concernant la santé » ne reste que dans la question de l'acte.\n"
        code, out = run(report)
        self.assertEqual(code, 0, out)


class HashesAndGuards(unittest.TestCase):
    def test_a_hash_of_39_characters_is_listed(self):
        code, out = run("# R\n", files={"search-log.md": f"Hash SHA256 : {HASH[:39]}\n"})
        self.assertEqual(code, 1)
        self.assertIn("a hash of 39 characters", out)

    def test_a_hash_written_in_a_given_text_passes_and_one_written_nowhere_is_listed(self):
        ok = run("# R\n", files={"search-log.md": f"Hash : {HASH}\n"}, texts={"texte.txt": f"sha256 du fichier lu {HASH}\n"})
        self.assertEqual(ok[0], 0, ok[1])
        bad = run("# R\n", files={"search-log.md": f"Hash : {'ab' * 32}\n"}, texts={"texte.txt": f"sha256 du fichier lu {HASH}\n"})
        self.assertEqual(bad[0], 1)
        self.assertIn("no given text's", bad[1])

    def test_a_finished_report_that_says_the_guards_did_not_run_is_listed(self):
        code, out = run("## Gardes\nLes trois gardes de la compétence n'ont pas encore été exécutés.\n")
        self.assertEqual(code, 1)
        self.assertIn("guards were not run", out)


if __name__ == "__main__":
    unittest.main()
