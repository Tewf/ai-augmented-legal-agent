# 0001: The legal agent gets a repository of its own

**Decision:** The legal agent is published as its own repository, beside law-oracle and ai-augmented-law-oracle, not
in one repository with every role agent.

**Status:** accepted, 2026-11-12. **Shape:** [decision record](https://github.com/Tewf/reader-ergonomics-software-design/blob/7fe39f8/shapes/decision-record.md). **Proposed in:** no proposal; a decision page put to the maintainer.

## Context

- The agent was built in a private repository with four other role agents (marketing, manager, CEO, customer
  service), and reviewed seven times there.
- The maintainer was asked whether role agents should share one public repository or have one each. He chose not to
  group them when it makes a role less important (12 Nov. 2026). He named the legal agent: it rests on the law oracle
  and its augmented twin, which need attention of their own.

## Decision

- This repository holds the agent, its one-time takeover job, its programs and their tests.
- A company's own register and legal pages never come here.
- The private repository where it was built keeps a copy pinned to a commit of this one.

## Options

| Option | Consequences | Outcome |
|---|---|---|
| A repository of its own | the role is visible beside the law oracle it rests on; two places hold it | chosen |
| One public repository for all role agents | one place for the card and its check; this role sits among others that need less | rejected: it makes the role less important |
| Keep it private | no publication cost | rejected: no family could link it |

## Consequences

- **Good:** the agent sits beside the law oracle and its twin, and can be read and reviewed on its own.
- **Bad:** two places hold the agent, this one and the pinned copy.
- **To keep it true:** a fix lands here first and is copied to the pinned copy the same day.

## See also

[Decisions](README.md); [README](../README.md); [law-oracle](https://github.com/Tewf/law-oracle/tree/26c95ee).
