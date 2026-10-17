"""Field-to-product feedback tracker (Chapter 16).

FDEs see what customers need before anyone else in the company does. Each
time they hit a gap they file a *field report*: the customer, the problem, the
workaround they built, how severe it is, and how much annual recurring revenue
(ARR) is affected. Individually these are anecdotes. Grouped, they are a
product roadmap.

This module:
  1. loads field reports from JSON and CSV;
  2. normalises each report into a set of *concepts* (tags plus keywords
     mapped through a synonym table, so 'Okta SAML' and 'single sign-on' both
     become 'sso');
  3. clusters reports whose concepts overlap (Jaccard similarity);
  4. de-duplicates by customer: two reports from Woodgrove Bank count as one
     customer, and their ARR is counted once;
  5. applies the *rule of three*: the same need at three or more distinct
     customers -> recommend productising it;
  6. ranks clusters and prints a prioritised list.

Usage:
    python3 tracker.py                                  # the bundled samples
    python3 tracker.py field_reports.json more_reports.csv
"""
from __future__ import annotations

import csv
import json
import pathlib
import re
import sys
from collections import Counter
from dataclasses import dataclass, field

HERE = pathlib.Path(__file__).parent
SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
RULE_OF_THREE = 3

# Phrases are replaced before splitting into words, so multi-word terms survive.
PHRASES = {
    r"single sign[- ]?on": "sso",
    r"log ?in": "login",
    r"audit (log|trail)": "audit-log",
}
# Word -> canonical concept. The table is the product team's shared vocabulary;
# grow it as new reports arrive.
SYNONYMS = {
    "sso": "sso", "saml": "sso", "okta": "sso", "entra": "sso", "login": "sso",
    "audit-log": "audit-log", "log": "audit-log", "trail": "audit-log", "record": "audit-log",
    "export": "export", "excel": "export", "csv": "export", "spreadsheet": "export", "download": "export",
    "permission": "permissions", "acl": "permissions",
    "sharepoint": "sharepoint",
    "welsh": "language", "translation": "language", "language": "language",
    "compliance": "compliance", "regulator": "compliance",
}


@dataclass
class FieldReport:
    id: str
    customer: str
    reported_by: str
    date: str
    problem: str
    workaround: str
    severity: str
    arr_affected: float
    tags: list[str] = field(default_factory=list)


def concepts(report: FieldReport) -> set[str]:
    """Normalised concepts: explicit tags (lower-cased) plus keywords from the
    problem statement that appear in the synonym table."""
    text = report.problem.lower()
    for pattern, replacement in PHRASES.items():
        text = re.sub(pattern, replacement, text)
    words = re.findall(r"[a-z][a-z-]*", text)
    found = set()
    for w in words:
        for candidate in (w, w[:-1] if w.endswith("s") else w):     # crude plural strip
            if candidate in SYNONYMS:
                found.add(SYNONYMS[candidate])
    return {t.strip().lower() for t in report.tags if t.strip()} | found


def jaccard(a: set[str], b: set[str]) -> float:
    """Overlap of two sets: |a ∩ b| / |a ∪ b|, from 0 (disjoint) to 1 (identical)."""
    return len(a & b) / len(a | b) if a | b else 0.0


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def _report(row: dict) -> FieldReport:
    tags = row.get("tags") or []
    if isinstance(tags, str):                                  # CSV: "sso;security-review"
        tags = [t for t in re.split(r"[;,|]", tags) if t.strip()]
    severity = str(row.get("severity", "medium")).strip().lower()
    if severity not in SEVERITY_RANK:
        raise ValueError(f"{row.get('id')}: unknown severity {severity!r}")
    return FieldReport(str(row["id"]), row["customer"].strip(), row.get("reported_by", ""),
                       row.get("date", ""), row["problem"], row.get("workaround", ""),
                       severity, float(row.get("arr_affected") or 0), list(tags))


def load_reports(path: str | pathlib.Path) -> list[FieldReport]:
    path = pathlib.Path(path)
    with open(path, encoding="utf-8", newline="") as f:
        rows = json.load(f) if path.suffix == ".json" else list(csv.DictReader(f))
    return [_report(r) for r in rows]


# --------------------------------------------------------------------------
# Clustering and prioritisation
# --------------------------------------------------------------------------

@dataclass
class Cluster:
    reports: list[FieldReport]

    @property
    def label(self) -> str:
        counts = Counter(c for r in self.reports for c in concepts(r))
        return ", ".join(c for c, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:3])

    @property
    def customers(self) -> list[str]:
        return sorted({r.customer for r in self.reports})

    @property
    def arr_affected(self) -> float:
        """ARR counted once per customer (the largest figure reported for them),
        so two reports from the same customer don't double-count revenue."""
        per_customer: dict[str, float] = {}
        for r in self.reports:
            per_customer[r.customer] = max(per_customer.get(r.customer, 0.0), r.arr_affected)
        return sum(per_customer.values())

    @property
    def max_severity(self) -> str:
        return max((r.severity for r in self.reports), key=SEVERITY_RANK.__getitem__)

    @property
    def recommendation(self) -> str:
        n = len(self.customers)
        if n >= RULE_OF_THREE:
            return "PRODUCTISE"
        if n == 2:
            return "WATCH"
        return "FIELD SOLUTION"


def cluster_reports(reports: list[FieldReport], threshold: float = 0.5) -> list[Cluster]:
    """Single-link clustering: two reports join the same cluster if their
    concept sets have Jaccard similarity >= threshold, directly or through a
    chain of similar reports. Implemented with union-find."""
    parent = list(range(len(reports)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]                         # path halving
            i = parent[i]
        return i

    sets = [concepts(r) for r in reports]
    for i in range(len(reports)):
        for j in range(i + 1, len(reports)):
            if jaccard(sets[i], sets[j]) >= threshold:
                parent[find(i)] = find(j)

    groups: dict[int, list[FieldReport]] = {}
    for i, r in enumerate(reports):
        groups.setdefault(find(i), []).append(r)
    return [Cluster(sorted(g, key=lambda r: r.id)) for g in groups.values()]


TIER = {"PRODUCTISE": 0, "WATCH": 1, "FIELD SOLUTION": 2}


def prioritise(clusters: list[Cluster]) -> list[Cluster]:
    """Rule-of-three clusters first, then those seen twice, then one-offs;
    within a tier by ARR affected, distinct customers and worst severity."""
    return sorted(clusters, key=lambda c: (
        TIER[c.recommendation],
        -c.arr_affected,
        -len(c.customers),
        -SEVERITY_RANK[c.max_severity],
        c.label,
    ))


def format_list(clusters: list[Cluster]) -> str:
    lines = []
    for rank, c in enumerate(clusters, 1):
        lines.append(f"{rank}. [{c.recommendation}] {c.label}")
        lines.append(f"   customers: {len(c.customers)} ({', '.join(c.customers)})   "
                     f"ARR affected: £{c.arr_affected:,.0f}   worst severity: {c.max_severity}   "
                     f"reports: {', '.join(r.id for r in c.reports)}")
        workarounds = [r.workaround for r in c.reports if r.workaround]
        if workarounds:
            lines.append(f"   workarounds in the field: {len(workarounds)}, e.g. {workarounds[0]!r}")
    return "\n".join(lines)


def main() -> None:
    paths = sys.argv[1:] or [HERE / "field_reports.json", HERE / "more_reports.csv"]
    reports = [r for p in paths for r in load_reports(p)]
    clusters = prioritise(cluster_reports(reports))
    print(f"{len(reports)} field reports -> {len(clusters)} needs\n")
    print(format_list(clusters))


if __name__ == "__main__":
    main()
