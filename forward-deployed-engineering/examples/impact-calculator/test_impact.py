import math
import unittest
from dataclasses import replace

from impact import (CHAPTER5_RANGES, DealYear, ValueInputs, annual_value, chapter3_example,
                    chapter5_example, deal_summary, fde_cost, payback_months, roi, scenarios,
                    sensitivity, tornado)


class Chapter5ValueTests(unittest.TestCase):
    def test_book_example_exact(self):
        # 60 adjusters x 3 h/week x 46 weeks x £45/h; the book rounds to £373,000.
        v = annual_value(chapter5_example())
        self.assertEqual(v.time, 372_600)
        self.assertEqual(v.total, 372_600)
        self.assertEqual(round(v.total, -3), 373_000)

    def test_error_and_revenue_terms(self):
        v = annual_value(ValueInputs(10, 1, 40, 50, errors_avoided_per_year=200,
                                     cost_per_error=75, revenue_uplift=10_000))
        self.assertEqual((v.time, v.errors, v.revenue), (20_000, 15_000, 10_000))
        self.assertEqual(v.total, 45_000)

    def test_payback_and_roi(self):
        self.assertAlmostEqual(payback_months(150_000, 372_600, 40_000), 5.41, places=2)
        self.assertEqual(payback_months(120_000, 120_000), 12)
        self.assertTrue(math.isinf(payback_months(100_000, 30_000, 40_000)))   # never pays back
        self.assertAlmostEqual(roi(300_000, 100_000), 2.0)

    def test_scenarios_and_sensitivity(self):
        base = chapter5_example()
        s = scenarios(replace(base, hours_saved_per_week=1.5), base, replace(base, hours_saved_per_week=4))
        self.assertEqual(s, {"low": 186_300, "base": 372_600, "high": 496_800})
        self.assertEqual(sensitivity(base, "people", [30, 60]), [(30, 186_300), (60, 372_600)])

    def test_tornado_ranks_least_certain_input_first(self):
        rows = tornado(chapter5_example(), CHAPTER5_RANGES)
        self.assertEqual(rows[0][0], "hours_saved_per_week")
        self.assertEqual([r[0] for r in rows][-1], "weeks_per_year")

    def test_tornado_default_swing_skips_zero_inputs(self):
        names = [r[0] for r in tornado(chapter5_example())]
        self.assertNotIn("revenue_uplift", names)
        self.assertEqual(len(names), 4)


class Chapter3DealTests(unittest.TestCase):
    def setUp(self):
        self.years = chapter3_example()

    def test_fde_cost(self):
        self.assertEqual(fde_cost(2, 0.5, 350_000), 350_000)
        self.assertEqual(fde_cost(0.5, 1.0, 350_000), 175_000)

    def test_year_inputs_match_book(self):
        got = [(y.acv, y.platform_cost, y.fde_cost) for y in self.years]
        self.assertEqual(got, [(600_000, 120_000, 350_000),
                               (1_500_000, 300_000, 175_000),
                               (2_500_000, 500_000, 175_000)])

    def test_yearly_margins(self):
        m = [y.gross_margin for y in self.years]
        self.assertAlmostEqual(m[0], 130_000 / 600_000)        # 21.67%, book ≈ 22%
        self.assertAlmostEqual(m[1], 1_025_000 / 1_500_000)    # 68.3%, book 68%
        self.assertAlmostEqual(m[2], 0.73)                     # 73%
        self.assertEqual([round(x * 100) for x in m], [22, 68, 73])

    def test_three_year_summary(self):
        total = deal_summary(self.years)
        self.assertEqual(total.revenue, 4_600_000)
        self.assertAlmostEqual(total.gross_profit, 2_980_000)
        self.assertAlmostEqual(total.gross_margin, 0.6478, places=4)
        self.assertEqual(round(total.gross_margin * 100), 65)

    def test_fde_share_of_revenue_falls(self):
        shares = [y.fde_share_of_revenue for y in self.years]
        self.assertEqual(shares, sorted(shares, reverse=True))
        self.assertAlmostEqual(shares[0], 0.5833, places=4)

    def test_negative_margin_when_fde_cost_exceeds_revenue(self):
        self.assertLess(DealYear(1, 200_000, 40_000, 350_000).gross_margin, 0)


if __name__ == "__main__":
    unittest.main()
