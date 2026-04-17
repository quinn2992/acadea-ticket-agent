"""Anti-pattern detection.

What current tickets — including our "gold standard" datasets — do
badly that the drafting agent should fix. Every anti-pattern must
be backed by concrete counts and a handful of verbatim examples.

Anti-patterns scanned:
  A1 urgency_in_subject: SOP says "do not insert urgency in ticket
     summary". Count tickets whose subject contains URGENT / ASAP /
     HIGH / DUE / "TODAY" etc.
  A2 vague_subject: subject <= 3 words or subject matches generic
     phrases (help, issue, question, problem, bug, stalled, error).
  A3 empty_or_tiny_desc: description < 80 chars.
  A4 forwarded_email_desc: description is a pasted email chain
     (starts with "From:" / "Sent:" / "-----Original Message-----").
  A5 solution_smuggling: description contains "can we just", "please
     just", "all you have to do", "easy fix", "simply change", "just
     make it"—i.e. customer prescribes the technical fix.
  A6 missing_screenshot_for_ui_issue: description mentions "error",
     "not working", "broken", "wrong", "weird", "looks" but has
     no image, URL, or "screenshot" mention.
  A7 no_business_use_case: description does not contain "because",
     "in order to", "use case", "impact", "blocking", "students
     need", "we need to", "so that", or any reason/purpose verb.
  A8 csm_authored_first_comment: first comment's author is not the
     ticket's requester_id (CSM-relay tickets).

Outputs: analysis/output/07_anti_patterns.json
"""
from __future__ import annotations
import json, re
from collections import Counter, defaultdict
from _common import load_all, customer_ids_for, strip_html, OUT

RE_URGENCY = re.compile(r"(?i)\b(urgent|asap|critical|emergency|top priority|high priority|rush|today|tomorrow|by eod|due\s+\d)\b")
RE_VAGUE_PHRASES = re.compile(r"(?i)^(help|issue|question|problem|bug|error|stalled platform|broken|it'?s broken|not working|re: .{0,40})$")
RE_FORWARDED = re.compile(r"(?im)^\s*(from:|sent:|to:|subject:\s|-{3,}\s*(original|forwarded) message|on .+ wrote:\s*$)")
RE_SOLUTION_SMUGGLE = re.compile(
    r"(?i)(can (we|you) just|please just|all you have to do|easy fix|simply (change|add|remove)|"
    r"just (make|change|add|remove|add)|quick fix|it('?s| is) (a )?simple|"
    r"just need to (add|remove|change|fix)|should be (a )?(simple|quick|easy))"
)
RE_USE_CASE = re.compile(
    r"(?i)(because|in order to|use case|impact|blocking|students? need|faculty need|we need to|"
    r"so that|so we can|so they can|to (meet|comply|fulfil|support)|compliance|"
    r"cannot (submit|approve|launch|publish|send)|unable to|can'?t (submit|approve|launch|publish))"
)
RE_UI_TROUBLE_WORDS = re.compile(r"(?i)(error|not working|broken|wrong|weird|strange|odd|missing|blank|disappear|displays?|showing|won'?t\s+(load|save|submit))")
RE_SCREENSHOT_OR_IMG = re.compile(r"(?i)(screenshot|screen shot|see image|attached image|!\[.*?\]\(http)")
RE_URL = re.compile(r"https?://\S+")

def main():
    all_data = load_all()
    counts = Counter()
    samples = defaultdict(list)
    per_dataset = defaultdict(Counter)
    per_dataset_n = Counter()

    for name, tickets in all_data.items():
        cust_ids = customer_ids_for(name, tickets)
        for t in tickets:
            per_dataset_n[name] += 1
            subj = (t.get("subject") or "").strip()
            desc = strip_html(t.get("description") or "")
            first_author = (t.get("comments") or [{}])[0].get("author_id")

            if RE_URGENCY.search(subj):
                counts["A1_urgency_in_subject"] += 1
                per_dataset[name]["A1_urgency_in_subject"] += 1
                if len(samples["A1_urgency_in_subject"]) < 20:
                    samples["A1_urgency_in_subject"].append({"id": t.get("id"), "dataset": name, "subject": subj})

            if len(subj.split()) <= 3 or RE_VAGUE_PHRASES.match(subj):
                counts["A2_vague_subject"] += 1
                per_dataset[name]["A2_vague_subject"] += 1
                if len(samples["A2_vague_subject"]) < 20:
                    samples["A2_vague_subject"].append({"id": t.get("id"), "dataset": name, "subject": subj})

            if len(desc) < 80:
                counts["A3_empty_or_tiny_desc"] += 1
                per_dataset[name]["A3_empty_or_tiny_desc"] += 1
                if len(samples["A3_empty_or_tiny_desc"]) < 20:
                    samples["A3_empty_or_tiny_desc"].append({
                        "id": t.get("id"), "dataset": name,
                        "subject": subj, "desc_len": len(desc), "desc": desc[:200]})

            if RE_FORWARDED.search(desc):
                counts["A4_forwarded_email_desc"] += 1
                per_dataset[name]["A4_forwarded_email_desc"] += 1
                if len(samples["A4_forwarded_email_desc"]) < 15:
                    samples["A4_forwarded_email_desc"].append({
                        "id": t.get("id"), "dataset": name,
                        "subject": subj, "desc": desc[:350]})

            if RE_SOLUTION_SMUGGLE.search(desc):
                counts["A5_solution_smuggling"] += 1
                per_dataset[name]["A5_solution_smuggling"] += 1
                if len(samples["A5_solution_smuggling"]) < 20:
                    m = RE_SOLUTION_SMUGGLE.search(desc)
                    start = max(0, m.start() - 80)
                    end = min(len(desc), m.end() + 120)
                    samples["A5_solution_smuggling"].append({
                        "id": t.get("id"), "dataset": name,
                        "subject": subj, "snippet": desc[start:end]})

            if RE_UI_TROUBLE_WORDS.search(desc) and not RE_SCREENSHOT_OR_IMG.search(desc) and not RE_URL.search(desc):
                counts["A6_ui_trouble_without_evidence"] += 1
                per_dataset[name]["A6_ui_trouble_without_evidence"] += 1
                if len(samples["A6_ui_trouble_without_evidence"]) < 15:
                    samples["A6_ui_trouble_without_evidence"].append({
                        "id": t.get("id"), "dataset": name,
                        "subject": subj, "desc": desc[:400]})

            if not RE_USE_CASE.search(desc) and len(desc) >= 80:
                counts["A7_no_business_use_case"] += 1
                per_dataset[name]["A7_no_business_use_case"] += 1
                if len(samples["A7_no_business_use_case"]) < 20:
                    samples["A7_no_business_use_case"].append({
                        "id": t.get("id"), "dataset": name,
                        "subject": subj, "desc": desc[:400]})

            if first_author is not None and first_author not in cust_ids:
                counts["A8_csm_authored_first_comment"] += 1
                per_dataset[name]["A8_csm_authored_first_comment"] += 1

    pct = {
        a: {
            "total_count": c,
            "pct_of_all_tickets": round(100 * c / max(1, sum(per_dataset_n.values())), 1),
            "per_dataset_pct": {
                ds: round(100 * per_dataset[ds][a] / max(1, per_dataset_n[ds]), 1)
                for ds in per_dataset_n
            },
        } for a, c in counts.most_common()
    }

    report = {
        "dataset_sizes": dict(per_dataset_n),
        "anti_pattern_counts": pct,
        "samples": samples,
    }
    (OUT / "07_anti_patterns.json").write_text(json.dumps(report, indent=2))

    print("== Anti-pattern rates ==")
    print(f"Dataset sizes: {dict(per_dataset_n)}\n")
    for a, d in pct.items():
        per = "  ".join(f"{ds}={p}%" for ds, p in d["per_dataset_pct"].items())
        print(f"  {a:36s}  {d['pct_of_all_tickets']:5.1f}% overall  (n={d['total_count']})   [{per}]")

if __name__ == "__main__":
    main()
