"""Mine support-side clarifying questions from comment threads.

This is the interview-flow goldmine referenced in the brief. For each
ticket, we find the first public support reply (author NOT in customer
ids) and detect whether it contains a clarifying question — a request
for information the customer could have included up front. We then
cluster those questions by the topic (module keyword) of the ticket so
we can say "when a REPORTS ticket comes in, support ends up asking X
60% of the time."

Heuristics for "this first reply is a clarifying question":
  * contains "?" AND
  * contains interrogative markers ("can you", "could you", "do you",
    "would you", "please provide", "please share", "which", "what is",
    "where", "who", "when", "how", "can we get", "can I see", "screenshot",
    "example", "steps", "url")

We then extract sentences ending with "?" (or sentences containing
"please" as a soft ask) and record verbatim. Verbatim is critical —
we need actual phrasings for the knowledge pack, not paraphrases.
"""
from __future__ import annotations
import json, re
from collections import Counter, defaultdict
from _common import load_all, customer_ids_for, first_support_reply, strip_html, OUT

INTERROGATIVE = re.compile(
    r"\b(can you|could you|would you|do you|are you|have you|did you|is there|was there|"
    r"please (provide|share|send|confirm|clarify|specify|attach|include|let me know)|"
    r"which |what |where |who |when |how |screenshot|example|url|steps to|"
    r"can I see|can we get|which (user|course|program|report)|any additional)\b",
    re.IGNORECASE
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
QUESTION_SENT = re.compile(r"[?]\s*$|please", re.IGNORECASE)

# Quick topic tagger from the ticket subject + description
TOPIC_KEYWORDS = {
    "Reports": ["report", "reporting", "rpt"],
    "Programs": ["program", "proposal"],
    "Courses": ["course"],
    "Catalog": ["catalog"],
    "Syllabus": ["syllabus", "simple syllabus"],
    "Workflow": ["workflow", "approval"],
    "Search": ["search", "dashboard"],
    "Admin": ["admin", "permission", "user access", "login"],
    "Articulations": ["articulation", "ar "],
    "CIP/Lookup": ["cip", "lookup", "top code"],
    "Units/Hours": ["units", "hours", "contact hours"],
    "System": ["system", "error 500", "internal server", "down", "outage", "timeout", "slow"],
}

def detect_topic(text: str) -> str:
    t = text.lower()
    for topic, kws in TOPIC_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                return topic
    return "Other"

def is_question_reply(body: str) -> bool:
    if not body:
        return False
    has_q = "?" in body
    has_marker = bool(INTERROGATIVE.search(body))
    return has_q or has_marker

def extract_questions(body: str) -> list[str]:
    """Extract plausible clarifying-question sentences verbatim."""
    body = strip_html(body)
    body = re.sub(r"\s+", " ", body).strip()
    # remove boilerplate signatures
    body = re.split(r"(?i)(thanks?,|best,|regards,|—|--\n|Sent from)", body)[0]
    sents = SENTENCE_SPLIT.split(body)
    out = []
    for s in sents:
        s = s.strip()
        if len(s) < 12 or len(s) > 400:
            continue
        if s.endswith("?"):
            out.append(s)
        elif INTERROGATIVE.search(s) and len(s) <= 300:
            # soft ask: "Please provide the URL where this is occurring."
            out.append(s)
    return out

def main():
    all_data = load_all()
    by_topic_questions = defaultdict(list)     # topic -> list of verbatim questions
    by_topic_ticket_count = Counter()
    by_topic_with_qreply = Counter()           # how many tickets had a clarifying first reply
    all_first_replies_text = []
    global_question_phrases = Counter()
    sample_by_topic = defaultdict(list)        # topic -> list of (ticket_id, subject, question, dataset)

    for name, tickets in all_data.items():
        cust_ids = customer_ids_for(name, tickets)
        for t in tickets:
            subj = t.get("subject") or ""
            desc = t.get("description") or ""
            topic = detect_topic(subj + "\n" + desc)
            by_topic_ticket_count[topic] += 1

            reply = first_support_reply(t, cust_ids)
            if not reply:
                continue
            body = reply.get("body") or ""
            if not is_question_reply(body):
                continue
            by_topic_with_qreply[topic] += 1
            questions = extract_questions(body)
            for q in questions:
                by_topic_questions[topic].append(q)
                # normalize for frequency count: lowercase, strip punctuation
                key = re.sub(r"[^a-z0-9 ]", "", q.lower())
                key = re.sub(r"\s+", " ", key).strip()
                # count only head of phrase (first 12 words) to allow clustering
                head = " ".join(key.split()[:12])
                global_question_phrases[head] += 1
                if len(sample_by_topic[topic]) < 30:
                    sample_by_topic[topic].append({
                        "ticket_id": t.get("id"),
                        "dataset": name,
                        "subject": subj[:160],
                        "question": q[:350],
                    })

    # most common question "heads" overall
    top_phrases = global_question_phrases.most_common(80)

    # percentage by topic
    pct = {
        topic: {
            "tickets_in_topic": by_topic_ticket_count[topic],
            "tickets_where_first_support_reply_was_a_question": by_topic_with_qreply[topic],
            "percent_clarification_needed": round(
                100 * by_topic_with_qreply[topic] / max(1, by_topic_ticket_count[topic]), 1
            ),
            "total_question_sentences_collected": len(by_topic_questions[topic]),
        } for topic in by_topic_ticket_count
    }

    report = {
        "topic_clarification_rates": pct,
        "top_question_heads_overall": top_phrases,
        "samples_by_topic": {k: v for k, v in sample_by_topic.items()},
    }
    (OUT / "05_followup_questions.json").write_text(json.dumps(report, indent=2))

    print("== Clarification-needed rate by topic ==")
    for topic, d in sorted(pct.items(), key=lambda x: -x[1]["percent_clarification_needed"]):
        print(f"  {topic:15s}  {d['percent_clarification_needed']:5.1f}%  "
              f"({d['tickets_where_first_support_reply_was_a_question']}/"
              f"{d['tickets_in_topic']})")
    print("\n== Top question heads (first 12 words, normalized) ==")
    for h, c in top_phrases[:40]:
        print(f"  {c:4d}  {h}")

if __name__ == "__main__":
    main()
