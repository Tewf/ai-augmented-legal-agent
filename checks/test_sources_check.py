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
rattachés à un service demandé par le destinataire. Article LEGIARTI000037813978.
Arrêt de la Cour, affaire C\u2011393/09. Article premier. Article 82. Code des postes, article L. 34-5. Loi, article 1-1."""


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

    def test_a_case_number_in_a_text_passes_whatever_its_dash(self):
        # EUR-Lex writes « C‑393/09 » with a non-breaking hyphen
        self.assertEqual(self.missing("l'arrêt C-393/09, point 35"), [])

    def test_a_case_number_in_no_text_is_listed(self):
        # 17 Nov. 2026: an invented « C-999/99 » passed the check
        self.assertEqual(self.missing("voir l'arrêt C-399/09 et l'arrêt T-12/21"), ["C-399/09", "T-12/21"])

    def test_an_article_number_in_a_text_passes_in_its_usual_forms(self):
        self.assertEqual(self.missing("l'article 82, l'art. 82 et l'article 1er"), [])

    def test_an_article_number_in_no_text_is_listed(self):
        # pass 11 of the legal agent described GDPR articles 13 and 28 from memory; neither was in a text given
        self.assertEqual(self.missing("selon les articles 13 et l'article 82"), ["article 13"])

    def test_a_hyphenated_article_number_is_checked_whole(self):
        # the LCEN numbers its articles « 1-1 »; « article 1-2 » must not pass on the text's « article 1 »
        self.assertEqual(self.missing("l'article 1-1 de la loi"), [])
        self.assertEqual(self.missing("l'article 1-2 de la loi"), ["article 1-2"])

    def test_a_code_article_in_no_text_is_listed(self):
        self.assertEqual(self.missing("l'article L. 34-5 du CPCE"), [])
        self.assertEqual(self.missing("l'article L34-5 et l'article L. 34-6"), ["L. 34-6"])

    def test_quote_marks_and_apostrophes_do_not_decide(self):
        out = 'elle dit "L’exemption ne vaut que pour la mesure individuelle de la délivrabilité"'
        self.assertEqual(self.missing(out), [])


if __name__ == "__main__":
    unittest.main()
