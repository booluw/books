"""Tests for the resilience components and the retry-storm simulation."""

import unittest

from components import (CLOSED, HALF_OPEN, OPEN, CircuitBreaker, RetryBudget,
                        TokenBucket, backoff_delays)
from herd import thundering_herd
from simulation import BY_NAME, Config, simulate


class BackoffTests(unittest.TestCase):
    def test_exponential_doubles_until_cap(self):
        self.assertEqual(backoff_delays(5, "exponential", base=0.1, cap=1.0),
                         [0.1, 0.2, 0.4, 0.8, 1.0])

    def test_full_jitter_stays_within_exponential_envelope(self):
        envelope = backoff_delays(8, "exponential", base=0.1, cap=2.0)
        for seed in range(50):
            jittered = backoff_delays(8, "full_jitter", base=0.1, cap=2.0, seed=seed)
            for d, top in zip(jittered, envelope):
                self.assertGreaterEqual(d, 0.0)
                self.assertLessEqual(d, top)

    def test_jitter_is_seeded_and_reproducible(self):
        self.assertEqual(backoff_delays(6, "full_jitter", seed=42),
                         backoff_delays(6, "full_jitter", seed=42))
        self.assertNotEqual(backoff_delays(6, "full_jitter", seed=42),
                            backoff_delays(6, "full_jitter", seed=43))

    def test_unknown_policy_rejected(self):
        with self.assertRaises(ValueError):
            backoff_delays(3, "fibonacci")


class TokenBucketTests(unittest.TestCase):
    def test_refills_over_time_up_to_capacity(self):
        bucket = TokenBucket(rate=2.0, capacity=5.0, now=0.0, initial=0.0)
        self.assertFalse(bucket.try_acquire(0.0))
        self.assertTrue(bucket.try_acquire(0.5))       # 1 token after 0.5 s
        self.assertAlmostEqual(bucket.available(100.0), 5.0)

    def test_retry_budget_caps_retries_at_ratio_of_requests(self):
        budget = RetryBudget(ratio=0.1, min_per_second=0.0, capacity=10.0)
        budget.bucket.tokens = 0.0
        retries = 0
        for i in range(1000):                          # 1000 requests, all at t=0
            budget.on_request(0.0)
            retries += budget.can_retry(0.0)
        self.assertIn(retries, (99, 100))              # 10%, give or take rounding


class CircuitBreakerTests(unittest.TestCase):
    def test_full_cycle_closed_open_half_open_closed(self):
        cb = CircuitBreaker(failure_threshold=0.5, window=10, min_calls=4,
                            open_seconds=1.0, half_open_probes=2)
        for t in range(4):
            self.assertTrue(cb.allow(t * 0.1))
            cb.record_failure(t * 0.1)
        self.assertEqual(cb.state, OPEN)
        self.assertFalse(cb.allow(0.5))                # still cooling down
        self.assertTrue(cb.allow(1.4))                 # cool-down over: probe 1
        self.assertEqual(cb.state, HALF_OPEN)
        self.assertTrue(cb.allow(1.4))                 # probe 2
        self.assertFalse(cb.allow(1.4))                # no more probes allowed
        cb.record_success(1.5)
        cb.record_success(1.5)
        self.assertEqual(cb.state, CLOSED)

    def test_failed_probe_reopens(self):
        cb = CircuitBreaker(min_calls=2, window=2, open_seconds=1.0)
        cb.record_failure(0.0)
        cb.record_failure(0.0)
        self.assertTrue(cb.allow(2.0))
        cb.record_failure(2.1)
        self.assertEqual(cb.state, OPEN)
        self.assertFalse(cb.allow(2.5))


class HerdTests(unittest.TestCase):
    def test_jitter_needs_far_less_work_than_plain_exponential(self):
        plain = thundering_herd("exponential")
        jitter = thundering_herd("full_jitter")
        self.assertLess(jitter.calls, plain.calls * 0.6)
        self.assertLess(jitter.completion, plain.completion)


class SimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = Config()
        cls.results = {name: simulate(s, cls.cfg, seed=1) for name, s in BY_NAME.items()}

    def test_same_seed_same_result(self):
        again = simulate(BY_NAME["naive retries"], self.cfg, seed=1)
        self.assertEqual(again, self.results["naive retries"])

    def test_naive_retries_are_metastable(self):
        naive = self.results["naive retries"]
        self.assertIsNone(naive.recovery)              # never recovers ...
        self.assertLess(naive.goodput_after, 5)        # ... although load is back to 70%
        self.assertGreater(naive.amplification, 3)

    def test_without_spike_naive_retries_are_fine(self):
        calm = Config(spike_rate=Config().base_rate)
        r = simulate(BY_NAME["naive retries"], calm, seed=1)
        self.assertGreater(r.goodput_after, 0.97 * calm.base_rate)
        self.assertLess(r.amplification, 1.05)

    def test_outcome_ordering(self):
        good = {k: v.goodput_after for k, v in self.results.items()}
        self.assertLess(good["naive retries"], good["jitter + retry budget"])
        self.assertLess(good["jitter + retry budget"], good["budget+jitter+shed+deadline"])
        self.assertLess(good["no retries"], good["budget+jitter+shed+deadline"])

    def test_combined_strategy_recovers_quickly_with_low_latency(self):
        best = self.results["budget+jitter+shed+deadline"]
        self.assertIsNotNone(best.recovery)
        self.assertLessEqual(best.recovery, 2)
        self.assertGreater(best.goodput_after, 0.95 * self.cfg.base_rate)
        self.assertLess(best.p99, self.cfg.attempt_timeout)
        self.assertLessEqual(best.max_queue_seen, self.cfg.max_queue)

    def test_ordering_holds_across_seeds(self):
        for seed in (2, 3, 4):
            naive = simulate(BY_NAME["naive retries"], self.cfg, seed)
            best = simulate(BY_NAME["budget+jitter+shed+deadline"], self.cfg, seed)
            self.assertLess(naive.goodput_after * 5, best.goodput_after)


if __name__ == "__main__":
    unittest.main()
