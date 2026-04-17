"""Subject-line prefix frequency.

SPC tickets famously lead with a category prefix like "SPC REPORTS - ..."
or "SYSTEM - ...". This script extracts whatever comes before the first
" - " separator and counts it. Gives us the empirical taxonomy that the
knowledge pack will map onto the SOP's Module / Category fields.

Outputs: analysis/output/02_prefixes.json + console summary.
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from _common import DATASETS, load_all, parse_subject_prefix, OUT

def main():
    all_data = load_all()
    global_prefix = Counter()
    per_dataset_prefix = defaultdict(Counter)
    unprefixed = defaultdict(list)
    for name, tickets in all_data.items():
        for t in tickets:
            subj = t.get("subject") or ""
            prefix, _rest = parse_subject_prefix(subj)
            if prefix:
                global_prefix[prefix] += 1
                per_dataset_prefix[name][prefix] += 1
            else:
                unprefixed[name].append(subj[:120])

    # Aggregate prefixes by stripping leading customer code (SPC, LPC, VVC, etc.).
    # Heuristic: if the prefix has two tokens and the first is ≤4 uppercase letters
    # and the second is also uppercase alpha, treat the second as the "module".
    def canonicalize(prefix: str) -> str:
        parts = prefix.split()
        if len(parts) >= 2 and len(parts[0]) <= 4 and parts[0].isupper() and parts[0].isalpha():
            return " ".join(parts[1:])
        return prefix
    canonical = Counter()
    for p, c in global_prefix.items():
        canonical[canonicalize(p)] += c

    report = {
        "global_prefixes_top50": global_prefix.most_common(50),
        "canonical_prefixes_top50": canonical.most_common(50),
        "per_dataset_prefix_top20": {k: v.most_common(20) for k, v in per_dataset_prefix.items()},
        "unprefixed_counts": {k: len(v) for k, v in unprefixed.items()},
        "unprefixed_samples": {k: v[:15] for k, v in unprefixed.items()},
    }
    (OUT / "02_prefixes.json").write_text(json.dumps(report, indent=2))

    print("== Top raw prefixes across all datasets ==")
    for p, c in global_prefix.most_common(30):
        print(f"  {c:4d}  {p}")
    print("\n== Canonical prefixes (customer-code stripped) ==")
    for p, c in canonical.most_common(30):
        print(f"  {c:4d}  {p}")
    print("\n== Unprefixed subjects per dataset ==")
    for k, v in unprefixed.items():
        print(f"  {k}: {len(v)} unprefixed")
        for s in v[:5]:
            print(f"    - {s}")

if __name__ == "__main__":
    main()
