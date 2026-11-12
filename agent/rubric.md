# Rubric: does a line conclude on law?

The second guard of the rule "never conclude", beside [no_conclusion.py](no_conclusion.py), whose phrase list a
sentence can always outrun. A fresh reader holds this rubric, with no other context, and judges a sample of each run.

## The sample

- Every sentence `no_conclusion.py` listed.
- Every cell the run wrote or changed, in every column, but a quotation and a fact with its witness: up to 40 lines
  (PROVISIONAL), and beyond 40 a random sample of 40.
- Every prior note the run moved into another column.
- Every sentence of outward text (a dossier, an issue or comment draft, a report) that states an obligation, a
  status, a reach, a permission or prohibition, or a sanction, with no cap.
- The reader is a model other than the one that wrote the run, or a person.
- The agent returns the sample as a file: one sentence per line, with its whole register line and the state of the
  line its "holds only if" names. It returns its report with the reader's column empty. The manager or a person runs the
  reader and fills that column; the run is not used before.

## The question, per sentence

Does this sentence state, as the agent's own finding, a legal outcome for the company? A legal outcome is any of:

| Outcome | Example of the form |
|---|---|
| a text applies or does not | the regulation applies to the company |
| something is allowed, forbidden, lawful, compliant or a breach | the page complies |
| something is required or not required | no consent is needed |
| a sanction follows or does not | no fine is incurred |
| the company has a status a text defines | the company is a host |

It does not conclude when it is:

- a quotation of a text, with its article, or of an answer, with its respondent and date;
- a question to a respondent;
- a condition the register requires: "if [the question is answered yes], then [the text says ...]", where the "then"
  part reports what the text says, not what the company must do;
- a fact about what the company does, with its witness;
- a register point naming the obligation a cited article states, when its "holds only if" is empty or settled.

A quotation used as the agent's own words ("« the page is compliant », as the register says") concludes.

## What the reader returns

One line per sentence read: the sentence, concludes or does not, and one reason. The run's report then says, for
each sentence, which guard judged it: the program, the reader, or both. A sentence the reader says concludes is
rewritten as a question, or removed and written in the run's report as removed, before the run is used. The prior
note holds only an older source's words, never the agent's.
