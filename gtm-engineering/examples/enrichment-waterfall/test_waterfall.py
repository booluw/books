import unittest

from waterfall import FakeProvider, Waterfall, fake_verifier

KEY = ("jane", "doe", "acme.com")


class WaterfallTests(unittest.TestCase):
    def make(self, a=None, b=None, c=None, verdicts=None, **kw):
        self.a = FakeProvider("a", 0.05, a or {})
        self.b = FakeProvider("b", 0.08, b or {})
        self.c = FakeProvider("c", 0.15, c or {})
        return Waterfall([self.a, self.b, self.c], verify=fake_verifier(verdicts or {}), **kw)

    def test_stops_at_first_valid_result(self):
        wf = self.make(a={KEY: "jane@acme.com"}, b={KEY: "j@acme.com"}, verdicts={"jane@acme.com": "valid"})
        r = wf.find("Jane", "Doe", "acme.com")
        self.assertEqual((r.status, r.email, r.source), ("found", "jane@acme.com", "a"))
        self.assertEqual(self.b.calls, 0)
        self.assertAlmostEqual(r.cost, 0.054)

    def test_invalid_result_continues_the_waterfall(self):
        wf = self.make(a={KEY: "jdoe@acme.com"}, b={KEY: "jane.doe@acme.com"},
                       verdicts={"jdoe@acme.com": "invalid", "jane.doe@acme.com": "valid"})
        r = wf.find("Jane", "Doe", "acme.com")
        self.assertEqual(r.source, "b")
        self.assertEqual(r.attempts, ["a:invalid", "b:valid"])

    def test_catch_all_rejected_unless_policy_allows(self):
        verdicts = {"jane@acme.com": "catch_all"}
        self.assertEqual(self.make(a={KEY: "jane@acme.com"}, verdicts=verdicts).find("Jane", "Doe", "acme.com").status,
                         "not_found")
        r = self.make(a={KEY: "jane@acme.com"}, verdicts=verdicts, accept_catch_all=True).find("Jane", "Doe", "acme.com")
        self.assertEqual((r.status, r.verification), ("found", "catch_all"))

    def test_domain_mismatch_rejected(self):
        wf = self.make(a={KEY: "jane@gmail.com"}, verdicts={"jane@gmail.com": "valid"})
        r = wf.find("Jane", "Doe", "acme.com")
        self.assertEqual(r.status, "not_found")
        self.assertIn("a:domain_mismatch", r.attempts)

    def test_provider_error_means_retry_later_and_is_not_cached(self):
        wf = self.make(verdicts={})
        self.a.fail = True
        r = wf.find("Jane", "Doe", "acme.com")
        self.assertEqual(r.status, "retry_later")
        self.assertEqual(wf.cache, {})

    def test_results_are_cached_by_normalised_key(self):
        wf = self.make(a={KEY: "jane@acme.com"}, verdicts={"jane@acme.com": "valid"})
        wf.find("Jane", "Doe", "acme.com")
        spent = wf.spent
        wf.find(" JANE ", "doe", "ACME.com")
        self.assertEqual(wf.spent, spent)
        self.assertEqual(self.a.calls, 1)

    def test_not_found_is_cached_but_expires(self):
        now = [1_000_000.0]
        wf = self.make(clock=lambda: now[0], freshness_seconds=100)
        wf.find("Jane", "Doe", "acme.com")
        wf.find("Jane", "Doe", "acme.com")
        self.assertEqual(self.a.calls, 1)
        now[0] += 101
        wf.find("Jane", "Doe", "acme.com")
        self.assertEqual(self.a.calls, 2)

    def test_budget_cap(self):
        wf = self.make(budget=0.06)
        r = wf.find("Jane", "Doe", "acme.com")
        self.assertEqual(r.status, "skipped_budget")
        self.assertLessEqual(wf.spent, 0.06)


if __name__ == "__main__":
    unittest.main()
