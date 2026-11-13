# Changelog

The releases this repository pins, newest first, in the form of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
A pin move is recorded here, not in decisions/.

## Unreleased

### Added

- `agent/sources_check.py` and its tests, a gate of every run: the reference numbers, Légifrance or EUR-Lex ids and
  quotations of eight words or more that appear in none of the texts the agent was given. The skill and the card name it.

- The site: Quarto renders the README and every page, with the standard's stylesheet at its pin, and `pages.yml`
  publishes it to https://tewf.github.io/ai-augmented-legal-agent/ on every push to master, as the family's other members do.

- Pinned reader-ergonomics v1.24.2 (`65e4247`), at the repository's start: the standard's pin, link, changelog and
  decision-record checks.
- The legal agent, moved from the private repository where it was built: its skill, four prompts, the register's
  columns, the rubric, `no_conclusion.py` and `register_check.py` with their tests, and the takeover job.
- Linked law-oracle at `26c95ee`, and ai-augmented-data-gathering's gather-data skill at `f1767a9`.
