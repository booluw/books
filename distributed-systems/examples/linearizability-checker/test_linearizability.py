import random
import time
import unittest

from checker import (brute_force_linearizable, check_linearizable,
                     check_sequentially_consistent)
from histories import EXAMPLES
from history import PENDING, Op, cas, read, render, step, validate, write
from simulate import SimConfig, generate_history, shrink, survey


def assert_witness(test, history, order, init=0):
    """A witness must contain every completed op, respect real time and be legal."""
    placed = {id(o) for o in order}
    for op in history:
        if not op.pending:
            test.assertIn(id(op), placed, f"{op} missing from witness")
    for a in range(len(order)):
        for b in range(a + 1, len(order)):
            test.assertFalse(order[b].ret < order[a].call,
                             f"{order[b]} returned before {order[a]} began but is ordered after it")
    state = init
    for op in order:
        legal, state = step(state, op)
        test.assertTrue(legal, f"{op} illegal in state {state}")


def random_history(rng, n_ops, values=3):
    """Small random well-formed history: each client runs operations one
    after another, with random gaps and durations and random (often
    impossible) results, so both verdicts are common."""
    ops, free_at = [], {}
    for _ in range(n_ops):
        client = f"C{rng.randrange(3)}"
        if free_at.get(client) == PENDING:
            continue                         # that client crashed mid-operation
        call = free_at.get(client, 0) + 1 + rng.randrange(6)
        ret = PENDING if rng.random() < 0.1 else call + 1 + rng.randrange(8)
        free_at[client] = ret
        kind = rng.choice(["read", "read", "write", "cas"])
        if kind == "read":
            ops.append(read(client, rng.randrange(values), call, ret))
        elif kind == "write":
            ops.append(write(client, rng.randrange(values), call, ret))
        else:
            ops.append(cas(client, rng.randrange(values), rng.randrange(values),
                           rng.random() < 0.5, call, ret))
    return ops


class SpecificationTests(unittest.TestCase):
    def test_register_sequential_specification(self):
        self.assertEqual(step(0, write("A", 5, 0, 1)), (True, 5))
        self.assertEqual(step(5, read("A", 5, 0, 1)), (True, 5))
        self.assertEqual(step(5, read("A", 4, 0, 1)), (False, 5))
        self.assertEqual(step(0, cas("A", 0, 7, True, 0, 1)), (True, 7))
        self.assertEqual(step(3, cas("A", 0, 7, False, 0, 1)), (True, 3))
        self.assertFalse(step(3, cas("A", 0, 7, True, 0, 1))[0])
        self.assertTrue(step(3, read("A", 99, 0))[0])     # pending: result unknown

    def test_validate_rejects_malformed_histories(self):
        with self.assertRaises(ValueError):
            validate([Op("A", "read", None, 0, 5, 4)])            # returns before call
        with self.assertRaises(ValueError):
            validate([write("A", 1, 0, 5), read("A", 1, 3, 6)])   # client not sequential
        with self.assertRaises(ValueError):
            validate([write("A", 1, 0), read("A", 1, 3, 6)])      # op after a pending one


class TextbookHistoryTests(unittest.TestCase):
    def test_every_example_gets_its_expected_verdicts(self):
        for name, ex in EXAMPLES.items():
            with self.subTest(name):
                lin = check_linearizable(ex.ops)
                sc = check_sequentially_consistent(ex.ops)
                self.assertEqual(lin.ok, ex.linearizable)
                self.assertEqual(sc.ok, ex.sequentially_consistent)
                self.assertEqual(lin.ok, brute_force_linearizable(ex.ops))
                if lin.ok:
                    assert_witness(self, ex.ops, lin.order)

    def test_sequentially_consistent_but_not_linearizable_examples_exist(self):
        names = {n for n, ex in EXAMPLES.items()
                 if ex.sequentially_consistent and not ex.linearizable}
        self.assertTrue({"stale-read", "new-old-inversion", "read-from-the-future"} <= names)

    def test_new_old_inversion_prefix_stops_at_the_stale_read(self):
        result = check_linearizable(EXAMPLES["new-old-inversion"].ops)
        self.assertFalse(result.ok)
        # W(1) and B's read fit; C's read of 0 can never be placed after them.
        self.assertEqual([o.label() for o in result.longest_prefix], ["A:W(1)", "B:R()->1"])

    def test_pending_write_witness_includes_it_only_when_needed(self):
        ignored = check_linearizable(EXAMPLES["pending-write-may-be-ignored"].ops)
        self.assertEqual([o.label() for o in ignored.order], ["B:R()->0"])
        needed = check_linearizable([write("A", 1, 0), read("B", 1, 5, 6)])
        self.assertEqual([o.label() for o in needed.order], ["A:W(1)", "B:R()->1"])


class RandomisedTests(unittest.TestCase):
    def test_agrees_with_brute_force_on_random_histories(self):
        verdicts = {True: 0, False: 0}
        for seed in range(400):
            rng = random.Random(seed)
            history = random_history(rng, rng.randint(1, 6))
            result = check_linearizable(history)
            self.assertEqual(result.ok, brute_force_linearizable(history), seed)
            if result.ok:
                assert_witness(self, history, result.order)
            verdicts[result.ok] += 1
        self.assertGreater(min(verdicts.values()), 50)   # both outcomes well exercised

    def test_linearizable_implies_sequentially_consistent(self):
        for seed in range(400):
            rng = random.Random(1000 + seed)
            history = random_history(rng, rng.randint(1, 7))
            if check_linearizable(history).ok:
                self.assertTrue(check_sequentially_consistent(history).ok, seed)


class SimulationTests(unittest.TestCase):
    def test_generation_is_deterministic(self):
        cfg = SimConfig(follower_reads=True)
        self.assertEqual(generate_history(7, cfg), generate_history(7, cfg))

    def test_leader_reads_are_always_linearizable(self):
        for seed in range(150):
            history = generate_history(seed, SimConfig())
            self.assertEqual(len(history), 24)
            result = check_linearizable(history)
            self.assertTrue(result.ok, seed)
            assert_witness(self, history, result.order)

    def test_follower_reads_are_caught_on_some_seeds(self):
        bad, not_sc = survey(range(200), follower_reads=True)
        self.assertEqual(len(bad), 119)
        self.assertEqual(bad[:4], [2, 6, 8, 9])
        self.assertEqual(len(not_sc), 50)

    def test_shrinking_gives_a_small_explained_counterexample(self):
        history = generate_history(2, SimConfig(follower_reads=True))
        small = shrink(history)
        self.assertLessEqual(len(small), 4)
        self.assertFalse(check_linearizable(small).ok)
        self.assertFalse(brute_force_linearizable(small))

    def test_memoisation_prunes_the_search(self):
        # Eight concurrent writes, then reads that no order can explain.
        ops = [write(f"W{i}", i + 1, 0, 100) for i in range(8)]
        ops += [read("R", 1, 101, 102), read("S", 99, 103, 104)]
        with_memo = check_linearizable(ops)
        without = check_linearizable(ops, memo=False)
        self.assertFalse(with_memo.ok or without.ok)
        self.assertEqual((with_memo.explored, without.explored), (3594, 114641))

    def test_memoisation_keeps_large_histories_fast(self):
        cfg = SimConfig(clients=8, ops_per_client=40, cas_fraction=0.0)
        history = generate_history(3, cfg)
        start = time.perf_counter()
        result = check_linearizable(history)
        self.assertTrue(result.ok)
        self.assertEqual(len(result.order), 320)
        self.assertLess(time.perf_counter() - start, 10.0)

    def test_render_draws_one_line_per_operation(self):
        history = generate_history(2, SimConfig())
        self.assertEqual(len(render(history).splitlines()), len(history))


if __name__ == "__main__":
    unittest.main()
