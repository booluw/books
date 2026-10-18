import random
import unittest

from clocks import (AFTER, BEFORE, CONCURRENT, EQUAL, HybridLogicalClock, LamportClock,
                    VectorClock, compare, ground_truth, happened_before, simulate, simulate_hlc)

RUNS = 200


def random_execution(seed):
    rng = random.Random(seed)
    return simulate(n=rng.randint(2, 5), steps=rng.randint(5, 40), seed=seed,
                    p_send=rng.uniform(0.1, 0.6), p_local=rng.uniform(0.1, 0.3))


class LamportTests(unittest.TestCase):
    def test_receive_jumps_past_message_time(self):
        c = LamportClock()
        c.tick()
        self.assertEqual(c.receive(10), 11)
        self.assertEqual(c.tick(), 12)

    def test_clock_condition_holds_over_random_executions(self):
        # Property: a -> b implies L(a) < L(b), for every pair in every run.
        for seed in range(RUNS):
            ex = random_execution(seed)
            succ = ground_truth(ex)
            for a in ex.events:
                for b_id in succ[a.eid]:
                    self.assertLess(a.lamport, ex.events[b_id].lamport, f"seed {seed}")

    def test_lamport_order_does_not_imply_causality(self):
        # The converse fails: some concurrent pairs have different Lamport times.
        found = 0
        for seed in range(50):
            ex = random_execution(seed)
            succ = ground_truth(ex)
            for a in ex.events:
                for b in ex.events:
                    if (a.lamport < b.lamport and b.eid not in succ[a.eid]
                            and a.eid not in succ[b.eid]):
                        found += 1
        self.assertGreater(found, 0)


class VectorClockTests(unittest.TestCase):
    def test_compare_cases(self):
        self.assertEqual(compare((1, 0), (1, 0)), EQUAL)
        self.assertEqual(compare((1, 0), (1, 1)), BEFORE)
        self.assertEqual(compare((2, 1), (1, 1)), AFTER)
        self.assertEqual(compare((1, 0), (0, 1)), CONCURRENT)
        self.assertTrue(happened_before((0, 1, 0), (1, 1, 0)))

    def test_receive_takes_elementwise_max_then_ticks(self):
        v = VectorClock(1, 3)
        v.tick()
        self.assertEqual(v.receive((4, 0, 2)), (4, 2, 2))

    def test_vector_clocks_match_ground_truth_exactly(self):
        # Property: V(a) < V(b) iff a -> b, and V(a) || V(b) iff a || b.
        for seed in range(RUNS):
            ex = random_execution(seed)
            succ = ground_truth(ex)
            for a in ex.events:
                for b in ex.events:
                    if a.eid == b.eid:
                        continue
                    truth = (BEFORE if b.eid in succ[a.eid] else
                             AFTER if a.eid in succ[b.eid] else CONCURRENT)
                    self.assertEqual(compare(a.vector, b.vector), truth,
                                     f"seed {seed}: {a} vs {b}")

    def test_vector_timestamps_are_unique(self):
        for seed in range(RUNS):
            ex = random_execution(seed)
            stamps = [e.vector for e in ex.events]
            self.assertEqual(len(stamps), len(set(stamps)))

    def test_every_send_is_received(self):
        for seed in range(RUNS):
            ex = random_execution(seed)
            self.assertEqual(set(ex.send_of), set(ex.recv_of))


class HLCTests(unittest.TestCase):
    def test_receive_from_a_fast_clock(self):
        hlc = HybridLogicalClock(lambda: 100)
        self.assertEqual(hlc.now(), (100, 0))
        self.assertEqual(hlc.now(), (100, 1))          # physical clock did not move
        self.assertEqual(hlc.receive((150, 3)), (150, 4))
        self.assertEqual(hlc.now(), (150, 5))

    def test_hlc_respects_causality_where_physical_clocks_do_not(self):
        physical_violations = 0
        for seed in range(RUNS):
            events, sends, recvs = simulate_hlc(n=3, steps=40, seed=seed, max_skew=50)
            for m in sends:
                s, r = events[sends[m]], events[recvs[m]]
                self.assertLess(s.hlc, r.hlc, f"seed {seed}")
                physical_violations += r.physical <= s.physical
            # Program order is respected too.
            for pid in range(3):
                own = [e.hlc for e in events if e.pid == pid]
                self.assertEqual(own, sorted(own))
                self.assertEqual(len(own), len(set(own)))
        self.assertGreater(physical_violations, 0)

    def test_hlc_stays_within_skew_of_physical_time(self):
        # Property: pt <= l <= pt + (largest offset - smallest offset).
        for seed in range(RUNS):
            events, _, _ = simulate_hlc(n=4, steps=60, seed=seed, max_skew=30)
            offsets = {e.pid: e.physical - e.true_time for e in events}
            eps = max(offsets.values()) - min(offsets.values())
            for e in events:
                self.assertGreaterEqual(e.hlc[0], e.physical)
                self.assertLessEqual(e.hlc[0] - e.physical, eps)


if __name__ == "__main__":
    unittest.main()
