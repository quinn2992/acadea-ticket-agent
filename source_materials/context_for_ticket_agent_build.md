# Ticket Writing Agent — Project Context & Data Extraction Summary

## The Goal

Quinn (CS team at Acadea) wants to build an AI agent that helps customers create high-quality support tickets. The agent will:

1. **Interview the customer** — When a customer comes in with a problem, the agent asks structured questions to extract all the relevant information (what's broken, where it's happening, what they expected, steps to reproduce, urgency, etc.)
2. **Generate a well-formatted ticket** — Using patterns learned from the best historical tickets, the agent produces a complete, well-structured ticket write-up
3. **Hand off to the customer** — The customer reviews the generated ticket, then copy-pastes it into Zendesk to submit it themselves

The agent does NOT submit tickets directly. It's a drafting assistant.

## Why These Specific Data Sources

Acadea's support team has identified specific customers and individuals who consistently write excellent, detailed, well-structured tickets. These are the "gold standard" examples the agent should learn from:

### 1. St. Petersburg College (SPC) — The Primary Training Source
- **Organization ID:** 540877 in Zendesk
- **Why them:** Considered the best ticket-writing customer across Acadea's entire client base. Their tickets consistently include clear subject lines with category prefixes (e.g., "SPC REPORTS - ...", "SPC SYSTEM - ..."), detailed descriptions of the issue, references to attachments and screenshots, and proper categorization.
- **Data extracted:** 606 tickets with 4,060 total comments (avg 6.7 comments per ticket)
- **File:** `spc_zendesk_tickets_606.json` (3 MB)
- **Date range:** April 2013 through April 2026
- **Status breakdown:** 12 open, 1 pending, 593 closed
- **Key requesters:** Andrijana Ekberg, Angela Ashe, Shirley Boyette, Ariel Hartman, and others (12 users total)
- **Common tags:** complete, priority_5_today_s_tasks, meta, jira_escalated, curricunet, s5___request, solvedemailsent, jira_update, billable

### 2. Craig Kutil — Las Positas College
- **User ID:** 403743042952 in Zendesk
- **Organization:** Las Positas College (org ID 540861)
- **Email:** ckutil@laspositascollege.edu
- **Why him:** Another strong ticket writer identified by Quinn
- **Data extracted:** 199 tickets with full comment threads
- **File:** `las_positas_craig_kutil_tickets_199.json` (938 KB)

### 3. Armando Barajas — Victor Valley Community College District (VVC)
- **User ID:** 30061744875419 in Zendesk
- **Organization:** Victor Valley Community College District (org ID 325127)
- **Email:** armando.barajas@vvc.edu
- **Why him:** Another strong ticket writer identified by Quinn
- **Data extracted:** 43 tickets with full comment threads
- **File:** `victor_valley_armando_barajas_tickets_43.json`

### Total Training Data: 848 tickets with full conversation threads

## Data Structure

Each JSON file contains an array of ticket objects. Every ticket has this structure:

```json
{
  "id": 44819,
  "subject": "SPC REPORTS - Course Outline Report Related Programs Issue",
  "description": "Some of the Active Course Outline Reports are erroneously pulling in drafts of now historical versions of proposals...",
  "tags": ["analysis", "configuration", "jira_escalated", "meta", "reporting"],
  "priority": "normal",
  "status": "open",
  "created_at": "2026-04-16T18:10:07Z",
  "updated_at": "2026-04-16T21:15:31Z",
  "requester_id": 405470019912,
  "assignee_id": 396363028,
  "group_id": 11269120460571,
  "comments": [
    {
      "author_id": 405470019912,
      "body": "The full text of the comment...",
      "public": true,
      "created_at": "2026-04-16T18:10:07Z"
    },
    {
      "author_id": 396363028,
      "body": "Agent response text...",
      "public": true,
      "created_at": "2026-04-16T21:15:31Z"
    }
  ]
}
```

### Key fields for agent training:
- **subject** — The ticket title. SPC tickets often use a prefix pattern like "SPC REPORTS - ...", "SPC SYSTEM - ...", "SYSTEM - ...", "PROGRAMS - ...", etc.
- **description** — The initial problem statement written by the requester. This is the most important field — it's the "good ticket" the agent should learn to produce.
- **comments** — The full conversation thread. The first comment typically mirrors the description. Subsequent comments show the back-and-forth, which reveals what information was missing initially and had to be clarified later. This is valuable for teaching the agent what questions to ask upfront.
- **comments[].public** — Whether the comment was public (customer-visible) or an internal note. Internal notes may contain agent-side context.
- **tags** — How tickets are categorized. Useful for the agent to understand issue taxonomy.
- **priority** — Urgency level (normal, high, urgent, low).

## How the Data Was Extracted

The data was pulled directly from Zendesk's REST API (`/api/v2/`) using JavaScript executed in Quinn's authenticated browser session on `acadea.zendesk.com`. No API token was needed — the browser's existing session cookies provided authentication.

### Process:
1. Used `/api/v2/search.json?query=type:ticket+organization:540877` to find all SPC tickets (paginated, 100 per page, 7 pages)
2. Used `/api/v2/search.json?query=type:ticket+requester_id:XXXXX` for Craig and Armando's tickets
3. For each ticket, fetched comments via `/api/v2/tickets/{id}/comments.json`
4. Comments were fetched in background batches (5 at a time with 500ms delays) to avoid rate limiting
5. Complete datasets were downloaded as JSON files via browser blob downloads

### Access Notes:
- Quinn has agent-level access to Zendesk with limited admin privileges
- Quinn can access Admin Center but does NOT have access to Apps & Integrations or API token management
- The Zendesk instance is `acadea.zendesk.com` (Pod 27, US East Ohio region)
- Full admin access would be needed to generate API tokens for future automated extractions

## What Acadea Does (Context)

Acadea appears to be a SaaS company serving higher education institutions (colleges). Based on the ticket subjects and tags, their product involves:
- Curriculum management (courses, programs, proposals)
- Academic program workflows (proposals, approvals, teach-outs)
- Reporting (course outlines, program reports, admin reports)
- Search functionality (course/program search dashboards)
- Integration with systems like Simple Syllabus
- A system called "Maverick" (possibly their platform name)
- JIRA integration for development escalations

Their customers are curriculum offices, registrars, and academic affairs staff at community colleges and universities.

## Suggested Next Steps for Building the Agent

1. **Analyze the ticket patterns** — Parse the 848 tickets to identify common structures, categorization patterns, and what makes a "good" ticket at Acadea
2. **Build a prompt/system instruction** — Create a system prompt that instructs the agent on Acadea's product domain, ticket categorization, and the interview flow
3. **Design the interview flow** — The agent should ask about: what feature/area is affected, what the expected vs. actual behavior is, steps to reproduce, urgency, any error messages or screenshots, and which users/roles are impacted
4. **Use the training data as few-shot examples** — Select the best tickets from the dataset as examples of ideal output format
5. **Test with real scenarios** — Have customers or internal team try the agent with real issues and compare output quality to the training examples
