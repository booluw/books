import unittest

from matching import (Account, find_duplicate_accounts, is_free_email_domain, match_lead_to_account,
                      name_similarity, normalise_company_name, registrable_domain, ultimate_parent)


class DomainTests(unittest.TestCase):
    def test_registrable_domain(self):
        cases = {
            "https://www.Acme-Logistics.com/about": "acme-logistics.com",
            "ACME-LOGISTICS.COM.": "acme-logistics.com",
            "jane@eu.acme-logistics.com": "acme-logistics.com",
            "shop.acme.co.uk": "acme.co.uk",
            "acme.co.uk": "acme.co.uk",
            "http://acme.com:8080/x": "acme.com",
            "localhost": None,
            "": None,
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(registrable_domain(value), expected)

    def test_free_email(self):
        self.assertTrue(is_free_email_domain(registrable_domain("someone@gmail.com")))
        self.assertFalse(is_free_email_domain("acme.com"))


class NameTests(unittest.TestCase):
    def test_normalise(self):
        self.assertEqual(normalise_company_name("ACME Logistics, GmbH & Co. KG"), "acme logistics")
        self.assertEqual(normalise_company_name("Café Nordïc Ltd."), "cafe nordic")

    def test_similarity(self):
        self.assertGreater(name_similarity("Acme Logistics Inc.", "ACME LOGISTICS LLC"), 0.99)
        self.assertLess(name_similarity("Acme Logistics", "Apex Foods"), 0.6)


class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.parent = Account("001", "Acme Group", "acme-group.com", owner="ae_kim", is_customer=True)
        self.sub = Account("002", "Acme Logistics GmbH", "acme-logistics.de",
                           extra_domains=["acme-logistics.com"], parent_id="001", owner="ae_lee")
        self.dup_unowned = Account("003", "Acme Logistics", "acme-logistics.de")
        self.other = Account("004", "Apex Foods", "apexfoods.com")
        self.accounts = [self.parent, self.sub, self.dup_unowned, self.other]

    def test_exact_domain_with_duplicate_tie_break(self):
        m = match_lead_to_account("jane@eu.acme-logistics.de", "Acme", self.accounts)
        self.assertEqual((m.account.id, m.method), ("002", "domain"))   # owned record wins
        self.assertEqual(m.duplicates, ["003"])

    def test_extra_domain(self):
        m = match_lead_to_account("jane@acme-logistics.com", "", self.accounts)
        self.assertEqual((m.account.id, m.method), ("002", "extra_domain"))

    def test_free_email_falls_back_to_fuzzy_name(self):
        m = match_lead_to_account("jane.doe@gmail.com", "ACME Logistics LLC", self.accounts)
        self.assertEqual(m.method, "fuzzy_name")
        self.assertIn(m.account.id, {"002", "003"})
        self.assertFalse(m.needs_review)

    def test_borderline_fuzzy_match_needs_review(self):
        m = match_lead_to_account(None, "Apex Fresh Foods", self.accounts)
        self.assertEqual(m.account.id, "004")
        self.assertTrue(m.needs_review)

    def test_no_match(self):
        self.assertEqual(match_lead_to_account("x@unknown.io", "Zebra Robotics", self.accounts).method, "none")

    def test_ultimate_parent_for_routing(self):
        by_id = {a.id: a for a in self.accounts}
        self.assertEqual(ultimate_parent(self.sub, by_id).owner, "ae_kim")

    def test_find_duplicates(self):
        pairs = find_duplicate_accounts(self.accounts)
        self.assertIn(("002", "003", "same domain acme-logistics.de"), pairs)
        self.assertFalse(any({"001", "004"} == {p[0], p[1]} for p in pairs))


if __name__ == "__main__":
    unittest.main()
