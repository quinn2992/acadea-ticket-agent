"""Classify support clarifying questions into canonical categories.

From 05 we learned what types of things support asks. This script
pattern-matches the first-support-reply text of each ticket against
a small set of canonical question-types so we can report:
"When a Courses ticket arrives, 33% of the time support has to ask
for a screenshot, 28% for steps-to-reproduce, ...".

Categories emerge from inspecting 05's samples:
  scope_confirmation: "just to confirm, you want X?"
  screenshot_with_url: "can you share a screenshot with the URL?"
  steps_to_reproduce: "what are your reproduction steps?"
  which_user: "which user is seeing this?"
  which_record: "which program/course/report exactly?"
  which_browser: "does this happen in other browsers?"
  still_happening: "are you still seeing this issue?"
  abbreviation: "what does ABC stand for?"
  which_field_column: "which column/field do you want this in?"
  scope_boundary: "do you want this for X only or also Y?"
"""
from __future__ import annotations
import json, re
from collections import Counter, defaultdict
from _common import load_all, customer_ids_for, first_support_reply, strip_html, OUT

CATEGORIES = [
    ("scope_confirmation",
     r"just to confirm|to confirm you want|confirm what (all )?is being requested|"
     r"confirm( for me)? (whether|if|that|the)|is this correct|did i (miss|understand)|"
     r"so you('re| are) (saying|asking|requesting)|is what you'?re asking"),
    ("screenshot_with_url",
     r"screenshot that (shows|includes)?\s*(the )?url|"
     r"screenshot.*url|url.*screenshot|include (the|a) url|"
     r"(a )?screen shot with the url|include url in your screenshot"),
    ("screenshot_generic",
     r"(can|could|please) (you )?(send|share|provide|attach) a screenshot|"
     r"screenshot (of|showing)|screen shot of|please provide.*image"),
    ("steps_to_reproduce",
     r"(duplication|reproduction|recreation) steps|"
     r"steps to (reproduce|recreate|replicate|duplicate|see)|"
     r"walk (me|us) through how you|how (are you|were you|did you) (getting|seeing|producing) this|"
     r"how to (reproduce|recreate|replicate)"),
    ("which_user",
     r"which user|what user|who (is|was) (logged|seeing|trying)|"
     r"user (id|account|role|permission|login) (that|is|was)"),
    ("which_record",
     r"(which|what) (exact|specific)? ?(course|program|proposal|report|record|item|catalog|syllabus|workflow|field)"),
    ("which_browser",
     r"(which|what) browser|different browsers|cross.?browser|chrome.*firefox|edge|safari|"
     r"does (this|it) happen (on|in) (other|different)"),
    ("still_happening",
     r"are you still (seeing|getting|experiencing|having)|is (this|it) still (happening|occurring|an issue)|"
     r"still seeing (this|the) (error|issue|problem)"),
    ("abbreviation",
     r"what does .{2,20} stand for|what is (meant by|the meaning of)|"
     r"acronym|abbreviation"),
    ("which_field_column",
     r"(which|what) (column|field|row|page|tab|section|location) (do|should|would)|"
     r"where (do|should|would) you (want|like) (this|it|the)"),
    ("scope_boundary",
     r"only (or|vs).{1,80}(all|every|other)|"
     r"(just|only).{1,40} (form|report|module|catalog|program type|user group)|"
     r"(for|on) (all|just|only|every) (courses|programs|proposals|reports|users|forms)"),
    ("environment",
     r"(production|sandbox|UAT|live|test) (site|environment)|"
     r"which (site|environment|tenant|instance)"),
    ("expected_vs_actual",
     r"what (do|did) you expect|expected (behavior|result|output)|"
     r"what should (this|it) (do|show|look)"),
    ("when_started",
     r"when did (this|it) (start|begin|first)|how long (has|have) (this|you)|"
     r"last (time|week|month) (this|it) worked"),
    ("urgency_due_date",
     r"(when|by what date) (do|would) you need|"
     r"target (date|launch)|hard (date|deadline|launch)|due date|by when"),
    ("impact_scope",
     r"(is this|are these) (affecting|impacting)|"
     r"how many (users|courses|programs|records)|"
     r"how (widespread|broadly)|"
     r"(all|some|specific|one) (user|users|courses|programs)"),
]
COMPILED = [(name, re.compile(pat, re.IGNORECASE)) for name, pat in CATEGORIES]

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

def categorize_reply(body: str) -> set[str]:
    hits = set()
    for name, pat in COMPILED:
        if pat.search(body):
            hits.add(name)
    return hits

def main():
    all_data = load_all()
    # per-topic: count of tickets where each category was triggered
    per_topic = defaultdict(lambda: Counter())
    per_topic_total = Counter()
    overall = Counter()
    overall_total = 0
    any_category_hit = Counter()

    # also keep a few verbatim examples per category
    examples = defaultdict(list)

    for name, tickets in all_data.items():
        cust_ids = customer_ids_for(name, tickets)
        for t in tickets:
            subj = t.get("subject") or ""
            desc = t.get("description") or ""
            topic = detect_topic(subj + "\n" + desc)
            per_topic_total[topic] += 1
            overall_total += 1

            reply = first_support_reply(t, cust_ids)
            if not reply:
                continue
            body = strip_html(reply.get("body") or "")
            body = re.sub(r"!\[\]\([^)]+\)", " ", body)   # strip image markdown
            body = re.sub(r"\s+", " ", body).strip()
            cats = categorize_reply(body)
            if cats:
                any_category_hit[topic] += 1
            for c in cats:
                per_topic[topic][c] += 1
                overall[c] += 1
                if len(examples[c]) < 10:
                    examples[c].append({
                        "ticket_id": t.get("id"),
                        "dataset": name,
                        "topic": topic,
                        "subject": subj[:160],
                        "snippet": body[:300],
                    })

    # normalize percentages
    pct_overall = {c: {"count": n, "pct_of_all_tickets": round(100*n/max(1, overall_total), 1)}
                   for c, n in overall.most_common()}
    per_topic_pct = {}
    for topic, ctr in per_topic.items():
        denom = per_topic_total[topic]
        per_topic_pct[topic] = {
            "tickets_in_topic": denom,
            "any_category_hit_pct": round(100*any_category_hit[topic]/max(1, denom), 1),
            "categories": {c: {"count": n, "pct_of_topic": round(100*n/max(1, denom), 1)}
                           for c, n in ctr.most_common()},
        }

    report = {
        "overall_category_counts": pct_overall,
        "per_topic": per_topic_pct,
        "examples": examples,
    }
    (OUT / "05b_question_categories.json").write_text(json.dumps(report, indent=2))

    print("== Overall: how often does support's first reply invoke each question-category? ==")
    print(f"   (denominator = {overall_total} tickets)")
    for c, d in sorted(pct_overall.items(), key=lambda x: -x[1]["count"]):
        print(f"  {d['pct_of_all_tickets']:5.1f}%  {c:24s}  (n={d['count']})")

    print("\n== Per topic: category hit rates ==")
    for topic, d in sorted(per_topic_pct.items(), key=lambda x: -x[1]["tickets_in_topic"]):
        print(f"\n  [{topic}] ({d['tickets_in_topic']} tickets, any_hit={d['any_category_hit_pct']}%)")
        for c, sub in d["categories"].items():
            print(f"    {sub['pct_of_topic']:5.1f}%  {c:24s}  (n={sub['count']})")

if __name__ == "__main__":
    main()
