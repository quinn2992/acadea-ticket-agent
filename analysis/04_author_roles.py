"""Who actually writes the first comment (description) of each ticket?

Critical question from the Apr 16 meeting: Kali said CSM-entered tickets
peaked at 80% pre-July 2024 and are now around 20%. Separately, she said
pass-through CSMs (copy/paste of customer email) produce worse tickets
than a customer writing directly. This script asks: within our three
"gold standard" datasets, how many ticket descriptions are actually
authored by the named customer, vs by someone else (typically an Acadea
CSM/support agent relaying on the customer's behalf)?

Signal: compare the ticket's requester_id to the author_id of the
FIRST comment. If they match → customer-authored. Otherwise → non-customer.

Outputs: analysis/output/04_author_roles.json
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from _common import DATASETS, load_all, customer_ids_for, OUT

def main():
    all_data = load_all()
    per_dataset = {}
    for name, tickets in all_data.items():
        cust_ids = customer_ids_for(name, tickets)
        customer_authored = 0
        non_customer_authored = 0
        no_comments = 0
        other_authors = Counter()
        for t in tickets:
            comments = t.get("comments") or []
            if not comments:
                no_comments += 1
                continue
            first_author = comments[0].get("author_id")
            if first_author in cust_ids:
                customer_authored += 1
            else:
                non_customer_authored += 1
                other_authors[first_author] += 1
        per_dataset[name] = {
            "n_tickets": len(tickets),
            "customer_authored_first_comment": customer_authored,
            "non_customer_authored_first_comment": non_customer_authored,
            "no_comments": no_comments,
            "percent_customer_authored": round(100 * customer_authored / max(1, len(tickets)), 1),
            "top_non_customer_authors": other_authors.most_common(10),
        }
    (OUT / "04_author_roles.json").write_text(json.dumps(per_dataset, indent=2))
    for name, r in per_dataset.items():
        print(f"\n== {name} ==")
        for k, v in r.items():
            print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
