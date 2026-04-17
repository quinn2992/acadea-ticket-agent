# Exemplars — four finished tickets to pattern-match on

These are reference outputs. They are not historical tickets verbatim; they are what the historical tickets *should have been*, reshaped into the format in `02_ticket_anatomy.md`. Study the shape. When you emit your own drafts, match this cadence.

## Exemplar 1 — Reports (clean, specific)

```zendesk
Subject: SPC - REPORTS - Course Outline Report pulling historical program drafts

Business Use Case:
SPC is using the Course Outline Report to prepare active course documentation for the upcoming catalog cycle. The report needs to reflect only current active program versions so the catalog and downstream systems stay consistent.

Impact:
Multiple active Course Outline Reports are affected. Any course whose "Related Programs" section is pulling in superseded or deleted drafts is unusable for catalog purposes. Scope appears to be system-wide for SPC rather than isolated to one course.

Environment:
Production.

Current Behavior:
The Related Programs section at the bottom of the Course Outline Report is showing drafts of historical program versions, and in some cases deleted draft programs, instead of only the active program version.

Expected Behavior:
Related Programs should list only currently active program versions. Historical and deleted drafts should not appear.

Steps to Reproduce:
1. Run a Course Outline Report on any active course tied to multiple program versions.
2. Scroll to the Related Programs section at the bottom.
3. Observe entries that reference deleted or historical draft programs.

Evidence:
Customer has screenshots and a prior related ticket. Customer will attach screenshots to the Zendesk ticket after pasting this draft.

Affected Users/Records:
Report output affects all SPC curriculum staff who consume the Course Outline Report.

Related Tickets:
Customer has not cited a specific prior ticket ID but believes this has come up before.

Target Date / Driver:
No hard deadline cited, but the catalog cycle is the driver for prioritization.

Priority (customer-suggested):
normal — impact is broad but there is no same-day blocker.
```

## Exemplar 2 — System, emergency (brief, precise)

```zendesk
Subject: SPC - SYSTEM - 500 errors on webservices getEntityData (LIVE)

Business Use Case:
SPC pulls course data from the webservices API to populate their public-facing catalog and student systems. The API being down means course data on their website is stale or missing, which is visible to students.

Impact:
Multiple course lookups are failing in production. Customer observed 500s across several course codes (MAC2311, DEP2004, DEP2102, CLP2140). TEST endpoint mostly returns 200, so the issue appears isolated to LIVE.

Environment:
Production. LIVE endpoint specifically:
https://mws.services.curriqunet.com/scripts/webservices/generic_meta/clients/versions/v5/stpetersburg.cfc?method=getEntityData

Current Behavior:
LIVE requests return: "500 - An internal error occcured, please reference RequestId 8000300c-0001-df00-b63f-84710c7967bb when contacting support." Same user, same requests, succeed on TEST endpoint with status 200.

Expected Behavior:
LIVE endpoint should return the same course data as TEST.

Steps to Reproduce:
1. Call LIVE getEntityData endpoint (URL above) with course code MAC2311.
2. Observe 500 with RequestId.
3. Call same endpoint on TEST — returns 200.

Evidence:
Verbatim error messages and RequestIds captured above. Customer can share Postman collection if needed.

Affected Users/Records:
Customer's API consumer (their website) is affected. Internal Acadea users may also be impacted.

Related Tickets:
None cited.

Target Date / Driver:
Ongoing outage — students are seeing missing course info on the public catalog right now.

Priority (customer-suggested):
urgent — production endpoint failing with 500s, customer-facing impact live.
```

## Exemplar 3 — Programs / Workflows (structured, time-bound)

```zendesk
Subject: SPC - WORKFLOW - C&I color group not pulling approved Level 2 courses

Business Use Case:
SPC's Curriculum and Instruction Committee meets tomorrow morning and needs the C&I color group (Yellow) to reflect courses that have passed Level 2 Technical Review. Right now the group is pulling the wrong set of courses and the committee cannot work off the current data.

Impact:
Affects the C&I Yellow color group for the entire upcoming committee meeting. Specific courses currently misrouted include CJE 2645 (approved 1/10/2023) and DEH 2804L (approved 1/12/2023). ATE 2612 was also tested in sandbox and routed incorrectly on disapproval.

Environment:
Sandbox tested; needs production fix followed by a sandbox refresh.

Current Behavior:
- Only some courses assigned to the Yellow group appear when filtering by that group.
- Disapproving a proposal (tested with ATE 2612) changes other members' actions to "Waiting on Changes" and makes the proposal disappear for them, without moving the proposal state.
- Level 2 Technical Review-approved courses (CJE 2645, DEH 2804L) are not appearing in the color group.

Expected Behavior:
- All courses assigned to the Yellow group should appear when the group filter is active.
- Level 2 Technical Review-approved courses should be included in the C&I color group eligibility set.
- Disapproval should move the proposal to the correct state without silently hiding it from other committee members.

Steps to Reproduce:
1. In sandbox, assign candi@spcollege.edu to the Yellow C&I color group.
2. Assign ATE 2612 to Yellow.
3. Filter by Yellow group — observe that other courses beyond ATE 2612 also appear.
4. Disapprove ATE 2612 — observe the state changes described above.

Evidence:
Customer has screenshots of both the filter behavior and the disapproval flow. Customer will attach to the Zendesk ticket after pasting this draft.

Affected Users/Records:
C&I Committee members, specifically reviewers assigned to the Yellow color group. ATE 2612, CJE 2645, DEH 2804L named as examples.

Related Tickets:
Related to ticket #36577 — customer requests both be addressed together.

Target Date / Driver:
Needed before C&I Committee meeting tomorrow morning. Production fix required, followed by sandbox refresh so committee can use sandbox if needed.

Priority (customer-suggested):
high — hard deadline tied to committee meeting, workaround unclear.
```

## Exemplar 4 — Catalog (configuration-shaped, short)

```zendesk
Subject: SPC - CATALOG - Semester/Term table add 2027 through Spring 2029

Business Use Case:
SPC's curriculum team is preparing proposals targeting Spring 2027 and beyond. The Semester/Term lookup does not yet include those entries, so proposals cannot be set to those terms.

Impact:
Blocks forward-dated proposal work across the curriculum team. Not currently blocking an active proposal launch, but the team wants the entries available to start drafting.

Environment:
Production.

Current Behavior:
Semester/Term lookup table ends before Spring 2027.

Expected Behavior:
Add the following entries to the Semester/Term table:

| Title | Catalog Year | Code |
|---|---|---|
| Spring 2027 | 2027 | 675 |
| Summer 2027 | 2027 | 680 |
| Fall 2027 | 2027 | 685 |
| Spring 2028 | 2028 | 690 |
| Summer 2028 | 2028 | 695 |
| Fall 2028 | 2028 | 700 |
| Spring 2029 | 2029 | 705 |
| Summer 2029 | 2029 | 710 |

Steps to Reproduce:
Not applicable — configuration request.

Evidence:
Not applicable.

Affected Users/Records:
SPC curriculum team.

Target Date / Driver:
Customer would like this as soon as possible so forward-dated proposal drafting can proceed.

Priority (customer-suggested):
normal — standard configuration update; no hard deadline cited.
```

## What these exemplars share

- **Subject** leads with org code + module + specific artifact + symptom, no urgency words.
- **Business Use Case** states the end goal, not the symptom.
- **Impact** is quantified (how many users / records) or at least scoped.
- **Environment** is always set.
- **Current vs Expected** uses contrasting, symmetrical structure.
- **Steps to Reproduce** uses numbered list when a repro is possible; says "Not applicable" when it isn't.
- **Evidence** names what exists and where the customer will attach it.
- **Priority** includes a one-sentence reason.
- No solution prescribed; no urgency screaming; no Jira fields.
