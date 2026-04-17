# Questions support asks most often — preempt them

These are the questions Acadea support ends up asking in their first reply when a ticket is incomplete. If you can head them off during the interview, the customer's ticket closes faster.

## The nine canonical follow-ups

1. **"Which environment — production, sandbox, or UAT?"**
   Always ask. It is the single most common clarifying question support asks. Even for feature requests.

2. **"Just to confirm — you want X on report/form Y in column/field Z. Correct?"**
   This is support's "scope confirmation." You should leave no doubt in the ticket. Name the specific artifact, the specific column/field, the specific expected behavior.

3. **"Is this affecting all users/programs/courses or only specific ones?"**
   The impact question. Always surface scope: one record, one proposal type, one division, all users.

4. **"Only this form/program type, or also \[adjacent one]?"**
   Scope boundary. Especially important on Programs and Courses tickets. When a customer says "change the form", ask which form version and whether it applies to all proposal types or just one.

5. **"Which exact program/course/proposal are you looking at?"**
   Always get a specific example. "Program #565", "Course MAC2311", "Proposal ID 12345". A generic description is not enough for support to reproduce.

6. **"Can you share a screenshot that includes the URL?"**
   For any UI issue, expect support will ask for this. Ask the customer during the interview.

7. **"Are you still seeing this issue?"**
   For intermittent or time-sensitive issues, note when the customer last saw it and whether it's currently reproducible.

8. **"Does this happen on different browsers? For different users?"**
   Browser and user-isolation data. Especially for rendering, login, session, and permission issues.

9. **"What does \[ABC] stand for?"**
   Acronym hygiene. Customers use org-specific shorthand (PSAV, TR form, POS report, BSC). If you use an acronym in the ticket, spell it out on first use.

## Module-specific preempts

**Reports tickets:** always ask environment, report name, column/field, and a specific record to use as example.

**Programs tickets:** always ask program ID/title, form version, proposal type, and whether the issue applies to all proposals of that type.

**Courses tickets:** always ask course code, proposal state, form tab, and the affected user's role.

**System/500 tickets:** always ask for exact error text (verbatim), RequestId, URL, browser, user account, and when it started.

**Workflow tickets:** always ask which workflow by name, which step, which user's role, and whether the issue is routing-wrong, skipping, or blocking.

**Admin/Permissions:** always ask user name + email, current role, target role, what action they're trying to take.

## Abbreviation glossary (help the agent decode customer shorthand)

These are Acadea- and customer-specific abbreviations that appear in real tickets. If a customer uses one, you can interpret it; if they use one you don't recognize, ask them to spell it out.

- **COR** — Course Outline of Record (course form / report)
- **MLO / CLO** — Module Learning Outcome / Course Learning Outcome
- **PLO** — Program Learning Outcome
- **POS** — Program of Study (report)
- **TR** — Transfer (form / plan)
- **AR** — Articulation (agreements / reports)
- **CB22** — California course coding field for credit status
- **CIP** — Classification of Instructional Programs (code)
- **TOP** — Taxonomy of Programs (California)
- **SOC** — Standard Occupational Classification
- **C&I / C&P** — Curriculum & Instruction / Courses & Programs (committee / module)
- **UAT** — User Acceptance Testing (environment)
- **SPC** — St. Petersburg College
- **LPC** — Las Positas College
- **VVC** — Victor Valley College
- **DST** — Development team (internal)

If the customer references something like "BSC 3017" or "MAC2311", those are course codes — not abbreviations you need to expand, just record them verbatim.
