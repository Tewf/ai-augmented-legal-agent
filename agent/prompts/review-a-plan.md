# Prompt: review a plan or an act

Load the [skill](../SKILL.md) `legal-constraints` first; its rules hold here.

**Input:** a plan, a page, a product change, a contract or an act to sign, given as a file or a text; the company's
register; its organisation description.

**Do:**

1. Say in one sentence what the plan does, who it touches (visitors, clients, suppliers, employees, the state) and
   what it collects, sells, signs or publishes.
2. For each of these, search what applies. Before you write that a domain holds nothing, run at least one search
   string in it. The domains, among others: data protection, consumer law, the trade's own rules,
   contracts, tax and invoicing, intellectual property, the company's own legal form, AI regulation, platform
   regulation, product safety. Log each result screened as the skill says.
3. For each constraint found, write one register line with every column of [register](../register.md) you can fill
   from the plan, the company's files and the text read. A constraint already in the register is updated, not
   duplicated. When the question needs a fact nobody has measured, fill "to establish first" with the fact and the
   role that measures it, and draft that role's task.
4. Before saying that nothing else applies, run the stopping estimator on your log and give its coverage.
5. For each open line, follow `temporary-measure.md`.

**Return:** the register lines, new and updated, the search log and the estimator's coverage, and the tasks drafted
for other roles. Run the two guards of the skill on what you return. The lines that may hold the plan
back come first, each with the text that bears on it; whether the plan waits is a person's decision, after the
jurist's answer where there is one.

**Never:** say the plan is legal or not; drop a point because it seems small.
