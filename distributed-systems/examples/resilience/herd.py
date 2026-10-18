"""Thundering herd: why jitter matters when clients fail together (Chapter 17).

``simulation.py`` shows that jitter alone does not stop a retry storm: the
problem there is *how much* extra work retries add, and only budgets,
shedding and deadlines limit that. Jitter solves a different problem:
*synchronisation*. When many clients fail at the same moment (a dropped
connection pool, a restart, a lock released), plain exponential backoff
makes them all retry at the same instants again, so they collide again.

This model reproduces the experiment in Marc Brooker's "Exponential Backoff
and Jitter" (AWS Architecture Blog, 2015): ``clients`` callers all start at
t = 0; the server accepts at most ``capacity`` calls in each ``slot`` of
time and rejects the rest; rejected callers back off and try again until
they succeed. We count total calls (work) and the time until the last
client succeeds (completion time).
"""

from __future__ import annotations

import heapq
import random
from collections import Counter
from dataclasses import dataclass

from components import next_backoff


@dataclass(frozen=True)
class HerdResult:
    policy: str
    calls: int
    completion: float           # seconds until the last client succeeded
    clients: int

    @property
    def calls_per_client(self) -> float:
        return self.calls / self.clients


def thundering_herd(policy: str, clients: int = 200, capacity: int = 10,
                    slot: float = 0.01, base: float = 0.01, cap: float = 1.0,
                    seed: int = 1, max_calls: int = 1_000_000) -> HerdResult:
    rng = random.Random(seed)
    # (time, client, retry number, previous delay)
    events = [(0.0, c, 0, None) for c in range(clients)]
    heapq.heapify(events)
    accepted: Counter[int] = Counter()
    calls, completion = 0, 0.0
    while events:
        t, client, retry, prev = heapq.heappop(events)
        calls += 1
        if calls > max_calls:
            raise RuntimeError("herd did not settle")
        s = int(t / slot)
        if accepted[s] < capacity:
            accepted[s] += 1
            completion = max(completion, t)
            continue
        delay = next_backoff(policy, retry + 1, base, cap, rng, prev)
        heapq.heappush(events, (t + delay, client, retry + 1, delay))
    return HerdResult(policy, calls, completion, clients)


if __name__ == "__main__":
    print("200 clients fail together; the server accepts 10 calls per 10 ms slot.")
    print("Backoff base 10 ms, cap 1 s. Calls = total work; completion = time to drain.\n")
    print(f"{'policy':<22}{'calls':>8}{'calls/client':>14}{'completion (s)':>16}")
    for policy in ("constant", "exponential", "full_jitter", "equal_jitter",
                   "decorrelated_jitter"):
        r = thundering_herd(policy)
        print(f"{policy:<22}{r.calls:>8}{r.calls_per_client:>14.1f}{r.completion:>16.2f}")
