import itertools
import random
import unittest

from quorum import NO_VERSION, QuorumStore, Replica, quorums_intersect, run_trial


class IntersectionTests(unittest.TestCase):
    def test_brute_force_matches_r_plus_w_greater_than_n(self):
        # The formal property: quorums always intersect iff R + W > N.
        for n in range(1, 8):
            for r in range(1, n + 1):
                for w in range(1, n + 1):
                    self.assertEqual(quorums_intersect(n, r, w), r + w > n, (n, r, w))

    def test_majority_quorums_pairwise_intersect(self):
        # Two write quorums intersect iff 2W > N, so writes cannot both "win" unseen.
        for n in range(1, 8):
            for w in range(1, n + 1):
                self.assertEqual(quorums_intersect(n, w, w), 2 * w > n, (n, w))
            self.assertTrue(quorums_intersect(n, n // 2 + 1, n // 2 + 1))   # majorities


class ReplicaTests(unittest.TestCase):
    def test_apply_never_goes_backwards(self):
        rep = Replica(0)
        self.assertTrue(rep.apply("k", (5, "a"), "five"))
        self.assertFalse(rep.apply("k", (3, "a"), "three"))
        self.assertFalse(rep.apply("k", (5, "a"), "five again"))   # duplicate
        self.assertTrue(rep.apply("k", (5, "b"), "tie broken by writer id"))
        self.assertEqual(rep.get("k")[1], "tie broken by writer id")
        self.assertEqual(Replica(1).get("missing"), (NO_VERSION, None))

    def test_late_deliveries_in_any_order_converge(self):
        # Property: whatever order versions arrive in, a replica ends with the max.
        rng = random.Random(0)
        for _ in range(200):
            versions = [(rng.randrange(20), rng.choice("abc")) for _ in range(10)]
            rep = Replica(0)
            for v in rng.sample(versions, len(versions)) + versions[:3]:
                rep.apply("k", v, v)
            self.assertEqual(rep.get("k")[0], max(versions))


class StoreTests(unittest.TestCase):
    def test_invalid_quorums_rejected(self):
        with self.assertRaises(ValueError):
            QuorumStore(3, 0, 2)
        with self.assertRaises(ValueError):
            QuorumStore(3, 2, 4)

    def test_write_fails_without_w_replicas_up(self):
        s = QuorumStore(3, 2, 2, seed=1)
        s.set_up(0, False)
        s.set_up(1, False)
        self.assertIsNone(s.write("x", 1))
        self.assertIsNone(s.read("x"))
        s.set_up(1, True)
        self.assertIsNotNone(s.write("x", 2))

    def test_r1_w1_can_read_stale(self):
        s = QuorumStore(3, 1, 1, seed=4, max_delay=10, read_repair=False)
        v = s.write("x", "new")
        results = [s.read("x") for _ in range(3)]
        self.assertTrue(any(res.version < v for res in results))

    def test_read_repair_fixes_contacted_replicas(self):
        s = QuorumStore(3, 3, 1, seed=2, max_delay=100)
        v = s.write("x", "new")
        res = s.read("x")
        self.assertEqual(res.version, v)
        self.assertEqual(len(res.repaired), 2)
        self.assertTrue(all(rep.get("x")[0] == v for rep in s.replicas))

    def test_eventual_delivery_without_failures(self):
        s = QuorumStore(5, 1, 1, seed=3, max_delay=4)
        v = s.write("x", "v")
        for _ in range(4):
            s.tick()
        self.assertTrue(all(rep.get("x")[0] == v for rep in s.replicas))


class StalenessProperties(unittest.TestCase):
    def test_overlapping_quorums_never_read_stale(self):
        # Property over many random runs with crashes and late delivery.
        for n in (3, 4, 5):
            for r, w in itertools.product(range(1, n + 1), repeat=2):
                if r + w <= n:
                    continue
                for seed in range(15):
                    for repair in (False, True):
                        st = run_trial(n, r, w, seed, ops=120, read_repair=repair)
                        self.assertEqual(st.stale, 0, (n, r, w, seed, repair))

    def test_non_overlapping_quorums_do_read_stale(self):
        for n in (3, 5):
            for r, w in itertools.product(range(1, n + 1), repeat=2):
                if r + w > n:
                    continue
                stale = sum(run_trial(n, r, w, seed, ops=120).stale for seed in range(30))
                self.assertGreater(stale, 0, (n, r, w))

    def test_trials_are_deterministic(self):
        self.assertEqual(run_trial(3, 1, 1, seed=9), run_trial(3, 1, 1, seed=9))


if __name__ == "__main__":
    unittest.main()
