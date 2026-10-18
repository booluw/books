"""Gossip: spreading a rumour, and gossip-style membership (Chapter 2).

Gossip (or epidemic) protocols spread information the way rumours spread:
in each round, every node talks to one peer chosen at random. No node needs
to know the whole cluster's state, no node is special, and lost messages or
crashed nodes only slow things down a little. The surprise is how fast it
is: a rumour reaches all N nodes in O(log N) rounds.

Three styles of exchange, in synchronous rounds:

  push       every node that knows the rumour sends it to a random peer
  pull       every node that does not know it asks a random peer
  push-pull  every node contacts a random peer and they exchange what they know

Push is fast while few nodes know (each informed node recruits one more) but
slow at the end (most pushes hit nodes that already know). Pull is the
reverse. Push-pull gets the best of both.

The second half is gossip-style failure detection (van Renesse, Minsky and
Hayden, 1998): every node keeps a heartbeat counter for every member and
gossips the whole table. A member whose counter has not grown for `t_fail`
rounds is suspected to have crashed.

Run `python3 gossip.py` for a demonstration.
"""
from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass

MODES = ("push", "pull", "push-pull")


# ---------------------------------------------------------------------------
# Rumour spreading
# ---------------------------------------------------------------------------


def spread(n: int, mode: str = "push-pull", loss: float = 0.0, seed: int = 0,
           max_rounds: int = 1000) -> list[int]:
    """Spread one rumour from node 0. Returns the informed count after each round.

    The list starts with 1 (before round 1). Its length minus one is the
    number of rounds taken; if it ends below n, max_rounds ran out.
    Each message is lost independently with probability `loss`.
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    rng = random.Random(seed)
    informed = [False] * n
    informed[0] = True
    count = 1
    history = [1]

    def peer(i: int) -> int:
        j = rng.randrange(n - 1)
        return j if j < i else j + 1           # uniform over the other n-1 nodes

    while count < n and len(history) <= max_rounds:
        before = informed[:]                   # synchronous: act on start-of-round state
        for i in range(n):
            j = peer(i)
            delivered = rng.random() >= loss
            if not delivered:
                continue
            if mode in ("push", "push-pull") and before[i] and not informed[j]:
                informed[j] = True
                count += 1
            if mode in ("pull", "push-pull") and before[j] and not informed[i]:
                informed[i] = True
                count += 1
        history.append(count)
    return history


def rounds_to_spread(n: int, mode: str = "push-pull", loss: float = 0.0, seed: int = 0) -> int:
    history = spread(n, mode, loss, seed)
    if history[-1] < n:
        raise RuntimeError("rumour did not reach every node")
    return len(history) - 1


def mean_rounds(n: int, mode: str, trials: int = 30, loss: float = 0.0) -> float:
    return statistics.mean(rounds_to_spread(n, mode, loss, seed) for seed in range(trials))


# ---------------------------------------------------------------------------
# Gossip-style membership and failure detection
# ---------------------------------------------------------------------------


@dataclass
class MembershipResult:
    first_detected: int | None    # rounds after the crash until some live node suspects it for good
    all_detected: int | None      # ... until every live node does
    false_rate: float             # fraction of (observer, live member, round) checks wrongly suspecting


def gossip_membership(n: int = 32, t_fail: int = 10, loss: float = 0.0, seed: int = 0,
                      crash_round: int = 40, rounds: int = 120) -> MembershipResult:
    """Gossip heartbeat tables among n nodes; node n-1 crashes at `crash_round`.

    Each round every live node increments its own heartbeat and pushes its
    table to one random member. The receiver keeps, per member, the larger
    heartbeat, noting the round it last increased. A member is suspected
    when its heartbeat has not increased for more than t_fail rounds.

    An observer has *detected* the crash from the first round after which it
    suspects the crashed node in every remaining round. `rounds` must leave
    time for that: the default 80 rounds after the crash is plenty for t_fail
    up to about 30.
    """
    rng = random.Random(seed)
    victim = n - 1
    heartbeat = [[0] * n for _ in range(n)]     # heartbeat[i][j]: i's view of j's counter
    updated = [[0] * n for _ in range(n)]       # round in which i last saw j's counter rise
    alive = [True] * n
    last_trusted = [crash_round - 1] * n        # last round i did NOT suspect the victim
    checks = wrong = 0

    for rnd in range(1, rounds + 1):
        if rnd == crash_round:
            alive[victim] = False
        messages = []
        for i in range(n):
            if not alive[i]:
                continue
            heartbeat[i][i] += 1
            updated[i][i] = rnd
            j = rng.randrange(n - 1)
            j = j if j < i else j + 1
            if rng.random() >= loss:
                messages.append((j, heartbeat[i][:]))
        for j, table in messages:
            if not alive[j]:
                continue                        # sent to a crashed node: wasted
            for m, hb in enumerate(table):
                if hb > heartbeat[j][m]:
                    heartbeat[j][m] = hb
                    updated[j][m] = rnd
        for i in range(n):
            if not alive[i]:
                continue
            for m in range(n):
                if m == i:
                    continue
                suspected = rnd - updated[i][m] > t_fail
                if alive[m]:
                    checks += 1
                    wrong += suspected
                elif not suspected:
                    last_trusted[i] = rnd

    live = [i for i in range(n) if alive[i]]
    detect = [last_trusted[i] + 1 - crash_round for i in live if last_trusted[i] < rounds]
    complete = len(detect) == len(live)
    return MembershipResult(min(detect) if detect else None,
                            max(detect) if complete else None,
                            wrong / checks)


def _demo() -> None:
    print("Rounds for one rumour to reach every node (mean of 30 runs, no loss)\n")
    print(f"  {'N':>6} {'log2 N':>7} {'push':>7} {'pull':>7} {'push-pull':>10}")
    for n in (16, 64, 256, 1024, 4096):
        cells = [f"{mean_rounds(n, m):7.1f}" for m in MODES]
        print(f"  {n:>6} {math.log2(n):7.1f} {cells[0]} {cells[1]} {cells[2]:>10}")

    print("\nOne run, N=1024, informed nodes after each round:")
    for mode in MODES:
        print(f"  {mode:<9} {spread(1024, mode, seed=1)}")

    print("\nMessage loss, N=1024, push-pull (mean of 30 runs):")
    for loss in (0.0, 0.1, 0.25, 0.5):
        print(f"  loss {loss:4.0%}: {mean_rounds(1024, 'push-pull', loss=loss):5.1f} rounds")

    print("\nGossip-style failure detection, N=32, node 31 crashes at round 40, 10 runs each.")
    print("Detection is in rounds after the crash; false rate is the share of checks on live")
    print("members that wrongly suspected them.\n")
    print(f"  {'t_fail':>6} {'loss':>5} {'first detect':>13} {'all detect':>11} {'false rate':>11}")
    for loss in (0.0, 0.2):
        for t_fail in (4, 6, 8, 10, 14, 20):
            rs = [gossip_membership(32, t_fail, loss, seed=s) for s in range(10)]
            first = statistics.mean(r.first_detected for r in rs)
            every = statistics.mean(r.all_detected for r in rs)
            fp = statistics.mean(r.false_rate for r in rs)
            print(f"  {t_fail:>6} {loss:>5.0%} {first:>13.1f} {every:>11.1f} {fp:>11.3%}")


if __name__ == "__main__":
    _demo()
