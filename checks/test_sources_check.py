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
        self.assertEqual(self.missing("l'article (LEGIARTI000037813978) ; RGPD CELEX:32016R0679"), ["CELEX:32016R0679"])

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


# Lines of the texts the agent was given on 13 Nov. 2026 (recommandation-pixels.txt, lines 235, 418, 463 and 554) and
# lines of its output of pass 10 (result.md, lines 136, 166, 173, 210), which a fresh reader checked by hand on 16 Nov.
GIVEN = """Article 82
Dans le respect du principe de minimisation (article 5.1.b) du RGPD, seule la date est conservée.
L'article 5.3 de la directive « ePrivacy » est transposé à l'article 82 de la loi « informatique et libertés ».
Chaque message rappelle le droit de s'opposer (conformément à l'article 34-5 du code des postes et des communications
électroniques (CPCE)). Le consentement doit être libre (article 7.1 du RGPD)."""


class ArticleNumbers(unittest.TestCase):
    def missing(self, output: str) -> list[str]:
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "texte.txt").write_text(GIVEN, encoding="utf-8")
            return sources.missing(output, sources.read_texts([Path(folder)]))

    def test_articles_cited_from_memory_are_listed(self):
        # pass 10: « RGPD art. 13, 28, 5.1, e et art. 7.1 (cités mais non lus) »; no given text writes article 13 or 28
        out = "RGPD art. 13, 28, 5.1, e et art. 7.1 (cités mais non lus)"
        self.assertEqual(self.missing(out), ["article 13", "article 28"])

    def test_a_list_after_et_counts_each_number(self):
        self.assertEqual(self.missing("Le RGPD (art. 13 et 28, sur l'information due et les sous-traitants)"),
                         ["article 13", "article 28"])

    def test_a_number_the_texts_write_in_another_form_is_found(self):
        # pass 10: « art. L. 34-5 du CPCE »; the recommendation writes « article 34-5 du code des postes »
        self.assertEqual(self.missing("art. L. 34-5 du CPCE (moyens de s'opposer à la prospection)"), [])
        self.assertEqual(self.missing("art. 5.1, b du RGPD ; art. 7.1 du RGPD ; article 82, al. 4, 2°"), [])

    def test_a_dotted_number_is_found_as_a_token_without_the_word_article(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "texte.txt").write_text("voir 4.2 du guide et 12-3 du code", encoding="utf-8")
            texts = sources.read_texts([Path(folder)])
        self.assertEqual(sources.missing("art. 4.2 et art. 12-3 et art. 4.22", texts), ["article 4.22"])

    def test_a_plain_number_needs_the_word_article_in_a_text(self):
        # « 13 » appears in the texts (a date), but not as an article: it is still listed
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "texte.txt").write_text("le 13 novembre 2026, article 82.", encoding="utf-8")
            texts = sources.read_texts([Path(folder)])
        self.assertEqual(sources.missing("art. 13 du RGPD", texts), ["article 13"])

    def test_a_range_of_paragraphs_is_no_article(self):
        # « al. 1 à 3 » follows the article number; 3 is a paragraph, not an article
        self.assertEqual(self.missing("Article 82, al. 1 à 3 de la loi"), [])

    def test_the_word_art_inside_another_word_is_no_article(self):
        self.assertEqual(self.missing("la part 99 et le départ 7"), [])


if __name__ == "__main__":
    unittest.main()
