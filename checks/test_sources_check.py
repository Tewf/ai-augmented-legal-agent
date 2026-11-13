"""Tests of agent/sources_check.py: a reference or a long quotation that appears in none of the texts the agent
was given is listed; one that appears, even across a line break or with other quote marks, is not.
Run: python3 -m unittest checks.test_sources_check"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("sources_check", Path(__file__).resolve().parents[1] / "agent/sources_check.py")
sources = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sources)

TEXT = """Recommandation relative aux pixels de suivi, délibération n° 2026-031.
L'exemption ne vaut que pour la mesure individuelle de la délivrabilité des courriels
rattachés à un service demandé par le destinataire. Article LEGIARTI000037813978."""


class Sources(unittest.TestCase):
    def missing(self, output: str) -> list[str]:
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "texte.txt").write_text(TEXT, encoding="utf-8")
            return sources.missing(output, sources.read_texts([Path(folder)]))

    def test_a_number_in_no_text_is_listed(self):
        # the legal agent's run of 13 Nov. 2026 called the recommendation « n° 2026-042 », a number in no text it had
        self.assertEqual(self.missing("Voir la recommandation CNIL n° 2026-042, § 3.2."), ["n° 2026-042"])

    def test_a_number_in_a_text_is_not(self):
        self.assertEqual(self.missing("la délibération n° 2026-031"), [])

    def test_ids_of_legifrance_and_eur_lex_are_checked(self):
        self.assertEqual(self.missing("art. 82 (LEGIARTI000037813978) ; RGPD CELEX:32016R0679"), ["CELEX:32016R0679"])

    def test_a_long_quotation_found_across_a_line_break_passes(self):
        out = "la recommandation dit « la mesure individuelle de la délivrabilité des courriels rattachés à un service »"
        self.assertEqual(self.missing(out), [])

    def test_a_long_quotation_in_no_text_is_listed(self):
        out = "elle dit « la mesure individuelle des ouvertures reste permise dans tous les cas sans exception »"
        self.assertEqual(len(self.missing(out)), 1)

    def test_a_short_quotation_is_not_checked(self):
        self.assertEqual(self.missing("le mot « transactionnel » seul"), [])

    def test_a_marked_cut_or_insertion_is_the_quoters_and_each_piece_is_checked(self):
        cut = "« L'exemption ne vaut que pour [...] la délivrabilité des courriels rattachés à un service »"
        self.assertEqual(self.missing(cut), [])
        wrong = "« L'exemption ne vaut que pour [...] la délivrabilité de tous les courriels sans exception »"
        self.assertEqual(self.missing(wrong), ["la délivrabilité de tous les courriels sans exception"])

    def test_one_word_changed_in_a_quotation_is_listed(self):
        # 13 Nov. 2026: « démontre que » quoted for the text's « devra démontrer que »
        self.assertEqual(len(self.missing("« L'exemption ne vaudrait que pour la mesure individuelle de la délivrabilité »")), 1)

    def test_quote_marks_and_apostrophes_do_not_decide(self):
        out = 'elle dit "L’exemption ne vaut que pour la mesure individuelle de la délivrabilité"'
        self.assertEqual(self.missing(out), [])


if __name__ == "__main__":
    unittest.main()
