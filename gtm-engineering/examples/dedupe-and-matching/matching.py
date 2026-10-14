"""Domain normalisation, company-name normalisation, duplicate detection and
lead-to-account matching (Chapter 5).

Real systems should use the full Public Suffix List (e.g. the `tldextract`
package); a small built-in subset keeps this example dependency-free.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from urllib.parse import urlparse

# Subset of the Public Suffix List, enough for the examples and tests.
MULTI_PART_SUFFIXES = {"co.uk", "org.uk", "ac.uk", "com.au", "co.nz", "co.jp", "com.br", "co.za", "com.mx"}

FREE_EMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com", "yahoo.com",
    "icloud.com", "me.com", "aol.com", "proton.me", "protonmail.com", "gmx.de", "web.de", "mail.com",
}

LEGAL_SUFFIXES = {
    "inc", "incorporated", "llc", "ltd", "limited", "plc", "gmbh", "ag", "sa", "sas", "bv", "nv",
    "corp", "corporation", "co", "company", "pty", "srl", "oy", "ab", "as", "kg",
}


def registrable_domain(value: str) -> str | None:
    """Turn a URL, hostname or email address into its registrable domain.

    'https://www.EU.Acme-Logistics.com/about' -> 'acme-logistics.com'
    'jane@eu.acme.co.uk'                      -> 'acme.co.uk'
    """
    if not value:
        return None
    value = value.strip().lower()
    if "@" in value:
        value = value.rsplit("@", 1)[1]
    if "://" in value:
        value = urlparse(value).hostname or ""
    value = value.split("/")[0].split(":")[0].rstrip(".")
    labels = [label for label in value.split(".") if label]
    if len(labels) < 2:
        return None
    if ".".join(labels[-2:]) in MULTI_PART_SUFFIXES and len(labels) >= 3:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def is_free_email_domain(domain: str | None) -> bool:
    return bool(domain) and domain in FREE_EMAIL_DOMAINS


def normalise_company_name(name: str) -> str:
    """'ACME Logistics, GmbH & Co. KG' -> 'acme logistics'"""
    text = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower()
    text = text.replace("&", " ")
    tokens = re.findall(r"[a-z0-9]+", text)
    while tokens and tokens[-1] in LEGAL_SUFFIXES:
        tokens.pop()
    return " ".join(tokens)


def name_similarity(a: str, b: str) -> float:
    a, b = normalise_company_name(a), normalise_company_name(b)
    if not a or not b:
        return 0.0
    tokens_a, tokens_b = set(a.split()), set(b.split())
    jaccard = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
    return max(jaccard, SequenceMatcher(None, a, b).ratio())


@dataclass
class Account:
    id: str
    name: str
    domain: str | None
    extra_domains: list[str] = field(default_factory=list)
    parent_id: str | None = None
    owner: str | None = None
    open_opportunities: int = 0
    is_customer: bool = False


@dataclass
class Match:
    account: Account | None
    method: str            # domain | extra_domain | fuzzy_name | none
    confidence: float
    duplicates: list[str] = field(default_factory=list)
    needs_review: bool = False


def _rank(accounts: list[Account]) -> list[Account]:
    """Tie-break duplicates: owned > has open opps > customer > lowest id (stable)."""
    return sorted(accounts, key=lambda a: (a.owner is None, -a.open_opportunities, not a.is_customer, a.id))


def match_lead_to_account(email: str | None, company_name: str, accounts: list[Account],
                          fuzzy_threshold: float = 0.88, review_threshold: float = 0.75) -> Match:
    domain = registrable_domain(email or "")
    if domain and not is_free_email_domain(domain):
        exact = [a for a in accounts if a.domain and registrable_domain(a.domain) == domain]
        if exact:
            ranked = _rank(exact)
            return Match(ranked[0], "domain", 1.0, duplicates=[a.id for a in ranked[1:]])
        extra = [a for a in accounts if domain in {registrable_domain(d) for d in a.extra_domains}]
        if extra:
            ranked = _rank(extra)
            return Match(ranked[0], "extra_domain", 0.95, duplicates=[a.id for a in ranked[1:]])

    scored = sorted(((name_similarity(company_name, a.name), a) for a in accounts),
                    key=lambda pair: pair[0], reverse=True)
    if scored and scored[0][0] >= review_threshold:
        best_score, best = scored[0]
        return Match(best, "fuzzy_name", round(best_score, 3), needs_review=best_score < fuzzy_threshold)
    return Match(None, "none", 0.0)


def ultimate_parent(account: Account, by_id: dict[str, Account]) -> Account:
    seen = set()
    while account.parent_id and account.parent_id in by_id and account.id not in seen:
        seen.add(account.id)
        account = by_id[account.parent_id]
    return account


def find_duplicate_accounts(accounts: list[Account], name_threshold: float = 0.92) -> list[tuple[str, str, str]]:
    """Return (id_a, id_b, reason) pairs that are likely duplicates."""
    pairs = []
    by_domain: dict[str, list[Account]] = {}
    for a in accounts:
        d = registrable_domain(a.domain or "")
        if d:
            by_domain.setdefault(d, []).append(a)
    for d, group in by_domain.items():
        for other in group[1:]:
            pairs.append((group[0].id, other.id, f"same domain {d}"))
    seen = {frozenset(p[:2]) for p in pairs}
    for i, a in enumerate(accounts):
        for b in accounts[i + 1:]:
            if frozenset((a.id, b.id)) in seen:
                continue
            da, db = registrable_domain(a.domain or ""), registrable_domain(b.domain or "")
            if da and db and da != db:
                continue    # different known domains: probably different companies
            score = name_similarity(a.name, b.name)
            if score >= name_threshold:
                pairs.append((a.id, b.id, f"name similarity {score:.2f}"))
    return pairs
