"""A deterministic discrete-event simulator and a faulty network (Chapter 11).

Real distributed systems are hard to test because the interesting bugs
depend on timing: which message arrives first, which node crashes when.
A *discrete-event simulation* replaces real time with a virtual clock and a
priority queue of future events. Running an event may schedule more events.
Every random choice comes from one seeded ``random.Random``, so a seed
reproduces a run exactly, including the bug it found. FoundationDB and
TigerBeetle test their production code this way ("deterministic simulation
testing").

The network can delay, lose, duplicate and reorder messages (reordering
falls out of random delays), and can be split into partitions.
"""

import heapq
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Set


class Scheduler:
    """A virtual clock (milliseconds) and a queue of timed callbacks."""

    def __init__(self) -> None:
        self.now: float = 0.0
        self._queue: list = []
        self._seq = 0          # tie-breaker: equal times run in scheduling order
        self.steps = 0

    def at(self, time: float, fn: Callable, *args: Any) -> None:
        heapq.heappush(self._queue, (time, self._seq, fn, args))
        self._seq += 1

    def after(self, delay: float, fn: Callable, *args: Any) -> None:
        self.at(self.now + delay, fn, *args)

    def step(self) -> bool:
        """Run the next event. Returns False when nothing is left."""
        if not self._queue:
            return False
        self.now, _, fn, args = heapq.heappop(self._queue)
        self.steps += 1
        fn(*args)
        return True

    def next_time(self) -> Optional[float]:
        return self._queue[0][0] if self._queue else None


@dataclass
class NetConfig:
    delay: tuple = (5.0, 25.0)   # one-way delay in ms, uniform: causes reordering
    loss: float = 0.0            # probability a message is dropped
    duplicate: float = 0.0       # probability a message is delivered twice


class Network:
    """Point-to-point messages between named endpoints."""

    def __init__(self, scheduler: Scheduler, rng: random.Random,
                 config: Optional[NetConfig] = None) -> None:
        self.scheduler = scheduler
        self.rng = rng
        self.config = config or NetConfig()
        self.handlers: Dict[str, Callable[[str, Any], None]] = {}
        self.groups: Optional[List[Set[str]]] = None    # None = fully connected
        self.servers: Set[str] = set()                   # endpoints partitions apply to
        self.stats = {"sent": 0, "delivered": 0, "lost": 0, "duplicated": 0, "cut": 0}

    def register(self, name: str, handler: Callable[[str, Any], None],
                 server: bool = True) -> None:
        self.handlers[name] = handler
        if server:
            self.servers.add(name)

    def partition(self, groups: Iterable[Iterable[str]]) -> None:
        """Only endpoints in the same group can talk. Unlisted ones are isolated.
        Clients are never partitioned, to keep the examples simple."""
        self.groups = [set(g) for g in groups]

    def heal(self) -> None:
        self.groups = None

    def connected(self, a: str, b: str) -> bool:
        if self.groups is None or a not in self.servers or b not in self.servers:
            return True
        return any(a in g and b in g for g in self.groups)

    def send(self, src: str, dst: str, msg: Any) -> None:
        self.stats["sent"] += 1
        if not self.connected(src, dst):
            self.stats["cut"] += 1
            return
        if self.rng.random() < self.config.loss:
            self.stats["lost"] += 1
            return
        copies = 1
        if self.rng.random() < self.config.duplicate:
            copies = 2
            self.stats["duplicated"] += 1
        for _ in range(copies):
            self.scheduler.after(self.rng.uniform(*self.config.delay), self._deliver, src, dst, msg)

    def _deliver(self, src: str, dst: str, msg: Any) -> None:
        # A partition that appeared while the message was in flight also cuts it.
        if not self.connected(src, dst):
            self.stats["cut"] += 1
            return
        self.stats["delivered"] += 1
        self.handlers[dst](src, msg)
