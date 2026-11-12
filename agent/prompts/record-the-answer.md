# Prompt: record the jurist's answer

Load the [skill](../SKILL.md) `legal-constraints` first; its rules hold here.

**Input:** a respondent's answer (a mail, a note, a comment on the issue) and the register lines it answers.

**Do:**

1. Quote the answer, or the part that answers each question, with its date and its medium. Say who gave it: the
   respondent, or someone who relayed it; a relayed answer is recorded as relayed, and the line stays "settled, to
   confirm" until the respondent's own words are recorded.
2. Update each line: the answer, and the state "settled, to confirm", which the approver confirms
   ([register](../register.md)). If the answer asks for
   something to be done, add a new line or a task for the role that does it, and propose its owner.
3. Propose how the answer replaces the temporary measure, or, if it allows the measure to stay, say so with the
   quote; a person approves the change.
4. Draft the comment that records the answer on the issue; a person posts it and closes the issue.
5. If the answer raises a new question, open a new line; do not reopen the line proposed as settled.
6. List the lines whose "holds only if" points at a question just answered, and propose their rewrite, for the
   approver to apply once the answer is confirmed; until then they stay as they are.

**Return:** the lines in "settled, to confirm", the tasks the answer creates, and the issue comment's draft. Run the two guards of the skill on your own text, not on the quoted answer.

**Never:** read more into the answer than it says; settle a line the answer does not address.
