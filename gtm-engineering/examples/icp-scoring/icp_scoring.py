"""Explainable, rules-based ICP fit scoring (Chapter 4).

Each rule adds points and records *why*, so sellers can see the reasons
behind a tier. Disqualifiers exclude an account outright. The model carries a
version string that is stored with every score.

Usage:  python icp_scoring.py accounts.csv
"""
from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field

MODEL_VERSION = "icp-v1.2"

TARGET_INDUSTRIES = {"third-party logistics", "freight forwarding"}
TARGET_COUNTRIES = {"US", "CA"}
LEGACY_TMS = {"legacytms", "oldroute", "shipclassic"}
TIERS = [(80, "Tier 1"), (55, "Tier 2"), (30, "Tier 3")]


@dataclass
class Score:
    domain: str
    points: int = 0
    tier: str = "Not ICP"
    reasons: list[str] = field(default_factory=list)
    disqualified_reason: str | None = None
    model_version: str = MODEL_VERSION


def _int_or_none(value):
    try:
        return int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def score_account(account: dict, *, customers: set[str] = frozenset(),
                  competitors: set[str] = frozenset()) -> Score:
    domain = (account.get("domain") or "").strip().lower()
    result = Score(domain=domain)

    # Disqualifiers first: they override any positive points.
    if not domain:
        result.disqualified_reason = "no domain"
    elif domain in competitors:
        result.disqualified_reason = "competitor"
    elif domain in customers:
        result.disqualified_reason = "existing customer"
    if result.disqualified_reason:
        result.tier = "Excluded"
        return result

    def add(points: int, reason: str):
        result.points += points
        result.reasons.append(f"{points:+d} {reason}")

    industry = (account.get("industry") or "").strip().lower()
    if industry in TARGET_INDUSTRIES:
        add(30, f"industry '{industry}'")

    employees = _int_or_none(account.get("employees"))
    if employees is None:
        result.reasons.append("+0 employee count unknown")
    elif 200 <= employees <= 2000:
        add(25, f"{employees} employees (core band 200-2,000)")
    elif 100 <= employees < 200 or 2000 < employees <= 5000:
        add(10, f"{employees} employees (adjacent band)")

    if (account.get("country") or "").strip().upper() in TARGET_COUNTRIES:
        add(15, f"country {account['country'].upper()}")

    tech = {t.strip().lower() for t in (account.get("tech") or "").split(";") if t.strip()}
    if tech & LEGACY_TMS:
        add(20, f"uses legacy TMS ({', '.join(sorted(tech & LEGACY_TMS))})")

    open_ops_roles = _int_or_none(account.get("open_ops_roles")) or 0
    if open_ops_roles >= 2:
        add(10, f"{open_ops_roles} open operations roles")

    for threshold, tier in TIERS:
        if result.points >= threshold:
            result.tier = tier
            break
    return result


def main(path: str) -> None:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    competitors = {"rivalroute.com"}          # in real use: loaded from a maintained list
    customers: set[str] = set()                # in real use: loaded from the CRM
    for row in rows:
        s = score_account(row, customers=customers, competitors=competitors)
        detail = s.disqualified_reason or "; ".join(s.reasons)
        print(f"{s.domain:30} {s.tier:9} {s.points:4}  {detail}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sample_accounts.csv")
