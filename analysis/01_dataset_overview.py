"""Dataset shape and basic stats.

What this tells us: how big each dataset is, how long the average thread is,
status and priority distributions, and how much of the conversation is
support-side vs customer-side. Establishes baseline shape before we dig
into content.

Outputs: analysis/output/01_overview.json and console summary.
"""
from __future__ import annotations
import json
from collections import Counter
from statistics import mean, median
from _common import DATASETS, load_all, OUT, customer_ids_for, strip_html

def summarize():
    all_data = load_all()
    report = {}
    for name, tickets in all_data.items():
        cust_ids = customer_ids_for(name, tickets)
        n = len(tickets)
        statuses = Counter(t.get("status") for t in tickets)
        priorities = Counter(t.get("priority") for t in tickets)
        comment_counts = [len(t.get("comments") or []) for t in tickets]
        desc_lens = [len(strip_html(t.get("description") or "")) for t in tickets]
        empty_desc = sum(1 for L in desc_lens if L < 10)

        # who talks: customer vs support
        cust_comments = 0
        sup_comments = 0
        for t in tickets:
            for c in t.get("comments") or []:
                if c.get("author_id") in cust_ids:
                    cust_comments += 1
                else:
                    sup_comments += 1

        report[name] = {
            "n_tickets": n,
            "statuses": dict(statuses),
            "priorities": dict(priorities),
            "total_comments": sum(comment_counts),
            "avg_comments_per_ticket": round(mean(comment_counts), 2) if n else 0,
            "median_comments_per_ticket": median(comment_counts) if n else 0,
            "max_comments": max(comment_counts) if n else 0,
            "avg_description_chars": round(mean(desc_lens), 1) if n else 0,
            "median_description_chars": median(desc_lens) if n else 0,
            "empty_or_near_empty_descriptions": empty_desc,
            "customer_comments": cust_comments,
            "support_comments": sup_comments,
            "customer_comment_ratio": round(cust_comments / max(1, cust_comments + sup_comments), 3),
        }
    return report

def main():
    rep = summarize()
    (OUT / "01_overview.json").write_text(json.dumps(rep, indent=2))
    for name, r in rep.items():
        label = next(d["label"] for d in DATASETS if d["name"] == name)
        print(f"\n== {name} :: {label} ==")
        for k, v in r.items():
            print(f"  {k}: {v}")
    totals = {
        "total_tickets": sum(r["n_tickets"] for r in rep.values()),
        "total_comments": sum(r["total_comments"] for r in rep.values()),
    }
    print("\n== totals ==")
    for k, v in totals.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
