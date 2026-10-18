"""Generate histories from a simulated replicated register (Chapters 8 and 23).

One leader and two followers hold a register. Writes and compare-and-set
operations go to the leader, which applies them immediately and then
replicates them to each follower after a random *replication lag*.

Reads are where the configurable bug lives:

* ``follower_reads=False`` (correct): every read is served by the leader.
  Each operation takes effect at one instant inside its interval, on one
  copy of the data, so every history is linearizable by construction.
* ``follower_reads=True`` (buggy): a read may be served by any replica,
  including a follower that has not caught up. Fast, and a popular
  optimisation, but a read can now miss a write that finished before it
  began: a *stale read*.

This is how tools such as Jepsen work: run random concurrent operations
against the system, record the history, and hand it to a checker.

Run ``python3 simulate.py`` for a summary over 200 seeds and one caught
violation drawn as a timeline.
"""

import heapq
import random
import sys
from dataclasses import dataclass
from typing import List

from checker import check_linearizable, check_sequentially_consistent
from history import Op, render


@dataclass
class SimConfig:
    clients: int = 3
    ops_per_client: int = 8
    follower_reads: bool = False
    followers: int = 2
    network_delay: tuple = (1.0, 5.0)    # one-way client <-> replica, uniform
    replication_lag: tuple = (1.0, 10.0)  # leader -> follower, uniform
    think_time: tuple = (0.0, 10.0)      # pause between a client's operations
    cas_fraction: float = 0.1
    write_fraction: float = 0.4


class Replica:
    """A copy of the register that applies the leader's writes in order."""

    def __init__(self, name: str):
        self.name = name
        self.value = 0
        self.applied = 0            # how many log entries applied
        self.arrived = {}           # log index -> value, waiting to be applied

    def receive(self, index: int, value) -> None:
        self.arrived[index] = value
        while self.applied + 1 in self.arrived:
            self.applied += 1
            self.value = self.arrived.pop(self.applied)


def generate_history(seed: int, config: SimConfig = None) -> List[Op]:
    """Run one simulation and return its history. Deterministic per seed."""
    cfg = config or SimConfig()
    rng = random.Random(seed)
    leader = Replica("leader")
    followers = [Replica(f"follower{i + 1}") for i in range(cfg.followers)]
    log: List = []                  # the leader's replication log of values
    next_value = 1                  # writes use fresh values: easier to read
    history: List[Op] = []
    events: list = []               # (time, sequence, action, payload)
    counter = 0

    def schedule(time: float, action: str, payload) -> None:
        nonlocal counter
        heapq.heappush(events, (time, counter, action, payload))
        counter += 1

    def delay(bounds) -> float:
        return round(rng.uniform(*bounds), 2)

    remaining = {f"C{i}": cfg.ops_per_client for i in range(cfg.clients)}
    for client in remaining:
        schedule(delay(cfg.think_time), "invoke", client)

    while events:
        now, _, action, payload = heapq.heappop(events)
        if action == "invoke":
            client = payload
            remaining[client] -= 1
            r = rng.random()
            if r < cfg.cas_fraction:
                kind, arg = "cas", (rng.choice([0] + list(range(1, next_value))), next_value)
                next_value += 1
            elif r < cfg.cas_fraction + cfg.write_fraction:
                kind, arg = "write", next_value
                next_value += 1
            else:
                kind, arg = "read", None
            if kind == "read" and cfg.follower_reads:
                replica = rng.choice([leader] + followers)
            else:
                replica = leader
            request = {"client": client, "kind": kind, "arg": arg, "call": now, "replica": replica}
            schedule(now + delay(cfg.network_delay), "serve", request)
        elif action == "serve":
            request = payload
            replica, kind = request["replica"], request["kind"]
            # This instant is the operation's linearization point.
            if kind == "read":
                result = replica.value
            elif kind == "write":
                result = None
                _leader_apply(leader, log, request["arg"], followers, now, schedule, delay, cfg)
            else:
                expected, new = request["arg"]
                result = leader.value == expected
                if result:
                    _leader_apply(leader, log, new, followers, now, schedule, delay, cfg)
            request["result"] = result
            schedule(now + delay(cfg.network_delay), "respond", request)
        elif action == "respond":
            request = payload
            history.append(Op(request["client"], request["kind"], request["arg"],
                              request["result"], request["call"], now))
            if remaining[request["client"]] > 0:
                schedule(now + delay(cfg.think_time), "invoke", request["client"])
        elif action == "replicate":
            follower, index, value = payload
            follower.receive(index, value)
    return history


def _leader_apply(leader, log, value, followers, now, schedule, delay, cfg) -> None:
    log.append(value)
    leader.receive(len(log), value)
    for follower in followers:
        schedule(now + delay(cfg.replication_lag), "replicate", (follower, len(log), value))


def shrink(history: List[Op], init=0) -> List[Op]:
    """Remove operations one at a time while the history stays non-linearizable.

    This is the *shrinking* step of property-based testing: a 24-operation
    failure is hard to read, a 3-operation one explains itself. An operation
    is only removed if every value still read was still written by someone,
    so the result never blames a read for a write we deleted.
    """
    ops = list(history)
    assert not check_linearizable(ops, init).ok, "history is already linearizable"
    changed = True
    while changed:
        changed = False
        for op in list(ops):
            candidate = [o for o in ops if o is not op]
            if _reads_explained(candidate, init) and not check_linearizable(candidate, init).ok:
                ops = candidate
                changed = True
    return ops


def _reads_explained(ops: List[Op], init) -> bool:
    written = {init}
    for o in ops:
        if o.kind == "write":
            written.add(o.arg)
        elif o.kind == "cas" and o.result:
            written.add(o.arg[1])
    return all(o.result in written for o in ops if o.kind == "read")


def survey(seeds: range, follower_reads: bool, config: SimConfig = None):
    """Check many generated histories. Returns (violating seeds, SC failures)."""
    cfg = config or SimConfig()
    cfg.follower_reads = follower_reads
    bad, not_sc = [], []
    for seed in seeds:
        history = generate_history(seed, cfg)
        if not check_linearizable(history).ok:
            bad.append(seed)
            if not check_sequentially_consistent(history).ok:
                not_sc.append(seed)
    return bad, not_sc


def main(argv) -> None:
    runs = int(argv[0]) if argv else 200
    seeds = range(runs)
    good, _ = survey(seeds, follower_reads=False)
    bad, not_sc = survey(seeds, follower_reads=True)
    print(f"{runs} histories each: 3 clients x 8 operations, 1 leader + 2 followers\n")
    print(f"leader reads:   {len(good):3d} / {runs} not linearizable")
    print(f"follower reads: {len(bad):3d} / {runs} not linearizable "
          f"(first seeds: {bad[:8]})")
    print(f"                {len(not_sc):3d} of those not even sequentially consistent\n")
    if bad:
        seed = bad[0]
        history = generate_history(seed, SimConfig(follower_reads=True))
        result = check_linearizable(history)
        small = shrink(history)
        print(f"seed {seed}: {len(history)} operations, {result.explored} search nodes; "
              f"shrunk to {len(small)} operations:\n")
        print(render(small, width=50))


if __name__ == "__main__":
    main(sys.argv[1:])
