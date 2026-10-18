import random
import statistics
import unittest

from hashring import (HashRing, ModNHashing, RendezvousHashing, assignment, fraction_moved,
                      load_imbalance, make_keys, movement_on_add, stable_hash)

KEYS = make_keys(5000)


def nodes(n, prefix="node"):
    return [f"{prefix}-{i}" for i in range(n)]


class StableHashTests(unittest.TestCase):
    def test_hash_is_fixed_across_runs(self):
        # sha256-based, so this value never changes (unlike Python's hash()).
        self.assertEqual(stable_hash("hello"), 0x2CF24DBA5FB0A30E)

    def test_empty_schemes_raise(self):
        for scheme in (HashRing(), ModNHashing(), RendezvousHashing()):
            with self.assertRaises(LookupError):
                scheme.lookup("k")


class MovementTests(unittest.TestCase):
    def test_added_node_only_steals_keys(self):
        # Property: on add, every key that moves, moves to the new node.
        rng = random.Random(1)
        for trial in range(20):
            n = rng.randint(2, 15)
            for scheme in (HashRing(nodes(n, f"t{trial}"), vnodes=rng.choice([1, 20, 100])),
                           RendezvousHashing(nodes(n, f"t{trial}"))):
                before = assignment(scheme, KEYS[:1000])
                scheme.add_node("newcomer")
                after = assignment(scheme, KEYS[:1000])
                for k in before:
                    if before[k] != after[k]:
                        self.assertEqual(after[k], "newcomer")

    def test_removed_node_only_loses_its_own_keys(self):
        rng = random.Random(2)
        for trial in range(20):
            names = nodes(rng.randint(3, 15), f"r{trial}")
            victim = rng.choice(names)
            for scheme in (HashRing(names, vnodes=50), RendezvousHashing(names)):
                before = assignment(scheme, KEYS[:1000])
                scheme.remove_node(victim)
                after = assignment(scheme, KEYS[:1000])
                for k in before:
                    self.assertEqual(before[k] != after[k], before[k] == victim)

    def test_ring_moves_about_one_over_n(self):
        for n in (5, 10, 20):
            moved = movement_on_add(lambda ns: HashRing(ns, vnodes=100), n, KEYS)
            self.assertGreater(moved, 0.5 / (n + 1))
            self.assertLess(moved, 1.5 / (n + 1))

    def test_rendezvous_moves_about_one_over_n(self):
        for n in (5, 10, 20):
            moved = movement_on_add(RendezvousHashing, n, KEYS)
            self.assertAlmostEqual(moved, 1 / (n + 1), delta=0.3 / (n + 1))

    def test_mod_n_moves_most_keys(self):
        # Expected fraction moved from N to N+1 is N/(N+1).
        for n in (5, 10, 20):
            moved = movement_on_add(ModNHashing, n, KEYS)
            self.assertAlmostEqual(moved, n / (n + 1), delta=0.03)

    def test_remove_then_readd_restores_placement(self):
        ring = HashRing(nodes(8), vnodes=64)
        before = assignment(ring, KEYS)
        ring.remove_node("node-5")
        ring.add_node("node-5")
        self.assertEqual(before, assignment(ring, KEYS))
        with self.assertRaises(ValueError):
            ring.add_node("node-5")


class BalanceTests(unittest.TestCase):
    def test_ownership_sums_to_one(self):
        ring = HashRing(nodes(7), vnodes=13)
        self.assertAlmostEqual(sum(ring.ownership().values()), 1.0, places=9)

    def test_more_vnodes_means_better_balance(self):
        # Averaged over 20 random clusters of 10 nodes, using exact ring shares.
        means = {}
        for v in (1, 10, 100, 1000):
            means[v] = statistics.mean(
                max(HashRing(nodes(10, f"c{s}"), vnodes=v).ownership().values()) * 10
                for s in range(20))
        self.assertGreater(means[1], means[10])
        self.assertGreater(means[10], means[100])
        self.assertGreater(means[100], means[1000])
        self.assertGreater(means[1], 2.0)       # one point per node is badly skewed
        self.assertLess(means[100], 1.3)
        self.assertLess(means[1000], 1.1)

    def test_rendezvous_and_mod_n_balance_well(self):
        keys = make_keys(20_000)
        self.assertLess(load_imbalance(RendezvousHashing(nodes(10)), keys), 1.1)
        self.assertLess(load_imbalance(ModNHashing(nodes(10)), keys), 1.1)

    def test_fraction_moved_helper(self):
        self.assertEqual(fraction_moved({"a": "x", "b": "y"}, {"a": "x", "b": "z"}), 0.5)


if __name__ == "__main__":
    unittest.main()
