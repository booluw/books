"""Inbound lead router (Chapter 9).

Implements agreed rules of engagement in order:
  1. disqualify (competitor, spam, free email without company)
  2. existing customer          -> account manager
  3. open opportunity           -> opportunity owner
  4. owned account (active rep) -> account owner
  5. territory + segment        -> weighted, availability-aware round robin
  6. nobody available           -> fallback queue (and alert)

Every decision carries a human-readable reason for the audit log. The round-robin
state lives in a store object so it survives restarts (use a database in production).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Rep:
    id: str
    territories: set[str]            # e.g. {"NA"}, {"EMEA"}
    segments: set[str]               # e.g. {"mid_market", "enterprise"}
    active: bool = True              # False once offboarded
    out_of_office: bool = False
    daily_cap: int = 20
    weight: int = 1                  # ramping reps 1, full capacity 2, etc.
    assigned_today: int = 0


@dataclass
class Lead:
    email: str
    country: str
    employees: int | None
    account_id: str | None = None    # from lead-to-account matching
    is_competitor: bool = False
    is_spam: bool = False
    free_email: bool = False
    company_name: str = ""


@dataclass
class AccountState:
    owner_id: str | None = None
    is_customer: bool = False
    account_manager_id: str | None = None
    open_opportunity_owner_id: str | None = None


@dataclass
class Decision:
    assignee: str | None
    queue: str | None
    reason: str


REGIONS = {"US": "NA", "CA": "NA", "MX": "NA", "GB": "EMEA", "DE": "EMEA", "FR": "EMEA",
           "NL": "EMEA", "AU": "APAC", "SG": "APAC", "JP": "APAC"}


def segment_for(employees: int | None) -> str:
    if employees is None:
        return "unknown"
    if employees >= 1000:
        return "enterprise"
    if employees >= 100:
        return "mid_market"
    return "smb"


@dataclass
class RoundRobinStore:
    """Durable pointer per pool. In production, persist this (database row with a lock)."""
    pointers: dict[str, int] = field(default_factory=dict)


class Router:
    def __init__(self, reps: list[Rep], accounts: dict[str, AccountState], store: RoundRobinStore):
        self.reps = {r.id: r for r in reps}
        self.accounts = accounts
        self.store = store

    def _usable(self, rep_id: str | None) -> bool:
        rep = self.reps.get(rep_id or "")
        return bool(rep and rep.active)

    def _eligible(self, region: str, segment: str) -> list[Rep]:
        # Unknown segment goes to the mid-market pool by policy rather than being dropped.
        seg = "mid_market" if segment == "unknown" else segment
        return [r for r in self.reps.values()
                if r.active and region in r.territories and seg in r.segments]

    def _round_robin(self, pool_key: str, candidates: list[Rep]) -> Rep | None:
        # Expand by weight into a stable slot list, then advance the durable pointer,
        # skipping reps who are out of office or at their daily cap.
        slots = [r for r in sorted(candidates, key=lambda r: r.id) for _ in range(max(1, r.weight))]
        if not slots:
            return None
        start = self.store.pointers.get(pool_key, 0)
        for offset in range(len(slots)):
            rep = slots[(start + offset) % len(slots)]
            if not rep.out_of_office and rep.assigned_today < rep.daily_cap:
                self.store.pointers[pool_key] = (start + offset + 1) % len(slots)
                return rep
        return None

    def route(self, lead: Lead) -> Decision:
        if lead.is_spam:
            return Decision(None, "discard", "spam")
        if lead.is_competitor:
            return Decision(None, "discard", "competitor")
        if lead.free_email and not lead.account_id and not lead.company_name:
            return Decision(None, "nurture", "free email domain and no company")

        acct = self.accounts.get(lead.account_id or "")
        if acct and acct.is_customer:
            if self._usable(acct.account_manager_id):
                return self._assign(acct.account_manager_id, "existing customer -> account manager")
            return Decision(None, "cs_queue", "existing customer; account manager inactive")
        if acct and acct.open_opportunity_owner_id and self._usable(acct.open_opportunity_owner_id):
            return self._assign(acct.open_opportunity_owner_id, "open opportunity -> opportunity owner")
        if acct and self._usable(acct.owner_id):
            return self._assign(acct.owner_id, "owned account -> account owner")

        region = REGIONS.get(lead.country.upper(), "ROW")
        segment = segment_for(lead.employees)
        pool = self._eligible(region, segment)
        rep = self._round_robin(f"{region}:{segment}", pool)
        if rep is None:
            return Decision(None, "fallback", f"no available rep for {region}/{segment}; alert manager")
        why = f"round robin {region}/{segment}"
        if acct and acct.owner_id and not self._usable(acct.owner_id):
            why += f" (previous owner {acct.owner_id} inactive)"
        return self._assign(rep.id, why)

    def _assign(self, rep_id: str, reason: str) -> Decision:
        self.reps[rep_id].assigned_today += 1
        return Decision(rep_id, None, reason)
