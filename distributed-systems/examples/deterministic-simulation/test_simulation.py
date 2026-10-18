"""Tests for the deterministic simulation harness and the primary-backup system."""

import unittest
from dataclasses import replace

from primary_backup import run
from sim import Simulator, SwarmConfig
from swarm import story, swarm


class HarnessTests(unittest.TestCase):
    def test_same_seed_gives_identical_trace(self):
        for seed in (0, 7, 100, 4242):
            a, b = run(seed, trace=True), run(seed, trace=True)
            self.assertEqual(a.trace, b.trace)
            self.assertEqual(a.trace_hash, b.trace_hash)

    def test_trace_hash_does_not_depend_on_keeping_the_trace(self):
        self.assertEqual(run(100, trace=True).trace_hash, run(100, trace=False).trace_hash)

    def test_different_seeds_explore_different_executions(self):
        hashes = {run(seed).trace_hash for seed in range(200)}
        self.assertEqual(len(hashes), 200)

    def test_swarm_config_is_a_function_of_the_seed_and_varies(self):
        self.assertEqual(SwarmConfig.from_seed(5), SwarmConfig.from_seed(5))
        configs = {SwarmConfig.from_seed(s) for s in range(100)}
        self.assertGreater(len({c.drop_rate for c in configs}), 3)
        self.assertGreater(len({c.clients for c in configs}), 2)

    def test_simultaneous_events_run_in_scheduling_order(self):
        sim = Simulator(0, SwarmConfig())
        order = []
        for name in "abc":
            sim.schedule(5.0, order.append, name)
        sim.schedule(1.0, order.append, "first")
        sim.schedule(99.0, order.append, "too late")
        sim.run(until=50.0)
        self.assertEqual(order, ["first", "a", "b", "c"])

    def test_network_without_loss_drops_nothing(self):
        r = run(3, config=replace(SwarmConfig(), drop_rate=0.0), trace=True)
        self.assertFalse(any("DROP" in line for line in r.trace))


class BugHuntTests(unittest.TestCase):
    def test_swarm_finds_the_bug_within_500_seeds(self):
        failures, _ = swarm(range(500), buggy=True)
        self.assertTrue(failures)
        self.assertEqual(failures[0], 100)

    def test_failing_seed_replays_exactly(self):
        first = run(100, buggy=True, trace=True)
        again = run(100, buggy=True, trace=True)
        self.assertFalse(first.ok)
        self.assertEqual(first.lost, again.lost)
        self.assertEqual(first.trace_hash, again.trace_hash)

    def test_story_explains_the_failure(self):
        lines = story(run(100, buggy=True, trace=True))
        text = "\n".join(lines)
        self.assertIn("DROP n0->n1 ('replicate', 1,", text)
        self.assertIn("releases ops [8, 1]", text)
        self.assertIn("CRASH", text)
        self.assertIn("FAILOVER", text)

    def test_bug_needs_a_dropped_message(self):
        calm = [s for s in range(500)
                if not run(s, config=replace(SwarmConfig.from_seed(s), drop_rate=0.0)).ok]
        self.assertEqual(calm, [])

    def test_bug_needs_a_failover(self):
        no_crash = [s for s in range(500)
                    if not run(s, config=replace(SwarmConfig.from_seed(s),
                                                 crash_primary=False)).ok]
        self.assertEqual(no_crash, [])


class FixTests(unittest.TestCase):
    def test_fixed_version_passes_every_seed(self):
        failures, _ = swarm(range(3_000), buggy=False)
        self.assertEqual(failures, [])

    def test_fixed_version_survives_a_hostile_network(self):
        hostile = SwarmConfig(clients=4, counters=1, ops_per_client=10, drop_rate=0.3)
        for seed in range(100):
            r = run(seed, buggy=False, config=hostile)
            self.assertTrue(r.ok, f"seed {seed} lost {r.lost}")
            self.assertEqual(r.acked, 40)              # every op eventually acknowledged


if __name__ == "__main__":
    unittest.main()
