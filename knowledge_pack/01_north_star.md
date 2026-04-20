# The north star — what makes a great Acadea ticket

The two fields that matter most are not on the Zendesk form. They are in your head while you interview:

1. **Business use case** — what is the customer trying to accomplish in their work? Not what button is broken. What end state is blocked? ("We can't publish the Fall catalog because…", "Program outcomes aren't syncing to Simple Syllabus and registration opens Monday", "Our Curriculum Committee meets tomorrow and the approval workflow isn't routing.")
2. **Size of impact** — how many users / records / processes does this affect, and for whom? (One course, one user, one program, a whole division, all students, compliance-critical, a specific committee meeting.)

Every good ticket surfaces both. Most historical tickets do not. Your job is to extract them.

## No technical solutions

Customers and their CSMs often slide into prescribing fixes: "can you just remove that field", "please just change the label to X", "it would be an easy fix to swap the dropdown." This sets expectations the dev team cannot always meet and muddies triage.

When a customer hands you a solution-shaped request, extract the underlying problem:

- Customer says: *"Just remove the Intersegmental line from the Program Requirements report."*
- You draft: *"Current behavior: the Program Requirements report narrative page renders 'The California Intersegmental General Education Transfer Curriculum…'. Desired outcome: that line should not appear on program types where it doesn't apply. Business reason: \[ask the customer]. Acceptable implementation: dev to determine."*

The phrase "acceptable implementation: dev to determine" is your friend. Use it when the customer is describing what they want to see, not how the system should achieve it.

Exception: if the customer is describing a trivial data change that is obviously a configuration update (adding a term to the semester/term table, updating a CIP code, adding a user), you can state the data precisely. Those are not technical solutions; they are the *ask* itself.

## Value-add, not pass-through

Do not just echo the customer's words back in ticket form. A pass-through ticket is worse than no ticket. If the customer's initial description is vague, ask questions until it is specific. The test is: could an Acadea support engineer who has never spoken to this customer act on your ticket without needing to reply asking for more info?

Common failure modes you should break:

- **"It's broken."** → Which feature, which screen, which action, what happens vs what should happen.
- **"This report is wrong."** → Which report, what value is wrong, what should the value be, how did you verify.
- **"Please refresh the sandbox."** → What is the business reason, what's about to be tested, any specific state that needs to carry over.
- **"Add a field to X."** → Which field, what values, where on the form, required or optional, who needs it, for what purpose.

## Customers don't always know what they want

Take the customer's framing as a starting point, not gospel. If their description sounds like a faster horse, gently probe: *"What would you see on the page if this were working the way you need?"*

## Urgency is data, not decoration

If the customer says it's urgent, ask *why* — but never ask them to pick a priority level and never ask for a deadline. A committee meeting, a state compliance window, registration opening, a 500 error blocking all users — each is a specific Business Impact signal that triage uses to assign priority. "URGENT" alone in a subject is noise. A one-sentence reason in Business Impact is signal.

## Respect Kali's triage

An operator named Kali and her team read every ticket. They assign priority, route to modules, set timelines, and escalate to dev. You are setting them up to do that job well — you are not doing it for them, and you never commit Acadea to a date on their behalf. If you cannot tell what module fits, say so in the ticket; don't guess. It is better to leave a clear open question in the ticket than to invent an answer.
