"""Two-phase commit with crashes, blocking and recovery from logs (Chapter 9).

One *coordinator* and several *participants* (each owning some data)
commit a transaction atomically: either every participant applies its
writes, or none does.

Phase 1 (prepare / voting): the coordinator logs ``begin`` and asks every
participant to *prepare*. A participant that can commit writes its changes
and a ``prepared`` record to its durable log, locks the keys, and votes
yes. From then on it has given up the right to abort on its own. A
participant that cannot commit logs ``abort`` and votes no.

Phase 2 (decision): if every vote is yes, the coordinator logs ``commit``;
otherwise it logs ``abort``. **The decision is made at the moment it reaches
the coordinator's log.** It then tells every participant, and logs ``end``
once all have acknowledged.

Crashes are simulated at the interesting points (``CRASH_POINTS``). A crash
throws away a node's memory (locks, transaction tables) and keeps its log,
as a real process restart would. Recovery rebuilds everything from the log.

The famous weakness shows up when the coordinator crashes after
participants have voted yes: they are *in doubt*. They may not commit (the
coordinator might have decided abort) and may not abort (it might have
decided commit), so they hold their locks and wait. That is the *blocking
problem*. Run ``python3 twopc.py`` to watch it.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

CRASH_POINTS = (
    None,
    "participant_before_vote",          # crashes on receiving PREPARE, before logging
    "participant_after_vote_yes",       # logged PREPARED and voted yes, then crashed
    "coordinator_before_decision_log",  # has every vote, crashes before logging decision
    "coordinator_after_decision_log",   # decision durable, crashes before telling anyone
    "coordinator_mid_broadcast",        # told the first participant, then crashed
)


class Unavailable(Exception):
    """The node is down; the message is lost and the caller will retry later."""


class Blocked(Exception):
    """A read hit a key locked by an in-doubt transaction."""


class Crash(Exception):
    """Raised inside the protocol at a simulated crash point."""


class DurableLog:
    """An append-only log that survives crashes (think: fsync'd file)."""

    def __init__(self) -> None:
        self.records: List[tuple] = []

    def append(self, *record) -> None:
        self.records.append(tuple(record))

    def for_tx(self, txid: str) -> List[tuple]:
        return [r for r in self.records if r[1] == txid]


class Participant:
    def __init__(self, name: str, data: Optional[Dict[str, int]] = None) -> None:
        self.name = name
        self.log = DurableLog()
        self.data: Dict[str, int] = dict(data or {})   # committed data, durable
        self.up = True
        self.locks: Dict[str, str] = {}                # key -> txid (volatile)
        self.prepared: Dict[str, Dict[str, int]] = {}  # txid -> writes (volatile)

    # -- phase 1 ------------------------------------------------------------
    def prepare(self, txid: str, writes: Dict[str, int], vote_yes: bool = True) -> str:
        self._check_up()
        busy = any(self.locks.get(k, txid) != txid for k in writes)
        if not vote_yes or busy:
            self.log.append("abort", txid)            # unilateral abort is allowed now
            return "no"
        self.log.append("prepared", txid, dict(writes))  # durable *before* voting yes
        self.prepared[txid] = dict(writes)
        for key in writes:
            self.locks[key] = txid
        return "yes"

    # -- phase 2 ------------------------------------------------------------
    def commit(self, txid: str) -> None:
        self._check_up()
        if self.status(txid) == "committed":
            return                                     # duplicate message: idempotent
        writes = self.prepared.pop(txid)
        self.log.append("commit", txid)
        self.data.update(writes)
        self._unlock(txid)

    def abort(self, txid: str) -> None:
        self._check_up()
        if self.status(txid) in ("aborted", "committed"):
            return
        self.prepared.pop(txid, None)
        self.log.append("abort", txid)
        self._unlock(txid)

    # -- reads by other transactions ------------------------------------------
    def read(self, key: str) -> int:
        self._check_up()
        if key in self.locks:
            raise Blocked(f"{self.name}: {key!r} is locked by in-doubt {self.locks[key]}")
        return self.data.get(key, 0)

    # -- crash and recovery --------------------------------------------------
    def crash(self) -> None:
        self.up = False
        self.locks.clear()
        self.prepared.clear()

    def recover(self) -> List[str]:
        """Rebuild locks from the log. Returns the in-doubt transactions."""
        self.up = True
        in_doubt = []
        txids = dict.fromkeys(r[1] for r in self.log.records)
        for txid in txids:
            if self.status(txid) == "in doubt":
                writes = next(r[2] for r in self.log.for_tx(txid) if r[0] == "prepared")
                self.prepared[txid] = writes
                for key in writes:
                    self.locks[key] = txid
                in_doubt.append(txid)
        return in_doubt

    def status(self, txid: str) -> str:
        kinds = [r[0] for r in self.log.for_tx(txid)]
        if "commit" in kinds:
            return "committed"
        if "abort" in kinds:
            return "aborted"
        if "prepared" in kinds:
            return "in doubt"
        return "unknown"            # never voted: free to abort on its own

    def _unlock(self, txid: str) -> None:
        for key in [k for k, t in self.locks.items() if t == txid]:
            del self.locks[key]

    def _check_up(self) -> None:
        if not self.up:
            raise Unavailable(f"{self.name} is down")


class Coordinator:
    def __init__(self, name: str = "coordinator") -> None:
        self.name = name
        self.log = DurableLog()
        self.up = True

    def decision(self, txid: str) -> Optional[str]:
        for record in self.log.for_tx(txid):
            if record[0] in ("commit", "abort"):
                return record[0]
        return None

    def outcome_for(self, txid: str) -> str:
        """Answer a participant asking "what happened to txid?"."""
        if not self.up:
            raise Unavailable("coordinator is down")
        # Presumed abort: no decision record means it never committed.
        return self.decision(txid) or "abort"

    def crash(self) -> None:
        self.up = False


@dataclass
class TwoPhaseCommit:
    """A coordinator and its participants, plus a record of what happened."""

    participants: Dict[str, Participant]
    coordinator: Coordinator = field(default_factory=Coordinator)
    events: List[str] = field(default_factory=list)

    @classmethod
    def create(cls, names=("orders", "payments", "inventory")) -> "TwoPhaseCommit":
        return cls({n: Participant(n) for n in names})

    def note(self, text: str) -> None:
        self.events.append(text)

    def run(self, txid: str, writes: Dict[str, Dict[str, int]],
            votes: Optional[Dict[str, bool]] = None,
            crash: Optional[str] = None, crash_participant: Optional[str] = None) -> str:
        """Run one transaction. Returns ``"committed"``, ``"aborted"`` or
        ``"interrupted"`` (the coordinator crashed part-way)."""
        if crash not in CRASH_POINTS:
            raise ValueError(f"unknown crash point {crash!r}")
        votes = votes or {}
        coordinator = self.coordinator
        names = list(writes)
        victim = crash_participant or names[-1]
        try:
            coordinator.log.append("begin", txid, tuple(names))
            self.note(f"coordinator logs BEGIN {txid}")
            # ---- phase 1 ------------------------------------------------------
            ballot = {}
            for name in names:
                p = self.participants[name]
                if crash == "participant_before_vote" and name == victim:
                    p.crash()
                    self.note(f"{name} CRASHES before voting")
                try:
                    ballot[name] = p.prepare(txid, writes[name], votes.get(name, True))
                    self.note(f"{name} votes {ballot[name]}")
                except Unavailable:
                    ballot[name] = "timeout"
                    self.note(f"coordinator times out waiting for {name}")
                if crash == "participant_after_vote_yes" and name == victim and ballot[name] == "yes":
                    p.crash()
                    self.note(f"{name} CRASHES after voting yes")
            if crash == "coordinator_before_decision_log":
                raise Crash("before decision log")
            # ---- the commit point -------------------------------------------
            decision = "commit" if all(v == "yes" for v in ballot.values()) else "abort"
            coordinator.log.append(decision, txid)
            self.note(f"coordinator logs {decision.upper()} (the decision is now final)")
            if crash == "coordinator_after_decision_log":
                raise Crash("after decision log")
            # ---- phase 2 ------------------------------------------------------
            self._broadcast(txid, decision, names,
                            crash_after_first=(crash == "coordinator_mid_broadcast"))
            return "committed" if decision == "commit" else "aborted"
        except Crash as c:
            coordinator.crash()
            self.note(f"coordinator CRASHES ({c})")
            return "interrupted"

    def _broadcast(self, txid: str, decision: str, names, crash_after_first=False) -> None:
        delivered = 0
        for name in names:
            p = self.participants[name]
            try:
                p.commit(txid) if decision == "commit" else p.abort(txid)
                self.note(f"{name} {decision}s")
                delivered += 1
            except Unavailable:
                self.note(f"{decision} to {name} lost ({name} is down); will retry")
            if crash_after_first and delivered == 1:
                raise Crash("part-way through sending the decision")
        if delivered == len(names):
            self.coordinator.log.append("end", txid)

    # -- recovery ---------------------------------------------------------------
    def recover_coordinator(self) -> None:
        """Restart the coordinator and finish every unfinished transaction."""
        c = self.coordinator
        c.up = True
        self.note("coordinator RECOVERS and reads its log")
        self.retry_unfinished()

    def retry_unfinished(self) -> None:
        """Resend decisions for transactions without an ``end`` record."""
        c = self.coordinator
        for record in list(c.log.records):
            if record[0] != "begin":
                continue
            txid, names = record[1], record[2]
            if any(r[0] == "end" for r in c.log.for_tx(txid)):
                continue
            decision = c.decision(txid)
            if decision is None:
                c.log.append("abort", txid)    # never decided: presumed abort
                decision = "abort"
                self.note(f"coordinator finds no decision for {txid}: logs ABORT")
            self._broadcast(txid, decision, names)

    def recover_participant(self, name: str) -> List[str]:
        """Restart a participant; it asks the coordinator about in-doubt work."""
        p = self.participants[name]
        in_doubt = p.recover()
        self.note(f"{name} RECOVERS; in doubt: {in_doubt or 'nothing'}")
        for txid in in_doubt:
            self.resolve(name, txid)
        return in_doubt

    def resolve(self, name: str, txid: str) -> str:
        """A participant asks the coordinator for the outcome of ``txid``."""
        p = self.participants[name]
        try:
            outcome = self.coordinator.outcome_for(txid)
        except Unavailable:
            self.note(f"{name} asks about {txid}: coordinator down, still in doubt")
            return "in doubt"
        p.commit(txid) if outcome == "commit" else p.abort(txid)
        self.note(f"{name} asks about {txid}: told {outcome}")
        return p.status(txid)

    def cooperative_termination(self, name: str, txid: str) -> str:
        """Ask the *other participants* instead of the coordinator.

        If any peer committed or aborted, or never voted (and so may still
        abort), the asker can decide. If every peer is also prepared, nobody
        knows the outcome: the protocol blocks.
        """
        p = self.participants[name]
        for peer in self.participants.values():
            if peer is p or not peer.up:
                continue
            status = peer.status(txid)
            if status in ("committed", "aborted", "unknown"):
                if status == "unknown":
                    peer.abort(txid)       # it had not voted: it may abort now
                outcome = "commit" if status == "committed" else "abort"
                p.commit(txid) if outcome == "commit" else p.abort(txid)
                self.note(f"{name} learns {outcome} from {peer.name}")
                return p.status(txid)
        self.note(f"{name}: every reachable peer is also in doubt; BLOCKED")
        return "in doubt"

    def statuses(self, txid: str) -> Dict[str, str]:
        return {n: p.status(txid) for n, p in self.participants.items()}

    def recover_everything(self) -> None:
        """Restart every crashed node, then let the coordinator finish its work."""
        for name, p in self.participants.items():
            if not p.up:
                self.recover_participant(name)
        self.recover_coordinator()


def demo() -> None:
    writes = {"orders": {"order-17": 1}, "payments": {"balance": 70}, "inventory": {"widget": 4}}

    def show(system, txid="T1"):
        print(f"  statuses: {system.statuses(txid)}")

    print("== 1. Happy path")
    s = TwoPhaseCommit.create()
    print(f"  result: {s.run('T1', writes)}")
    print("  " + "\n  ".join(s.events))

    print("\n== 2. Coordinator crashes after logging COMMIT: participants block")
    s = TwoPhaseCommit.create()
    s.run("T1", writes, crash="coordinator_after_decision_log")
    print("  " + "\n  ".join(s.events))
    show(s)
    try:
        s.participants["inventory"].read("widget")
    except Blocked as b:
        print(f"  another transaction tries to read: Blocked: {b}")
    s.events.clear()
    s.resolve("payments", "T1")
    s.cooperative_termination("payments", "T1")
    s.recover_coordinator()
    print("  " + "\n  ".join(s.events))
    show(s)
    print(f"  inventory widget = {s.participants['inventory'].read('widget')}")

    print("\n== 3. Coordinator crashes before logging a decision: presumed abort")
    s = TwoPhaseCommit.create()
    s.run("T1", writes, crash="coordinator_before_decision_log")
    show(s)
    s.events.clear()
    s.recover_coordinator()
    print("  " + "\n  ".join(s.events))
    show(s)

    print("\n== 4. Participant crashes after voting yes; recovers in doubt")
    s = TwoPhaseCommit.create()
    print(f"  result: {s.run('T1', writes, crash='participant_after_vote_yes')}")
    show(s)
    s.events.clear()
    s.recover_participant("inventory")
    print("  " + "\n  ".join(s.events))
    show(s)

    print("\n== 5. Participant crashes before voting: coordinator aborts")
    s = TwoPhaseCommit.create()
    print(f"  result: {s.run('T1', writes, crash='participant_before_vote')}")
    s.recover_participant("inventory")
    s.retry_unfinished()
    show(s)

    print("\n== 6. Coordinator crashes mid-broadcast: peers can help")
    s = TwoPhaseCommit.create()
    s.run("T1", writes, crash="coordinator_mid_broadcast")
    show(s)
    s.events.clear()
    s.cooperative_termination("payments", "T1")
    s.cooperative_termination("inventory", "T1")
    print("  " + "\n  ".join(s.events))
    show(s)


if __name__ == "__main__":
    demo()
