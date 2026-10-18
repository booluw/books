import itertools
import random
import unittest

from twopc import CRASH_POINTS, Blocked, TwoPhaseCommit

NAMES = ("orders", "payments", "inventory")


def writes_for(names, txid="T1"):
    return {n: {f"{n}-{txid}": 1} for n in names}


def recover_in_order(system, rng=None):
    """Bring every node back, in a random order if ``rng`` is given, and let
    the coordinator retry until nothing is left unfinished."""
    nodes = ["coordinator"] + [n for n, p in system.participants.items() if not p.up]
    if rng:
        rng.shuffle(nodes)
    for node in nodes:
        if node == "coordinator":
            if not system.coordinator.up:
                system.recover_coordinator()
        else:
            system.recover_participant(node)
    system.retry_unfinished()


def assert_atomic(test, system, txid, writes, context=""):
    statuses = set(system.statuses(txid).values())
    test.assertEqual(len(statuses), 1, f"{context}: {system.statuses(txid)}")
    outcome = statuses.pop()
    test.assertIn(outcome, ("committed", "aborted"), context)
    for name, ws in writes.items():
        p = system.participants[name]
        for key, value in ws.items():
            test.assertEqual(p.data.get(key), value if outcome == "committed" else None, context)
        test.assertEqual(p.locks, {}, context)
    return outcome


class TwoPhaseCommitTests(unittest.TestCase):
    def test_happy_path_commits_everywhere(self):
        s = TwoPhaseCommit.create()
        w = writes_for(NAMES)
        self.assertEqual(s.run("T1", w), "committed")
        self.assertEqual(assert_atomic(self, s, "T1", w), "committed")
        self.assertEqual(s.coordinator.log.records[-1], ("end", "T1"))

    def test_one_no_vote_aborts_everywhere(self):
        s = TwoPhaseCommit.create()
        w = writes_for(NAMES)
        self.assertEqual(s.run("T1", w, votes={"payments": False}), "aborted")
        self.assertEqual(assert_atomic(self, s, "T1", w), "aborted")

    def test_coordinator_crash_after_decision_blocks_participants(self):
        s = TwoPhaseCommit.create()
        w = writes_for(NAMES)
        self.assertEqual(s.run("T1", w, crash="coordinator_after_decision_log"), "interrupted")
        self.assertEqual(set(s.statuses("T1").values()), {"in doubt"})
        with self.assertRaises(Blocked):                       # locks still held
            s.participants["orders"].read("orders-T1")
        self.assertEqual(s.resolve("orders", "T1"), "in doubt")
        self.assertEqual(s.cooperative_termination("orders", "T1"), "in doubt")
        s.recover_coordinator()
        self.assertEqual(assert_atomic(self, s, "T1", w), "committed")

    def test_coordinator_crash_before_decision_is_presumed_abort(self):
        s = TwoPhaseCommit.create()
        w = writes_for(NAMES)
        s.run("T1", w, crash="coordinator_before_decision_log")
        self.assertEqual(set(s.statuses("T1").values()), {"in doubt"})   # blocked too
        s.recover_coordinator()
        self.assertEqual(assert_atomic(self, s, "T1", w), "aborted")

    def test_participant_recovers_in_doubt_with_locks_rebuilt(self):
        s = TwoPhaseCommit.create()
        w = writes_for(NAMES)
        self.assertEqual(s.run("T1", w, crash="participant_after_vote_yes"), "committed")
        inventory = s.participants["inventory"]
        self.assertEqual(inventory.recover(), ["T1"])          # from the log alone
        self.assertEqual(inventory.locks, {"inventory-T1": "T1"})
        self.assertEqual(s.resolve("inventory", "T1"), "committed")
        self.assertEqual(assert_atomic(self, s, "T1", w), "committed")

    def test_cooperative_termination_works_after_partial_broadcast(self):
        s = TwoPhaseCommit.create()
        w = writes_for(NAMES)
        s.run("T1", w, crash="coordinator_mid_broadcast")
        self.assertEqual(s.statuses("T1")["orders"], "committed")
        self.assertEqual(s.cooperative_termination("inventory", "T1"), "committed")
        self.assertEqual(s.cooperative_termination("payments", "T1"), "committed")
        s.recover_coordinator()                                 # duplicate commits are harmless
        self.assertEqual(assert_atomic(self, s, "T1", w), "committed")

    def test_every_crash_point_vote_victim_and_recovery_order_is_atomic(self):
        cases = 0
        for crash, no_voter, victim, coordinator_first in itertools.product(
                CRASH_POINTS, (None,) + NAMES, NAMES, (True, False)):
            s = TwoPhaseCommit.create()
            w = writes_for(NAMES)
            votes = {no_voter: False} if no_voter else {}
            s.run("T1", w, votes=votes, crash=crash, crash_participant=victim)
            if coordinator_first and not s.coordinator.up:
                s.recover_coordinator()
            recover_in_order(s)
            outcome = assert_atomic(self, s, "T1", w, f"{crash}/{no_voter}/{victim}")
            # Commit only if everyone voted yes and the decision reached the log.
            can_commit = (no_voter is None and crash not in
                          ("participant_before_vote", "coordinator_before_decision_log"))
            self.assertEqual(outcome == "committed", can_commit, f"{crash}/{no_voter}/{victim}")
            cases += 1
        self.assertEqual(cases, 6 * 4 * 3 * 2)

    def test_randomised_transaction_sequences_stay_atomic(self):
        outcomes = {"committed": 0, "aborted": 0}
        for seed in range(300):
            rng = random.Random(seed)
            names = tuple(f"p{i}" for i in range(rng.randint(2, 5)))
            s = TwoPhaseCommit.create(names)
            expected = {n: {} for n in names}
            for t in range(rng.randint(1, 4)):
                txid = f"T{t}"
                involved = tuple(rng.sample(names, rng.randint(1, len(names))))
                w = {n: {"balance": rng.randint(1, 99)} for n in involved}
                votes = {n: rng.random() > 0.15 for n in involved}
                s.run(txid, w, votes=votes, crash=rng.choice(CRASH_POINTS),
                      crash_participant=rng.choice(involved))
                recover_in_order(s, rng)
                statuses = {s.participants[n].status(txid) for n in involved}
                self.assertEqual(len(statuses), 1, f"seed {seed} {txid}: {statuses}")
                outcome = statuses.pop()
                outcomes[outcome] += 1
                if outcome == "committed":
                    for n in involved:
                        expected[n].update(w[n])
            for n in names:
                self.assertEqual(s.participants[n].data, expected[n], f"seed {seed}")
                self.assertEqual(s.participants[n].locks, {}, f"seed {seed}")
        self.assertGreater(min(outcomes.values()), 100)

    def test_logged_decision_never_changes(self):
        s = TwoPhaseCommit.create()
        s.run("T1", writes_for(NAMES), crash="coordinator_after_decision_log")
        for _ in range(3):
            s.recover_coordinator()
            self.assertEqual(s.coordinator.outcome_for("T1"), "commit")
        self.assertEqual([r[0] for r in s.coordinator.log.for_tx("T1")],
                         ["begin", "commit", "end"])


if __name__ == "__main__":
    unittest.main()
