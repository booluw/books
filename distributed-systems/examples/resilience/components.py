"""Reusable resilience building blocks (Chapter 17).

Everything here is deliberately small and free of I/O so that it can be
used both inside the discrete-event simulation in ``simulation.py`` and in
real code. Time is always passed in explicitly as ``now`` (seconds, as a
float) rather than read from a clock. That keeps the classes deterministic
and testable: a test can step time forward without sleeping.

Contents
--------
backoff_delays()  the delays before retry 1, 2, 3, ... for several policies
TokenBucket       a rate limiter that refills over time and can be topped up
RetryBudget       a TokenBucket used to cap retries at a fraction of requests
CircuitBreaker    closed / open / half-open state machine
"""

from __future__ import annotations

import random
from collections import deque

# ---------------------------------------------------------------------------
# Backoff
# ---------------------------------------------------------------------------

BACKOFF_POLICIES = ("none", "constant", "exponential", "full_jitter",
                    "equal_jitter", "decorrelated_jitter")


def next_backoff(policy: str, retry: int, base: float, cap: float,
                 rng: random.Random, previous: float | None = None) -> float:
    """Return the delay (seconds) before retry number ``retry`` (1-based).

    The policies follow Marc Brooker, "Exponential Backoff and Jitter",
    AWS Architecture Blog, 4 March 2015:

    - ``none``: retry immediately (delay 0). The "retry storm" default.
    - ``constant``: always wait ``base``.
    - ``exponential``: ``min(cap, base * 2**(retry-1))``. Spreads retries out
      in time but every client that failed together retries together.
    - ``full_jitter``: a uniform random delay in ``[0, exponential]``.
    - ``equal_jitter``: half the exponential delay plus a uniform random
      amount up to the other half.
    - ``decorrelated_jitter``: ``min(cap, uniform(base, previous * 3))``.
    """
    if retry < 1:
        raise ValueError("retry numbers start at 1")
    if policy == "none":
        return 0.0
    if policy == "constant":
        return min(cap, base)
    exp = min(cap, base * 2 ** (retry - 1))
    if policy == "exponential":
        return exp
    if policy == "full_jitter":
        return rng.uniform(0, exp)
    if policy == "equal_jitter":
        return exp / 2 + rng.uniform(0, exp / 2)
    if policy == "decorrelated_jitter":
        prev = base if previous is None else previous
        return min(cap, rng.uniform(base, prev * 3))
    raise ValueError(f"unknown backoff policy {policy!r}; choose from {BACKOFF_POLICIES}")


def backoff_delays(retries: int, policy: str = "full_jitter", base: float = 0.1,
                   cap: float = 10.0, seed: int | random.Random | None = 0) -> list[float]:
    """Return the list of delays before retries 1..``retries``.

    >>> backoff_delays(5, "exponential", base=0.1, cap=1.0)
    [0.1, 0.2, 0.4, 0.8, 1.0]
    """
    rng = seed if isinstance(seed, random.Random) else random.Random(seed)
    delays: list[float] = []
    previous = None
    for retry in range(1, retries + 1):
        previous = next_backoff(policy, retry, base, cap, rng, previous)
        delays.append(previous)
    return delays


# ---------------------------------------------------------------------------
# Token bucket and retry budget
# ---------------------------------------------------------------------------

class TokenBucket:
    """A token bucket: holds up to ``capacity`` tokens, refilled at ``rate``/s.

    ``try_acquire`` takes tokens if enough are present and reports whether it
    did. ``deposit`` adds tokens directly, which is how a retry budget earns
    tokens from successful first attempts rather than from the clock.
    """

    def __init__(self, rate: float, capacity: float, now: float = 0.0,
                 initial: float | None = None):
        if rate < 0 or capacity <= 0:
            raise ValueError("rate must be >= 0 and capacity > 0")
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity if initial is None else min(initial, capacity)
        self.updated = now

    def _refill(self, now: float) -> None:
        if now > self.updated:
            self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
            self.updated = now

    def available(self, now: float) -> float:
        self._refill(now)
        return self.tokens

    def deposit(self, amount: float, now: float) -> None:
        self._refill(now)
        self.tokens = min(self.capacity, self.tokens + amount)

    def try_acquire(self, now: float, cost: float = 1.0) -> bool:
        self._refill(now)
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


class RetryBudget:
    """Allow retries up to ``ratio`` of first attempts, plus a small floor.

    Every new request deposits ``ratio`` tokens; every retry spends one. So in
    steady state at most ``ratio`` extra load is added by retries, however bad
    things get. ``min_per_second`` lets a trickle of retries through when
    traffic is low. This is the design used by Finagle and by gRPC's
    ``retryThrottling`` (which uses a token ratio in the same spirit).
    """

    def __init__(self, ratio: float = 0.1, min_per_second: float = 1.0,
                 capacity: float = 10.0, now: float = 0.0):
        self.ratio = ratio
        self.bucket = TokenBucket(rate=min_per_second, capacity=capacity, now=now)

    def on_request(self, now: float) -> None:
        self.bucket.deposit(self.ratio, now)

    def can_retry(self, now: float) -> bool:
        return self.bucket.try_acquire(now, 1.0)


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------

CLOSED, OPEN, HALF_OPEN = "closed", "open", "half-open"


class CircuitBreaker:
    """A count-based circuit breaker.

    - **closed**: calls flow. The last ``window`` outcomes are remembered; once
      at least ``min_calls`` are recorded and the failure fraction reaches
      ``failure_threshold``, the breaker trips to **open**.
    - **open**: calls are refused immediately ("fail fast") for
      ``open_seconds``, giving the dependency room to recover.
    - **half-open**: up to ``half_open_probes`` trial calls are let through.
      If they all succeed the breaker closes; any failure re-opens it.
    """

    def __init__(self, failure_threshold: float = 0.5, window: int = 20,
                 min_calls: int = 10, open_seconds: float = 1.0,
                 half_open_probes: int = 3):
        self.failure_threshold = failure_threshold
        self.window = window
        self.min_calls = min_calls
        self.open_seconds = open_seconds
        self.half_open_probes = half_open_probes
        self.state = CLOSED
        self.outcomes: deque[bool] = deque(maxlen=window)   # True = failure
        self.opened_at = 0.0
        self.probes_sent = 0
        self.probes_ok = 0
        self.transitions: list[tuple[float, str]] = []

    def _move(self, state: str, now: float) -> None:
        self.state = state
        self.transitions.append((now, state))
        if state == OPEN:
            self.opened_at = now
        if state == HALF_OPEN:
            self.probes_sent = self.probes_ok = 0
        if state == CLOSED:
            self.outcomes.clear()

    def allow(self, now: float) -> bool:
        """Return True if a call may be made now (and count it if a probe)."""
        if self.state == OPEN and now - self.opened_at >= self.open_seconds:
            self._move(HALF_OPEN, now)
        if self.state == CLOSED:
            return True
        if self.state == HALF_OPEN and self.probes_sent < self.half_open_probes:
            self.probes_sent += 1
            return True
        return False

    def record_success(self, now: float) -> None:
        if self.state == HALF_OPEN:
            self.probes_ok += 1
            if self.probes_ok >= self.half_open_probes:
                self._move(CLOSED, now)
        elif self.state == CLOSED:
            self.outcomes.append(False)

    def record_failure(self, now: float) -> None:
        if self.state == HALF_OPEN:
            self._move(OPEN, now)
        elif self.state == CLOSED:
            self.outcomes.append(True)
            if (len(self.outcomes) >= self.min_calls and
                    sum(self.outcomes) / len(self.outcomes) >= self.failure_threshold):
                self._move(OPEN, now)


if __name__ == "__main__":
    print("Delays (s) before retries 1-6, base 0.1 s, cap 2.0 s, seed 1\n")
    print(f"{'policy':<22}" + "".join(f"{'r' + str(i):>8}" for i in range(1, 7)))
    for policy in BACKOFF_POLICIES:
        delays = backoff_delays(6, policy, base=0.1, cap=2.0, seed=1)
        print(f"{policy:<22}" + "".join(f"{d:>8.3f}" for d in delays))
