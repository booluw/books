"""SPF and DMARC record checker (Chapter 11).

Works on TXT records supplied through a `resolver` function, so it runs offline
and in tests. In production, plug in a DNS library (e.g. dnspython):

    import dns.resolver
    def resolver(name):
        try:
            return [b"".join(r.strings).decode() for r in dns.resolver.resolve(name, "TXT")]
        except Exception:
            return []

Checks:
  SPF   exactly one v=spf1 record; DNS-lookup count <= 10 (recursing into include/redirect);
        a terminating 'all'; warns on '+all' and '?all'; flags missing include targets.
  DMARC record present at _dmarc.<domain>; policy p=; reporting address; alignment modes;
        pct below 100; explains what each finding means.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

Resolver = Callable[[str], list[str]]


@dataclass
class Report:
    domain: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _spf_records(domain: str, resolve: Resolver) -> list[str]:
    return [r.strip() for r in resolve(domain) if r.strip().lower().startswith("v=spf1")]


def _counts_lookup(term: str) -> bool:
    t = term.lstrip("+-~?").lower()
    return t in ("a", "mx", "ptr") or t.startswith(("a:", "a/", "mx:", "mx/", "ptr:", "include:", "exists:", "redirect="))


def count_spf_lookups(domain: str, resolve: Resolver, report: Report, _seen: set[str] | None = None) -> int:
    seen = _seen if _seen is not None else set()
    if domain in seen:
        report.errors.append(f"SPF include loop at {domain}")
        return 0
    seen.add(domain)
    records = _spf_records(domain, resolve)
    if not records:
        report.errors.append(f"SPF include target {domain} has no SPF record (permerror)")
        return 0
    total = 0
    for term in records[0].split()[1:]:
        if not _counts_lookup(term):
            continue
        total += 1
        t = term.lstrip("+-~?").lower()
        if t.startswith("include:"):
            total += count_spf_lookups(t.split(":", 1)[1], resolve, report, seen)
        elif t.startswith("redirect="):
            total += count_spf_lookups(t.split("=", 1)[1], resolve, report, seen)
    return total


def check_spf(domain: str, resolve: Resolver, report: Report) -> None:
    records = _spf_records(domain, resolve)
    if not records:
        report.errors.append("No SPF record: receivers cannot confirm which servers may send for this domain")
        return
    if len(records) > 1:
        report.errors.append(f"{len(records)} SPF records found: more than one causes a permerror (SPF fails)")
    record = records[0]
    report.info.append(f"SPF: {record}")
    terms = record.split()[1:]
    all_terms = [t for t in terms if t.lstrip("+-~?").lower() == "all"]
    if not all_terms and not any(t.lower().startswith("redirect=") for t in terms):
        report.warnings.append("SPF has no 'all' mechanism; unlisted senders get a neutral result")
    for t in all_terms:
        if t in ("+all", "all"):
            report.errors.append("SPF '+all' authorises every server on the internet to send as you")
        elif t == "?all":
            report.warnings.append("SPF '?all' is neutral; prefer '~all' or '-all'")
    lookups = count_spf_lookups(domain, resolve, report)
    report.info.append(f"SPF DNS lookups: {lookups}/10")
    if lookups > 10:
        report.errors.append(f"SPF needs {lookups} DNS lookups; more than 10 causes a permerror (SPF fails)")
    elif lookups >= 8:
        report.warnings.append(f"SPF uses {lookups}/10 lookups; adding another tool may break it")


def parse_tags(record: str) -> dict[str, str]:
    tags = {}
    for part in record.split(";"):
        if "=" in part:
            key, value = part.split("=", 1)
            tags[key.strip().lower()] = value.strip()
    return tags


def check_dmarc(domain: str, resolve: Resolver, report: Report) -> None:
    records = [r for r in resolve(f"_dmarc.{domain}") if r.strip().lower().startswith("v=dmarc1")]
    if not records:
        report.errors.append("No DMARC record at _dmarc." + domain +
                             ": Gmail, Yahoo and Outlook.com require DMARC for high-volume senders")
        return
    if len(records) > 1:
        report.errors.append("Multiple DMARC records: receivers will ignore DMARC")
    tags = parse_tags(records[0])
    report.info.append(f"DMARC: {records[0]}")
    policy = tags.get("p", "").lower()
    if policy not in ("none", "quarantine", "reject"):
        report.errors.append("DMARC policy p= missing or invalid")
    elif policy == "none":
        report.warnings.append("DMARC p=none monitors only (meets the minimum requirement); "
                               "plan to move to quarantine/reject once all senders are aligned")
    if "rua" not in tags:
        report.warnings.append("No rua= reporting address: you won't see who sends as your domain")
    if tags.get("adkim", "r") == "s" or tags.get("aspf", "r") == "s":
        report.info.append("Strict alignment set: sending tools must use the exact From domain")
    pct = tags.get("pct")
    if pct and pct.isdigit() and int(pct) < 100:
        report.warnings.append(f"pct={pct}: policy applies to only {pct}% of failing mail")


def check_domain(domain: str, resolve: Resolver) -> Report:
    report = Report(domain=domain.lower())
    check_spf(report.domain, resolve, report)
    check_dmarc(report.domain, resolve, report)
    return report


def dict_resolver(zone: dict[str, list[str]]) -> Resolver:
    return lambda name: zone.get(name.lower().rstrip("."), [])


if __name__ == "__main__":
    zone = {
        "example-mail.com": ["v=spf1 include:_spf.google.com include:sendgrid.net ~all",
                             "google-site-verification=abc"],
        "_spf.google.com": ["v=spf1 include:_netblocks.google.com include:_netblocks2.google.com ~all"],
        "_netblocks.google.com": ["v=spf1 ip4:35.190.247.0/24 ~all"],
        "_netblocks2.google.com": ["v=spf1 ip6:2001:4860:4000::/36 ~all"],
        "sendgrid.net": ["v=spf1 ip4:167.89.0.0/17 ~all"],
        "_dmarc.example-mail.com": ["v=DMARC1; p=none; rua=mailto:dmarc@example.com"],
    }
    r = check_domain("example-mail.com", dict_resolver(zone))
    for label, lines in (("ERROR", r.errors), ("WARNING", r.warnings), ("INFO", r.info)):
        for line in lines:
            print(f"[{label}] {line}")
    print("PASS" if r.ok else "FAIL")
