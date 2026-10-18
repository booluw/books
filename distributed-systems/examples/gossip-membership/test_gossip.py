import math
import unittest

from gossip import MODES, gossip_membership, mean_rounds, rounds_to_spread, spread


class RumourTests(unittest.TestCase):
    def test_every_mode_reaches_everyone_and_never_forgets(self):
        # Property over many seeds: counts start at 1, never fall, end at n.
        for mode in MODES:
            for seed in range(40):
                h = spread(200, mode, loss=0.2, seed=seed)
                self.assertEqual(h[0], 1)
                self.assertEqual(h[-1], 200)
                self.assertEqual(h, sorted(h))

    def test_push_at_most_doubles_each_round(self):
        # Each informed node pushes to one peer, so round k informs at most 2**k.
        for seed in range(40):
            for k, count in enumerate(spread(500, "push", seed=seed)):
                self.assertLessEqual(count, 2 ** k)

    def test_rounds_grow_logarithmically(self):
        # 16x more nodes should cost only a few more rounds, close to log2(16) = 4.
        for mode in MODES:
            small, large = mean_rounds(256, mode, trials=15), mean_rounds(4096, mode, trials=15)
            self.assertGreater(large, small)
            self.assertLess(large - small, 2 * math.log2(16))
            self.assertLess(large, 2.5 * math.log2(4096))

    def test_push_pull_is_fastest(self):
        pp = mean_rounds(1024, "push-pull", trials=15)
        self.assertLess(pp, mean_rounds(1024, "push", trials=15))
        self.assertLess(pp, mean_rounds(1024, "pull", trials=15))
        self.assertLess(pp, math.log2(1024))

    def test_loss_slows_but_does_not_stop_gossip(self):
        clean = mean_rounds(512, "push-pull", trials=15)
        lossy = mean_rounds(512, "push-pull", trials=15, loss=0.5)
        self.assertGreater(lossy, clean)
        self.assertLess(lossy, 3 * clean)

    def test_total_loss_spreads_nothing_and_bad_mode_rejected(self):
        self.assertEqual(spread(10, "push", loss=1.0, max_rounds=5), [1] * 6)
        with self.assertRaises(RuntimeError):
            rounds_to_spread(10, "push", loss=1.0)
        with self.assertRaises(ValueError):
            spread(10, "shout")


class MembershipTests(unittest.TestCase):
    def test_no_loss_detection_takes_exactly_t_fail_for_the_first_node(self):
        for seed in range(10):
            for t_fail in (5, 10, 15):
                r = gossip_membership(16, t_fail, seed=seed)
                self.assertEqual(r.first_detected, t_fail)
                self.assertGreaterEqual(r.all_detected, t_fail)

    def test_longer_timeout_trades_speed_for_accuracy(self):
        def avg(t_fail, field):
            rs = [gossip_membership(24, t_fail, loss=0.1, seed=s) for s in range(6)]
            return sum(getattr(r, field) for r in rs) / len(rs)
        false = [avg(t, "false_rate") for t in (4, 8, 14)]
        detect = [avg(t, "all_detected") for t in (4, 8, 14)]
        self.assertEqual(false, sorted(false, reverse=True))
        self.assertEqual(detect, sorted(detect))
        self.assertGreater(false[0], 0.01)
        self.assertLess(false[-1], 0.001)


if __name__ == "__main__":
    unittest.main()
