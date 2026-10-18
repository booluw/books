import random
import unittest

from cluster import CHAOS_NET, Cluster, chaos_run, find_bug
from figure8 import Figure8, ManualNetwork, ManualScheduler
from invariants import InvariantChecker, InvariantViolation
from raft import (LEADER, AppendEntries, AppendEntriesReply, Command, Entry,
                  KVStateMachine, RaftConfig, RaftNode, RequestVote, RequestVoteReply)
from sim import NetConfig

IDS = ["S1", "S2", "S3", "S4", "S5"]


def manual_nodes(bugs=frozenset()):
    net = ManualNetwork()
    nodes = {i: RaftNode(i, IDS, ManualScheduler(), net, random.Random(0), RaftConfig(), bugs)
             for i in IDS}
    net.nodes = nodes
    return net, nodes


def put(seq, value):
    return Command("c", seq, "put", "x", value)


class NodeUnitTests(unittest.TestCase):
    def test_crash_keeps_term_vote_and_log_and_forgets_the_rest(self):
        net, nodes = manual_nodes()
        s1 = nodes["S1"]
        s1.receive("S2", RequestVote(term=3, candidate="S2", last_log_index=0, last_log_term=0))
        s1.receive("S2", AppendEntries(3, "S2", 0, 0, (Entry(3, put(1, 7)),), leader_commit=1))
        self.assertEqual((s1.commit_index, s1.state_machine.data), (1, {"x": 7}))
        s1.crash()
        s1.restart()
        self.assertEqual((s1.current_term, s1.voted_for), (3, "S2"))
        self.assertEqual(s1.log, [Entry(3, put(1, 7))])
        self.assertEqual((s1.commit_index, s1.state_machine.data), (0, {}))
        # The persisted vote stops it voting twice in term 3 after the restart.
        net.in_flight.clear()
        s1.receive("S3", RequestVote(3, "S3", 5, 3))
        self.assertEqual(net.in_flight[-1][2], RequestVoteReply(3, False))

    def test_vote_requires_up_to_date_log_unless_bugged(self):
        for bugs, expected in ((frozenset(), False), ({"vote_without_log_check"}, True)):
            net, nodes = manual_nodes(bugs)
            s1 = nodes["S1"]
            s1.receive("S2", AppendEntries(1, "S2", 0, 0, (Entry(1, put(1, 1)),), 0))
            net.in_flight.clear()
            s1.receive("S3", RequestVote(term=2, candidate="S3", last_log_index=0, last_log_term=0))
            self.assertEqual(net.in_flight[-1][2].granted, expected, bugs)

    def test_consistency_check_and_leader_back_up(self):
        net, nodes = manual_nodes()
        follower = nodes["S2"]
        follower.receive("S1", AppendEntries(1, "S1", 0, 0, (Entry(1, put(1, 1)),), 0))
        net.in_flight.clear()
        # The leader claims entry 3 has term 2; the follower has only 1 entry.
        follower.receive("S1", AppendEntries(2, "S1", 3, 2, (Entry(2, put(4, 4)),), 0))
        reply = net.in_flight[-1][2]
        self.assertIsInstance(reply, AppendEntriesReply)
        self.assertFalse(reply.success)
        self.assertEqual(reply.hint, 2)              # "try from index 2"
        self.assertEqual(len(follower.log), 1)

    def test_stale_duplicate_append_does_not_truncate(self):
        net, nodes = manual_nodes()
        f = nodes["S2"]
        e1, e2, e3 = Entry(1, put(1, 1)), Entry(1, put(2, 2)), Entry(1, put(3, 3))
        f.receive("S1", AppendEntries(1, "S1", 0, 0, (e1, e2, e3), 0))
        f.receive("S1", AppendEntries(1, "S1", 0, 0, (e1,), 0))   # old message, arriving late
        self.assertEqual(f.log, [e1, e2, e3])
        f.receive("S1", AppendEntries(2, "S1", 1, 1, (Entry(2, put(9, 9)),), 0))  # real conflict
        self.assertEqual(f.log, [e1, Entry(2, put(9, 9))])

    def test_state_machine_applies_a_retried_command_once(self):
        sm = KVStateMachine()
        self.assertEqual(sm.apply(Command("c", 1, "put", "x", 1)), 1)
        sm.apply(Command("c", 2, "put", "x", 2))
        self.assertEqual(sm.apply(Command("c", 2, "put", "x", 2)), 2)   # retry of seq 2
        sm.apply(Command("c", 1, "put", "x", 1))                         # very late duplicate
        self.assertEqual(sm.data, {"x": 2})
        self.assertEqual(sm.last_seq["c"], (2, 2))

    def test_unknown_bug_name_is_rejected(self):
        with self.assertRaises(ValueError):
            manual_nodes({"made_up"})


class CheckerUnitTests(unittest.TestCase):
    def test_checker_detects_two_leaders_and_mismatched_logs(self):
        _, nodes = manual_nodes()
        checker = InvariantChecker(nodes, stop_on_violation=False)
        for n in ("S1", "S2"):
            nodes[n].role = LEADER
            nodes[n].storage.current_term = 4
        nodes["S3"].storage.log[:] = [Entry(1, put(1, 1)), Entry(2, put(2, 2))]
        nodes["S4"].storage.log[:] = [Entry(1, put(1, 9)), Entry(2, put(2, 2))]
        nodes["S3"].storage.version += 1
        checker.check()
        self.assertEqual({v.invariant for v in checker.violations},
                         {"Election Safety", "Log Matching"})


class LivenessTests(unittest.TestCase):
    def test_leader_elected_within_bound_on_stable_network(self):
        times = []
        for seed in range(100):
            c = Cluster(seed)
            t = c.run_until(lambda: c.leader() is not None, limit=1000)
            self.assertIsNotNone(t, f"seed {seed}: no leader within 1000 ms")
            times.append(t)
            c.run(c.scheduler.now + 500)
            self.assertEqual(len(c.leaders()), 1, seed)          # and it stays alone
        self.assertLess(sorted(times)[50], 300)                  # median is one timeout

    def test_commands_commit_and_replicas_converge(self):
        for seed in range(30):
            c = Cluster(seed)
            client = c.add_client(20)
            t = c.run_until(lambda: len(client.completed) == 20, limit=4000)
            self.assertIsNotNone(t, f"seed {seed}")
            c.run(c.scheduler.now + 200)                         # let followers learn the commit
            stores = {n: node.state_machine.data for n, node in c.nodes.items()}
            self.assertEqual(len({str(sorted(d.items())) for d in stores.values()}), 1, seed)
            self.assertEqual(stores["S1"], {"k0": 18, "k1": 19, "k2": 20})

    def test_cluster_recovers_after_faults_stop(self):
        for seed in range(40):
            c = Cluster(seed, net=CHAOS_NET)
            client = c.add_client(1000)
            c.start_nemesis(until=3000)
            c.run(3000)
            c.stop_faults()
            before = len(client.completed)
            t = c.run_until(lambda: len(client.completed) >= before + 10, limit=13000)
            self.assertIsNotNone(t, f"seed {seed}: no progress after healing")


class SafetyUnderChaosTests(unittest.TestCase):
    def test_hundreds_of_chaotic_schedules_keep_every_invariant(self):
        steps = committed = 0
        for seed in range(300):
            r = chaos_run(seed)
            self.assertIsNone(r.violation, f"seed {seed}: {r.violation}")
            steps += r.steps
            committed += r.committed
        self.assertGreater(steps, 300_000)        # invariants checked after every one
        self.assertGreater(committed, 3000)

    def test_runs_are_deterministic(self):
        a, b = chaos_run(42), chaos_run(42)
        self.assertEqual((a.steps, a.committed, a.faults), (b.steps, b.committed, b.faults))

    def test_heavy_duplication_and_reordering_is_safe(self):
        for seed in range(30):
            c = Cluster(seed, net=NetConfig(delay=(1.0, 80.0), loss=0.2, duplicate=0.3))
            client = c.add_client(15)
            # Raises on any invariant violation; slow, but it gets there.
            t = c.run_until(lambda: len(client.completed) == 15, limit=15000, poll=50)
            self.assertIsNotNone(t, seed)
            self.assertGreater(c.network.stats["duplicated"], 0)


class BugDetectionTests(unittest.TestCase):
    def test_vote_without_log_check_is_caught(self):
        found = find_bug("vote_without_log_check", range(20))
        self.assertIsNotNone(found)
        self.assertEqual(found.seed, 1)
        self.assertIn("Leader Completeness", found.violation)

    def test_commit_previous_term_is_caught_by_random_search(self):
        found = find_bug("commit_previous_term", range(100))
        self.assertIsNotNone(found)
        self.assertEqual(found.seed, 91)
        self.assertIn("committed in term 8", found.violation)

    def test_figure8_scenario(self):
        correct = Figure8().run()
        self.assertEqual(correct.checker.violations, [])
        self.assertEqual([e.term for e in correct.nodes["S2"].log], [1, 3, 5])
        buggy = Figure8({"commit_previous_term"}).run()
        kinds = {v.invariant for v in buggy.checker.violations}
        self.assertEqual(kinds, {"Leader Completeness", "State Machine Safety"})
        entry, by = buggy.checker.applied[2]
        self.assertEqual((by, entry.term, entry.command.value), ("S1", 2, 2))
        self.assertEqual(buggy.nodes["S5"].log[1].command.value, 3)


if __name__ == "__main__":
    unittest.main()
