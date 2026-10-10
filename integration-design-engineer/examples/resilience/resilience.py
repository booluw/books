"""Resilience building blocks from Chapter 8, in plain Python.

- classify(): turn an HTTP outcome into RETRY / FAIL_PERMANENT / REFRESH_AUTH / SUCCESS
- retry_call(): exponential backoff with full jitter, Retry-After, attempt cap and deadline
- CircuitBreaker: closed -> open -> half-open state machine over a sliding window
- TokenBucket: client-side rate limiter

Clocks and sleeps are injectable so the behaviour can be tested deterministically.
"""
from __future__ import annotations

import random
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class Outcome(Enum):
    SUCCESS = "success"
    RETRY = "retry"                    # transient: try again later
    REFRESH_AUTH = "refresh_auth"      # refresh credentials once, then retry
    FAIL_PERMANENT = "fail_permanent"  # do not retry unchanged: dead-letter / business error


RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


def classify(status: int | None, *, idempotent: bool) -> Outcome:
    """Classify an HTTP result. status=None means a network error or timeout.

    A timeout on a non-idempotent call has an unknown outcome, so it is NOT
    safe to retry blindly; we treat it as permanent here so a human or a
    reconciliation step decides (Chapter 8, section 8.3).
    """
    if status is None:
        return Outcome.RETRY if idempotent else Outcome.FAIL_PERMANENT
    if 200 <= status < 300:
        return Outcome.SUCCESS
    if status == 401:
        return Outcome.REFRESH_AUTH
    if status in RETRYABLE_STATUS:
        # 429/503 mean the request was not processed, so retrying is safe.
        if status in (429, 503) or idempotent:
            return Outcome.RETRY
        return Outcome.FAIL_PERMANENT
    return Outcome.FAIL_PERMANENT


@dataclass
class Response:
    status: int | None
    headers: dict
    body: object = None


class RetriesExhausted(Exception):
    def __init__(self, last: Response, attempts: int):
        super().__init__(f"gave up after {attempts} attempts (last status {last.status})")
        self.last = last
        self.attempts = attempts


def backoff_delay(attempt: int, base: float, cap: float, rng: random.Random) -> float:
    """'Full jitter': uniform between 0 and min(cap, base * 2**attempt)."""
    return rng.uniform(0, min(cap, base * (2 ** attempt)))


def parse_retry_after(headers: dict) -> float | None:
    value = {k.lower(): v for k, v in headers.items()}.get("retry-after")
    if value is None:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        return None  # HTTP-date form not handled in this example


def retry_call(
    send: Callable[[], Response],
    *,
    idempotent: bool,
    max_attempts: int = 5,
    base: float = 0.5,
    cap: float = 30.0,
    deadline: float | None = None,
    refresh_auth: Callable[[], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
    rng: random.Random | None = None,
) -> Response:
    rng = rng or random.Random()
    refreshed = False
    last = Response(None, {})
    for attempt in range(max_attempts):
        try:
            last = send()
        except (ConnectionError, TimeoutError):
            last = Response(None, {})
        outcome = classify(last.status, idempotent=idempotent)
        if outcome is Outcome.SUCCESS:
            return last
        if outcome is Outcome.FAIL_PERMANENT:
            raise RetriesExhausted(last, attempt + 1)
        if outcome is Outcome.REFRESH_AUTH:
            if refreshed or refresh_auth is None:
                raise RetriesExhausted(last, attempt + 1)
            refresh_auth()
            refreshed = True
            continue  # retry immediately with new credentials
        if attempt == max_attempts - 1:
            break
        delay = backoff_delay(attempt, base, cap, rng)
        server_hint = parse_retry_after(last.headers)
        if server_hint is not None:
            delay = max(delay, server_hint)
        if deadline is not None and clock() + delay > deadline:
            break  # do not outlive the caller's deadline
        sleep(delay)
    raise RetriesExhausted(last, max_attempts)


class CircuitOpen(Exception):
    pass


class CircuitBreaker:
    """Opens when the failure rate over the last `window` calls reaches `threshold`."""

    CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"

    def __init__(self, *, window: int = 20, threshold: float = 0.5, min_calls: int = 10,
                 cooldown: float = 30.0, half_open_trials: int = 3,
                 clock: Callable[[], float] = time.monotonic):
        self.window = window
        self.threshold = threshold
        self.min_calls = min_calls
        self.cooldown = cooldown
        self.half_open_trials = half_open_trials
        self.clock = clock
        self.state = self.CLOSED
        self.results: deque[bool] = deque(maxlen=window)
        self.opened_at = 0.0
        self.trial_successes = 0

    def allow(self) -> bool:
        if self.state == self.OPEN:
            if self.clock() - self.opened_at >= self.cooldown:
                self.state = self.HALF_OPEN
                self.trial_successes = 0
                return True
            return False
        return True

    def record(self, success: bool) -> None:
        if self.state == self.HALF_OPEN:
            if not success:
                self._open()
                return
            self.trial_successes += 1
            if self.trial_successes >= self.half_open_trials:
                self.state = self.CLOSED
                self.results.clear()
            return
        self.results.append(success)
        if len(self.results) >= self.min_calls:
            failure_rate = self.results.count(False) / len(self.results)
            if failure_rate >= self.threshold:
                self._open()

    def _open(self) -> None:
        self.state = self.OPEN
        self.opened_at = self.clock()

    def call(self, fn: Callable[[], Response]) -> Response:
        if not self.allow():
            raise CircuitOpen("circuit open: failing fast")
        try:
            response = fn()
        except (ConnectionError, TimeoutError):
            self.record(False)
            raise
        self.record(response.status is not None and response.status < 500 and response.status != 429)
        return response


class TokenBucket:
    """Allows bursts up to `capacity` and a sustained rate of `rate` tokens per second."""

    def __init__(self, rate: float, capacity: float, clock: Callable[[], float] = time.monotonic):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.clock = clock
        self.updated = clock()

    def _refill(self) -> None:
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
        self.updated = now

    def try_acquire(self, tokens: float = 1.0) -> bool:
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def wait_time(self, tokens: float = 1.0) -> float:
        self._refill()
        return 0.0 if self.tokens >= tokens else (tokens - self.tokens) / self.rate
