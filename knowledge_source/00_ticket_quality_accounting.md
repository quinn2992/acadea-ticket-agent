# Ticket Quality Accounting — Acadea Ticket Agent

> Status: analytical groundwork, not the final knowledge pack. Everything here is evidence-based from the 848-ticket corpus + the SOP + the April 16 meeting transcript. A later pass will distill this into the 5–8 curated markdown files that the agent actually loads into its system prompt.

---

## 0. TL;DR for the team

- **The "gold standard" data is rougher than the label suggests.** 82% of historical tickets do not state a business use case. 23% have vague subjects. 20% describe a UI problem with no screenshot or URL. 25% of first comments were authored by someone other than the ticket's named requester (likely CSM-relay). The SPC/Craig/Armando datasets are the best we have, but Kali's remark — "none come to mind" when asked who writes stellar tickets — is confirmed by the numbers, not just intuition.
- **The SOP and actual practice diverge meaningfully.** The SOP prescribes a `Customer Short Code - Module Category - Meta Data` summary; only ~30% of tickets use that shape. The SOP bans urgency in the summary; SPC puts URGENT in subjects all the time. The SOP requires a Business Use Case section; almost nobody writes one.
- **There is enough real signal to train an interview.** The same ~10 clarifying questions appear again and again in support's first reply. If the agent asks those 10 up front, most tickets would not need triage clarification.
- **The hierarchy is: Kali's philosophy > SOP mechanics > current customer practice.** Current practice is the training data floor, not the ceiling.

---

## 1. Data footprint

| Dataset | Tickets | Comments | Avg comments/ticket | Customer ↔ Support comment ratio |
|---|---:|---:|---:|---:|
| SPC (St. Petersburg) | 606 | 4,060 | 6.7 | 31.5% / 68.5% |
| Craig Kutil (Las Positas) | 199 | 1,331 | 6.7 | 38.1% / 61.9% |
| Armando Barajas (Victor Valley) | 43 | 342 | 7.95 | 30.1% / 69.9% |
| **Totals** | **848** | **5,733** | — | ~33% / ~67% |

Observations:

- Every dataset shows **roughly 2 support comments for every customer comment**. Tickets are conversations, not documents. The thread length (median 5, max 50) tells us a well-written description avoids multiple back-and-forths, not zero of them.
- SPC has 12 open tickets out of 606; Craig has 12 open of 199; Armando has 4 open of 43. The overwhelming bulk are closed, so we can see the full lifecycle.
- 25 of 606 SPC tickets have `priority: null`. Priority is often left default.

*Source: [analysis/01_dataset_overview.py](../analysis/01_dataset_overview.py) — [analysis/output/01_overview.json](../analysis/output/01_overview.json).*

---

## 2. Structural anatomy of a good ticket

### 2.1 What Zendesk actually holds

Each ticket is a JSON object with:

- `id` — internal Zendesk ID (e.g. 44819)
- `subject` — the title that matters most for triage
- `description` — the initial problem statement (this is the "ticket" the agent must produce)
- `tags` — free-form categorization applied by support during triage
- `priority` — low / normal / high / urgent (null is common)
- `status` — new / open / pending / hold / solved / closed
- `requester_id` — who opened it
- `comments[]` — full thread; first comment usually mirrors `description`

### 2.2 Kali's SOP: the canonical structure

From `META-Ticketing (SOP)-170426-080916.pdf`:

**Summary format:** `Customer Short Code - Module Category - Meta Data` — explicitly *"do not insert urgency in ticket summary"*.

**Description structure** (from the SOP, verbatim):

```
Business Use Case: Brief Summary of the situation and ask. Use as much
detail as possible:
  - Define the request.
  - What is the purpose of the request? What problem are we solving for?
    Highlight the consequences of not addressing the problem or leveraging
    the opportunity.
  - Who is impacted: all customers, specific customer, customers w/ certain
    settings? (if full scope of impact is unknown - keep as question)
  - Is there a target due date? (hard launch date from 3rd party?)

Functionality Overview: (technical scope added by triaging resource)
```

**Priority:** default Medium; adjusted after triage. SLAs:

| Priority | Definition | SLA |
|---|---|---|
| Critical | Production outage, connection errors, major security, 500s | 1–2 business days |
| High | Break/fix for specific product function, no workaround, UI bugs, long load times, session expiration | 1–5 business days |
| Medium | Commercially necessary configuration (form, tab, reporting, workflows, lookups), break/fix with a workaround available | within 30 days |
| Custom Support (Complex Config) | 5–16 hours: new proposal types, proposal cloning/reactivation, new agenda reports, new calculated fields, new show/hide, course block libraries | 30–60 days |
| Custom Support (Enhanced Service) | Paid project work: data imports, bulk updates, custom reports, API integrations, module revamps | Per SOW |
| Low | 90+ days out, CSS/logo updates | ICB |

**Modules (Jira, "new" scheme):** API-Webservices, Assessment, C&P, Catalog, Courses, Course Block Library, Packages, Policy, Program Mapper, Program Review, Programs, SSO, Syllabus.

**Categories (Jira, "new" scheme):** Admin/Users, Course Blocks, Cross Listings, Lookup Manager, Organization, Proposal Types, Proposals, Reports, Search, Tab, Workflows.

**Versions:** Maverick, Meta (V3), V2.

**Issue types:** Epic, Story, Task, Sub-task, Bug (break/fix).

### 2.3 The Maverick internal template

`Issue Ticket TEMPLATE-MAVERICK 1.docx` adds structure that is internal-testing-oriented:

- Ticket #, Title, Date, Requester, Final Pass Date
- Ticket Reason: FIX/BUG ◻︎ CHANGE ◻︎ NEW ◻︎
- Priority: High (ASAP) / Normal-Medium / Low (all with a "by [date]" field)
- Apply to: Sandbox ◻︎ Production ◻︎
- Description, Expected Results, Navigation
- TESTING block with test #, scenario, pass/fail, screenshot included (Y/N), comments

This template is a downstream artifact — testers use it to frame the fix. Customers don't fill it in, but the fields it asks for (Expected Results, Navigation, Apply to: Sandbox/Production) are worth extracting during the interview because support eventually needs them.

### 2.4 Where SOP and actual practice agree vs diverge

| Rule | SOP says | Actual practice says |
|---|---|---|
| Summary format `Short Code - Module Category - Meta Data` | Required | **~30% compliance.** 210/606 SPC tickets use an all-caps prefix. Craig: 8/199. Armando: 9/43. |
| "Do not insert urgency in ticket summary" | Prohibited | **28 tickets put URGENT/ASAP/CRITICAL/DUE in the subject.** All 28 are SPC. Zero in Craig/Armando. |
| Business Use Case in description | Required | **~18% of descriptions mention purpose, impact, or a reason.** Most just state the request. |
| Default priority Medium | Prescribed | Customers routinely self-assign urgent/high (117 urgent in SPC, 67 in Craig) — often from in-subject escalation rather than explicit field use. |
| No proposed solutions from non-dev | Kali's rule (Apr 16) | Common in small requests: "Please just remove the word 'Intersegmental'", "It is OK to keep the field in the proposal, just remove from the report." |

*Sources: [02b_subject_patterns.py](../analysis/02b_subject_patterns.py), [07_anti_patterns.py](../analysis/07_anti_patterns.py).*

---

## 3. Content criteria per field

### 3.1 Subject

**What "good" looks like (empirical):**

- Leads with a customer short code (SPC / LPC / VVC) so triage can route by org at a glance.
- Names a module (REPORTS, PROGRAMS, COURSES, CATALOG, WORKFLOW, SYSTEM) — matches one of the 13 SOP modules.
- Includes a terse but specific artifact: a report name, a course number, a form element.
- Is a self-contained headline. A triage person who only reads the subject should know enough to route it.

**SPC's best prefixed subjects:**

- `SPC REPORTS - Course Outline Report Related Programs Issue` (id 44819) — customer code + module + specific artifact + nature of issue
- `REPORTS - Revise Adtl' Admin Report - 3 Year Course Review #2` — module + specific report + version
- `SPC SYSTEM - Proposal Launch Permissions`
- `COURSES Reports - Course Impact Programs fix (from CS188 / ZD 39053)` (id 39760) — module + artifact + cross-reference to prior ticket

**Armando's descriptive-pipe style (mixed case, pipe-separated):**

- `Custom Comparison Report | Missing Example Assignments` (id 42680-ish) — artifact + specific symptom
- `Contact Hours Per Term Chart Error | Course Outline of Record Report` — symptom + parent report
- `Active Program | Cannot Add/Change Division & Department` — context + concrete blocker

**Craig's weakness:** 41% of Craig's subjects were flagged as vague ("Stalled platform", "Catalog Errors", "Requisite page issue", "Legacy Methods of Instruction"). This is the single biggest subject-line quality gap across datasets.

**Rule we'll codify for the agent:**

`<Org Short Code> – <Module> – <Specific artifact / symptom>`

Where *artifact* is a concrete noun (a specific report, a course code, a form tab) and *symptom* is what is wrong with it or what is being requested. No urgency words. No ALL-CAPS shouting.

### 3.2 Description

The SOP prescribes `Business Use Case:` as a literal section header. Real tickets rarely use the header but the best ones do carry the information inline. The strongest patterns:

- **First sentence is the situation in one breath.** (SPC 44819: *"Some of the Active Course Outline Reports are erroneously pulling in drafts of now historical versions of proposals or deleted draft programs in the Related Programs at the bottom of the report."*)
- **Immediate follow-up names the scope.** (SPC 36599: *"We'll need everything completed from Zendesk ticket 36577 and everything that was talked about this morning. Our C&I Committee meets tomorrow morning, so we are in a time crunch..."*)
- **Numbered or bulleted list when there are multiple sub-issues.** (SPC 36599 goes 1. Workflows 2. C&I Color Groups, then nested bullets with specific course codes and test cases.)
- **Direct URL or screenshot for UI issues.** (SPC 37326: *"Go to the Welcom tab and you will see a link. https://blog.spcollege.edu/.../TonjuaWilliams-241x300.jpg"*)
- **Verbatim error text + request ID for 500s.** (SPC 44755: *"LIVE: 500 - An internal error occcured, please reference RequestId 8000300c-0001-df00-b63f-84710c7967bb when contacting support."*)

**What tends to be missing even in strong descriptions:**

1. **The "why".** Most tickets say what is wrong; few say why it matters. The exception is when there is an external deadline ("registration opens today", "C&I Committee meets tomorrow morning", "hard launch date from third party"). The agent should probe for this every time.
2. **Who is affected.** Kali's SOP explicitly asks for scope of impact ("all customers / specific customer / customers with certain settings"); this is absent in >80% of tickets.
3. **What the customer expected vs what happened.** The Maverick template has `Expected Results:` but customers don't fill it in. They describe the bug, not the contrast.
4. **Steps to reproduce.** Rare and usually inferred by support from screenshots.

### 3.3 Screenshots and attachments

About 35% of tickets reference a screenshot or include an inline image. Support's single most common clarifying ask is *"Please share a screenshot that includes the URL"* — they want to see both the bug and the environment proof in one frame.

**Good screenshot practice observed:**

- Inline at the point in the description where the visual matters, not dumped at the end.
- Multiple screenshots labeled by what they show (SPC 36599 references "my production screenshot and your video of your production site").
- URL bar visible (Kali's note in old exec brief: screenshots without URL bars force a clarification round).

**Anti-pattern:** screenshots attached with no description, or described as "see attached" with no framing.

### 3.4 Priority

The SOP says default Medium. Customers don't do that — they escalate via subject (URGENT in title) or via the priority field directly. 117/606 SPC tickets are marked `urgent`, which is far more than a reasonable triage rate.

The agent should set priority to `normal` by default and only raise it when the customer describes a condition that matches an SOP Critical/High definition (outage, 500s, blocked flow with no workaround). Even then it should frame the priority as the customer's claim, not a decision — triage adjusts after.

### 3.5 Tags

Tags are 90% operational/workflow state — `complete`, `jira_escalated`, `meta`, `priority_5_today_s_tasks`, `solvedemailsent`, `curricunet`, `billable`, `for_approval`. Not customer-authored. The agent does not need to emit tags. They get applied by support during triage. Noting here that only 12% of tickets carry any of the SOP's semantic labels (`Configuration` at 108, `Reporting` at 56, `ConfigFeatureRequest` at 9, etc.).

*Source: [03_tags.py](../analysis/03_tags.py) — [03_tags.json](../analysis/output/03_tags.json).*

---

## 4. The Kali overlay

Quoted from the April 16 "Follow-up: Quinn Fresh Eye Report" transcript. These are the rules that sit on top of the SOP mechanics — they are what separates a mechanically complete ticket from a genuinely useful one.

### 4.1 Business Use Case and Size of Impact are the two most important things

> *"Use case and size of impact — the two things I think we really talked about."*

> *"Business use case and finding the size of impact would uncover \[the real problem\] when you go and you are that support role on the client services side."*

Both are optional fields in practice today and missing from 80%+ of tickets. They are the two fields the agent must extract and make non-optional.

- **Business use case** = *what is the customer trying to accomplish in their world.* Not what button is broken — what end state is blocked.
- **Size of impact** = *how many users / how much money / how much time is this costing, and for whom.* All users, one curriculum specialist, the entire registration window?

The agent does not need a rigid Q&A. It needs to get these two facts out of the customer without the customer noticing they're answering a fixed form.

### 4.2 Client services should not propose technical solutions

> *"We don't want customer service, client services to tell us how to solve the business use case they are trying \[for\] or problem that the customer is having that we are solving for, because we need to empower our triage and our support team and the programmers and developers to make those judgments based off all the expectations for how our system should behave."*

> *"The client services is setting a technical expectation for something we can't support. The customers copied on that, and then we don't look aligned internally about what we can do and what we can't do."*

By extension: **the customer should not propose technical solutions either.** The agent must translate "please just remove the word 'Intersegmental'" → "on the Program Requirements report, narrative page, the string 'The California Intersegmental General Education…' needs to change; business reason: \[…\]; acceptable outcomes: \[…\]".

The rule: **describe the problem and the desired end state. Do not prescribe the implementation.**

### 4.3 Value-add, not pass-through

> *"Let's not just pass through. Let's be intentional. I'm not cutting and pasting the customer's issue and just sending it on. I'm actually trying to understand what problem the customer is having. And I'm a resource for them asking specific questions so I can arm our support with more information."*

The three downstream harms of pass-through that Kali called out:
1. Slower response time from support.
2. Slower UAT time.
3. Missed work / rework, because customer expectation diverges from what got built.

**The agent is the value-add layer.** It plays the role Kali wants CSMs to play — the fact-finder who asks "why do you want it like that?" before anything is written.

### 4.4 Customers don't always know what they want

> *"Users don't even really know what they want and users will make requests that are different than what their behavior actually matches."* — Quinn, paraphrasing Henry Ford

> *"None come to mind. I think you have your answer, Quinn. It's not obvious and immediate. None, none, none come to mind."* — Kali, when asked if any customer writes stellar tickets consistently

Take current ticket style as a floor, not a target. The agent should be strictly better than the best customers we have today.

### 4.5 Don't add more fields, extract better information

From the transcript: Acadea recently **took fields out** of the ticket form because customers complained of too much friction. Adding "business use case" and "size of impact" as form fields was discussed and backed off — the worry is they'd be filled with a restatement of the issue.

Implication: **the interview, not the form, is where these get extracted.** That's exactly what this agent is for. The agent can ask about business use case without adding a required field to Zendesk.

---

## 5. Issue taxonomy — derived empirically

### 5.1 Subject-prefix frequencies (all-caps form)

After stripping leading customer code (SPC/LPC/VVC):

| Canonical prefix | Count | Likely SOP Module | Likely SOP Category |
|---|---:|---|---|
| REPORTS | 21 | — | Reports |
| PROGRAMS | 18 | Programs | Proposals |
| COURSES | 15 | Courses | Proposals |
| ARTICULATIONS | 6 | Programs / Courses | Cross Listings |
| SYSTEM | 5 | — | (platform-wide) |
| PROPOSAL LANDING PAGE | 2 | — | Proposals |
| APPROVALS | 2 | — | Workflows |
| SEMESTER/TERM TABLE | 1 | — | Lookup Manager |
| WORKFLOW | 1 | — | Workflows |
| CATALOG | 1 | Catalog | — |
| SEARCH | 1 | — | Search |

### 5.2 Module-keyword hits across all 848 subjects (keyword anywhere, case-insensitive)

| Keyword | Tickets |
|---|---:|
| COURSE(S) | 82 |
| PROGRAM(S) | 68 |
| PROPOSAL | 65 |
| REPORT(S) | 55 |
| ADMIN | 35 |
| CATALOG | 29 |
| SEARCH | 23 |
| ARTICULATION | 21 |
| SYSTEM | 15 |
| WORKFLOW | 13 |
| API | 6 |
| PROGRAM MAPPER | 5 |
| POLICY | 2 |
| SSO | 2 |
| ASSESSMENT | 2 |
| SYLLABUS | 1 |

### 5.3 Recommended module list for the agent (empirically justified)

From most to least frequent in the corpus, collapsing synonyms:

1. **Reports / Reporting** — course outline reports, program reports, admin reports, comparison reports, agenda reports. Largest single bucket (~38% of tickets when you include "Reports" ticket-topic classification at 321/848).
2. **Programs / Proposals** — proposal types, proposal launches, pathways, transfer plans, program forms, teach-outs. ~35%.
3. **Courses / Course Outlines** — COR, requisites, course blocks, units/hours.
4. **Catalog** — articulations catalog, catalog downloads, images/RTEs in catalog, catalog policy pages.
5. **Workflows / Approvals** — C&I committees, approval groups, level-N tech review.
6. **Articulations** — AR forms, AR reports, articulation agreements.
7. **Search / Dashboard** — search dashboards, output fields, sort options.
8. **System / Platform** — outages, 500 errors, login issues, sandbox refresh, API issues.
9. **Admin / Permissions / Users** — user access, permission changes, lookups, role assignments.
10. **Syllabus (Simple Syllabus)** — MLO/CLO sync issues.
11. **CIP / Lookup Data** — FL CIP table updates, TOP/CIP crosswalks.
12. **Units / Hours** — CB22 fields, contact hours, noncredit calculations.

Note: **this list is denser than the SOP's 13 modules** because it also covers cross-cutting concerns (Admin, System) that sit outside a single module. The agent should let the customer pick from a flat list and map to the SOP's Module/Category fields after.

*Source: [02b_subject_patterns.py](../analysis/02b_subject_patterns.py), [05_followup_questions.py](../analysis/05_followup_questions.py).*

---

## 6. Common follow-up questions by issue type

The interview-flow goldmine. Derived by taking the first public support reply on each ticket and pattern-matching against 16 clarifying-question categories. These are the questions support ends up asking in clarifying first replies, and that the agent should preempt.

*Source: [05b_question_categories.py](../analysis/05b_question_categories.py) — [05b_question_categories.json](../analysis/output/05b_question_categories.json).*

### 6.1 The nine canonical clarifying questions (observed, ranked by frequency)

| Rank | Category | What support actually asks | Observed in |
|---:|---|---|---:|
| 1 | **Environment** | *"Is this happening on production, sandbox, or UAT? Which site/environment?"* | 9.4% of first replies |
| 2 | **Scope confirmation** | *"Just to confirm, you want X on report Y in column Z, is that right?"* | 2.7% |
| 3 | **Impact scope** | *"Is this affecting all users/programs/courses or only specific ones?"* | 2.7% |
| 4 | **Scope boundary** | *"Do you want this change on all forms or only \[this specific form\]?"* | 2.1% |
| 5 | **Which specific record** | *"I need to know the exact program you're looking at"* | 1.4% |
| 6 | **Screenshot (general)** | *"Can you send me a screenshot?"* | 0.7% |
| 7 | **Still happening** | *"Are you still seeing this error?"* | 0.6% |
| 8 | **Screenshot with URL bar** | *"Can you include a screenshot from the user that includes the URL?"* | 0.5% |
| 9 | **Which browser** | *"Does this happen on different browsers?"* | 0.5% |

Note: these percentages are conservative (regex-based pattern matching; a human reader would likely find 2–3× as many clarifying-question cases, many phrased more colloquially). But the *ranking* is what matters — these are the top categories, and the agent should address all of them in the interview.

### 6.2 Verbatim exemplar questions (for the knowledge pack)

All quoted from actual support replies:

- *"Can you include a screenshot from the user that includes the URL?"* — SPC ticket 37639
- *"What are your duplication steps, so I can follow along to reproduce the error you're seeing?"* — SPC ticket 38314
- *"What user that is logged in that is not seeing this option for this course?"* — SPC ticket 43926
- *"I need to know the exact program that you're looking in, so I know which program form version needs to be refreshed."* — SPC ticket 44327
- *"Just to confirm, you want this field 'Active Status' from page 'Codes and Dates' added to the admin reports 'Articulation AR articulated programs' and 'Articulation AR courses', correct?"* — SPC ticket 44467
- *"Do you want to remove these three dropdowns from the Distance Education course form only, or do you want to remove them from all course forms?"* — Craig ticket 42417
- *"Are you still getting the error does it happen on different browsers does it happen for different users?"* — SPC ticket 21366
- *"Karen, to add this option I need to know what PSAV stands for."* — SPC ticket 27031 (abbreviation resolution)
- *"Which column in both reports do you want this field to display in?"* — SPC ticket 44467

### 6.3 Topic-specific preempts

From the question-category analysis by topic:

- **Reports tickets (321 in corpus, 18% need clarification):** environment (production vs sandbox) is the single most common ask. Scope-confirmation ("which column, which report") is second. Agent should always ask: *which report name, which column/field, production or sandbox, before or after a specific refresh?*

- **Programs tickets (299 in corpus, 15% need clarification):** scope boundary ("only this proposal type? all? specific form version?") is disproportionately common. Agent should always ask: *which program, which form version, which proposal type, does this apply to all or one?*

- **Courses tickets (119, 23% need clarification):** environment + scope confirmation lead. Course code + form version + what section of the form is the agent's must-have.

- **System tickets (10, small N but high-stakes):** the two biggest asks are steps to reproduce and whether the issue is still happening. Agent should always capture: *the exact error text (copy-paste), RequestId if shown, browser, logged-in user, what action triggered it.*

- **Workflow/Approvals tickets:** which step, which user, which role, approval vs disapproval flow. SPC's best workflow tickets (e.g. 36599, 37910) contain numbered reproduction in the description itself.

- **Admin/Permissions tickets:** which user, which role, which site. "Low N but near-100% need clarification" if the customer just says "please update access."

---

## 7. Exemplar shortlist

Fourteen tickets picked for diverse strengths. Each is cited with ID, dataset, a verbatim excerpt of the description, and a short note on what the agent should learn from it. Full descriptions available in [analysis/output/06_exemplar_candidates.json](../analysis/output/06_exemplar_candidates.json).

### E1. SPC #25523 — "Curriculum Committee Agenda Report" [Reports]

> *"I've attached some screen shots of the report as it is running right now (which is indicating a Server Error) and some updates to the formatting and fields. Most important for this report is the ability to identify the type of change that occurred in the proposal, i.e. prerequisites, MLOs, credit hours, Course Description, etc., which is already identified via the Comparison report. Can this be added on this report ('Impact' field)?"*

**Why it's strong:** Opens with a specific artifact (Curriculum Committee Agenda Report), frames the issue in one sentence, offers a parallel-precedent ("already identified via the Comparison report"), and asks a concrete binary question at the end. Support did not need to clarify. Highest score in its topic.

### E2. Craig Kutil #40786 — "NMAT 210 - Unit and Hours / Validation and Missing Data" [Reports/Courses]

> *"A recent ticket added the CB22 field to the units and hours tab in course proposals. The new CB22 field is not filtering correctly based on the credit status of N-Non Credit.  
> - See the image below you can see that the CB22 option of 'Y' is not correct since it is a Non Credit Course. According to the course detail in V2 this course should have 'C' as selected value for CB22  
> - Also note that there are '0' hours in the total noncredit hours / According to the same course in V2 it should have 72.0 Lecture hours and 72.0 Total Non Credit Hours.  
> - This course is part of program #565 - Foundational Mathematics Pathway - Certificate of Competency (Active)..."*

**Why it's strong:** Structured bullet list, specific course code (NMAT 210), specific field (CB22), specific program (#565), specific expected values (72.0 Lecture hours). Expected-vs-actual implied cleanly by cross-referencing V2. Caveat: first line is `**This ticket created by NancyH on behalf of Craig Kutil**` — literally a CSM-relay, which is the pattern Kali wants to move away from, even though the content is strong.

### E3. SPC #36599 — "SPC - Workflows and Sandbox - UYRGENT - DUE 01/19" [Programs / Workflows]

> *"In looking at both the workflows and C&I color groups we are still experiencing problems. \[…\] We'll need everything completed from Zendesk ticket 36577 and everything that was talked about this morning. Our C&I Committee meets tomorrow morning, so we are in a time crunch for being able to have this all ready and working for them.  
> 1. **Workflows** – please see the screenshots in the email trail below.  
> 2. **C&I Color Groups** – Tested in sandbox  
>    - candi@spcollege.edu was assigned C&I Yellow Group  
>    - I changed ATE 2612 from blue assignment to yellow, this was the only course assigned to yellow but all these other courses still come up as well.  
>    - Also, it seems to only be pulling in certain courses due to workflow issues and not pulling everything that has gone through our Level 2 Technical Review.  
>      - E.g., CJE 2645 (was approved in prod tech review 1/10/23), DEH 2804L (was approved in prod tech review 1/12/2023)..."*

**Why it's strong:** Gives a concrete *business reason* ("C&I Committee meets tomorrow morning, so we are in a time crunch"), links to the prior ticket (36577), groups the sub-issues with headers, tests cases include course codes with approval dates. Customer does their own QA in sandbox before filing. **Caveat:** SOP violation — "URGENT" and "DUE 01/19" in subject. Also typo ("UYRGENT"). The content is a model; the subject is not.

### E4. Armando Barajas #44323 — "VVC - Water Treatment Leverl I & II" [Workflow]

> *"We need to look at this workflow. Liisa Harvey and and Scott Jones are showing required as Curriculum Area Representative and they are not for this Division or Deparment."* *(+ inline screenshot)*

**Why it's strong:** Two sentences, names the specific workflow, names the specific people who shouldn't be there, provides the visual. Support closed without clarification.

### E5. SPC #37326 — "SPC - Adding a Image" [Catalog]

> *"Go to the Welcom tab and you will see a link. https://blog.spcollege.edu/president/wp-content/uploads/sites/45/2022/10/TonjuaWilliams-241x300.jpg  
> This link is a picture and we want the picture to show on the page. I got with Heather and we both tried to figure this out, it seems like the image in the RTE is not working like it should. We need to either correct this or provide instructions and screen shots to SPC on how to add a picture inside the catalog with a link."*

**Why it's strong:** Contains a *navigation path* ("Go to the Welcom tab"), an actual public URL, names who tried to reproduce internally ("I got with Heather and we both tried"), and names two acceptable outcomes ("either correct this or provide instructions"). That last pattern — giving support two acceptable resolutions — is rare and very good.

### E6. SPC #44755 — "SPC - URGENT Course requisite and level 500 errors etc. Credentials" [Courses / System]

> *"Angela and Troy, I think we have a multi-level issue going on here. Please note that I've received the same 500-level errors when stepping thru the code, but everything from this point in the email is a reference to Postman.  
> LIVE: https://mws.services.curriqunet.com/scripts/webservices/generic_meta/clients/versions/v5/stpetersburg.cfc?method=getEntityData  
> TEST: https://mwsdev.services.curriqunet.com/scripts/webservices/generic_meta/clients/versions/v5/stpetersburg.cfc?method=getEntityData  
> Username: stevens.paul@spcollege.edu  
> MAC2311  
> LIVE: 500 - An internal error occcured, please reference RequestId 8000300c-0001-df00-b63f-84710c7967bb…  
> TEST: 200 - Okay  
> DEP2004  
> LIVE: 500 - An internal error occcured, please reference RequestId 8000300c-0001-df00-b63f-84710c7967bb…  
> TEST: 500 - An internal error occurred -- RequestId: 8000b248-0007-fb00-b63f-84710c7967bb; Exception message: Expected to find column AACodeId in entity data for table CourseAACode, but did not."*

**Why it's strong:** This is the **gold standard for system/API tickets.** Differentiates LIVE vs TEST endpoints, provides exact URLs, provides the credentials to reproduce, provides verbatim 500 error text with RequestId. Support has everything they need to hand this to dev without asking a single question.

### E7. SPC #42140 — "SPC - URGENT - System error; server down?" [System / Search]

> *"We are getting the following error when trying to login to META. The public search and sandbox appear to be fine. I tried to put in a ticket but not sure that it worked. Please let me know ASAP when fixed."* *(+ inline screenshot)*

**Why it's strong:** Three sentences. Names what's broken (login to META), what's NOT broken (public search and sandbox — isolates the layer), confirms the ticket-creation path itself may be unreliable (useful metadata), and includes a screenshot. This is the "emergency" template done right — minimum words, maximum triage-relevant facts.

### E8. Craig Kutil #39886 — "Repetitive Actions" [Admin/Workflow]

> *"Hello, In the attached screenshot, you can see that under Take action as an administrator, I can select Articulation Officer, Articulation Officer - Revisions Requested, and Articulation Officer - Support. The last two options send you to the same screen as the first option - just Articulation Officer. Since the other two are repetitive and redundant, can you please remove them? This occurs at every Step, so they can just be removed for all participants."*

**Why it's strong:** Describes the observed behavior precisely, diagnoses that two options are functionally duplicates of a third, proposes the removal AND scopes it ("at every Step, so they can just be removed for all participants"). The subject is weak ("Repetitive Actions" — vague) but the description is exemplary. **Caveat (Kali):** this is on the edge of solution-smuggling. Better framing would be "the three options behave identically; customer wants only one visible." Agent should rephrase.

### E9. SPC #28272 — "Error on modifying MLOs" [Courses]

> *"When trying to modify MLOs on EMS 2601 we are receiving the error: 'We're Sorry! An error has occurred. The details of this error have been emailed to the web site administrator.' The user errantly structured the MLOs but we cannot get into it to correct. Thanks!"*

**Why it's strong:** Short. Specific course code (EMS 2601). Exact error text in quotes. And — rare — self-diagnosis of the *cause* ("The user errantly structured the MLOs") plus the *blocker* ("we cannot get into it to correct"). The interview flow that produces this is: *what's the error, what course/record, what did you do right before it, what do you suspect caused it, what can't you do now?*

### E10. SPC #44819 — "SPC REPORTS - Course Outline Report Related Programs Issue" [Reports]

> *"Some of the Active Course Outline Reports are erroneously pulling in drafts of now historical versions of proposals or deleted draft programs in the Related Programs at the bottom of the report. Please see the attached ticket for details and screenshots…"*

**Why it's strong:** Single-sentence problem statement that specifies WHICH report, WHICH section of the report, WHICH data is wrong, and HOW it's wrong ("drafts of now historical versions", "deleted draft programs"). Subject is perfect SOP format (`SPC REPORTS - <specific artifact + issue>`).

### E11. SPC #43301 — "SPC - REPORTS - Program of Study & Comparison - Program - Follow up - #43221" [Reports]

**Why it's strong (from subject alone):** Cross-references prior ticket 43221. Names two specific reports in scope. Tags itself as a "Follow up" so triage can see the lineage. This is the cleanest "continuation ticket" subject pattern in the corpus.

### E12. Armando Barajas #43743 — "VVC - Assist - Getting an Error" [Assist/Third-party integration]

**Why it's strong:** Armando explicitly separates "Acadea system" issues from "Assist" (a third-party California articulation system) issues. Customer is doing their own layer isolation before submitting. Agent should encourage customers to do this.

### E13. SPC #37614 — "SPC - Follow up on 37575 and 37588 - URGENT" [Courses]

**Why it's strong (structural):** Cross-references two prior tickets in the subject. This is how SPC handles re-opens / related-issue bundles. The agent should mimic this pattern whenever a customer mentions "this keeps happening" or "like ticket X."

### E14. SPC #41817 — "SPC - API - URGENT" [Courses / API]

> *"Starts with ticket # 41694 that you submitted 11/14/2024. There are no comments or anything to indicate this is being worked on. Please let me know status. This needs to be fixed ASAP. And, maybe along with that… Since moving to Maverick some more things have come to light that are not working correctly. This issue may be related to the above or at least indirectly. The API pull, before V4, was looking \[…\]"*

**Why it's strong:** Ties directly to ticket #41694 with date. Explicitly hypothesizes a relationship ("may be related to the above or at least indirectly") — the *agent should capture customer hypotheses as hypotheses, not commit to them as diagnoses.* **Caveat:** This is also an example of a status-check ticket bundled with a new issue, which makes triage harder. Agent should separate these into two tickets if the customer does this.

### Summary of the 14

- 11/14 are SPC, 2/14 Craig, 1/14 Armando. Reflects both SPC's volume (71%) and the depth of content there.
- Strengths distribute across: specific artifact naming (E1, E2, E10), business-reason/time-constraint (E3), verbatim error capture (E6, E9), layer isolation (E7, E12), structured bullet sub-issues (E2, E3), cross-referenced prior tickets (E11, E13, E14), two-outcome framing (E5), navigation path (E5).
- Weaknesses still present in even the best: "URGENT" in subject (E3, E6, E13, E14), missing explicit business use case (E9 has self-diagnosis but no impact scope), subtle solution-prescription (E8).

---

## 8. Anti-patterns with evidence

All rates computed across 848 tickets. *Source: [07_anti_patterns.py](../analysis/07_anti_patterns.py).*

### A1. Urgency in the subject — 3.3% overall, 4.6% of SPC, 0% of Craig/Armando

Violates the SOP's explicit rule: *"do not insert urgency in ticket summary"*. 28 tickets carry `URGENT`, `ASAP`, `CRITICAL`, or `DUE <date>` in the subject, all from SPC.

Examples:
- *"SPC URGENT API access"* (44319)
- *"URGENT - any system or server changes?"* (43963)
- *"URGENT Course Block Library, blocks missing"* (42931)
- *"URGENT Catalog is not accessible"* (42766)
- *"SPC - Workflows and Sandbox - UYRGENT - DUE 01/19"* (36599)

Agent rule: strip urgency words from the subject and route urgency into the priority field + a dedicated "business impact / deadline" line in the description.

### A2. Vague subject — 22.8% overall, 17% SPC, **41.2% Craig**, 18.6% Armando

Three or fewer words, or matches generic phrases ("help", "issue", "question", "problem", "bug", "error", "re: …"). Craig's dataset is the heaviest offender.

Examples:
- *"Stalled platform"* (Craig)
- *"Catalog Errors"* (Craig)
- *"Requisite page issue"* (Craig)
- *"Legacy Methods of Instruction"* (Craig)
- *"Refresh Sandbox"* (SPC 40010)
- *"SPC - Cloning"* (SPC 39998)
- *"Ind Cert file"* (SPC 40780)
- *"Courses missing number"* (SPC 41964)

Craig in particular is a reminder: the "gold standard" label for a customer applies to his description quality more than his subject quality. The agent must not copy his subject style.

### A3. Empty or tiny description — 5.3% overall

45 tickets have descriptions under 80 characters. Most common pattern: a one-liner request with no surrounding context.

Examples:
- SPC 44766: *"Please refresh our SANDBOX at your earliest opportunity. Thank you!"*
- SPC 43661: *"Please send SPC a new Data Dictionary."*
- SPC 41625: *"Would like to have Program Code added to the Sort Options."*
- SPC 41552: *"After they go live with Maverick, remove this tab from Programs."*

These aren't useless — sandbox refresh is a routine request — but they carry zero business context. Even for routine asks, the agent should append "purpose" and "anything else we should refresh at the same time?"

### A4. Forwarded email dumped as description — 0.1% in strict regex, ~3 more observed on inspection

Rare but damaging when it happens. Description is literally a pasted email chain with `From:`/`Sent:`/`Subject:` headers. Loses all structure.

Example: SPC 22588 (*"Either of those - whatever works best for you. The ENC-1101, ENC-1102 format is how we have done so with the legacy system."*) — description is the tail of a pasted email reply, with no opening context.

Agent rule: if the user pastes an email chain, extract the underlying issue and re-write from scratch.

### A5. Solution-smuggling — observed in ~0.2% by strict regex, but qualitatively higher

Customer prescribes the technical fix instead of describing the problem. The regex was strict; inspection of samples suggests the real rate is closer to 5-10%.

Regex-caught examples:
- SPC 41029: *"…It is OK to keep the field in the proposal, just remove from the report."*
- Craig 41392: *"Please just remove the word 'Intersegmental' where it currently says…"*

Informal examples from the exemplar list:
- Craig 39886: *"the other two are repetitive and redundant, can you please remove them? This occurs at every Step, so they can just be removed for all participants."*

Kali's rule (Apr 16): *"The client services is setting a technical expectation for something we can't support. The customers copied on that, and then we don't look aligned internally."* Same rule applies to customer-to-support directly.

Agent rule: if the customer says "just remove X" or "just change X", rephrase into "current behavior: X appears; desired behavior: customer wants it not to appear; reason: …; acceptable implementations: dev team to determine".

### A6. UI problem described with no screenshot or URL — 20.3% overall

1 in 5 tickets describe error/broken/missing/wrong behavior without giving support any visual or navigational anchor. Support then asks (see §6) — the #1 clarifying ask is screenshot-with-URL.

**Note this count includes plenty of requests that genuinely don't need a screenshot** (e.g., "add a new column to report X"). The cleaner metric would be "bug-shaped descriptions" only; a tighter heuristic would lower this but still leave a sizable rate. The conservative reading: at least ~1 in 5 tickets would benefit from an attached screenshot and didn't include one.

### A7. No business use case — 82.4% overall (83% SPC, 83% Craig, 67% Armando)

The biggest single gap in the corpus. 699 of 848 tickets have no language matching purpose, impact, blocking, compliance, or any explicit reason. Armando is the closest to compliant (67% gap vs 83%), consistent with his descriptive style.

This is the single largest value-add surface for the agent. Kali's Apr 16 remarks make business-use-case extraction a non-optional interview step.

### A8. First comment not authored by the named requester — 24.9% overall (28.5% SPC)

The CSM-relay pattern. 211 of 848 tickets have a first comment whose author_id is not the ticket's listed requester. In SPC, a single author_id (372620713451) accounts for 129 of these — almost certainly a CSM repeatedly entering tickets on behalf of SPC contacts.

Kali's Apr 16 number for this (org-wide): ~20% of tickets are CSM-entered today, down from ~80% pre-July 2024. The 28.5% rate in our SPC sample is consistent with historical drag, since the dataset goes back to 2013.

The agent's product position — customer writes in → agent interviews → customer copy-pastes — is *the direct fix for this anti-pattern.* If the agent works, we should see A8's rate trend toward zero for customers using it.

---

## 9. Implications for the agent (preview, not yet the prompt)

What the interview must extract, in priority order:

1. **One-sentence problem statement** in the customer's voice. ("The course outline report is pulling in historical program drafts.")
2. **Business use case / impact.** *Who needs this, to do what, and what happens if we don't fix it or don't deliver it by when.* Kali's top field.
3. **Size of impact.** *One record / one program / one user / all users / site-wide.* Kali's second top field.
4. **Artifact identifiers.** Which report name, which course code, which program ID, which proposal type, which form version, which URL.
5. **Environment.** Production vs sandbox vs UAT. Most common single support follow-up question.
6. **Expected vs actual.** What the customer thought would happen vs what did happen.
7. **Steps to reproduce.** At least "go to X, click Y, observe Z."
8. **Evidence.** Screenshot with URL bar if UI. Verbatim error text + RequestId if error. "I tested in sandbox and got same result" if confirmed.
9. **Target date and driver.** "We need this by X because Y."
10. **Affected users and roles.** Names if known, roles if pattern.
11. **Prior related tickets.** Cross-reference IDs if customer volunteers them.

What the generated ticket must produce:

- **Subject:** `<Org Short Code> – <Module> – <Specific artifact + symptom>`. No urgency. Under ~80 chars.
- **Description:** Plain prose (not a form dump) that reads in the following order: one-sentence problem → business use case + impact scope → environment + artifact IDs → expected vs actual → repro steps → evidence (inline or referenced) → target date/driver → related tickets. No proposed technical fix; "desired outcome" is allowed.
- **Priority suggestion:** default `normal`. Raise to `high` if customer describes a blocker with no workaround. Raise to `urgent` only for outage / security / can't-submit-proposals-at-all / 500s.

What the agent must refuse to do:

- Prescribe the implementation. ("Please change field X to value Y" is the customer's language; "current behavior is X, desired end state is Y" is the agent's translation.)
- Declare root cause. ("I think this is a database issue" is the customer's guess; the agent captures it as a hypothesis labeled as such.)
- Include urgency words in the subject.
- Pass through the customer's vague wording unchanged.

---

## 10. Open questions and data weaknesses

Things the data cannot answer on its own; we should confirm with Kali or the support team before finalizing the knowledge pack.

1. **What customer short codes are authoritative?** SPC and VVC/VCCD are obvious in the data. Is LPC the code for Las Positas, or LPL? Both appear. Craig's tickets use "Las Positas" (mixed case) far more than either abbreviation — no consistent code is used.
2. **Module mapping for hybrid issues.** Many tickets span modules (e.g. "Articulation AR courses report" is both Reports and Articulations). The SOP's Module / Category model is single-valued; the agent will need to pick one and put the other in description.
3. **How support wants `Expected vs actual` phrased.** Do they want an explicit header, or inline prose? The Maverick template has it as a header; no customer ticket uses it.
4. **Is there a short-code convention we're missing?** 396/606 SPC subjects have no all-caps prefix. Are these considered sub-standard, or is the prefix-style only required for certain modules?
5. **Does Kali want the agent to push back on "URGENT"?** Mechanically, strip from subject. Conversationally, the agent could also ask "what makes this urgent?" to surface the actual business driver. Confirm desired behavior.
6. **Third-party boundary handling.** Simple Syllabus, Assist (California articulation), various SIS integrations — when a customer reports an issue, the agent should help them figure out whether it's Acadea or the upstream/downstream system. Do we have a list of known Acadea integrations + common failure modes?
7. **How granular should "module" be at collection time?** The SOP has 13 modules + 11 categories; the empirical data supports ~12 top-level topics. A flat picklist of ~12 is probably right, but customers without full vocabulary may need the agent to translate free-text into a module label.
8. **Priority self-reporting.** Today 117 SPC tickets are `urgent`; most do not meet the SOP's Critical threshold. Does Kali want the agent to show the SLA definitions during the interview so customers self-calibrate, or is that likely to add friction?

---

## 11. What this doc is NOT

- Not the system prompt.
- Not the final knowledge pack. The pack will be 5–8 small files distilled from this. Candidate file list for a future pass:
  - `01_north_star.md` — the agent's role, Kali's philosophy, what to refuse.
  - `02_ticket_anatomy.md` — subject/description/priority/evidence rules.
  - `03_interview_flow.md` — the 11 extraction targets + how to ask without interrogation.
  - `04_module_taxonomy.md` — the flat module list + mapping to SOP Module/Category.
  - `05_followup_preempts.md` — the 9 canonical clarifying questions, phrased as things to ASK the customer.
  - `06_exemplars.md` — 4-6 of the 14 shortlisted tickets as few-shot output templates.
  - `07_anti_patterns.md` — short list of things NOT to emit, with one-line reasons.
- Not a scoring rubric. Metrics here are descriptive, not a spec for a quality evaluator.
- Not design for the UI or the product. Copy-paste handoff, not API submission, is the v1 product — the knowledge pack doesn't need to know about that.

---

*Analysis scripts and raw outputs live in [`../analysis/`](../analysis). Re-run any script with `python3 analysis/<name>.py`.*
