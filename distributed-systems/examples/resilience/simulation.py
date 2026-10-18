"""A discrete-event simulation of a retry storm and how to prevent it (Chapter 17).

The world
---------
- A **server** has ``workers`` threads and an unbounded FIFO queue. Each
  piece of work takes an exponentially distributed time with mean
  ``service_mean``. Capacity is ``workers / service_mean`` requests/second.
- **Clients** create logical requests as a Poisson process at
  ``base_rate``/s, except during a short **spike** when the rate jumps to
  ``spike_rate``/s. Each request has an overall **deadline**; each
  **attempt** has its own **timeout**. When an attempt times out (or is
  rejected), the client may retry, depending on the strategy.
- The server does not know that a client has given up. Unless deadlines are
  propagated, it still does the work for a timed-out attempt: wasted work.

The experiment
--------------
The spike briefly pushes offered load above capacity. A queue builds, every
attempt times out, and naive clients retry. Retries add load, the queue
never drains, and the system stays down long after the spike has gone:
a **metastable failure**. The same spike with retry budgets, jitter, load
shedding and deadline propagation is a blip.

Run ``python3 simulation.py`` to print the comparison table.
"""

from __future__ import annotations

import heapq
import itertools
import math
import random
from collections import deque
from dataclasses import dataclass, field

from components import CircuitBreaker, RetryBudget, next_backoff


@dataclass(frozen=True)
class Config:
    workers: int = 4
    service_mean: float = 0.040        # seconds -> capacity 100 requests/s
    base_rate: float = 70.0            # 70% utilisation in normal times
    spike_rate: float = 200.0          # 2x capacity ...
    spike_start: float = 10.0
    spike_end: float = 15.0            # ... for five seconds
    duration: float = 60.0
    attempt_timeout: float = 0.5
    request_deadline: float = 2.0
    max_attempts: int = 4              # one try plus three retries
    backoff_base: float = 0.1
    backoff_cap: float = 1.0
    max_queue: int = 30                # used only when shedding is on
    budget_ratio: float = 0.1          # used only when a retry budget is on
    bin_seconds: float = 1.0           # resolution of the recovery check
    recovered_success: float = 0.9     # a bin is healthy at >= 90% success


@dataclass(frozen=True)
class Strategy:
    name: str
    max_attempts: int | None = None    # None -> Config.max_attempts
    backoff: str = "none"
    budget: bool = False
    breaker: bool = False
    shed: bool = False
    deadline_propagation: bool = False


STRATEGIES = [
    Strategy("no retries", max_attempts=1),
    Strategy("naive retries", backoff="none"),
    Strategy("exponential backoff", backoff="exponential"),
    Strategy("backoff + full jitter", backoff="full_jitter"),
    Strategy("jitter + retry budget", backoff="full_jitter", budget=True),
    Strategy("jitter + circuit breaker", backoff="full_jitter", breaker=True),
    Strategy("deadline propagation", backoff="none", deadline_propagation=True),
    Strategy("load shedding", backoff="none", shed=True),
    Strategy("budget+jitter+shed+deadline", backoff="full_jitter", budget=True,
             shed=True, deadline_propagation=True),
]
BY_NAME = {s.name: s for s in STRATEGIES}


@dataclass
class Request:
    rid: int
    created: float
    deadline: float
    attempts: int = 0
    finished: bool = False
    ok: bool = False
    finished_at: float = 0.0
    last_delay: float | None = None


@dataclass
class Attempt:
    request: Request
    sent: float
    deadline: float
    live: bool = True                  # client still waiting for this attempt


@dataclass
class Result:
    strategy: str
    requests: int
    attempts: int
    successes: int
    goodput_after: float               # successful requests/s arriving after the spike
    p50: float                         # latency (s) of successes, spike start onwards
    p99: float
    recovery: float | None             # seconds after spike end; None = never
    wasted_work: int                   # attempts served after the client gave up
    shed: int
    expired_skipped: int
    short_circuited: int
    max_queue_seen: int
    bins: list[float] = field(default_factory=list)

    @property
    def amplification(self) -> float:
        return self.attempts / self.requests if self.requests else 0.0


def percentile(values: list[float], q: float) -> float:
    """Nearest-rank percentile; ``nan`` for an empty list."""
    if not values:
        return math.nan
    ordered = sorted(values)
    rank = max(1, math.ceil(q / 100 * len(ordered)))
    return ordered[rank - 1]


def arrival_times(cfg: Config, rng: random.Random) -> list[float]:
    """Poisson arrivals with a rate step (thinning is unnecessary for a step)."""
    times, t = [], 0.0
    while True:
        rate = cfg.spike_rate if cfg.spike_start <= t < cfg.spike_end else cfg.base_rate
        t += rng.expovariate(rate)
        if t >= cfg.duration:
            return times
        times.append(t)


def simulate(strategy: Strategy, cfg: Config = Config(), seed: int = 1) -> Result:
    """Run one strategy against one seeded workload and summarise it."""
    arrivals = arrival_times(cfg, random.Random(seed))     # same workload for every strategy
    service_rng = random.Random(seed * 7919 + 1)
    jitter_rng = random.Random(seed * 104729 + 2)
    max_attempts = strategy.max_attempts or cfg.max_attempts

    budget = RetryBudget(ratio=cfg.budget_ratio) if strategy.budget else None
    breaker = CircuitBreaker() if strategy.breaker else None

    events: list = []
    seq = itertools.count()

    def schedule(time: float, kind: str, payload) -> None:
        heapq.heappush(events, (time, next(seq), kind, payload))

    queue: deque[Attempt] = deque()
    busy = 0
    stats = dict(attempts=0, wasted=0, shed=0, expired=0, short=0, maxq=0)
    requests: list[Request] = []

    # ---- client side ------------------------------------------------------
    def finish(req: Request, now: float, ok: bool) -> None:
        if not req.finished:
            req.finished, req.ok, req.finished_at = True, ok, now

    def send_attempt(req: Request, now: float) -> None:
        if breaker is not None and not breaker.allow(now):
            stats["short"] += 1
            finish(req, now, False)          # fail fast, no load on the server
            return
        req.attempts += 1
        stats["attempts"] += 1
        attempt = Attempt(req, now, min(now + cfg.attempt_timeout, req.deadline))
        schedule(attempt.deadline, "timeout", attempt)
        server_receive(attempt, now)

    def attempt_failed(attempt: Attempt, now: float) -> None:
        """Called on timeout or rejection: decide whether to retry."""
        if not attempt.live:
            return
        attempt.live = False
        if breaker is not None:
            breaker.record_failure(now)
        req = attempt.request
        if req.attempts >= max_attempts:
            return finish(req, now, False)
        delay = next_backoff(strategy.backoff, req.attempts, cfg.backoff_base,
                             cfg.backoff_cap, jitter_rng, req.last_delay)
        req.last_delay = delay
        if now + delay >= req.deadline:
            return finish(req, now, False)
        if budget is not None and not budget.can_retry(now):
            return finish(req, now, False)
        schedule(now + delay, "retry", req)

    def attempt_succeeded(attempt: Attempt, now: float) -> None:
        if not attempt.live:
            stats["wasted"] += 1             # the client stopped listening
            return
        attempt.live = False
        if breaker is not None:
            breaker.record_success(now)
        finish(attempt.request, now, True)

    # ---- server side ------------------------------------------------------
    def server_receive(attempt: Attempt, now: float) -> None:
        if strategy.shed and len(queue) >= cfg.max_queue:
            stats["shed"] += 1
            attempt_failed(attempt, now)     # fast rejection, e.g. HTTP 503
            return
        queue.append(attempt)
        stats["maxq"] = max(stats["maxq"], len(queue))
        start_work(now)

    def start_work(now: float) -> None:
        nonlocal busy
        while busy < cfg.workers and queue:
            attempt = queue.popleft()
            if strategy.deadline_propagation and now >= attempt.deadline:
                stats["expired"] += 1        # caller already gave up: skip it
                continue
            busy += 1
            schedule(now + service_rng.expovariate(1 / cfg.service_mean), "done", attempt)

    # ---- main loop --------------------------------------------------------
    for rid, t in enumerate(arrivals):
        schedule(t, "arrival", rid)

    while events:
        now, _, kind, payload = heapq.heappop(events)
        if now > cfg.duration + cfg.request_deadline:
            break
        if kind == "arrival":
            req = Request(payload, now, now + cfg.request_deadline)
            requests.append(req)
            if budget is not None:
                budget.on_request(now)
            send_attempt(req, now)
        elif kind == "retry":
            if not payload.finished:
                send_attempt(payload, now)
        elif kind == "timeout":
            attempt_failed(payload, now)
        elif kind == "done":
            busy -= 1
            attempt_succeeded(payload, now)
            start_work(now)

    return summarise(strategy, cfg, requests, stats)


def summarise(strategy: Strategy, cfg: Config, requests: list[Request], stats: dict) -> Result:
    nbins = int(cfg.duration / cfg.bin_seconds)
    totals, oks = [0] * nbins, [0] * nbins
    for r in requests:
        b = min(nbins - 1, int(r.created / cfg.bin_seconds))
        totals[b] += 1
        oks[b] += r.ok
    bins = [ok / tot if tot else 1.0 for ok, tot in zip(oks, totals)]

    # Recovery: first bin at or after the spike's end from which every later
    # bin is healthy. Measured from the end of the spike.
    first_after = int(cfg.spike_end / cfg.bin_seconds)
    recovery = None
    for b in range(first_after, nbins):
        if all(x >= cfg.recovered_success for x in bins[b:]):
            recovery = max(0.0, b * cfg.bin_seconds - cfg.spike_end)
            break

    after = [r for r in requests if r.created >= cfg.spike_end]
    goodput = sum(r.ok for r in after) / (cfg.duration - cfg.spike_end)
    lat = [r.finished_at - r.created for r in requests if r.ok and r.created >= cfg.spike_start]
    return Result(strategy.name, len(requests), stats["attempts"],
                  sum(r.ok for r in requests), goodput,
                  percentile(lat, 50), percentile(lat, 99), recovery,
                  stats["wasted"], stats["shed"], stats["expired"], stats["short"],
                  stats["maxq"], bins)


def run_all(cfg: Config = Config(), seed: int = 1) -> list[Result]:
    return [simulate(s, cfg, seed) for s in STRATEGIES]


def print_table(results: list[Result], cfg: Config) -> None:
    capacity = cfg.workers / cfg.service_mean
    print(f"Server capacity {capacity:.0f} req/s; base load {cfg.base_rate:.0f} req/s; "
          f"spike {cfg.spike_rate:.0f} req/s from t={cfg.spike_start:.0f}s to "
          f"t={cfg.spike_end:.0f}s; run {cfg.duration:.0f}s")
    print(f"Attempt timeout {cfg.attempt_timeout}s, request deadline {cfg.request_deadline}s, "
          f"up to {cfg.max_attempts} attempts\n")
    head = (f"{'strategy':<29}{'goodput':>8}{'p50':>7}{'p99':>7}{'recover':>9}"
            f"{'amplif':>8}{'wasted':>8}{'shed':>7}{'max q':>7}")
    print(head)
    print(f"{'':<29}{'req/s':>8}{'(s)':>7}{'(s)':>7}{'(s)':>9}{'x':>8}")
    print("-" * len(head))
    for r in results:
        rec = "never" if r.recovery is None else f"{r.recovery:.0f}"
        print(f"{r.strategy:<29}{r.goodput_after:>8.1f}{r.p50:>7.2f}{r.p99:>7.2f}{rec:>9}"
              f"{r.amplification:>8.2f}{r.wasted_work:>8}{r.shed:>7}{r.max_queue_seen:>7}")
    print("\ngoodput: successful requests/s among requests arriving after the spike "
          f"(ideal {cfg.base_rate:.0f})")
    print("p50/p99: end-to-end latency of successful requests from the spike onwards")
    print("recover: seconds after the spike until every later 1 s bin has >= "
          f"{cfg.recovered_success:.0%} success")
    print("amplif: attempts per request; wasted: attempts served after the client gave up")


def print_timeline(results: list[Result], cfg: Config, names: list[str]) -> None:
    print("\nSuccess rate per 5 s window (by request arrival time)\n")
    step = int(5 / cfg.bin_seconds)
    starts = range(0, len(results[0].bins), step)
    print(f"{'strategy':<29}" + "".join(f"{int(s * cfg.bin_seconds):>5}" for s in starts))
    for r in results:
        if r.strategy in names:
            cells = [sum(r.bins[s:s + step]) / len(r.bins[s:s + step]) for s in starts]
            print(f"{r.strategy:<29}" + "".join(f"{c * 100:>5.0f}" for c in cells))


if __name__ == "__main__":
    config = Config()
    results = run_all(config, seed=1)
    print_table(results, config)
    print_timeline(results, config, ["no retries", "naive retries", "exponential backoff",
                                     "jitter + retry budget", "budget+jitter+shed+deadline"])
