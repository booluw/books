"""Chandy-Lamport distributed snapshots over FIFO channels (Chapter 16).

Three processes (think: bank branches) hold balances and keep sending money
to each other. We want a **global snapshot**: every balance *and* every
transfer in flight, as of one consistent moment, without stopping the system.
Reading each balance at a slightly different time gets the total wrong,
because money in transit is counted twice or not at all.

The Chandy-Lamport algorithm (K. Mani Chandy and Leslie Lamport, 1985):

1. The initiator records its own state and sends a **marker** on every
   outgoing channel.
2. When a process receives a marker on channel c:
   - if it has not yet recorded its state, it records it now, records
     channel c as empty, starts recording every *other* incoming channel,
     and sends a marker on every outgoing channel;
   - otherwise it stops recording channel c. The channel's state is the
     messages that arrived on c between recording and the marker.
3. The snapshot is complete when every process has received a marker on
   every incoming channel.

It needs **FIFO channels** (messages on one channel arrive in the order they
were sent): the marker then separates "sent before the sender's snapshot"
from "sent after". Flink's checkpoints use a variant of this algorithm
(asynchronous barrier snapshotting) with barriers playing the part of markers.
"""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field

MARKER = "MARKER"


@dataclass
class Process:
    pid: int
    balance: int
    recorded_balance: int | None = None
    recording: set = field(default_factory=set)        # incoming channels being recorded
    channel_state: dict = field(default_factory=dict)  # channel -> list of amounts
    done_channels: set = field(default_factory=set)
    sent: list = field(default_factory=list)           # message ids sent
    received: list = field(default_factory=list)       # message ids received
    sent_at_record: frozenset = frozenset()
    received_at_record: frozenset = frozenset()


@dataclass
class Snapshot:
    balances: dict
    channels: dict          # (src, dst) -> list of amounts in flight

    @property
    def total(self) -> int:
        return sum(self.balances.values()) + sum(sum(v) for v in self.channels.values())


class Bank:
    """N processes, a FIFO channel for every ordered pair, a seeded scheduler."""

    def __init__(self, n: int = 3, initial: int = 1_000, seed: int = 0, fifo: bool = True):
        self.rng = random.Random(seed)
        self.fifo = fifo
        self.procs = [Process(i, initial) for i in range(n)]
        self.channels = {(i, j): deque() for i in range(n) for j in range(n) if i != j}
        self.invariant = n * initial
        self.next_msg = 0
        self.messages: dict[int, tuple[int, int, int]] = {}   # id -> (src, dst, amount)
        self.trace: list[str] = []

    # ---- actions ----------------------------------------------------------
    def send_money(self, src: int, dst: int, amount: int) -> None:
        p = self.procs[src]
        p.balance -= amount
        mid = self.next_msg
        self.next_msg += 1
        p.sent.append(mid)
        self.messages[mid] = (src, dst, amount)
        self.channels[(src, dst)].append((mid, amount))
        self.trace.append(f"P{src} sends {amount} to P{dst} (m{mid})")

    def _record(self, p: Process, skip_channel=None) -> None:
        p.recorded_balance = p.balance
        p.sent_at_record = frozenset(p.sent)
        p.received_at_record = frozenset(p.received)
        for c in self.channels:
            if c[1] == p.pid:
                p.channel_state[c] = []
                if c != skip_channel:
                    p.recording.add(c)
        if skip_channel is not None:
            p.done_channels.add(skip_channel)
        for c in self.channels:
            if c[0] == p.pid:
                self.channels[c].append(MARKER)
        self.trace.append(f"P{p.pid} records balance {p.balance} and sends markers")

    def initiate_snapshot(self, pid: int = 0) -> None:
        self._record(self.procs[pid])

    def deliver(self, channel) -> None:
        q = self.channels[channel]
        if self.fifo:
            msg = q.popleft()
        else:                                   # a channel that may reorder messages
            idx = self.rng.randrange(len(q))
            msg = q[idx]
            del q[idx]
        p = self.procs[channel[1]]
        if msg == MARKER:
            if p.recorded_balance is None:
                self._record(p, skip_channel=channel)
            else:
                p.recording.discard(channel)
                p.done_channels.add(channel)
            self.trace.append(f"P{p.pid} gets marker from P{channel[0]}")
            return
        mid, amount = msg
        p.balance += amount
        p.received.append(mid)
        if channel in p.recording:
            p.channel_state[channel].append(amount)
        self.trace.append(f"P{p.pid} receives {amount} from P{channel[0]} (m{mid})")

    # ---- scheduler --------------------------------------------------------
    def step(self) -> None:
        """One random action: a transfer, or one delivery on a non-empty channel."""
        busy = [c for c, q in self.channels.items() if q]
        if busy and self.rng.random() < 0.5:
            self.deliver(self.rng.choice(busy))
            return
        src = self.rng.randrange(len(self.procs))
        if self.procs[src].balance <= 0:
            return
        dst = self.rng.choice([j for j in range(len(self.procs)) if j != src])
        self.send_money(src, dst, self.rng.randint(1, min(100, self.procs[src].balance)))

    def snapshot_complete(self) -> bool:
        incoming = {p.pid: {c for c in self.channels if c[1] == p.pid} for p in self.procs}
        return all(p.recorded_balance is not None and p.done_channels >= incoming[p.pid]
                   for p in self.procs)

    def result(self) -> Snapshot:
        return Snapshot({p.pid: p.recorded_balance for p in self.procs},
                        {c: list(self.procs[c[1]].channel_state[c]) for c in self.channels})

    def is_consistent_cut(self) -> bool:
        """Every message received before the cut was also sent before it."""
        sent_before = set().union(*(p.sent_at_record for p in self.procs))
        return all(p.received_at_record <= sent_before for p in self.procs)


def run_snapshot(seed: int, steps: int = 200, fifo: bool = True, n: int = 3) -> tuple[Bank, Snapshot]:
    """Run traffic, start a snapshot at a random step, keep going until it completes."""
    bank = Bank(n=n, seed=seed, fifo=fifo)
    start = bank.rng.randrange(steps // 4, steps // 2)
    initiator = bank.rng.randrange(n)
    for i in range(steps):
        if i == start:
            bank.initiate_snapshot(initiator)
        bank.step()
    while not bank.snapshot_complete():                # traffic carries on meanwhile
        bank.step()
    return bank, bank.result()


def naive_snapshot(seed: int, steps: int = 200, n: int = 3) -> int:
    """Read each balance at a different moment and ignore channels."""
    bank = Bank(n=n, seed=seed)
    read_at = sorted(bank.rng.sample(range(steps // 4, steps), n))
    seen = {}
    for i in range(steps):
        for pid, t in enumerate(read_at):
            if t == i:
                seen[pid] = bank.procs[pid].balance
        bank.step()
    return sum(seen.values())


if __name__ == "__main__":
    bank, snap = run_snapshot(seed=3, steps=40)
    print("One snapshot (seed 3), with three processes starting at 1,000 each\n")
    print("Recorded balances: " + ", ".join(f"P{p}={b}" for p, b in snap.balances.items()))
    for c, amounts in snap.channels.items():
        if amounts:
            print(f"In flight on P{c[0]}->P{c[1]}: {amounts}")
    print(f"Total: {snap.total} (invariant {bank.invariant}); consistent cut: "
          f"{bank.is_consistent_cut()}\n")

    runs = 1_000
    rows = []
    for label, fn in [("Chandy-Lamport, FIFO channels",
                       lambda s: run_snapshot(s)[1].total),
                      ("Chandy-Lamport, reordering channels",
                       lambda s: run_snapshot(s, fifo=False)[1].total),
                      ("naive: read balances one by one",
                       lambda s: naive_snapshot(s))]:
        totals = [fn(s) for s in range(runs)]
        wrong = [t for t in totals if t != 3_000]
        worst = max((abs(t - 3_000) for t in wrong), default=0)
        rows.append((label, len(wrong), worst))
    print(f"{runs} randomised runs each; the true total is always 3,000\n")
    print(f"{'method':<38}{'wrong totals':>13}{'worst error':>13}")
    for label, wrong, worst in rows:
        print(f"{label:<38}{wrong:>13}{worst:>13}")
