"""Tests of agent/register_check.py: columns, states, sources, the one-line key, the approver's states with and
without the register before, the counts, and the reading of tables a reader broke on 12 Nov. 2026.
Run: python3 -m unittest discover -s checks
"""
import importlib.util
import tempfile
import unicodedata
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("register_check", Path(__file__).resolve().parents[1] / "agent/register_check.py")
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)

COLS = list(rc.COLUMNS)


def write(rows, french=False, header=None):
    names = header or [rc.COLUMNS[c] if french else c for c in COLS]
    lines = ["| " + " | ".join(names) + " |", "|" + "---|" * len(names)]
    lines += ["| " + " | ".join(r.get(c, "") for c in COLS) + " |" for r in rows]
    path = Path(tempfile.mkdtemp()) / "r.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def table(rows, french=False):
    return rc.read(write(rows, french))[0]


def line(**kw):
    base = {"source": "inventory#1", "point": "p", "article": "art. 1", "issue": "o/r#1", "question": "q1", "state": "open"}
    base.update(kw)
    return base


def check(rows, before=None, expect=None, issues=None):
    return rc.problems(rows, before, expect or {}, issues)


class Form(unittest.TestCase):
    def test_a_clean_register_in_french_passes(self):
        self.assertEqual(check(table([line(state="ouvert")], french=True)), [])

    def test_a_state_outside_the_five_or_two_languages_fail(self):
        self.assertTrue(check(table([line(state="validé")])))
        self.assertTrue(any("both languages" in p for p in check(table([line(), line(source="i#2", question="q2", state="ouvert")]))))

    def test_a_missing_or_shared_source_fails(self):
        self.assertTrue(any("no source" in p for p in check(table([line(source="")]))))
        self.assertTrue(any("already another" in p for p in check(table([line(), line(question="q2")]))))

    def test_one_line_per_question_of_an_issue_passes_and_a_true_duplicate_fails(self):
        self.assertEqual(check(table([line(), line(source="i#2", question="q2")])), [])
        self.assertTrue(any("same issue" in p for p in check(table([line(), line(source="i#2")]))))

    def test_an_empty_file_or_a_table_with_no_row_fails(self):
        path = Path(tempfile.mkdtemp()) / "e.md"
        path.write_text("", encoding="utf-8")
        self.assertTrue(rc.read(path)[1])
        self.assertTrue(rc.read(write([]))[1])

    def test_bold_headers_nfd_accents_and_curly_apostrophes_are_read(self):
        names = ["**" + unicodedata.normalize("NFD", rc.COLUMNS[c]).replace("'", "’") + "**" for c in COLS]
        rows, problems = rc.read(write([line(state="ouvert")], header=names))
        self.assertEqual((len(rows), problems, check(rows)), (1, [], []))

    def test_an_escaped_pipe_stays_in_its_cell_and_a_bare_one_is_refused(self):
        path = write([line(**{"prior note": "a \\| b"})])
        rows, problems = rc.read(path)
        self.assertEqual((rows[0]["prior note"], problems), ("a | b", []))
        bare = write([line(**{"prior note": "a | b"})])
        self.assertTrue(rc.read(bare)[1])


class ApproverStates(unittest.TestCase):
    def test_without_before_an_approver_state_fails(self):
        self.assertTrue(any("only the approver" in p for p in check(table([line(state="réglé")], french=True))))

    def test_with_before_an_unchanged_approver_state_passes(self):
        old = table([line(state="temporary")])
        self.assertEqual(check(table([line(state="temporary")]), before=old), [])

    def test_with_before_the_agent_may_not_write_or_leave_an_approver_state(self):
        old = table([line(), line(source="i#2", question="q2", state="settled")])
        new = table([line(state="temporary"), line(source="i#2", question="q2", state="open")])
        found = check(new, before=old)
        self.assertTrue(any("became" in p for p in found))
        self.assertTrue(any("moved out of" in p for p in found))

    def test_a_line_dropped_from_the_register_fails(self):
        old = table([line(), line(source="i#2", question="q2")])
        self.assertTrue(any("missing" in p for p in check(table([line()]), before=old)))


class PassFive(unittest.TestCase):
    def test_every_table_is_read(self):
        one = write([line()]).read_text()
        two = write([line(source="i#2", question="q2", state="réglé")], french=False).read_text()
        path = Path(tempfile.mkdtemp()) / "m.md"
        path.write_text(one + "\n## Second group\n\n" + two, encoding="utf-8")
        rows, _ = rc.read(path)
        self.assertEqual(len(rows), 2)

    def test_a_header_of_both_languages_is_refused(self):
        names = [rc.COLUMNS[c] for c in COLS]
        names[names.index("état")] = "state"
        self.assertTrue(rc.read(write([line(state="ouvert")], header=names))[1])

    def test_a_temporary_line_keeps_its_measure_date_and_state(self):
        old = table([line(state="temporary", **{"temporary measure": "m", "settle by": "2026-12-01"})])
        withdrawn = table([line(state="measure proposed", **{"temporary measure": "m", "settle by": "2026-12-01"})])
        moved = table([line(state="temporary", **{"temporary measure": "m", "settle by": "2027-06-01"})])
        answered = table([line(state="settled, to confirm", answer="yes, 2026-11-20", **{"temporary measure": "m", "settle by": "2026-12-01"})])
        self.assertTrue(check(withdrawn, before=old))
        self.assertTrue(check(moved, before=old))
        self.assertEqual(check(answered, before=old), [])

    def test_issue_references_are_normalised_and_drafts_left_out(self):
        rows = table([line(issue="o/r#1, o/r#2"), line(source="i#2", question="q2", issue="https://github.com/o/r/issues/1"),
                      line(source="i#3", question="q3", issue="draft: 07-x.md")])
        self.assertEqual(rc.issue_refs(rows), {"o/r#1", "o/r#2"})


class PassSix(unittest.TestCase):
    def test_a_settled_line_cannot_change_and_to_confirm_needs_an_answer(self):
        old = table([line(state="settled", answer="yes")])
        self.assertTrue(any("changed" in p for p in check(table([line(state="settled", answer="no")]), before=old)))
        self.assertTrue(any("no answer" in p for p in check(table([line(state="settled, to confirm")]))))

    def test_a_table_with_a_point_but_no_state_is_refused(self):
        names = list(rc.COLUMNS)
        names[names.index("state")] = "statut"
        self.assertTrue(rc.read(write([line()], header=names))[1])

    def test_an_issue_without_its_repository_is_refused(self):
        self.assertTrue(any("owner and repository" in p for p in check(table([line(issue="studio#37")]))))
        self.assertTrue(any("owner and repository" in p for p in check(table([line(issue="#36")]))))
        self.assertEqual(check(table([line(issue="acme/studio#37")])), [])

    def test_states_follow_the_language_of_the_header(self):
        self.assertTrue(any("English state" in p for p in check(table([line(state="open")], french=True))))


class Counts(unittest.TestCase):
    def test_counts_match_whole_sources_not_prefixes_of_words(self):
        rows = table([line(source="a-ouvrir#1"), line(source="app#43", question="q2"), line(source="a#1", question="q3")])
        self.assertEqual(check(rows, expect={"a": 1, "a-ouvrir": 1, "app#43": 1}), [])

    def test_distinct_issues_are_counted(self):
        rows = table([line(), line(source="i#2", question="q2"), line(source="i#3", question="q3", issue="o/r#2")])
        self.assertEqual(check(rows, issues=2), [])
        self.assertTrue(check(rows, issues=3))


if __name__ == "__main__":
    unittest.main()


class TableShape(unittest.TestCase):
    """The two faults of the legal agent's gallery runs (16 Nov. 2026, passes 1, 3 and 4 of work/2026-11-16_law-2): a header
    that names a column twice, and a separator row whose cells differ in number from the header's. A reader found each
    by hand; the rows alone, which the older check compared, were all the right length."""

    def broken(self, header_extra=0, separator_extra=0):
        names = [rc.COLUMNS[c] for c in COLS] + ["source"] * header_extra
        lines = ["| " + " | ".join(names) + " |", "|" + "---|" * (len(names) + separator_extra)]
        row = line(state="ouvert")
        lines.append("| " + " | ".join(row.get(c, "") for c in COLS) + " |" * 1)
        path = Path(tempfile.mkdtemp()) / "r.md"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return rc.read(path)

    def test_a_clean_table_reads_without_problem(self):
        self.assertEqual(self.broken()[1], [])

    def test_a_column_named_twice_is_refused(self):
        _, problems = self.broken(header_extra=1)
        self.assertTrue(any("named twice" in p and "source" in p for p in problems), problems)

    def test_a_separator_with_one_cell_too_many_is_refused(self):
        _, problems = self.broken(separator_extra=1)
        self.assertTrue(any("separator row has" in p for p in problems), problems)

    def test_a_separator_with_one_cell_too_few_is_refused(self):
        _, problems = self.broken(separator_extra=-1)
        self.assertTrue(any("separator row has" in p for p in problems), problems)
