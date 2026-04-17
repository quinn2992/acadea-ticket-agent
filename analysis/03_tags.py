"""Tag frequency and co-occurrence across the 848 tickets.

Zendesk tags are how tickets are actually categorized after triage. The
SOP's Module / Category fields are Jira-side; tags live on the Zendesk
ticket. We count tag frequency globally and per dataset, and attempt to
map the top tags onto the SOP label list.

Outputs: analysis/output/03_tags.json and console summary.
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from _common import load_all, OUT

# The SOP "Source-Based Labels" list. Lowercased for matching.
SOP_LABELS = {l.lower(): l for l in [
    "ADACompliance","Administrator","Permissions","API","WebServices","AutoUpdate",
    "CIP","ConfigKickback","ConfigKickbackDST","Configuration","ConfigFeatureRequest",
    "CSS","DataImport","Enhancement","Feature_Request","Implementation","Notifications",
    "OL","Paid_Project","ProcessImprovement","Production","Reporting","SystemPerformance",
    "Test","tshirtestimateneeded","Units_Hours","V2DataExtract",
]}

# Common Zendesk tag slugs we'd expect to align with SOP modules/labels.
SOP_MODULES = {
    "courses","programs","catalog","syllabus","proposals","policy","assessment",
    "search","reports","reporting","workflows","workflow","admin","permissions",
    "sso","api","courseblocks","programmapper","programreview",
}

def main():
    all_data = load_all()
    global_tags = Counter()
    per_dataset = defaultdict(Counter)
    co_occurrence = Counter()

    for name, tickets in all_data.items():
        for t in tickets:
            tags = t.get("tags") or []
            tags = sorted(set(tags))
            for tag in tags:
                global_tags[tag] += 1
                per_dataset[name][tag] += 1
            for i in range(len(tags)):
                for j in range(i+1, len(tags)):
                    co_occurrence[(tags[i], tags[j])] += 1

    # which SOP labels / modules do actual tags match?
    sop_hits = Counter()
    module_hits = Counter()
    for tag, count in global_tags.items():
        t = tag.lower().replace(" ", "").replace("_", "")
        for label_lower, label_display in SOP_LABELS.items():
            if label_lower.replace("_","") in t:
                sop_hits[label_display] += count
                break
        for m in SOP_MODULES:
            if m in t:
                module_hits[m] += count
                break

    report = {
        "global_top60_tags": global_tags.most_common(60),
        "per_dataset_top20": {k: v.most_common(20) for k, v in per_dataset.items()},
        "top50_co_occurrences": [[f"{a}+{b}", c] for (a,b), c in co_occurrence.most_common(50)],
        "sop_label_hits": sop_hits.most_common(),
        "module_hits_via_tags": module_hits.most_common(),
        "total_unique_tags": len(global_tags),
    }
    (OUT / "03_tags.json").write_text(json.dumps(report, indent=2))

    print(f"== Total unique tags across all datasets: {len(global_tags)} ==")
    print("\n== Top 40 tags ==")
    for tag, c in global_tags.most_common(40):
        print(f"  {c:4d}  {tag}")
    print("\n== Top 20 co-occurrences ==")
    for (a, b), c in co_occurrence.most_common(20):
        print(f"  {c:3d}  {a} + {b}")
    print("\n== SOP label matches ==")
    for l, c in sop_hits.most_common():
        print(f"  {c:4d}  {l}")
    print("\n== Module hits via tags ==")
    for m, c in module_hits.most_common():
        print(f"  {c:4d}  {m}")

if __name__ == "__main__":
    main()
