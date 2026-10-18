import math
import unittest

from detector import (PhiAccrual, heartbeat_arrivals, phi_detector, sweep, tail_z,
                      timeout_detector)


class StreamTests(unittest.TestCase):
    def test_stream_is_deterministic_and_stops_at_crash(self):
        a = heartbeat_arrivals(seed=3, crash_at=10_000)
        self.assertEqual(a, heartbeat_arrivals(seed=3, crash_at=10_000))
        self.assertEqual(a, sorted(a))
        calm = heartbeat_arrivals(seed=3, crash_at=10_000, loss=0, p_pause=0)
        self.assertEqual(len(calm), 100)


class TimeoutTests(unittest.TestCase):
    def test_tradeoff_is_monotone(self):
        # Property over seeds: longer timeouts never add false positives and never detect sooner.
        for seed in range(10):
            arr = heartbeat_arrivals(seed=seed, crash_at=120_000)
            results = [timeout_detector(arr, 120_000, t) for t in (120, 200, 400, 800, 1600)]
            fps = [r.false_positives for r in results]
            dets = [r.detection_ms for r in results]
            self.assertEqual(fps, sorted(fps, reverse=True))
            self.assertEqual(dets, sorted(dets))

    def test_detection_time_is_about_timeout(self):
        arr = heartbeat_arrivals(seed=1, crash_at=60_000, loss=0, p_pause=0)
        r = timeout_detector(arr, 60_000, 500)
        self.assertGreater(r.detection_ms, 500 - 100)    # last beat was sent < 100 ms before the crash
        self.assertLess(r.detection_ms, 500)


class PhiTests(unittest.TestCase):
    def setUp(self):
        self.fd = PhiAccrual()
        for a in heartbeat_arrivals(seed=1, crash_at=60_000, p_pause=0):
            self.fd.heartbeat(a)

    def test_phi_rises_with_silence(self):
        values = [self.fd.phi(self.fd.last + dt) for dt in range(0, 1000, 25)]
        self.assertEqual(values, sorted(values))
        mean, _ = self.fd.stats()
        self.assertAlmostEqual(self.fd.phi(self.fd.last + mean), -math.log10(0.5), places=6)

    def test_suspect_after_inverts_phi(self):
        for threshold in (1, 3, 8, 12):
            t = self.fd.suspect_after(threshold)
            self.assertAlmostEqual(self.fd.phi(self.fd.last + t), threshold, places=4)
        self.assertAlmostEqual(tail_z(-math.log10(0.5)), 0.0, places=6)

    def test_running_stats_match_window(self):
        fd = PhiAccrual(window=5, min_std=0)
        for t in (0, 100, 210, 300, 420, 500, 650, 700):
            fd.heartbeat(t)
        mean, std = fd.stats()
        window = [90, 120, 80, 150, 50]
        self.assertAlmostEqual(mean, sum(window) / 5)
        self.assertAlmostEqual(std, math.sqrt(sum((x - mean) ** 2 for x in window) / 5))

    def test_phi_adapts_where_a_fixed_timeout_floods(self):
        [(_, timeout_fp, _)] = sweep(timeout_detector, (250,), seeds=range(4), jitter=80, p_pause=0)
        [(_, phi_fp, _)] = sweep(phi_detector, (12,), seeds=range(4), jitter=80, p_pause=0)
        self.assertGreater(timeout_fp, 100 * max(phi_fp, 1))


if __name__ == "__main__":
    unittest.main()
