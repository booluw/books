"""Impact and deal-economics calculator (Chapters 3 and 5).

Two questions come up in every engagement:

  * For the customer: what is this worth per year, and how quickly does it
    pay back? (Chapter 5, "Quick value estimation")
  * For the vendor: what does the deal look like once FDE time is counted as
    a cost? (Chapter 3, "A simple model")

This module reproduces both worked examples from the book exactly and adds
payback, ROI and simple sensitivity analysis, because a single number with no
range invites false confidence.

Usage:
    python3 impact.py
"""
from __future__ import annotations

from dataclasses import dataclass, fields, replace


# --------------------------------------------------------------------------
# Customer value (Chapter 5)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class ValueInputs:
    """Inputs to the quick value estimate. Every one is an assumption: write
    down where each came from and have the customer's finance team check it."""
    people: float                       # people affected
    hours_saved_per_week: float         # per person
    weeks_per_year: float               # working weeks (excludes leave and holidays)
    loaded_hourly_cost: float           # salary + employer costs + overheads, per hour
    errors_avoided_per_year: float = 0.0
    cost_per_error: float = 0.0
    revenue_uplift: float = 0.0         # extra annual revenue attributable to the change


@dataclass(frozen=True)
class ValueBreakdown:
    time: float
    errors: float
    revenue: float

    @property
    def total(self) -> float:
        return self.time + self.errors + self.revenue


def annual_value(v: ValueInputs) -> ValueBreakdown:
    """annual_value = people x hours saved/week x weeks x loaded hourly cost
                    + errors avoided x cost per error
                    + revenue uplift"""
    return ValueBreakdown(
        time=v.people * v.hours_saved_per_week * v.weeks_per_year * v.loaded_hourly_cost,
        errors=v.errors_avoided_per_year * v.cost_per_error,
        revenue=v.revenue_uplift,
    )


def payback_months(one_off_cost: float, annual_value: float, annual_running_cost: float = 0.0) -> float:
    """Months until cumulative net benefit covers the one-off cost.
    Returns infinity if the project never pays back."""
    net_monthly = (annual_value - annual_running_cost) / 12
    return one_off_cost / net_monthly if net_monthly > 0 else float("inf")


def roi(total_value: float, total_cost: float) -> float:
    """Return on investment: (value - cost) / cost. 2.0 means value is three times cost."""
    return (total_value - total_cost) / total_cost


def sensitivity(base: ValueInputs, field_name: str, values: list[float]) -> list[tuple[float, float]]:
    """Annual value as one input varies and the rest stay at base."""
    return [(x, annual_value(replace(base, **{field_name: x})).total) for x in values]


def tornado(base: ValueInputs, ranges: dict[str, tuple[float, float]] | None = None,
            swing: float = 0.2) -> list[tuple[str, float, float]]:
    """Annual value at the low and high end of each input's plausible range,
    others held at base, largest effect first. Inputs without a range given
    swing by ±`swing` (default 20%). The top rows are the assumptions to verify
    with the customer first.

    (In a pure product such as people x hours x weeks x cost, the same
    percentage swing moves the total equally for every input, so the ranking
    only means something when the ranges reflect real uncertainty.)"""
    ranges = ranges or {}
    rows = []
    for f in fields(base):
        x = getattr(base, f.name)
        lo_x, hi_x = ranges.get(f.name, (x * (1 - swing), x * (1 + swing)))
        if not x and f.name not in ranges:
            continue
        lo = annual_value(replace(base, **{f.name: lo_x})).total
        hi = annual_value(replace(base, **{f.name: hi_x})).total
        rows.append((f.name, lo, hi))
    return sorted(rows, key=lambda r: -(r[2] - r[1]))


def scenarios(low: ValueInputs, base: ValueInputs, high: ValueInputs) -> dict[str, float]:
    """Low / base / high annual value. Lead with the low case when you present."""
    return {name: annual_value(v).total for name, v in (("low", low), ("base", base), ("high", high))}


# --------------------------------------------------------------------------
# Vendor deal economics (Chapter 3)
# --------------------------------------------------------------------------

def fde_cost(fdes: float, share_of_year: float, loaded_cost_per_fde: float) -> float:
    """Cost of FDE time on one customer: number of FDEs x share of their year
    x fully loaded annual cost (salary, benefits, travel, management)."""
    return fdes * share_of_year * loaded_cost_per_fde


@dataclass(frozen=True)
class DealYear:
    year: int
    acv: float                          # annual contract value (revenue that year)
    platform_cost: float                # hosting, inference, support
    fde_cost: float

    @property
    def gross_profit(self) -> float:
        return self.acv - self.platform_cost - self.fde_cost

    @property
    def gross_margin(self) -> float:
        """(revenue - cost of delivering it) / revenue."""
        return self.gross_profit / self.acv

    @property
    def fde_share_of_revenue(self) -> float:
        return self.fde_cost / self.acv


@dataclass(frozen=True)
class DealSummary:
    revenue: float
    gross_profit: float

    @property
    def gross_margin(self) -> float:
        return self.gross_profit / self.revenue


def deal_summary(years: list[DealYear]) -> DealSummary:
    return DealSummary(sum(y.acv for y in years), sum(y.gross_profit for y in years))


def build_deal(acvs: list[float], platform_cost_rate: float,
               fde_plan: list[tuple[float, float]], loaded_cost_per_fde: float) -> list[DealYear]:
    """Deal years from ACVs, a platform cost as a share of ACV, and per-year
    (FDEs, share of year) pairs."""
    return [DealYear(i + 1, acv, acv * platform_cost_rate, fde_cost(n, share, loaded_cost_per_fde))
            for i, (acv, (n, share)) in enumerate(zip(acvs, fde_plan))]


# --------------------------------------------------------------------------
# The book's worked examples
# --------------------------------------------------------------------------

def chapter5_example() -> ValueInputs:
    """60 claims adjusters each save 3 hours a week, 46 working weeks a year,
    at a loaded cost of £45 an hour."""
    return ValueInputs(people=60, hours_saved_per_week=3, weeks_per_year=46, loaded_hourly_cost=45)


def chapter3_example() -> list[DealYear]:
    """Year 1: $600k ACV, 2 FDEs for half the year. Years 2-3: expansion to
    $1.5M and $2.5M with 0.5 FDE. Platform cost 20% of ACV; FDE loaded cost $350k."""
    return build_deal(acvs=[600_000, 1_500_000, 2_500_000], platform_cost_rate=0.20,
                      fde_plan=[(2, 0.5), (0.5, 1.0), (0.5, 1.0)], loaded_cost_per_fde=350_000)


# Plausible ranges for the Chapter 5 inputs (illustrative, not from the book).
CHAPTER5_RANGES = {
    "people": (50, 60),                 # some adjusters may not adopt the tool
    "hours_saved_per_week": (1.5, 4),   # the least certain number: measure it in the pilot
    "weeks_per_year": (44, 47),
    "loaded_hourly_cost": (40, 50),
}

# Illustrative costs for the payback example (not from the book): a one-off
# deployment of £150,000 and £40,000 a year to run.
ILLUSTRATIVE_DEPLOYMENT_COST = 150_000
ILLUSTRATIVE_RUNNING_COST = 40_000


def main() -> None:
    base = chapter5_example()
    value = annual_value(base).total
    print("Chapter 5: quick value estimate")
    print(f"  {base.people:g} people x {base.hours_saved_per_week:g} h/week x {base.weeks_per_year:g} weeks"
          f" x £{base.loaded_hourly_cost:g}/h = £{value:,.0f} per year (book: ≈ £373,000)")
    s = scenarios(replace(base, hours_saved_per_week=1.5), base, replace(base, hours_saved_per_week=4))
    print("  scenarios (hours saved 1.5 / 3 / 4): " +
          ", ".join(f"{k} £{v:,.0f}" for k, v in s.items()))
    print("  sensitivity (each input across its plausible range, largest effect first):")
    for name, lo, hi in tornado(base, CHAPTER5_RANGES):
        print(f"    {name:22} £{lo:,.0f} – £{hi:,.0f}")
    pb = payback_months(ILLUSTRATIVE_DEPLOYMENT_COST, value, ILLUSTRATIVE_RUNNING_COST)
    first_year_roi = roi(value, ILLUSTRATIVE_DEPLOYMENT_COST + ILLUSTRATIVE_RUNNING_COST)
    print(f"  illustrative: £{ILLUSTRATIVE_DEPLOYMENT_COST:,} to deploy, £{ILLUSTRATIVE_RUNNING_COST:,}/yr to run"
          f" -> payback {pb:.1f} months, first-year ROI {first_year_roi:.0%}")

    print("\nChapter 3: deal gross margin with FDE cost")
    print(f"  {'Year':>4} {'ACV':>11} {'Platform':>10} {'FDE':>10} {'Gross profit':>13} {'Margin':>7} {'FDE % rev':>9}")
    years = chapter3_example()
    usd = lambda x: f"${x:,.0f}"                                   # noqa: E731
    for y in years:
        print(f"  {y.year:>4} {usd(y.acv):>11} {usd(y.platform_cost):>10} {usd(y.fde_cost):>10}"
              f" {usd(y.gross_profit):>13} {y.gross_margin:>7.1%} {y.fde_share_of_revenue:>9.1%}")
    total = deal_summary(years)
    print(f"  3 years: revenue ${total.revenue:,.0f}, gross profit ${total.gross_profit:,.0f},"
          f" gross margin {total.gross_margin:.1%} (book: ≈ 65%)")


if __name__ == "__main__":
    main()
