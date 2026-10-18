import random
import unittest
from collections import deque

from checker import Model, check, format_trace
from models import (MODELS, lease_lock_model, naive_mutex_model, peterson_model,
                    two_phase_commit_model)


def assert_valid_trace(test, model, result):
    """Every step in the trace must be a real transition of the model."""
    test.assertEqual(result.trace[0][0], "Init")
    test.assertIn(result.trace[0][1], set(model.initial_states()))
    for (_, before), (action, after) in zip(result.trace, result.trace[1:]):
        test.assertIn((action, after), list(model.next_states(before)))
    final = result.trace[-1][1]
    test.assertFalse(model.invariants[result.violated](final))
    for _, state in result.trace[:-1]:
        test.assertTrue(all(inv(state) for inv in model.invariants.values()))


class BundledModelTests(unittest.TestCase):
    def test_naive_mutex_race_is_found_in_six_steps(self):
        model = naive_mutex_model()
        result = check(model)
        self.assertFalse(result.ok)
        self.assertEqual(result.violated, "MutualExclusion")
        self.assertEqual(len(result.trace) - 1, 6)
        actions = [a for a, _ in result.trace[1:]]
        # Both processes see the lock free before either sets it.
        self.assertLess(actions.index("P1: sees lock free"), actions.index("P0: sets lock"))
        assert_valid_trace(self, model, result)

    def test_peterson_passes(self):
        result = check(peterson_model())
        self.assertTrue(result.ok)
        self.assertEqual((result.states, result.transitions, result.depth), (20, 34, 6))
        self.assertEqual(result.terminal_states, 0)   # never deadlocks

    def test_peterson_with_swapped_writes_fails(self):
        model = peterson_model(swap_writes=True)
        result = check(model)
        self.assertFalse(result.ok)
        assert_valid_trace(self, model, result)

    def test_lease_without_fencing_allows_stale_write(self):
        model = lease_lock_model(fencing=False)
        result = check(model)
        self.assertFalse(result.ok)
        self.assertEqual(result.violated, "WritesInLeaseOrder")
        self.assertEqual(len(result.trace) - 1, 8)
        self.assertEqual(result.trace[-1][1].writes, (2, 1))
        assert_valid_trace(self, model, result)

    def test_lease_with_fencing_passes_and_rejects_the_stale_write(self):
        model = lease_lock_model(fencing=True)
        result = check(model)
        self.assertTrue(result.ok)
        self.assertEqual(result.states, 166)
        # The fix works by rejection: some reachable step is a rejected write.
        actions = set()
        frontier, seen = deque(model.initial_states()), set()
        while frontier:
            s = frontier.popleft()
            for a, n in model.next_states(s):
                actions.add(a.split(" (")[0] + (" REJECTED" if "REJECTED" in a else ""))
                if n not in seen:
                    seen.add(n)
                    frontier.append(n)
        self.assertIn("C0: write REJECTED", actions)

    def test_fencing_holds_for_three_clients_and_longer_time(self):
        self.assertTrue(check(lease_lock_model(fencing=True, clients=3, max_time=4)).ok)
        self.assertFalse(check(lease_lock_model(fencing=False, clients=3, max_time=4)).ok)

    def test_two_phase_commit_is_atomic(self):
        counts = {n: check(two_phase_commit_model(n)).states for n in (2, 3, 4, 5)}
        self.assertEqual(counts, {2: 22, 3: 62, 4: 178, 5: 518})

    def test_two_phase_commit_on_majority_breaks_atomicity(self):
        model = two_phase_commit_model(commit_on_majority=True)
        result = check(model)
        self.assertEqual(result.violated, "Atomicity")
        self.assertEqual(len(result.trace) - 1, 5)
        assert_valid_trace(self, model, result)

    def test_state_counts_are_stable_across_runs(self):
        first = {name: check(make()).summary() for name, make in MODELS.items()}
        second = {name: check(make()).summary() for name, make in MODELS.items()}
        self.assertEqual(first, second)

    def test_format_trace_numbers_every_step(self):
        model = naive_mutex_model()
        text = format_trace(model, check(model))
        self.assertEqual(len(text.splitlines()), 7)
        self.assertIn("P1: sets lock", text)


class CheckerEngineTests(unittest.TestCase):
    def counter_model(self, limit, bad):
        """Count up by 1 or 2 from 0 to ``limit``; ``bad`` must never be reached."""
        return Model(
            name="counter",
            initial_states=lambda: [0],
            next_states=lambda n: [(f"+{k}", n + k) for k in (1, 2) if n + k <= limit],
            invariants={"NotBad": lambda n: n != bad},
        )

    def test_trace_is_shortest_path(self):
        result = check(self.counter_model(limit=20, bad=9))
        # 9 = 2+2+2+2+1: five steps is the minimum.
        self.assertEqual(len(result.trace) - 1, 5)

    def test_violating_initial_state_has_one_step_trace(self):
        result = check(self.counter_model(limit=5, bad=0))
        self.assertEqual(result.trace, [("Init", 0)])

    def test_max_states_truncates(self):
        result = check(self.counter_model(limit=1000, bad=-1), max_states=50)
        self.assertTrue(result.ok)
        self.assertTrue(result.truncated)
        self.assertEqual(result.states, 50)

    def test_duplicate_initial_states_are_counted_once(self):
        model = Model("dup", lambda: [0, 0, 1], lambda n: [], {"T": lambda n: True})
        result = check(model)
        self.assertEqual(result.states, 2)
        self.assertEqual(result.terminal_states, 2)

    def test_random_graphs_match_independent_reachability(self):
        """Seeded random state graphs: state counts and trace lengths agree
        with a separately computed BFS distance table."""
        for seed in range(200):
            rng = random.Random(seed)
            nodes = rng.randint(2, 40)
            edges = {n: [rng.randrange(nodes) for _ in range(rng.randint(0, 3))]
                     for n in range(nodes)}
            bad = rng.randrange(nodes)
            model = Model(
                name=f"random-{seed}",
                initial_states=lambda: [0],
                next_states=lambda n, e=edges: [(f"{n}->{m}", m) for m in e[n]],
                invariants={"NotBad": lambda n, b=bad: n != b},
            )
            # Reference BFS distances.
            dist, queue = {0: 0}, deque([0])
            while queue:
                n = queue.popleft()
                for m in edges[n]:
                    if m not in dist:
                        dist[m] = dist[n] + 1
                        queue.append(m)
            result = check(model)
            if bad in dist:
                self.assertFalse(result.ok, seed)
                self.assertEqual(len(result.trace) - 1, dist[bad], seed)
                assert_valid_trace(self, model, result)
            else:
                self.assertTrue(result.ok, seed)
                self.assertEqual(result.states, len(dist), seed)


if __name__ == "__main__":
    unittest.main()
