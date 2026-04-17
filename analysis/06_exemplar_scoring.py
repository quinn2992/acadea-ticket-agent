"""Score ticket descriptions and surface candidate exemplars.

We want ~10-15 "exemplar" tickets that illustrate different strengths.
Score each ticket description on a simple rubric and then pick the
best per module/topic, favoring diversity.

Rubric (each point adds 1 to score):
  + description >= 200 chars and <= 3000 chars (neither empty nor a wall)
  + has a section header ("Business Use Case", "Expected", "Steps",
    "Description", "Issue", "Navigation", "Impact")
  + references a screenshot or image URL
  + references a specific record id, course code, report #, or proposal id
  + includes a URL (points to where the problem lives)
  + has a "when/who" signal (date, specific user, role)
  + description is not a forwarded email from another sender
  + first support reply is NOT a clarifying question (this means the
    description was sufficient — strongest signal)

Diversity: we want to cover Reports, Programs, Courses, Catalog,
Syllabus, Workflow, Admin, Search, Articulations, System where possible.

Output: analysis/output/06_exemplar_candidates.json — top 15 per topic
with scores, plus a curated shortlist.
"""
from __future__ import annotations
import json, re
from collections import defaultdict
from _common import load_all, customer_ids_for, first_support_reply, strip_html, OUT

SECTION_HEADERS = re.compile(
    r"(?i)\b(business use case|expected (result|behavior|output)|actual (result|behavior|output)|"
    r"steps to (reproduce|replicate|recreate)|impact|navigation|issue\s*:|description\s*:|"
    r"problem\s*:|who is impacted|purpose of the request|target (date|launch))\b"
)
SCREENSHOT = re.compile(r"(?i)(screenshot|screen shot|attached image|see image|see attached|attached.{0,20}pic|!\[\]\(http)")
URL = re.compile(r"https?://\S+")
RECORD_ID = re.compile(
    r"(?i)(#\s*\d{2,}|\b(course|program|proposal|report|rpt|cert|pos|ticket) ?#?\s*\w{2,}\b|"
    r"[A-Z]{2,4}\s?\d{3,4}[A-Za-z]?\b)"
)
DATE = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}|\d{1,2}/\d{1,2}/\d{2,4}\b|20\d{2}-\d{2}-\d{2}")
FORWARDED = re.compile(r"(?i)(^from:\s|-{3,}\s*forwarded message|original message|^sent:\s|^to:\s)")
CLARIFYING_Q = re.compile(
    r"(?i)(just to confirm|can you (send|share|provide)|please provide|which (user|browser|course|program|report)|"
    r"are you still (seeing|getting)|what (user|browser|column|field|exactly)|"
    r"steps to (reproduce|recreate|duplicate|replicate)|"
    r"(include|share|send) (a )?screenshot)"
)

TOPIC_KEYWORDS = {
    "Reports": ["report","reporting","rpt"],
    "Programs": ["program","proposal"],
    "Courses": ["course"],
    "Catalog": ["catalog"],
    "Syllabus": ["syllabus"],
    "Workflow": ["workflow","approval"],
    "Search": ["search","dashboard"],
    "Admin": ["admin","permission","user access","login"],
    "Articulations": ["articulation"],
    "System": ["system","error 500","internal server","down","outage","timeout","slow"],
}

def detect_topic(text: str) -> str:
    t = text.lower()
    for topic, kws in TOPIC_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                return topic
    return "Other"

def score_ticket(t: dict, customer_ids: set) -> tuple[int, dict]:
    desc_raw = strip_html(t.get("description") or "")
    subj = t.get("subject") or ""
    length = len(desc_raw)
    score = 0
    signals = {}
    if 200 <= length <= 3000:
        score += 1; signals["reasonable_length"] = True
    if SECTION_HEADERS.search(desc_raw):
        score += 2; signals["has_section_header"] = True
    if SCREENSHOT.search(desc_raw):
        score += 1; signals["mentions_screenshot"] = True
    if URL.search(desc_raw):
        score += 1; signals["includes_url"] = True
    if RECORD_ID.search(desc_raw):
        score += 1; signals["specific_record_id"] = True
    if DATE.search(desc_raw):
        score += 1; signals["specific_date"] = True
    if not FORWARDED.search(desc_raw):
        score += 1; signals["not_forwarded_email"] = True

    # strongest: did support not have to ask a clarifying question?
    reply = first_support_reply(t, customer_ids)
    if reply:
        body = strip_html(reply.get("body") or "")
        if not CLARIFYING_Q.search(body):
            score += 3; signals["no_clarifying_followup"] = True
    return score, signals

def main():
    all_data = load_all()
    by_topic = defaultdict(list)   # topic -> list of (score, ticket_id, dataset, subject, signals)
    for name, tickets in all_data.items():
        cust_ids = customer_ids_for(name, tickets)
        for t in tickets:
            subj = t.get("subject") or ""
            desc = strip_html(t.get("description") or "")
            if len(desc) < 80:
                continue
            topic = detect_topic(subj + "\n" + desc)
            score, signals = score_ticket(t, cust_ids)
            by_topic[topic].append({
                "score": score,
                "ticket_id": t.get("id"),
                "dataset": name,
                "subject": subj,
                "description": desc,
                "signals": signals,
            })

    # top 5 per topic
    top_per_topic = {}
    for topic, lst in by_topic.items():
        lst.sort(key=lambda x: (-x["score"], -len(x["description"])))
        top_per_topic[topic] = lst[:5]

    (OUT / "06_exemplar_candidates.json").write_text(json.dumps(top_per_topic, indent=2))

    print("== Top exemplar candidates by topic ==")
    for topic, lst in top_per_topic.items():
        print(f"\n[{topic}]")
        for c in lst:
            print(f"  score={c['score']}  id={c['ticket_id']} [{c['dataset']}]  {c['subject'][:120]}")
            print(f"    signals: {list(c['signals'].keys())}")

if __name__ == "__main__":
    main()
