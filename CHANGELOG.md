# Changelog

The releases this repository pins, newest first, in the form of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
A pin move is recorded here, not in decisions/.

## Unreleased

### Changed

- `agent/register_check.py` also refuses a header that names a column twice and a separator row whose cells differ in number from the header's. The older check compared only the rows: in passes 1, 3 and 4 of the agent on one act (16 Nov. 2026) a reader found each by hand. Four tests added.
- `agent/sources_check.py` also lists an article number (« art. 13 et 28 », « article L. 34-5 ») that no given text writes after « art. » or « article », or, for a number with a hyphen or a dot, anywhere as a token. A fresh reader found « art. 13 et 28 » of the RGPD cited from memory in pass 10 on 16 Nov. 2026, and the program let it through. Rerun on the pass-10 output and on the run before it, it lists articles 13 and 28 and nothing else; 5.1, 7.1, 34-5 and 82 are found in the given texts. Seven tests added.

### Added

- `agent/own_claims_check.py` and `agent/measure_check.py`, with their tests, for the faults the readers of five passes found again and again (16 Nov. 2026).
  One lists what the agent's report says of its own files that the files contradict; the other refuses a temporary measure whose condition names something it does not test.
  Rerun on those five passes, they list what the readers found by hand of these kinds; the table is in the task's notes.
- `agent/sources_check.py` and its tests, a gate of every run: the reference numbers, Légifrance or EUR-Lex ids and
  quotations of eight words or more that appear in none of the texts the agent was given. The skill and the card name it.

- The site: Quarto renders the README and every page, with the standard's stylesheet at its pin, and `pages.yml`
  publishes it to https://tewf.github.io/ai-augmented-legal-agent/ on every push to master, as the family's other members do.

- Pinned reader-ergonomics v1.24.2 (`65e4247`), at the repository's start: the standard's pin, link, changelog and
  decision-record checks.
- The legal agent, moved from the private repository where it was built: its skill, four prompts, the register's
  columns, the rubric, `no_conclusion.py` and `register_check.py` with their tests, and the takeover job.
- Linked law-oracle at `26c95ee`, and ai-augmented-data-gathering's gather-data skill at `f1767a9`.
