"""Signal-to-action pipeline (Chapter 8).

  ingest -> normalise -> de-duplicate -> score with exponential decay ->
  act at threshold (or immediately for hand-raisers), with cool-downs and suppression.

Pure Python and deterministic (an explicit `now` is passed in), so it is easy to test.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

# weight = points when fresh; half_life_days = how fast it fades.
SIGNAL_TYPES = {
    "demo_request":          {"weight": 100, "half_life_days": 3,   "immediate": True},
    "champion_job_change":   {"weight": 60,  "half_life_days": 45,  "immediate": True},
    "pricing_page_visit":    {"weight": 25,  "half_life_days": 7,   "immediate": False},
    "new_exec_hire":         {"weight": 30,  "half_life_days": 60,  "immediate": False},
    "funding_round":         {"weight": 20,  "half_life_days": 90,  "immediate": False},
    "relevant_job_posts":    {"weight": 15,  "half_life_days": 30,  "immediate": False},
    "topic_intent_surge":    {"weight": 10,  "half_life_days": 14,  "immediate": False},
}
THRESHOLD = 50
COOLDOWN = timedelta(days=21)


@dataclass(frozen=True)
class Signal:
    type: str
    account_domain: str
    occurred_at: datetime
    source: str
    person_email: str | None = None

    @property
    def dedupe_key(self) -> str:
        # Same type + entity + calendar day = same event, whichever source reported it.
        who = self.person_email or self.account_domain
        return f"{self.type}:{who}:{self.occurred_at.date().isoformat()}"


@dataclass
class Action:
    account_domain: str
    kind: str              # immediate | threshold
    score: float
    reasons: list[str]


@dataclass
class SignalPipeline:
    suppressed_domains: set[str] = field(default_factory=set)      # customers in active deals, competitors, opt-outs
    seen_keys: set[str] = field(default_factory=set)
    signals: dict[str, list[Signal]] = field(default_factory=dict)
    last_actioned: dict[str, datetime] = field(default_factory=dict)

    def ingest(self, signal: Signal) -> bool:
        if signal.type not in SIGNAL_TYPES:
            raise ValueError(f"unknown signal type {signal.type}")
        signal = Signal(signal.type, signal.account_domain.strip().lower(), signal.occurred_at,
                        signal.source, (signal.person_email or None) and signal.person_email.lower())
        if signal.dedupe_key in self.seen_keys:
            return False
        self.seen_keys.add(signal.dedupe_key)
        self.signals.setdefault(signal.account_domain, []).append(signal)
        return True

    @staticmethod
    def decayed(signal: Signal, now: datetime) -> float:
        cfg = SIGNAL_TYPES[signal.type]
        age_days = max(0.0, (now - signal.occurred_at).total_seconds() / 86400)
        return cfg["weight"] * 0.5 ** (age_days / cfg["half_life_days"])

    def score(self, domain: str, now: datetime) -> tuple[float, list[str]]:
        parts = sorted(((self.decayed(s, now), s) for s in self.signals.get(domain, [])),
                       key=lambda p: p[0], reverse=True)
        reasons = [f"{s.type} ({s.source}, {s.occurred_at.date()}) +{pts:.1f}" for pts, s in parts if pts >= 0.5]
        return round(sum(p for p, _ in parts), 1), reasons

    def evaluate(self, now: datetime) -> list[Action]:
        actions = []
        for domain, sigs in self.signals.items():
            if domain in self.suppressed_domains:
                continue
            last = self.last_actioned.get(domain)
            fresh_immediate = [s for s in sigs if SIGNAL_TYPES[s.type]["immediate"]
                               and (last is None or s.occurred_at > last)]
            score, reasons = self.score(domain, now)
            if fresh_immediate:
                kind = "immediate"          # hand-raisers bypass the cool-down
            elif score >= THRESHOLD and (last is None or now - last >= COOLDOWN):
                kind = "threshold"
            else:
                continue
            self.last_actioned[domain] = now
            actions.append(Action(domain, kind, score, reasons))
        return sorted(actions, key=lambda a: (a.kind != "immediate", -a.score))


if __name__ == "__main__":
    now = datetime(2026, 10, 14, 12, 0)
    p = SignalPipeline(suppressed_domains={"competitor.io"})
    for s in [
        Signal("new_exec_hire", "acme-logistics.com", now - timedelta(days=10), "enrichment"),
        Signal("pricing_page_visit", "acme-logistics.com", now - timedelta(days=1), "web"),
        Signal("pricing_page_visit", "acme-logistics.com", now - timedelta(days=1), "reverse_ip"),  # duplicate
        Signal("funding_round", "acme-logistics.com", now - timedelta(days=20), "crunchbase"),
        Signal("topic_intent_surge", "bigco.com", now - timedelta(days=2), "bombora"),
        Signal("demo_request", "smallco.com", now - timedelta(minutes=5), "form", "ops@smallco.com"),
        Signal("pricing_page_visit", "competitor.io", now, "web"),
    ]:
        p.ingest(s)
    for a in p.evaluate(now):
        print(f"{a.kind:9} {a.account_domain:20} score={a.score:6.1f}  " + "; ".join(a.reasons))
