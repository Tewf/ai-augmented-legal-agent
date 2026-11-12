# Prompt: prepare the jurist's dossier

Load the [skill](../SKILL.md) `legal-constraints` first; its rules hold here.

**Input:** the register lines waiting for an answer. Their "asked on" is empty, or their point, facts or measure
changed since that date, as the register's history shows. Also, how each respondent wants them: issues, one list, or a monthly
dossier. When no form is given, a comment on the line's existing issue, or a new issue if it has none.

**Do:**

- For a line whose issue already poses its question, link that issue; do not post the question again. A breach
  question (below) that the issue does not hold goes into the dossier as a new question.
- Hold back every line whose "to establish first" is not empty, and list it with the fact to measure.
- Hold back every line whose question is empty, and list it for a person to write the question.
- Group the others by "who answers"; each respondent gets their own dossier. A line with no respondent goes to the
  person who handed you the task.
- For each point, in the company's language, follow the pattern the legal track used on 11 Nov. 2026:

1. One opening paragraph: the situation in facts, with its witness.
2. A table whose columns are point, what we do and article, named in the company's language. It gives what the
   company does or plans, and the article that bears on it, linked at its source with the date read.
3. A part on what already bears on the point, from the register's "what bears on it". Give the guidance found (an authority's guide, a court
   decision) with its source, its date read and what stays open; or say none was found, and what was searched.
4. A numbered list of questions, each answerable by yes, no or a short reason: one point per question, no question
   that asks for a whole opinion. For a line whose "what a text attaches" is "not found in a text read", add the
   question of what follows a breach.
5. A line of links: the register line, the decisions it touches, the temporary measure if any.

Order the points by the order of the register ([register](../register.md)).

**Return:** one dossier per respondent, ready for a person to send, with the "asked on" each line will get once a
person sends it. When the person confirms the sending, this task fills "asked on" with the date and medium they
give, and changes nothing else; nothing is sent by you. Run the two guards of the skill on it.

**Never:** conclude in the dossier; put a person's private document in it; name how it was prepared.
