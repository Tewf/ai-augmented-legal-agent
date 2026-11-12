# Job: take over an existing legal register or legal track, once per company

A one-time job, done with a person, before the [legal agent](../agent/README.md) keeps a company's register.

- It left the agent on 12 Nov. 2026, by the maintainer's decision: it is specific to each company's inputs.
- Load the agent's [skill](../agent/SKILL.md) `legal-constraints` first; its rules hold here, except the one
  this job names.
- A person reads the draft and the report before the register is used.

**Input:** what the company already has, where the draft register is to be written, and a takeover map. The inputs
may be any of:

- an older register, in any columns;
- a legal track's per-point inventory: one row per point with its article, link, date read, witness and issues;
- the issues a track posted, each with its numbered questions;
- a list of obligations not yet in any issue;
- a summary page, whose rows may group several points and whose counts the takeover must reconcile.

**The takeover map** is a short file, `takeover-map.md` beside the draft register, written for the company and
confirmed by a person. It has three tables:

| Table | One row per | Columns |
|---|---|---|
| columns | register column | column, input, field |
| codes | code an input uses (a tier, an event code, a shorthand for a sanction) | code, input, what it means |
| joins | way two inputs meet (an issue file and its number, a line and the issue it left, an inventory row and the question it feeds) | from, to, how they match |

It also names the readings log of the track, if one exists, as the source of the grade. Without a map, draft one from
the inputs, return it alone, and stop: the takeover runs on a confirmed map. A join the inputs do not settle is left
empty in the draft map, and the person settles it.

**Do:**

1. Keep only the target company's lines; a line whose company is unclear goes into the report, not the register.
2. Write one register line per obligation and per question:
   - a posted issue gives one line per numbered question, with the readings the issue states;
   - the per-point inventory gives the dates read and the witnesses of those readings;
   - an obligation not yet in an issue gives one line with an empty issue;
   - an inventory row whose question is not among the posted questions gives its own line, with its old issue, if
     any, in the issue column;
   - an old-register row feeds the lines the map's joins table names for it, its cells copied to each;
   - an old-register row with no join gives its own line, its question left empty for a person to write.
   Fill every column from the source the map names; write the line's source (input and row, or issue and question
   number) in the source column.
3. Carry what a section states once to every line it governs: a condition goes into "holds only if", and a code is
   expanded as the map says. When the question of a line is whether the obligation reaches the company at all, its
   "holds only if" points at that question and its point is written conditionally.
4. Copy every old cell verbatim into "prior note", with its source and date, whatever else you map from it. A cell that
   says a source answers the question keeps its words in the prior note and goes into "what bears on it" as guidance,
   with "the respondent confirms". An old cell that states a legal outcome goes only to the prior note, never into
   another column.
5. Merge only lines that are the same point and question: same issue, article, point and question. Lines that share
   an issue but not all four stay separate. The dated reading wins; the older text stays in the prior note.
6. "Who answers": the one respondent an input names. Leave it empty when none does, or when the organisation
   description's Decides cell of the risk row names several roles or a doer. List such a line in the report, and put
   any respondent an input named ("who settles it") in the prior note. A name that signs or does something is not a
   respondent.
7. "Asked on" is filled only on evidence that the respondent received the question: a sent mail, a comment they
   answered. An issue opened with no recipient is not evidence; leave the cell empty and list the line in the report.
8. "When it must hold": the summary page's tier that says the practice is public or running sets "past or running";
   otherwise the map's expansion of the inventory's code. When they disagree, the earlier event wins, and the report
   says so. A line with neither, such as an obligation not yet in an issue, takes the event of the issue it left
   (the map's joins), else stays empty and sorts last.
9. Set the states: at most "open" or "measure proposed". An old state that reads as settled or validated stays in the
   prior note, and the line is "open".
10. **The exception to the skill.** During the takeover you do not read the law again. An article already read keeps
    its link and date; one with neither gets "not read" and a line in the report. The grade comes from the readings
    log the map names, copied into `readings.csv`. A track's `how` becomes `route`, other columns are dropped, and
    paths are made relative to the register. Without a log, a dated article is "read in a secondary source (the
    track's inventory)".
11. Run `register_check.py` on the draft, without `--before` (the draft holds no approver state). Give `--expect`
    for each count of lines an input gives by source: the obligations not yet in an issue, the questions of an
    issue. Give `--expect-issues` for every distinct issue the inputs name, old issues of unposted rows included. A count the program cannot take (groups, tiers) is
    reconciled by hand in the report. Every error is fixed or explained in the report.

**Return:**

- the draft register at the draft path, never over the old register, and the report beside it, `takeover-report.md`;
- the report: the map used, the counts reconciled and the lines merged;
- in the report too: the lines with no single respondent, the lines with no evidence of being asked, the articles
  not read, and the lines left out with why;
- every file of the inputs' folders that no step read (a search log, a coverage, a list of open sorries), named, so
  that the draft does not read as complete. Carrying them into the register is queued ([queue](../agent/queue.md)).

Run the two guards of the skill on both. The
approver confirms before the draft replaces the old register; with no approver known, the draft stays a draft.

**Never:** lose a line, an old cell, a question, a respondent, an issue or a state; join two obligations in one line;
reword the company's earlier words as a finding of yours.
