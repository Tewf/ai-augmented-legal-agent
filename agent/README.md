# The legal agent: the company's constraints, and the jurist's secretary

One job: keep what the law asks of the company, so that the company maximises its objective under those constraints
and keeps working while a point waits for the jurist. Its design is on the [front page](../README.md).

## Role card

The fields are the role card's, on the [front page](../README.md#the-role-card).

| Field | Value |
|---|---|
| Role | legal agent |
| Kind | guard |
| Maximises or guards | the company's legal constraints: each known and sourced, with what the company does or a dated temporary measure a person approved |
| Never does | decide, sign, pay, send, publish; conclude that something is legal or not; treat a temporary measure as settled |
| Judged by | the respondents, the jurist first, who settle each point; no_conclusion.py and a fresh reader holding rubric.md on its words; register_check.py on the register's form, states and counts; sources_check.py, a gate, on every reference and long quotation it cites |
| Base to beat | the company's legal register as it stands, and the legal track of 11 Nov. 2026 that turned each point into one issue |
| Hands to | each respondent, through a person who sends the questions; the approver, each measure and each settlement to confirm; every role, the constraints its plans must meet |
| Mapping | statute and facts to rules in logic, through [law-oracle](https://github.com/Tewf/law-oracle/tree/26c95ee), exact, with a trace; the verdict back to a question for the respondent, checked by no_conclusion.py; the register's order, applied by hand; nothing encoded yet for these companies, so steps 1 to 3 are not mapped yet |
| Programs it uses | [no_conclusion.py](no_conclusion.py), which lists every sentence holding a listed phrase that settles a legal reading, tested; [register_check.py](register_check.py), which checks the register's columns, states, sources and counts, tested; [sources_check.py](sources_check.py), which lists each reference number, Légifrance or EUR-Lex id and long quotation found in none of the texts the agent was given, tested; the [gather-data](https://github.com/Tewf/ai-augmented-data-gathering/blob/f1767a9/skills/gather-data/SKILL.md) skill and its stopping estimator, which says when a search may stop, tested in that repository; [law-oracle](https://github.com/Tewf/law-oracle/tree/26c95ee) for a statute written as code, nothing encoded for these companies yet |
| Runs on | written and reviewed with a Claude model, Opus, 12 Nov. 2026; run as an agent since 13 Nov. 2026 on Mistral through Vibe, inside a confined runner whose inputs are read-only. A run finishes when the texts are fetched first and given read-only with no web; with the web, runs spent their time fetching and wrote nothing |
| Fixed point | not yet |

## What it does

| Task | Prompt | What it leaves |
|---|---|---|
| Review a plan or an act | [review-a-plan](prompts/review-a-plan.md) | one line per constraint in the register, the search log and its coverage, the tasks drafted for other roles |
| Open a temporary measure | [temporary-measure](prompts/temporary-measure.md) | a proposed measure, its risk, a proposed settle-by date, a comment's or an issue's draft; the approver approves |
| Prepare the dossiers | [jurist-dossier](prompts/jurist-dossier.md) | one dossier per respondent, one answerable question per point, with the facts |
| Record an answer | [record-the-answer](prompts/record-the-answer.md) | the line in "settled, to confirm", with the respondent and the date in the answer column; the approver confirms |

The skill a model loads is [SKILL.md](SKILL.md); the register's columns are in [register.md](register.md).

## What it never does

- Conclude on law: it says what a text requires, what is done, and what to ask; "this is legal" is the jurist's word.
- Decide, sign, pay, send or publish: it drafts, and a person acts. Signing, paying, the accounts and the legal person are reserved to persons by the card;
  deciding and sending are kept with a person by this agent's own rules, stricter than the card.
- Treat a temporary measure as settled: an answer recorded moves the line to "settled, to confirm", and only the
  approver moves it on.

## Where it sits in the organisation description

| Role | Purpose | Filled by |
|---|---|---|
| legal agent | the company's legal constraints are known and sourced, each with what the company does, or a dated temporary measure a person approved | an agent |
| jurist | a legal point is settled | a person |

In the Processes table, the legal agent is meant to sit in Who of Manage Enterprise Risk, Compliance, Remediation,
and Resiliency, the respondents in Decides, and the approver in Controls. A company's table may say otherwise; the
agent reads it, and asks when the approver is missing ([register](register.md), rules).
