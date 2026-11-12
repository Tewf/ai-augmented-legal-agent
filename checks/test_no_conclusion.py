"""Tests of agent/no_conclusion.py: a sentence that settles a legal reading is found, in French and English;
a question and a quotation are not. Run: python3 -m unittest discover -s checks
"""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("no_conclusion", Path(__file__).resolve().parents[1] / "agent/no_conclusion.py")
nc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nc)


class NoConclusion(unittest.TestCase):
    def test_a_settled_reading_is_found_in_both_languages(self):
        self.assertEqual(len(nc.conclusions("Le bandeau est conforme. The page is lawful.")), 2)

    def test_outcome_sentences_shaped_like_a_register_are_found(self):
        # Invented sentences, in the shapes a reader found in a real register on 12 Nov. 2026.
        for sentence in ["Donc aucun consentement n'est exigé pour ce script.",
                         "Il n'y a pas d'obligation de consentement.",
                         "Le site n'est pas soumis au règlement.",
                         "La société entre dans le champ de l'article 3.",
                         "Le règlement s'applique à la société.",
                         "Aucune obligation de déclaration pour cette activité.",
                         "This is allowed.", "No DPA is needed here.", "The page complies.",
                         "La société n'est pas tenue de désigner un délégué.",
                         "Une marque vivante interdit d'utiliser ce nom.",
                         "Sans ce contrat, la société est le fabricant au sens du règlement.",
                         # A reviewer's attacks of 12 Nov. 2026.
                         "Rien dans le texte n'interdit cette comparaison.",
                         "The company may lawfully keep these records.",
                         "La collecte est autorisée par l'article 6.",
                         "No DPIA is necessary for this processing.",
                         "Aucune analyse d'impact n'est nécessaire ici.",
                         "The newsletter is permitted under the regulation.",
                         # Pass 4 of 12 Nov. 2026.
                         "Pas de droit de rétractation pour un bien confectionné sur mesure.",
                         "La page n'est pas conforme.", "This processing is not lawful.", "The form is not compliant.",
                         "La société est tenue de désigner un délégué.", "Une analyse d'impact est obligatoire.",
                         "Un contrat est requis.", "Une marque vivante interdit d’utiliser ce nom."]:
            self.assertEqual(len(nc.conclusions(sentence)), 1, sentence)

    def test_a_stray_guillemet_does_not_hide_a_conclusion(self):
        self.assertEqual(len(nc.conclusions("« début. Le site est conforme. Plus loin, « une autre citation »")), 1)

    def test_a_bullet_or_heading_does_not_merge_into_the_next_question(self):
        for text in ["- Le script est exempté de consentement\n- Faut-il le dire sur la page ?",
                     "## Le site est conforme\n\nFaut-il un bandeau ?",
                     "Un consentement n'est pas requis\n\n**Question** faut-il le demander ?"]:
            self.assertEqual(len(nc.conclusions(text)), 1, text)

    def test_a_quotation_does_not_span_table_cells(self):
        self.assertEqual(len(nc.conclusions('| écran 27" | le site est conforme | voir "x |')), 1)

    def test_a_question_is_not_a_conclusion(self):
        self.assertEqual(nc.conclusions("Le bandeau est-il conforme à l'article 82, ou est conforme seulement en partie ?"), [])

    def test_a_quotation_of_the_text_is_not_a_conclusion(self):
        self.assertEqual(nc.conclusions("L'article dit « le traitement est licite si la personne a consenti »."), [])

    def test_a_phrase_inside_a_longer_word_is_not_matched(self):
        self.assertEqual(nc.conclusions("The reviolet palette was chosen."), [])

    def test_what_the_text_requires_is_not_a_conclusion(self):
        self.assertEqual(nc.conclusions("L'article 82 demande un consentement avant la lecture d'un traceur."), [])


if __name__ == "__main__":
    unittest.main()
