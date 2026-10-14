import unittest

from icp_scoring import MODEL_VERSION, score_account


class IcpScoringTests(unittest.TestCase):
    def test_perfect_fit_is_tier_1_with_reasons(self):
        s = score_account({"domain": "Acme-Logistics.com", "industry": "Third-Party Logistics",
                           "employees": "640", "country": "us", "tech": "LegacyTMS;Salesforce",
                           "open_ops_roles": "3"})
        self.assertEqual(s.points, 100)
        self.assertEqual(s.tier, "Tier 1")
        self.assertEqual(s.domain, "acme-logistics.com")
        self.assertEqual(len(s.reasons), 5)
        self.assertEqual(s.model_version, MODEL_VERSION)

    def test_adjacent_band_scores_lower(self):
        s = score_account({"domain": "x.ca", "industry": "freight forwarding", "employees": "150",
                           "country": "CA"})
        self.assertEqual(s.points, 55)
        self.assertEqual(s.tier, "Tier 2")

    def test_unknown_employee_count_is_explained_not_guessed(self):
        s = score_account({"domain": "tinyhaul.io", "industry": "third-party logistics",
                           "employees": "", "country": "US"})
        self.assertIn("+0 employee count unknown", s.reasons)
        self.assertEqual(s.points, 45)
        self.assertEqual(s.tier, "Tier 3")

    def test_disqualifiers_override_points(self):
        perfect = {"domain": "acme-logistics.com", "industry": "third-party logistics",
                   "employees": "640", "country": "US", "tech": "legacytms", "open_ops_roles": "3"}
        self.assertEqual(score_account(perfect, customers={"acme-logistics.com"}).tier, "Excluded")
        self.assertEqual(score_account(perfect, competitors={"acme-logistics.com"}).disqualified_reason,
                         "competitor")

    def test_missing_domain_excluded(self):
        self.assertEqual(score_account({"industry": "third-party logistics"}).tier, "Excluded")

    def test_non_icp(self):
        self.assertEqual(score_account({"domain": "bigbox-retail.com", "industry": "retail",
                                        "employees": "12000", "country": "US"}).tier, "Not ICP")


if __name__ == "__main__":
    unittest.main()
