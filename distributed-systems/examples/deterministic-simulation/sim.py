"""A deterministic simulation testing harness (Chapter 23).

FoundationDB and TigerBeetle test their distributed systems by running the
real protocol code inside a simulated world: one thread, a virtual clock, a
simulated network and simulated crashes, all driven by a single seeded
random-number generator. Because nothing depends on real time, real threads
or real sockets, **a seed fully determines a run**. That gives two powers:

1. **Search**: try thousands of seeds per second, each a different
   interleaving of message delays, drops and crashes, and check invariants.
2. **Replay**: when seed 4,711 fails, run seed 4,711 again and get exactly
   the same execution, as many times as you need to debug it.

This module is the harness: ``Simulator`` (clock, event queue, network,
fault injection, trace) and ``SwarmConfig`` (per-seed randomised settings).
The system under test is in ``primary_backup.py``.
"""

from __future__ import annotations

import hashlib
import heapq
import itertools
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class SwarmConfig:
    """Settings for one run. Swarm testing (Groce et al., ISSTA 2012) varies
    the *configuration* per seed as well as the schedule, so that some runs
    are calm and some are hostile, instead of every run being average."""
    clients: int = 3
    counters: int = 2
    ops_per_client: int = 8
    drop_rate: float = 0.05
    latency: tuple[float, float] = (1.0, 10.0)        # milliseconds
    crash_primary: bool = True
    crash_window: tuple[float, float] = (5.0, 150.0)
    detect_delay: float = 50.0
    client_timeout: float = 60.0
    retransmit: float = 30.0

    @classmethod
    def from_seed(cls, seed: int) -> "SwarmConfig":
        rng = random.Random(f"config-{seed}")
        return cls(clients=rng.randint(1, 4),
                   counters=rng.randint(1, 6),
                   ops_per_client=rng.randint(3, 10),
                   drop_rate=rng.choice([0.0, 0.0, 0.001, 0.005, 0.01, 0.02]),
                   latency=(1.0, rng.choice([2.0, 10.0, 40.0])),
                   crash_primary=rng.random() < 0.7,
                   crash_window=(5.0, rng.choice([50.0, 150.0, 400.0])))


class Simulator:
    """Virtual time, a priority queue of events, a lossy network, a trace."""

    def __init__(self, seed: int, config: SwarmConfig, trace: bool = True):
        self.seed = seed
        self.config = config
        self.rng = random.Random(seed)
        self.now = 0.0
        self._queue: list = []
        self._seq = itertools.count()            # tie-breaker: equal times stay ordered
        self.nodes: dict[str, object] = {}
        self.keep_trace = trace
        self.trace: list[str] = []
        self._hash = hashlib.sha256()
        self.messages_sent = self.messages_dropped = 0

    # ---- time ---------------------------------------------------------------
    def schedule(self, delay: float, action, *args) -> None:
        heapq.heappush(self._queue, (self.now + delay, next(self._seq), action, args))

    def run(self, until: float = 10_000.0) -> None:
        while self._queue:
            t, _, action, args = heapq.heappop(self._queue)
            if t > until:
                break
            self.now = t
            action(*args)

    # ---- network ------------------------------------------------------------
    def send(self, src: str, dst: str, msg: tuple) -> None:
        """Deliver ``msg`` after a random latency, or drop it."""
        self.messages_sent += 1
        if self.rng.random() < self.config.drop_rate:
            self.messages_dropped += 1
            self.log(f"DROP {src}->{dst} {msg}")
            return
        lo, hi = self.config.latency
        self.schedule(self.rng.uniform(lo, hi), self._deliver, src, dst, msg)

    def _deliver(self, src: str, dst: str, msg: tuple) -> None:
        node = self.nodes[dst]
        if not getattr(node, "alive", True):
            self.log(f"LOST {src}->{dst} {msg} (destination down)")
            return
        self.log(f"RECV {src}->{dst} {msg}")
        node.receive(src, msg)

    # ---- trace --------------------------------------------------------------
    def log(self, text: str) -> None:
        line = f"{self.now:9.3f} {text}"
        self._hash.update(line.encode())
        if self.keep_trace:
            self.trace.append(line)

    @property
    def trace_hash(self) -> str:
        """A fingerprint of the whole execution: equal hashes, equal runs."""
        return self._hash.hexdigest()[:16]
