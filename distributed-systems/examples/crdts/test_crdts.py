import random
import unittest

from crdts import (GCounter, LWWRegister, NaiveCounter, ORSet, PNCounter, converges,
                   deliver_in_random_order, merge_all, random_run)

TYPES = (GCounter, PNCounter, LWWRegister, ORSet)
RUNS = 150


def state_pool(cls, seed):
    """Many related states of one type from a random run."""
    return random_run(cls, random.Random(seed), n_replicas=3, steps=25)


class SemilatticeLaws(unittest.TestCase):
    """merge must be commutative, associative and idempotent, for all states."""

    def check(self, law):
        for cls in TYPES:
            for seed in range(RUNS):
                rng = random.Random(seed)
                pool = state_pool(cls, seed)
                a, b, c = (rng.choice(pool) for _ in range(3))
                law(cls, a, b, c)

    def test_commutative(self):
        def law(cls, a, b, c):
            self.assertEqual(a.merge(b).state(), b.merge(a).state(), cls.__name__)
        self.check(law)

    def test_associative(self):
        def law(cls, a, b, c):
            self.assertEqual(a.merge(b).merge(c).state(), a.merge(b.merge(c)).state(), cls.__name__)
        self.check(law)

    def test_idempotent_and_absorbing(self):
        def law(cls, a, b, c):
            self.assertEqual(a.merge(a).state(), a.state(), cls.__name__)
            ab = a.merge(b)
            self.assertEqual(ab.merge(b).state(), ab.state(), cls.__name__)   # re-delivery is harmless
        self.check(law)

    def test_merge_does_not_mutate_its_inputs(self):
        for cls in TYPES:
            pool = state_pool(cls, 1)
            a, b = pool[3], pool[-1]
            before = (a.state(), b.state())
            a.merge(b)
            self.assertEqual((a.state(), b.state()), before)


class Convergence(unittest.TestCase):
    def test_any_order_with_duplicates_converges(self):
        rng = random.Random(7)
        for cls in TYPES:
            for _ in range(RUNS):
                self.assertTrue(converges(random_run(cls, rng), rng), cls.__name__)

    def test_counters_count_every_increment_exactly_once(self):
        # Property: after all states meet, the value equals the true total of all operations.
        for seed in range(RUNS):
            rng = random.Random(seed)
            replicas = [PNCounter(f"r{i}") for i in range(4)]
            total = 0
            states = []
            for _ in range(40):
                r = rng.choice(replicas)
                n = rng.randint(1, 5)
                if rng.random() < 0.5:
                    r.increment(n)
                    total += n
                else:
                    r.decrement(n)
                    total -= n
                states.append(r.copy())
                if rng.random() < 0.2:
                    replicas[0] = replicas[0].merge(rng.choice(replicas))
            final = deliver_in_random_order(states, rng, PNCounter("observer"), duplicates=10)
            self.assertEqual(final.value, total)

    def test_naive_counter_loses_updates_or_diverges(self):
        a, b = NaiveCounter("A", "max"), NaiveCounter("B", "max")
        a.increment(5)
        b.increment(5)
        self.assertEqual(a.merge(b).value, 5)                 # 5 increments lost
        s, t = NaiveCounter("A", "sum"), NaiveCounter("B", "sum")
        s.increment(5)
        t.increment(5)
        self.assertEqual(s.merge(t).merge(t).value, 15)        # duplicate double-counted
        self.assertNotEqual(s.merge(s).state(), s.state())     # not idempotent
        rng = random.Random(3)
        self.assertFalse(all(converges(random_run(NaiveCounter, rng, mode="sum"), rng)
                             for _ in range(20)))
        g = merge_all(random_run(GCounter, random.Random(5))).value
        n = merge_all(random_run(NaiveCounter, random.Random(5), mode="max")).value
        self.assertLess(n, g)                                   # same workload, fewer counted


class Semantics(unittest.TestCase):
    def test_gcounter_rejects_decrement(self):
        with self.assertRaises(ValueError):
            GCounter("a").increment(-1)

    def test_lww_highest_stamp_wins_and_ties_break_by_replica(self):
        x, y = LWWRegister("x"), LWWRegister("y")
        x.set("old", 1)
        y.set("new", 2)
        self.assertEqual(x.merge(y).value, "new")
        x.set("tie-x", 5)
        y.set("tie-y", 5)
        self.assertEqual(x.merge(y).value, "tie-y")            # "y" > "x"
        self.assertEqual(y.merge(x).value, "tie-y")

    def test_orset_add_wins_over_concurrent_remove(self):
        a, b = ORSet("a"), ORSet("b")
        a.add("milk")
        b = b.merge(a)
        a.remove("milk")
        b.add("milk")
        self.assertIn("milk", a.merge(b))
        self.assertIn("milk", b.merge(a))

    def test_orset_observed_remove_and_readd(self):
        a = ORSet("a")
        a.add("x")
        a.remove("x")
        self.assertNotIn("x", a)
        a.add("x")
        self.assertIn("x", a)
        b = ORSet("b").merge(a)
        b.remove("x")
        self.assertNotIn("x", a.merge(b))                     # b had observed every tag

    def test_orset_value_matches_sequential_set_when_no_concurrency(self):
        # Property: on a single replica, an OR-Set behaves exactly like a Python set.
        for seed in range(RUNS):
            rng = random.Random(seed)
            s, model = ORSet("solo"), set()
            for _ in range(30):
                e = rng.choice("abcd")
                if rng.random() < 0.6:
                    s.add(e)
                    model.add(e)
                else:
                    s.remove(e)
                    model.discard(e)
            self.assertEqual(s.value, frozenset(model))


if __name__ == "__main__":
    unittest.main()
