"""Cost-aware email enrichment waterfall (Chapter 7).

Providers are tried in order until one returns an email that passes
verification. Demonstrates:
  * caching (never pay twice inside the freshness window)
  * verification after every finder; continue on invalid
  * treating provider errors (rate limits, outages) as "retry later", NOT "not found"
  * rejecting results whose domain conflicts with the company domain
  * provenance (source, timestamp, status) and per-run cost tracking with a budget cap

Providers here are fakes so the example runs offline; replace them with real API clients.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Protocol


class ProviderError(Exception):
    """Transient provider failure (429, 5xx, timeout). Do not record as 'not found'."""


class Provider(Protocol):
    name: str
    cost: float                                   # cost per lookup, in dollars

    def find_email(self, first: str, last: str, domain: str) -> str | None: ...


@dataclass
class Result:
    status: str                                   # found | not_found | retry_later | skipped_budget
    email: str | None = None
    source: str | None = None
    verification: str | None = None              # valid | catch_all | invalid | unknown
    checked_at: float = field(default_factory=time.time)
    cost: float = 0.0
    attempts: list[str] = field(default_factory=list)


@dataclass
class Waterfall:
    providers: list[Provider]
    verify: Callable[[str], str]                  # returns valid | catch_all | invalid | unknown
    verify_cost: float = 0.004
    accept_catch_all: bool = False
    freshness_seconds: float = 90 * 24 * 3600
    budget: float = 50.0
    spent: float = 0.0
    cache: dict[str, Result] = field(default_factory=dict)
    clock: Callable[[], float] = time.time

    @staticmethod
    def cache_key(first: str, last: str, domain: str) -> str:
        return f"email:{first.strip().lower()}|{last.strip().lower()}|{domain.strip().lower()}"

    def _charge(self, amount: float, result: Result) -> bool:
        if self.spent + amount > self.budget:
            return False
        self.spent += amount
        result.cost += amount
        return True

    def find(self, first: str, last: str, domain: str) -> Result:
        domain = domain.strip().lower()
        key = self.cache_key(first, last, domain)
        cached = self.cache.get(key)
        if cached and cached.status in {"found", "not_found"} \
                and self.clock() - cached.checked_at < self.freshness_seconds:
            return cached

        result = Result(status="not_found", checked_at=self.clock())
        transient_failure = False
        for provider in self.providers:
            if not self._charge(provider.cost, result):
                result.status = "skipped_budget"
                return result                     # don't cache: try again with budget later
            try:
                email = provider.find_email(first, last, domain)
            except ProviderError:
                result.attempts.append(f"{provider.name}:error")
                transient_failure = True
                continue
            if not email:
                result.attempts.append(f"{provider.name}:miss")
                continue
            email = email.strip().lower()
            if email.rsplit("@", 1)[-1] != domain:
                result.attempts.append(f"{provider.name}:domain_mismatch")
                continue
            if not self._charge(self.verify_cost, result):
                result.status = "skipped_budget"
                return result
            verdict = self.verify(email)
            result.attempts.append(f"{provider.name}:{verdict}")
            if verdict == "valid" or (verdict == "catch_all" and self.accept_catch_all):
                result.status, result.email = "found", email
                result.source, result.verification = provider.name, verdict
                break
        else:
            if transient_failure:
                result.status = "retry_later"     # a provider was down: not proof of absence

        if result.status in {"found", "not_found"}:
            self.cache[key] = result
        return result


# ---------------------------------------------------------------------------
# Fake providers and verifier for the demo and tests
# ---------------------------------------------------------------------------
@dataclass
class FakeProvider:
    name: str
    cost: float
    data: dict[tuple[str, str, str], str]
    fail: bool = False
    calls: int = 0

    def find_email(self, first, last, domain):
        self.calls += 1
        if self.fail:
            raise ProviderError("429 Too Many Requests")
        return self.data.get((first.lower(), last.lower(), domain))


def fake_verifier(table: dict[str, str]) -> Callable[[str], str]:
    return lambda email: table.get(email, "unknown")


if __name__ == "__main__":
    cheap = FakeProvider("provider_a", 0.05, {("jane", "doe", "acme-logistics.com"): "jdoe@acme-logistics.com"})
    mid = FakeProvider("provider_b", 0.08, {("jane", "doe", "acme-logistics.com"): "jane.doe@acme-logistics.com"})
    wf = Waterfall([cheap, mid], verify=fake_verifier({"jdoe@acme-logistics.com": "invalid",
                                                        "jane.doe@acme-logistics.com": "valid"}))
    r = wf.find("Jane", "Doe", "acme-logistics.com")
    print(r.status, r.email, r.source, r.attempts, f"cost=${r.cost:.3f}")
    spent_before = wf.spent
    wf.find("Jane", "Doe", "ACME-logistics.com")
    print(f"second lookup added ${wf.spent - spent_before:.3f} (served from cache)")
