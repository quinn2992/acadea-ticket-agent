"""Shared loaders and helpers for ticket analysis.

All scripts in analysis/ import from here. Keeps path handling and
per-dataset metadata in one place so individual scripts stay focused.
"""
from __future__ import annotations
import json, re
from pathlib import Path
from collections import Counter
from typing import Iterable

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "source_materials"
OUT = REPO / "analysis" / "output"
OUT.mkdir(parents=True, exist_ok=True)

DATASETS = [
    {"name": "spc",        "file": "spc_zendesk_tickets_606.json",         "label": "St. Petersburg College"},
    {"name": "craig",      "file": "las_positas_craig_kutil_tickets_199.json", "label": "Craig Kutil (Las Positas)"},
    {"name": "armando",    "file": "victor_valley_armando_barajas_tickets_43.json", "label": "Armando Barajas (Victor Valley)"},
]

# Author IDs for the three "gold standard" customers we're mining. When an
# author_id in comments matches one of these, the comment is customer-side
# (requester). Everything else is support-side — used to separate the
# "customer voice" from the "support clarifying question" voice.
CUSTOMER_IDS = {
    # Craig Kutil
    403743042952,
    # Armando Barajas
    30061744875419,
}

# SPC requesters from context_for_ticket_agent_build.md — populated
# dynamically below by sniffing the SPC file (any requester_id seen as
# ticket.requester_id in SPC file is considered a customer).

def load_dataset(name: str) -> list[dict]:
    entry = next(d for d in DATASETS if d["name"] == name)
    with (SRC / entry["file"]).open() as f:
        return json.load(f)

def load_all() -> dict[str, list[dict]]:
    return {d["name"]: load_dataset(d["name"]) for d in DATASETS}

def all_tickets() -> Iterable[tuple[str, dict]]:
    for d in DATASETS:
        for t in load_dataset(d["name"]):
            yield d["name"], t

def customer_ids_for(dataset: str, tickets: list[dict]) -> set[int]:
    """Return the set of author_ids that represent the customer side for
    this dataset. For SPC we pull all requester_ids from tickets. For
    Craig/Armando it's the hard-coded single requester."""
    if dataset == "spc":
        return {t.get("requester_id") for t in tickets if t.get("requester_id")}
    if dataset == "craig":
        return {403743042952}
    if dataset == "armando":
        return {30061744875419}
    return set()

# Subject prefix pattern: TOKEN(S) followed by " - " or ": ". e.g. "SPC REPORTS - X", "SYSTEM - X", "PROGRAMS: X"
PREFIX_RE = re.compile(r"^\s*([A-Z][A-Z0-9 &/]{1,40}?)\s*[-:–]\s+(.*)$")

def parse_subject_prefix(subject: str) -> tuple[str | None, str]:
    if not subject:
        return None, ""
    m = PREFIX_RE.match(subject)
    if not m:
        return None, subject.strip()
    prefix = m.group(1).strip()
    rest = m.group(2).strip()
    return prefix, rest

def strip_html(s: str) -> str:
    if not s:
        return ""
    # zendesk descriptions are typically plain text already, but be safe.
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&nbsp;", " ", s)
    s = re.sub(r"&amp;", "&", s)
    s = re.sub(r"&lt;", "<", s)
    s = re.sub(r"&gt;", ">", s)
    s = re.sub(r"\s+\n", "\n", s)
    return s.strip()

def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()

def iter_customer_comments(ticket: dict, customer_ids: set[int]):
    for c in ticket.get("comments") or []:
        if c.get("author_id") in customer_ids:
            yield c

def iter_support_comments(ticket: dict, customer_ids: set[int]):
    for c in ticket.get("comments") or []:
        aid = c.get("author_id")
        if aid not in customer_ids:
            yield c

def first_support_reply(ticket: dict, customer_ids: set[int]) -> dict | None:
    for c in ticket.get("comments") or []:
        if c.get("author_id") not in customer_ids and c.get("public", True):
            return c
    return None
