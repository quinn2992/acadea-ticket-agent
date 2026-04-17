"""Deeper look at subject patterns, not just all-caps prefixes.

The first pass showed most subjects don't match a strict ALL CAPS prefix
regex. Here we look at three subject shapes:
  A) all-caps prefix ("SPC REPORTS - ...")
  B) mixed-case "customer - module - ..." ("Las Positas - Catalog - ...")
  C) no clear prefix (free-form title)

Also pulls sample subjects from each category so we can see what
customers actually write.
"""
from __future__ import annotations
import json, re
from collections import Counter, defaultdict
from _common import load_all, OUT

ALL_CAPS_PREFIX = re.compile(r"^\s*([A-Z][A-Z0-9 &/]{1,50}?)\s*[-:–]\s+(.*)$")
MIXED_CASE_PREFIX = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 &/]{1,50}?)\s*[-–]\s+(.*)$")

def classify(subj: str):
    if not subj:
        return "empty", None
    m = ALL_CAPS_PREFIX.match(subj)
    if m:
        return "all_caps", m.group(1).strip()
    m2 = MIXED_CASE_PREFIX.match(subj)
    if m2:
        tok = m2.group(1).strip()
        # skip cases that are just a long fragment (e.g. plain sentence)
        if len(tok.split()) <= 6:
            return "mixed_case", tok
    return "none", None

def main():
    all_data = load_all()
    shape_counts = defaultdict(Counter)   # dataset -> shape -> count
    all_caps_tokens = Counter()
    mixed_tokens = Counter()
    samples_none = defaultdict(list)

    # Also count how many subjects contain any of a set of module keywords
    MODULES = ["REPORTS", "SYSTEM", "PROGRAMS", "COURSES", "SYLLABUS",
               "CATALOG", "PROPOSAL", "WORKFLOW", "SEARCH", "ARTICULATION",
               "ADMIN", "PROGRAM MAPPER", "ASSESSMENT", "POLICY", "SSO", "API"]
    module_hits = Counter()

    for name, tickets in all_data.items():
        for t in tickets:
            subj = t.get("subject") or ""
            shape, tok = classify(subj)
            shape_counts[name][shape] += 1
            if shape == "all_caps":
                all_caps_tokens[tok] += 1
            elif shape == "mixed_case":
                mixed_tokens[tok] += 1
            else:
                samples_none[name].append(subj[:140])

            upper = subj.upper()
            for m in MODULES:
                if m in upper:
                    module_hits[m] += 1

    def strip_cust_code(tok):
        parts = tok.split()
        if parts and parts[0].upper() in {"SPC","LPC","VVC","LPL","CRV","CCD"} and len(parts) > 1:
            return " ".join(parts[1:])
        return tok

    canonical_all_caps = Counter()
    for tok, c in all_caps_tokens.items():
        canonical_all_caps[strip_cust_code(tok)] += c

    report = {
        "shape_by_dataset": {k: dict(v) for k, v in shape_counts.items()},
        "all_caps_top30": all_caps_tokens.most_common(30),
        "canonical_all_caps_top30": canonical_all_caps.most_common(30),
        "mixed_case_top30": mixed_tokens.most_common(30),
        "module_keyword_hits": module_hits.most_common(),
        "no_prefix_samples": {k: v[:20] for k, v in samples_none.items()},
    }
    (OUT / "02b_subject_patterns.json").write_text(json.dumps(report, indent=2))

    print("== Shape distribution by dataset ==")
    for k, v in shape_counts.items():
        print(f"  {k}: {dict(v)}")
    print("\n== Module keyword hits (keyword appears anywhere in subject) ==")
    for m, c in module_hits.most_common():
        print(f"  {c:4d}  {m}")
    print("\n== Canonical ALL CAPS prefixes (customer code stripped) top 20 ==")
    for p, c in canonical_all_caps.most_common(20):
        print(f"  {c:4d}  {p}")
    print("\n== Mixed case prefixes (e.g. 'Las Positas - ...') top 20 ==")
    for p, c in mixed_tokens.most_common(20):
        print(f"  {c:4d}  {p}")

if __name__ == "__main__":
    main()
