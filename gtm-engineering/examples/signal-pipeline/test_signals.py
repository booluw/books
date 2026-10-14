import unittest
from datetime import datetime, timedelta

from signals import COOLDOWN, Signal, SignalPipeline

NOW = datetime(2026, 10, 14, 12, 0)


def sig(t, domain="acme.com", days_ago=0.0, source="x", email=None):
    return Signal(t, domain, NOW - timedelta(days=days_ago), source, email)


class SignalTests(unittest.TestCase):
    def test_decay_halves_at_half_life(self):
        p = SignalPipeline()
        self.assertAlmostEqual(p.decayed(sig("pricing_page_visit", days_ago=7), NOW), 12.5)
        self.assertAlmostEqual(p.decayed(sig("pricing_page_visit", days_ago=14), NOW), 6.25)

    def test_duplicates_from_two_sources_count_once(self):
        p = SignalPipeline()
        self.assertTrue(p.ingest(sig("funding_round", source="crunchbase")))
        self.assertFalse(p.ingest(sig("funding_round", domain="ACME.com", source="news")))
        self.assertEqual(len(p.signals["acme.com"]), 1)

    def test_threshold_action_with_reasons(self):
        p = SignalPipeline()
        for s in [sig("new_exec_hire", days_ago=0), sig("pricing_page_visit", days_ago=0)]:
            p.ingest(s)
        actions = p.evaluate(NOW)
        self.assertEqual(len(actions), 1)
        self.assertEqual((actions[0].kind, actions[0].score), ("threshold", 55.0))
        self.assertEqual(len(actions[0].reasons), 2)

    def test_old_signals_do_not_trigger(self):
        p = SignalPipeline()
        p.ingest(sig("new_exec_hire", days_ago=120))
        p.ingest(sig("pricing_page_visit", days_ago=30))
        self.assertEqual(p.evaluate(NOW), [])

    def test_cooldown_prevents_repeat_actions(self):
        p = SignalPipeline()
        p.ingest(sig("new_exec_hire"))
        p.ingest(sig("pricing_page_visit"))
        self.assertEqual(len(p.evaluate(NOW)), 1)
        p.ingest(sig("pricing_page_visit", days_ago=-1))          # new visit tomorrow
        self.assertEqual(p.evaluate(NOW + timedelta(days=1)), [])
        p.ingest(sig("pricing_page_visit", days_ago=-COOLDOWN.days))
        p.ingest(sig("new_exec_hire", days_ago=-COOLDOWN.days, source="other-feed"))
        self.assertEqual(len(p.evaluate(NOW + COOLDOWN)), 1)

    def test_hand_raiser_bypasses_cooldown(self):
        p = SignalPipeline()
        p.ingest(sig("new_exec_hire"))
        p.ingest(sig("pricing_page_visit"))
        p.evaluate(NOW)
        p.ingest(sig("demo_request", days_ago=-0.01, email="ops@acme.com"))
        actions = p.evaluate(NOW + timedelta(hours=1))
        self.assertEqual(actions[0].kind, "immediate")

    def test_suppressed_accounts_never_actioned(self):
        p = SignalPipeline(suppressed_domains={"acme.com"})
        p.ingest(sig("demo_request", email="a@acme.com"))
        self.assertEqual(p.evaluate(NOW), [])

    def test_unknown_signal_type_rejected(self):
        with self.assertRaises(ValueError):
            SignalPipeline().ingest(sig("horoscope"))


if __name__ == "__main__":
    unittest.main()
