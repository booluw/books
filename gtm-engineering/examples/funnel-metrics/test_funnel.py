import unittest

from funnel import (ReverseFunnel, cac, cac_payback_months, conversion, cost_per_meeting, ltv, nrr,
                    pipeline_coverage, pipeline_velocity, sample_size_per_arm, two_proportion_test)


class FunnelTests(unittest.TestCase):
    def test_reverse_funnel_matches_chapter_3_worked_example(self):
        plan = ReverseFunnel(3_000_000, 30_000, 0.25, 0.5, 0.5, 0.01).plan()
        self.assertEqual(plan["customers"], 100)
        self.assertEqual(plan["opportunities"], 400)
        self.assertEqual(plan["meetings"], 800)
        self.assertEqual(plan["meetings_per_month"], 66.7)
        self.assertEqual(plan["delivered_emails"], 160_000)
        self.assertEqual(plan["delivered_per_month"], 13_334)

    def test_doubling_relevance_halves_volume(self):
        base = ReverseFunnel(3_000_000, 30_000, 0.25, 0.5, 0.5, 0.01).plan()["delivered_emails"]
        better = ReverseFunnel(3_000_000, 30_000, 0.25, 0.5, 0.5, 0.02).plan()["delivered_emails"]
        self.assertEqual(better * 2, base)

    def test_unit_economics(self):
        self.assertEqual(conversion(0, 0), 0.0)
        self.assertAlmostEqual(pipeline_velocity(40, 30_000, 0.25, 90), 3333.33, places=2)
        c = cac(600_000, 40)
        self.assertEqual(c, 15_000)
        self.assertAlmostEqual(cac_payback_months(c, 2_500, 0.8), 7.5)
        self.assertAlmostEqual(ltv(2_500, 0.8, 0.01), 200_000)
        self.assertAlmostEqual(nrr(1_000_000, 250_000, 50_000, 80_000), 1.12)
        self.assertAlmostEqual(pipeline_coverage(9_000_000, 3_000_000), 3.0)

    def test_cost_per_meeting_matches_chapter_17(self):
        costs = {"enrichment": 240, "ai": 60, "infra": 150, "seats": 200, "qa": 360}
        self.assertAlmostEqual(cost_per_meeting(costs, 18), 56.11, places=2)

    def test_sample_size_matches_chapter_15(self):
        n = sample_size_per_arm(0.02, 0.03)
        self.assertTrue(3_700 <= n <= 3_900, n)

    def test_two_proportion_test(self):
        z, p = two_proportion_test(40, 2000, 70, 2000)
        self.assertGreater(z, 0)
        self.assertLess(p, 0.01)
        _, p_null = two_proportion_test(40, 2000, 42, 2000)
        self.assertGreater(p_null, 0.5)


if __name__ == "__main__":
    unittest.main()
