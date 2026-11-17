"""Tests of agent/claimed_fixes.py: a claimed fix that is absent is found, a real one is not, an unread claim is never counted as held.
Run: python3 -m unittest checks.test_claimed_fixes"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("claimed_fixes", Path(__file__).resolve().parents[1] / "agent/claimed_fixes.py")
cf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cf)


def outdir(result: str, register: str = "| a |\n", drafts: dict[str, str] | None = None) -> Path:
    root = Path(tempfile.mkdtemp())
    (root / "result.md").write_text(result, encoding="utf-8")
    (root / "register.md").write_text(register, encoding="utf-8")
    (root / "search-log.md").write_text("log\n", encoding="utf-8")
    for name, text in (drafts or {}).items():
        (root / f"{name}.md").write_text(text, encoding="utf-8")
    return root


REPORT = "## Passe 2\n\n1. Le titre de brouillon-02 ne dit plus « information due » : il nomme la § 7.\n"


class ClaimedFixes(unittest.TestCase):
    def test_a_gone_claim_that_is_still_there_is_absent(self):
        root = outdir("corps\n" + REPORT, drafts={"brouillon-02-x": "# information due aux adresses\n"})
        absent, _, holds = cf.check(root)
        self.assertEqual(len(absent), 1)
        self.assertIn("still in brouillon-02-x", absent[0])
        self.assertEqual(holds, 0)

    def test_a_gone_claim_that_is_gone_holds(self):
        root = outdir("corps\n" + REPORT, drafts={"brouillon-02-x": "# la § 7 et les adresses\n"})
        self.assertEqual(cf.check(root)[0], [])
        self.assertEqual(cf.check(root)[2], 1)

    def test_the_report_itself_is_not_the_file_checked(self):
        # the quoted words are in the report section only: they must not make a gone claim fail
        root = outdir("corps\n" + REPORT, drafts={"brouillon-02-x": "rien\n"})
        self.assertEqual(cf.check(root)[0], [])

    def test_a_there_claim_with_the_words_missing_is_absent(self):
        report = "## Passe 2\n\n1. La cellule de la ligne 3 dit « à désigner par la personne » désormais.\n"
        absent, _, _ = cf.check(outdir("corps\n" + report, register="| x |\n"))
        self.assertEqual(len(absent), 1)
        self.assertIn("is there, in none of", absent[0])

    def test_a_there_claim_with_the_words_present_holds(self):
        report = "## Passe 2\n\n1. La cellule de la ligne 3 dit « à désigner par la personne » désormais.\n"
        root = outdir("corps\n" + report, register="| à désigner par la personne qui a confié |\n")
        self.assertEqual(cf.check(root)[:1], ([],))

    def test_a_span_whose_claim_is_not_read_is_never_a_hold(self):
        report = "## Passe 2\n\n1. Voir « un mot » plus loin.\n"
        absent, unread, holds = cf.check(outdir("corps\n" + report))
        self.assertEqual((absent, holds), ([], 0))
        self.assertEqual(len(unread), 1)

    def test_a_line_break_inside_the_words_does_not_hide_them(self):
        report = "## Passe 2\n\n1. Le titre de brouillon-02 ne dit plus « information\n   due ».\n"
        root = outdir("corps\n" + report, drafts={"brouillon-02-x": "information due\n"})
        self.assertEqual(len(cf.check(root)[0]), 1)

    def test_the_item_scope_narrows_to_the_draft_it_names(self):
        report = "## Passe 2\n\n1. Le titre de brouillon-02 ne dit plus « information due ».\n"
        root = outdir("corps\n" + report, drafts={"brouillon-02-x": "propre\n", "brouillon-05-y": "information due\n"})
        self.assertEqual(cf.check(root)[0], [])

    def test_main_exit_codes(self):
        root = outdir("corps\n" + REPORT, drafts={"brouillon-02-x": "information due\n"})
        self.assertEqual(cf.main([str(root)]), 1)
        self.assertEqual(cf.main([str(root / "nowhere")]), 2)


if __name__ == "__main__":
    unittest.main()
