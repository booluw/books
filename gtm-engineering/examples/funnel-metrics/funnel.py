"""GTM metrics toolkit (Chapters 3 and 15, Appendix B).

Reverse-funnel planning, unit economics, pipeline velocity, and the statistics
needed to run outbound experiments honestly (sample size, two-proportion test).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist


@dataclass
class ReverseFunnel:
    revenue_target: float          # new ARR for the period
    acv: float                     # average contract value
    win_rate: float                # opportunity -> closed-won
    meeting_to_opp: float          # meeting held -> opportunity
    reply_to_meeting: float        # positive reply -> meeting held
    positive_reply_rate: float     # positive replies / delivered emails
    months: int = 12

    def plan(self) -> dict[str, float]:
        customers = math.ceil(self.revenue_target / self.acv)
        opps = math.ceil(customers / self.win_rate)
        meetings = math.ceil(opps / self.meeting_to_opp)
        replies = math.ceil(meetings / self.reply_to_meeting)
        delivered = math.ceil(replies / self.positive_reply_rate)
        return {
            "customers": customers, "opportunities": opps, "meetings": meetings,
            "positive_replies": replies, "delivered_emails": delivered,
            "meetings_per_month": round(meetings / self.months, 1),
            "delivered_per_month": math.ceil(delivered / self.months),
        }


def conversion(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def pipeline_velocity(opportunities: int, avg_deal: float, win_rate: float, cycle_days: float) -> float:
    """Expected revenue per day."""
    return opportunities * avg_deal * win_rate / cycle_days


def cac(sales_marketing_cost: float, new_customers: int) -> float:
    return sales_marketing_cost / new_customers


def cac_payback_months(cac_value: float, new_mrr_per_customer: float, gross_margin: float) -> float:
    return cac_value / (new_mrr_per_customer * gross_margin)


def ltv(arpa_per_month: float, gross_margin: float, monthly_churn: float) -> float:
    return arpa_per_month * gross_margin / monthly_churn


def nrr(starting_arr: float, expansion: float, contraction: float, churn: float) -> float:
    return (starting_arr + expansion - contraction - churn) / starting_arr


def pipeline_coverage(open_pipeline: float, target: float) -> float:
    return open_pipeline / target


def cost_per_meeting(costs: dict[str, float], meetings_held: int) -> float:
    return sum(costs.values()) / meetings_held


def sample_size_per_arm(p1: float, p2: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Contacts needed per arm to detect p1 -> p2 with a two-sided two-proportion z-test."""
    z_a = NormalDist().inv_cdf(1 - alpha / 2)
    z_b = NormalDist().inv_cdf(power)
    p_bar = (p1 + p2) / 2
    numerator = (z_a * math.sqrt(2 * p_bar * (1 - p_bar)) + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(numerator / (p2 - p1) ** 2)


def two_proportion_test(success_a: int, n_a: int, success_b: int, n_b: int) -> tuple[float, float]:
    """Return (z, two-sided p-value) for H0: rate_a == rate_b."""
    p_a, p_b = success_a / n_a, success_b / n_b
    pooled = (success_a + success_b) / (n_a + n_b)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    z = (p_b - p_a) / se
    return z, 2 * (1 - NormalDist().cdf(abs(z)))


if __name__ == "__main__":
    plan = ReverseFunnel(3_000_000, 30_000, 0.25, 0.5, 0.5, 0.01).plan()
    for k, v in plan.items():
        print(f"{k:22} {v:>10,}")
    print("Contacts per arm to detect 2% -> 3% positive replies:", sample_size_per_arm(0.02, 0.03))
