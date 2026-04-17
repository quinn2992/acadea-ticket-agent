# Modules — pick one for every ticket

Use ALL CAPS in the subject. Pick the single closest match. If it truly spans two, pick the more specific one and mention the other in the body.

| Module | What it covers | Common tickets |
|---|---|---|
| **REPORTS** | All reporting: course outline reports, program reports, admin reports, comparison reports, agenda reports, impact reports, catalog exports | "This report shows the wrong value in column X", "Add a column to the AR report", "New custom report" |
| **PROGRAMS** | Program proposals, program forms, program outcomes (PLOs), program types (new/modify/teach-out), pathways, transfer plans | Proposal launch issues, form changes, active status bugs, PLO pages, pathway display |
| **COURSES** | Course proposals, course outlines (COR), course requisites, course blocks, MLOs/CLOs, methods of instruction, hour calculations | Course form issues, requisite logic, assessment components, course codes, Simple Syllabus sync |
| **CATALOG** | Published and unpublished catalog, articulations catalog, catalog policy pages, RTE content, catalog images, catalog PDF output | Catalog page errors, image/link issues, policy text, catalog access |
| **WORKFLOW** | Approval workflows, approval groups, color groups, review steps, disapproval flow, in-review states | "Proposal routing to wrong reviewer", "approval step skipped", "color group assignment" |
| **ARTICULATIONS** | Articulation agreements, AR forms, AR courses, AR programs, cross-listings | AR report changes, articulation program status, teach-out tracking |
| **SEARCH** | Public search dashboard, admin search, proposal landing page, output field configuration, sort options | "Add field to search output", "sort options not working", "dashboard layout" |
| **SYSTEM** | Platform-wide issues: outages, 500 errors, login failures, sandbox refresh requests, session expiration, webservices, API | Outages, API 500s, sandbox refresh, login errors, site down |
| **ADMIN** | User access, roles, permissions, lookup manager, admin reports configuration | "Add user X", "Change role for Y", "Lookup data update" |
| **SYLLABUS** | Simple Syllabus integration only. MLO/CLO sync issues, field mapping | MLOs not appearing, CLO mismatches, syllabus data wrong |
| **CIP** | CIP table updates (Federal, state-specific), TOP codes, CIP crosswalks | "Add FL CIP code 1101510014", "new TOP/CIP crosswalk entry" |
| **UNITS** | Unit/hour field calculations, CB22, contact hours, credit status, noncredit hours | "CB22 not filtering by credit status", "noncredit total hours = 0" |

## When in doubt

- If a report is the broken thing → **REPORTS** (even if it's a course-level report)
- If the issue is on a program form but about the workflow it goes through → **WORKFLOW**
- If the customer can't log in at all → **SYSTEM**
- If it's a user's access that's wrong → **ADMIN**
- If you honestly can't pick, write `[module]` in the subject, mark in the ticket body that module assignment is unclear, and let Acadea triage pick. Do not force a guess.

## Mapping to Acadea's internal SOP fields

(You don't need to emit these, but knowing the mapping helps you disambiguate.)

Acadea's internal triage maps your module to a Jira "Module" + "Category" pair. Rough mapping:

| Your module | Likely Jira Module | Likely Jira Category |
|---|---|---|
| REPORTS | — | Reports |
| PROGRAMS | Programs | Proposals |
| COURSES | Courses | Proposals |
| CATALOG | Catalog | — |
| WORKFLOW | — | Workflows |
| ARTICULATIONS | Programs / Courses | Cross Listings |
| SEARCH | — | Search |
| SYSTEM | (platform-wide) | — |
| ADMIN | — | Admin/Users |
| SYLLABUS | Syllabus | — |
| CIP | — | Lookup Manager |
| UNITS | Courses | — |

This is context only. Do not put these fields in the ticket body — they are for the Acadea triage person to set.
