import unittest
from collections import Counter

from router import AccountState, Lead, Rep, RoundRobinStore, Router


def reps():
    return [
        Rep("ana", {"NA"}, {"mid_market"}, weight=2),
        Rep("ben", {"NA"}, {"mid_market"}, weight=1),
        Rep("cho", {"NA"}, {"enterprise"}),
        Rep("dev", {"EMEA"}, {"mid_market", "enterprise"}),
        Rep("eve", {"NA"}, {"mid_market"}, active=False),          # offboarded
        Rep("am_kim", {"NA", "EMEA"}, {"enterprise"}),
    ]


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.accounts = {
            "cust": AccountState(is_customer=True, account_manager_id="am_kim", owner_id="cho"),
            "opp": AccountState(owner_id="ben", open_opportunity_owner_id="cho"),
            "owned": AccountState(owner_id="ben"),
            "orphan": AccountState(owner_id="eve"),                  # owner deactivated
        }
        self.store = RoundRobinStore()
        self.router = Router(reps(), self.accounts, self.store)

    def lead(self, **kw):
        base = dict(email="x@acme.com", country="US", employees=300)
        base.update(kw)
        return Lead(**base)

    def test_disqualifiers(self):
        self.assertEqual(self.router.route(self.lead(is_spam=True)).queue, "discard")
        self.assertEqual(self.router.route(self.lead(is_competitor=True)).reason, "competitor")
        self.assertEqual(self.router.route(self.lead(free_email=True)).queue, "nurture")

    def test_customer_first(self):
        d = self.router.route(self.lead(account_id="cust"))
        self.assertEqual((d.assignee, d.reason), ("am_kim", "existing customer -> account manager"))

    def test_open_opportunity_owner_beats_account_owner(self):
        self.assertEqual(self.router.route(self.lead(account_id="opp")).assignee, "cho")

    def test_account_owner(self):
        self.assertEqual(self.router.route(self.lead(account_id="owned")).assignee, "ben")

    def test_inactive_owner_falls_through_to_round_robin(self):
        d = self.router.route(self.lead(account_id="orphan"))
        self.assertIn(d.assignee, {"ana", "ben"})
        self.assertIn("previous owner eve inactive", d.reason)

    def test_weighted_round_robin_and_never_inactive(self):
        counts = Counter(self.router.route(self.lead()).assignee for _ in range(30))
        self.assertEqual(counts, Counter({"ana": 20, "ben": 10}))     # weight 2:1, eve never

    def test_out_of_office_and_caps_are_skipped(self):
        self.router.reps["ana"].out_of_office = True
        self.router.reps["ben"].daily_cap = 2
        got = [self.router.route(self.lead()).assignee for _ in range(3)]
        self.assertEqual(got[:2], ["ben", "ben"])
        self.assertIsNone(got[2])

    def test_fallback_queue_when_nobody_available(self):
        d = self.router.route(self.lead(country="BR"))
        self.assertEqual(d.queue, "fallback")

    def test_unknown_employee_count_goes_to_mid_market_pool(self):
        self.assertIn(self.router.route(self.lead(employees=None)).assignee, {"ana", "ben"})

    def test_pointer_is_durable_across_router_instances(self):
        first = self.router.route(self.lead()).assignee
        restarted = Router(reps(), self.accounts, self.store)       # same store, new process
        second = restarted.route(self.lead()).assignee
        fresh = Router(reps(), self.accounts, RoundRobinStore()).route(self.lead()).assignee
        self.assertEqual(first, fresh)        # same starting slot
        self.assertEqual((first, second), ("ana", "ana"))  # weight 2 -> ana twice, then ben
        third = restarted.route(self.lead()).assignee
        self.assertEqual(third, "ben")


if __name__ == "__main__":
    unittest.main()
