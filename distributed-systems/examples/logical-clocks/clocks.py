"""Logical clocks (Chapter 3): Lamport clocks, vector clocks and hybrid logical clocks.

Distributed processes have no shared clock, so "which happened first?" has to
be answered from the messages they exchange. Lamport's *happened-before*
relation (written a -> b) is the smallest relation such that

  1. if a and b are on the same process and a comes first, then a -> b;
  2. if a is the sending of a message and b its receipt, then a -> b;
  3. if a -> b and b -> c, then a -> c (transitivity).

Two distinct events with neither a -> b nor b -> a are *concurrent* (a || b).

This module provides:

  LamportClock        a single counter; guarantees a -> b  implies  L(a) < L(b)
  VectorClock         one counter per process; a -> b  iff  V(a) < V(b)
  HybridLogicalClock  physical time plus a logical counter (HLC)
  simulate()          a random message-passing run that records every clock
  ground_truth()      happened-before computed directly from the event graph

Run `python3 clocks.py` for a demonstration.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Lamport clocks
# ---------------------------------------------------------------------------


class LamportClock:
    """A scalar logical clock.

    Rules: increment before every event; a message carries the sender's value;
    on receipt, set the clock to max(local, received) and then increment.
    """

    def __init__(self) -> None:
        self.time = 0

    def tick(self) -> int:
        """A local event (including a send)."""
        self.time += 1
        return self.time

    def send(self) -> int:
        return self.tick()

    def receive(self, message_time: int) -> int:
        self.time = max(self.time, message_time) + 1
        return self.time


# ---------------------------------------------------------------------------
# Vector clocks
# ---------------------------------------------------------------------------

BEFORE, AFTER, EQUAL, CONCURRENT = "before", "after", "equal", "concurrent"


class VectorClock:
    """A vector of counters, one per process, held by process `pid`.

    Entry i counts the events of process i that this process knows about.
    """

    def __init__(self, pid: int, n: int) -> None:
        self.pid = pid
        self.v = [0] * n

    def tick(self) -> tuple[int, ...]:
        self.v[self.pid] += 1
        return tuple(self.v)

    def send(self) -> tuple[int, ...]:
        return self.tick()

    def receive(self, message_v: tuple[int, ...]) -> tuple[int, ...]:
        # Take the element-wise maximum (everything the sender knew), then count the receive.
        self.v = [max(a, b) for a, b in zip(self.v, message_v)]
        return self.tick()


def compare(a: tuple[int, ...], b: tuple[int, ...]) -> str:
    """Compare two vector timestamps.

    a < b  (BEFORE)  when every entry of a is <= the matching entry of b and
    at least one is strictly smaller. If neither a <= b nor b <= a, the
    events are CONCURRENT.
    """
    le = all(x <= y for x, y in zip(a, b))
    ge = all(x >= y for x, y in zip(a, b))
    if le and ge:
        return EQUAL
    if le:
        return BEFORE
    if ge:
        return AFTER
    return CONCURRENT


def happened_before(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    return compare(a, b) == BEFORE


# ---------------------------------------------------------------------------
# A simulated execution
# ---------------------------------------------------------------------------


@dataclass
class Event:
    eid: int                 # global index, in simulation order
    pid: int                 # process on which the event happened
    kind: str                # "local", "send" or "recv"
    lamport: int
    vector: tuple[int, ...]
    msg: int | None = None   # message id for send/recv events
    label: str = ""

    def __str__(self) -> str:
        return f"{self.label:<4} P{self.pid} {self.kind:<5} L={self.lamport:<3} V={list(self.vector)}"


@dataclass
class Execution:
    n: int
    events: list[Event] = field(default_factory=list)
    send_of: dict[int, int] = field(default_factory=dict)   # msg id -> eid of send
    recv_of: dict[int, int] = field(default_factory=dict)   # msg id -> eid of receive


def simulate(n: int = 3, steps: int = 20, seed: int = 1, p_send: float = 0.4,
             p_local: float = 0.3) -> Execution:
    """Run a random message-passing execution among `n` processes.

    At each step a random process does one thing: a local event, a send to a
    random peer, or the receipt of one of the messages waiting for it (chosen
    at random, so channels may reorder). Undelivered messages are delivered
    at the end so every send has a matching receive.
    """
    rng = random.Random(seed)
    lam = [LamportClock() for _ in range(n)]
    vec = [VectorClock(i, n) for i in range(n)]
    ex = Execution(n)
    in_flight: list[tuple[int, int, int, tuple[int, ...]]] = []  # (msg, dest, lamport, vector)
    next_msg = 0
    counters = [0] * n

    def record(pid: int, kind: str, l: int, v: tuple[int, ...], msg: int | None) -> None:
        counters[pid] += 1
        label = "abcdefghijklmnopqrstuvwxyz"[pid % 26] + str(counters[pid])
        ex.events.append(Event(len(ex.events), pid, kind, l, v, msg, label))

    def deliver(index: int) -> None:
        msg, dest, l, v = in_flight.pop(index)
        record(dest, "recv", lam[dest].receive(l), vec[dest].receive(v), msg)
        ex.recv_of[msg] = len(ex.events) - 1

    for _ in range(steps):
        pid = rng.randrange(n)
        waiting = [i for i, m in enumerate(in_flight) if m[1] == pid]
        r = rng.random()
        if waiting and r >= p_send + p_local:
            deliver(rng.choice(waiting))
        elif r < p_send and n > 1:
            dest = rng.choice([p for p in range(n) if p != pid])
            l, v = lam[pid].send(), vec[pid].send()
            record(pid, "send", l, v, next_msg)
            ex.send_of[next_msg] = len(ex.events) - 1
            in_flight.append((next_msg, dest, l, v))
            next_msg += 1
        else:
            record(pid, "local", lam[pid].tick(), vec[pid].tick(), None)
    while in_flight:
        deliver(rng.randrange(len(in_flight)))
    return ex


def ground_truth(ex: Execution) -> list[set[int]]:
    """Happened-before computed from the event graph, without any clock.

    Returns `succ` where succ[e] is the set of event ids f with e -> f.
    Edges are program order (each event to the next on its process) and
    message edges (send to receive); we then take the transitive closure.
    Simulation order is a topological order, so one backwards pass suffices.
    """
    direct: list[list[int]] = [[] for _ in ex.events]
    last_on: dict[int, int] = {}
    for e in ex.events:
        if e.pid in last_on:
            direct[last_on[e.pid]].append(e.eid)
        last_on[e.pid] = e.eid
    for msg, s in ex.send_of.items():
        direct[s].append(ex.recv_of[msg])
    succ: list[set[int]] = [set() for _ in ex.events]
    for e in reversed(range(len(ex.events))):
        for f in direct[e]:
            succ[e].add(f)
            succ[e] |= succ[f]
    return succ


# ---------------------------------------------------------------------------
# Hybrid logical clocks
# ---------------------------------------------------------------------------


class HybridLogicalClock:
    """Hybrid logical clock (Kulkarni et al., 2014).

    A timestamp is a pair (l, c): l is the largest physical time this process
    has heard of, and c is a logical counter that breaks ties when l does not
    advance. HLC timestamps (compared as tuples) respect happened-before like
    a Lamport clock, yet l stays within the clock skew of real physical time,
    so they can be read as approximate wall-clock times.

    `physical` is a zero-argument function returning this node's (possibly
    skewed) physical clock reading.
    """

    def __init__(self, physical) -> None:
        self.physical = physical
        self.l = 0
        self.c = 0

    def now(self) -> tuple[int, int]:
        """A local or send event."""
        pt = self.physical()
        if pt > self.l:
            self.l, self.c = pt, 0
        else:
            self.c += 1
        return (self.l, self.c)

    send = now

    def receive(self, msg: tuple[int, int]) -> tuple[int, int]:
        ml, mc = msg
        pt = self.physical()
        new_l = max(self.l, ml, pt)
        if new_l == self.l and new_l == ml:
            self.c = max(self.c, mc) + 1
        elif new_l == self.l:
            self.c += 1
        elif new_l == ml:
            self.c = mc + 1
        else:
            self.c = 0
        self.l = new_l
        return (self.l, self.c)


@dataclass
class HLCEvent:
    pid: int
    kind: str
    true_time: int          # simulator's "real" time, invisible to the processes
    physical: int           # what the process's own clock read
    hlc: tuple[int, int]
    msg: int | None = None


def simulate_hlc(n: int = 3, steps: int = 40, seed: int = 1, max_skew: int = 50,
                 p_send: float = 0.5, max_delay: int = 5) -> tuple[list[HLCEvent], dict, dict]:
    """A random run where each process's physical clock is offset by up to
    `max_skew` time units from true time. True time advances by 1 to 3 units
    per step; messages take 1 to `max_delay` units to arrive.

    Returns (events, send_index, recv_index) where the indices map message id
    to the position of its send and receive events.
    """
    rng = random.Random(seed)
    offsets = [rng.randint(-max_skew, max_skew) for _ in range(n)]
    true_time = 1000

    def clock(pid: int):
        return lambda: true_time + offsets[pid]

    hlcs = [HybridLogicalClock(clock(i)) for i in range(n)]
    events: list[HLCEvent] = []
    in_flight: list[tuple[int, int, int, tuple[int, int]]] = []   # (arrival, msg, dest, ts)
    sends: dict[int, int] = {}
    recvs: dict[int, int] = {}
    next_msg = 0
    for _ in range(steps):
        true_time += rng.randint(1, 3)
        due = [m for m in in_flight if m[0] <= true_time]
        if due and rng.random() < 0.5:
            m = rng.choice(due)
            in_flight.remove(m)
            _, msg, dest, ts = m
            phys = hlcs[dest].physical()
            events.append(HLCEvent(dest, "recv", true_time, phys, hlcs[dest].receive(ts), msg))
            recvs[msg] = len(events) - 1
            continue
        pid = rng.randrange(n)
        phys = hlcs[pid].physical()
        if rng.random() < p_send and n > 1:
            dest = rng.choice([p for p in range(n) if p != pid])
            ts = hlcs[pid].send()
            events.append(HLCEvent(pid, "send", true_time, phys, ts, next_msg))
            sends[next_msg] = len(events) - 1
            in_flight.append((true_time + rng.randint(1, max_delay), next_msg, dest, ts))
            next_msg += 1
        else:
            events.append(HLCEvent(pid, "local", true_time, phys, hlcs[pid].now()))
    for arrival, msg, dest, ts in sorted(in_flight):
        true_time = max(true_time, arrival)
        phys = hlcs[dest].physical()
        events.append(HLCEvent(dest, "recv", true_time, phys, hlcs[dest].receive(ts), msg))
        recvs[msg] = len(events) - 1
    return events, sends, recvs


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------


def _demo() -> None:
    ex = simulate(n=3, steps=14, seed=7)
    print("A random run of 3 processes (L = Lamport, V = vector clock)\n")
    for e in ex.events:
        extra = f"  msg m{e.msg}" if e.msg is not None else ""
        print(f"  {e}{extra}")

    succ = ground_truth(ex)
    pairs = [(a, b) for a in ex.events for b in ex.events if a.eid < b.eid]
    causal = sum(1 for a, b in pairs if b.eid in succ[a.eid] or a.eid in succ[b.eid])
    concurrent = len(pairs) - causal
    print(f"\n{len(pairs)} pairs of events: {causal} causally related, {concurrent} concurrent")

    # Lamport: a -> b implies L(a) < L(b), but L(a) < L(b) does not imply a -> b.
    misleading = [(a, b) for a, b in pairs
                  if b.eid not in succ[a.eid] and a.eid not in succ[b.eid] and a.lamport != b.lamport]
    print(f"Concurrent pairs whose Lamport times differ (Lamport makes them *look* ordered): "
          f"{len(misleading)} of {concurrent}")
    if misleading:
        a, b = misleading[0]
        lo, hi = (a, b) if a.lamport < b.lamport else (b, a)
        print(f"  e.g. {lo.label} (L={lo.lamport}) and {hi.label} (L={hi.lamport}): "
              f"vector clocks say {compare(lo.vector, hi.vector)}")

    agree = sum(1 for a, b in pairs
                if (compare(a.vector, b.vector) == BEFORE) == (b.eid in succ[a.eid])
                and (compare(a.vector, b.vector) == CONCURRENT)
                == (b.eid not in succ[a.eid] and a.eid not in succ[b.eid]))
    print(f"Vector-clock verdict matches the event graph for {agree} of {len(pairs)} pairs")

    print("\nHybrid logical clocks with physical clocks skewed by up to +/-50 units")
    events, sends, recvs = simulate_hlc(n=3, steps=40, seed=3, max_skew=50)
    phys_violations = sum(1 for m in sends if events[recvs[m]].physical <= events[sends[m]].physical)
    hlc_violations = sum(1 for m in sends if events[recvs[m]].hlc <= events[sends[m]].hlc)
    drift = max(e.hlc[0] - e.physical for e in events)
    print(f"  {len(sends)} messages; receive stamped no later than send by physical clocks: "
          f"{phys_violations}; by HLC: {hlc_violations}")
    print(f"  largest gap between HLC l and the local physical clock: {drift} units "
          f"(bounded by the skew between clocks, here at most 100)")
    print(f"  largest logical counter c: {max(e.hlc[1] for e in events)}")


if __name__ == "__main__":
    _demo()
