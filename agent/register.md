# The register of constraints: its columns

One table per company, one line per constraint, kept by the legal agent in the company's language.

- The columns follow, renamed, the inventory a legal track used on 11 Nov. 2026: point, article, link, date read,
  what we do, witness, question, issue, when it must hold, what already bears on it.
- They add the group, the condition a line holds under, the grade of the reading and what a text attaches to a
  breach. Then a fact to establish first, who answers and when the question was asked. Then what the point stops, the answer, the
  state, the temporary measure with its risk and date, the prior note that keeps an older register's words, and the
  source each line comes from.
- The example is invented and names no real text: a client wants to show a price comparison with its competitors on
  its page.

| Column | Nom en français | What it holds | Example of form |
|---|---|---|---|
| source | source | where the line comes from: the input and its row, or the issue and its question number; one value per line | inventory#12, or owner/repo#N:q3 |
| group | groupe | the input's group, kept as given by the takeover job ([jobs](../jobs/take-over-a-legal-register.md)); when two inputs group a point differently, the first named in the [takeover map](../jobs/take-over-a-legal-register.md), the other in the prior note; empty for a line written later | the group's label in the input |
| point | point | one obligation, in a few words, written "if ..., then the text says ..." when "holds only if" is filled | if the comparison is advertising, then the statute says it names the products compared |
| holds only if | vaut seulement si | the source of the line or question this one depends on, or empty | inventory#4: is the comparison advertising in the statute's sense? |
| article | article | the texts and articles one question rests on, each with its text named | statute S, art. 12 and 14 |
| link | lien | the article at its source, the address a person opens | the publisher's address of art. 12 |
| read on | lu le | the date the article was read there, or "not read" | 2026-11-12 |
| grade | niveau | read at the source, read in a secondary source (which one), or not read | read at the source |
| what a text attaches | ce que le texte attache | the sanction a text attaches to a breach, quoted with its article, or "not found in a text read" | not found in a text read |
| what bears on it | ce qui l'éclaire | guidance found (an authority's guide, a court decision): its source, date read and what stays open; or "none found", with what was searched; or "not searched"; never an answer | none found; searched: the authority's guides |
| what we do | ce que nous faisons | the company's practice today, in facts | the page lists the client's price beside two others |
| witness | témoin | where that practice is shown | a file and its lines, at a commit |
| to establish first | à établir d'abord | a fact that must be measured before the question can be asked, and the role that measures it; emptied once the fact is in "what we do", the run's report saying so with the date | when the competitors' prices were read; a role to name |
| question | question | one question its respondent can answer | must the page say the date the prices were read? |
| who answers | qui répond | the respondent, as the company names them: the jurist, the accountant, a workshop; never a signer or a doer; a workshop answers only on facts of its own work | the jurist |
| asked on | demandé le | the date and medium the question was put to the respondent, or empty | 2026-11-11, comment on the issue |
| issue | ticket | the issue that holds the question; a drafted one is written "draft: <file>" until a person posts it | owner/repo#N, or draft: 07-comparison.md |
| when it must hold | avant quand | the event before which it must be settled, and its date if known; "past or running" when the practice is already public or running | before the page goes live, date not set |
| what it stops | ce qu'il bloque | what waits while the point is open | the page's launch with the comparison |
| answer | réponse | the respondent's answer and its date, or empty | empty until answered |
| state | état | one of the states below | measure proposed |
| temporary measure | mesure provisoire | what the company does meanwhile | the page goes live without the comparison |
| risk | risque | what the measure leaves exposed | no comparison for the first weeks |
| settle by | à régler avant | the date the measure must be replaced by an answer: proposed by the agent while the state is "measure proposed", set by the approver | 2026-12-01 |
| prior note | note antérieure | the words of an older register or page for this line, verbatim, with their source and date; never the agent's own | "…", old register, section 2, before 2026-11-11 |

## States

The person who confirms what the agent proposes is called **the approver**; the rules below say who it is.

| State | État | Meaning | How a line leaves it |
|---|---|---|---|
| open | ouvert | no answer, no measure | the agent proposes a measure (measure proposed), or records an answer (settled, to confirm) |
| measure proposed | mesure proposée | a measure is drafted, not approved | the approver approves it (temporary) or not (open); or the agent records an answer (settled, to confirm) |
| temporary | provisoire | a measure approved by a person applies until the answer | the agent records an answer (settled, to confirm) |
| settled, to confirm | réglé, à confirmer | an answer is recorded, not confirmed | the approver confirms it (settled) or reopens it: back to temporary if a measure was approved, else open |
| settled | réglé | the answer is confirmed | a new text or fact reopens it (open), by the approver |

## Rules of the register

- The approver is the role in Controls of the row "Manage Enterprise Risk, Compliance, Remediation, and Resiliency"
  of the company's organisation description. If there is no description, or that cell is empty or "?", the agent
  goes on drafting, writes nothing as approved, and asks the person who handed it the task who approves.
- Only the approver moves a line to "temporary" or "settled", by their own edit or commit. An approval given in
  words, in a mail or a chat, is quoted in the run's report; the agent never writes the state for it.
- Only the approver moves a line to "temporary" or "settled". The agent writes only "open", "measure proposed" and
  "settled, to confirm".
- A line whose "holds only if" is open stays conditional: its point says "if ... then ...", never as an obligation of
  the company.
- **The order of the lines** is used by every prompt:
  1. the lines whose settle-by date has passed;
  2. the lines whose event is "past or running";
  3. the others by "when it must hold", nearest event first, an undated event after the dated ones, an empty cell
     last;
  4. ties to the line that stops the most work.
- Everything in the register is written in the company's language, with the column and state names of that language
  (the tables above give the French ones). The prior note keeps its own words. The fixed values in French:

  | Value | En français |
  |---|---|
  | read at the source | lu à la source |
  | read in a secondary source | lu dans une source secondaire |
  | not read | non lu |
  | none found | rien trouvé |
  | not searched | non cherché |
  | past or running | passé ou en cours |
  | not found in a text read | rien trouvé dans un texte lu |
  | draft | brouillon |

  A search log keeps its header `string,result,concepts`, which the
  stopping estimator reads.
- `python3 register_check.py <register>` checks the form after every task. It compares with the version committed
  at HEAD, or with `--before <old>`, a file a person gives; the agent never gives `--before` and never commits the
  register. It checks the columns, the states, one line per point and question, and a source on every line. With a
  baseline, it checks that no line became temporary or settled. With `--expect`, it checks the counts against the
  inputs.