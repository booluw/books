"""Event-time windows, watermarks and late data (Chapter 16).

A stream processor sees events in **processing time** order (when they
arrive) but usually wants answers in **event time** (when they happened).
The two differ because networks delay messages, phones go offline, and
retries reorder things. This module implements the core machinery of
Apache Flink, Beam and Kafka Streams in miniature:

- window assigners for tumbling and sliding windows;
- a bounded-out-of-orderness watermark: "I believe no event older than
  (largest event time seen - max_delay) is still coming";
- a window operator that emits a window when the watermark passes its end,
  and handles late events by dropping them, sending them to a side output,
  or updating the window within an allowed lateness;
- processing-time windows, for contrast.

Run ``python3 windows.py`` for the comparison tables.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class Event:
    arrival: float          # processing time: when the operator sees it
    event_time: float       # event time: when it happened at the source
    key: str = "all"
    value: float = 1.0
    eid: int = 0


Window = tuple[float, float]    # [start, end)


class Tumbling:
    """Fixed-size, non-overlapping windows: [0,10), [10,20), ..."""

    def __init__(self, size: float):
        self.size = size

    def assign(self, t: float) -> list[Window]:
        start = math.floor(t / self.size) * self.size
        return [(start, start + self.size)]


class Sliding:
    """Windows of ``size`` starting every ``slide``; each event is in size/slide windows."""

    def __init__(self, size: float, slide: float):
        if size % slide:
            raise ValueError("size must be a multiple of slide")
        self.size, self.slide = size, slide

    def assign(self, t: float) -> list[Window]:
        last_start = math.floor(t / self.slide) * self.slide
        starts = [last_start - i * self.slide for i in range(int(self.size / self.slide))]
        return sorted((s, s + self.size) for s in starts if s + self.size > t)


@dataclass
class WindowResult:
    key: str
    window: Window
    count: int
    total: float
    emitted_at: float       # processing time at which the result was emitted
    update: bool = False    # True if this revises an earlier result for the window


class BoundedOutOfOrderness:
    """Watermark = max event time seen - max_delay. It never moves backwards."""

    def __init__(self, max_delay: float):
        self.max_delay = max_delay
        self.max_seen = -math.inf

    def observe(self, event_time: float) -> float:
        self.max_seen = max(self.max_seen, event_time)
        return self.current

    @property
    def current(self) -> float:
        return self.max_seen - self.max_delay


@dataclass
class WindowOperator:
    """Event-time windowed count and sum per key.

    ``late_policy`` decides what happens to an event whose window has
    already been emitted *and* whose allowed lateness has expired:
    ``"drop"`` discards it, ``"side"`` puts it on ``side_output``.
    Within ``allowed_lateness`` a late event updates the window and the
    operator emits a revised result.
    """
    assigner: object
    max_delay: float
    allowed_lateness: float = 0.0
    late_policy: str = "drop"
    side_output: list = field(default_factory=list)
    dropped: list = field(default_factory=list)

    def __post_init__(self):
        self.watermark = BoundedOutOfOrderness(self.max_delay)
        self.state: dict[tuple[str, Window], list] = {}     # (key, window) -> [count, total]
        self.fired: set[tuple[str, Window]] = set()
        self.results: list[WindowResult] = []
        self.late_updates = 0

    def process(self, event: Event) -> list[WindowResult]:
        wm = self.watermark.current               # lateness is judged before this event
        out: list[WindowResult] = []
        late_for_all = True
        for window in self.assigner.assign(event.event_time):
            sk = (event.key, window)
            if window[1] + self.allowed_lateness <= wm:
                continue                          # too late for this window
            late_for_all = False
            acc = self.state.setdefault(sk, [0, 0.0])
            acc[0] += 1
            acc[1] += event.value
            if sk in self.fired:                  # late, but within allowed lateness
                self.late_updates += 1
                out.append(WindowResult(event.key, window, acc[0], acc[1], event.arrival, True))
        if late_for_all:
            (self.side_output if self.late_policy == "side" else self.dropped).append(event)
        self.watermark.observe(event.event_time)
        out += self._advance(event.arrival)
        self.results += out
        return out

    def _advance(self, now: float) -> list[WindowResult]:
        wm = self.watermark.current
        out = []
        for sk in sorted(self.state, key=lambda s: (s[1], s[0])):
            key, window = sk
            if window[1] <= wm and sk not in self.fired:
                self.fired.add(sk)
                count, total = self.state[sk]
                out.append(WindowResult(key, window, count, total, now))
            if window[1] + self.allowed_lateness <= wm:
                del self.state[sk]                # garbage-collect closed windows
        return out

    def finish(self, now: float) -> list[WindowResult]:
        """End of stream: the watermark jumps to +infinity, firing everything."""
        self.watermark.max_seen = math.inf
        out = self._advance(now)
        self.results += out
        return out

    def final(self) -> dict[tuple[str, Window], int]:
        """The latest emitted count for each (key, window)."""
        latest: dict[tuple[str, Window], int] = {}
        for r in self.results:
            latest[(r.key, r.window)] = r.count
        return latest


def run_event_time(events: list[Event], assigner, max_delay: float,
                   allowed_lateness: float = 0.0, late_policy: str = "drop") -> WindowOperator:
    op = WindowOperator(assigner, max_delay, allowed_lateness, late_policy)
    for e in sorted(events):                      # arrival order
        op.process(e)
    op.finish(max(e.arrival for e in events))
    return op


def event_time_truth(events: list[Event], assigner) -> dict[tuple[str, Window], int]:
    """The correct answer: a batch job run after every event has arrived."""
    counts: dict[tuple[str, Window], int] = defaultdict(int)
    for e in events:
        for w in assigner.assign(e.event_time):
            counts[(e.key, w)] += 1
    return dict(counts)


def processing_time_windows(events: list[Event], assigner) -> dict[tuple[str, Window], int]:
    """Windows by arrival time: simple, low latency, and answering a different question."""
    counts: dict[tuple[str, Window], int] = defaultdict(int)
    for e in events:
        for w in assigner.assign(e.arrival):
            counts[(e.key, w)] += 1
    return dict(counts)


def generate_events(n_seconds: float = 120.0, rate: float = 20.0, seed: int = 1,
                    straggler_fraction: float = 0.01,
                    outage: tuple[float, float, float] | None = (40.0, 50.0, 56.0)) -> list[Event]:
    """Seeded events with realistic delays, returned in arrival order.

    Most events arrive within about a second; 9% are delayed 2-8 s (a slow
    network path); ``straggler_fraction`` are delayed 20-60 s (a phone that
    went into a tunnel). ``outage = (start, end, release)`` models the
    ingestion pipeline being down: events that happen between ``start`` and
    ``end`` are held back and delivered together from ``release`` onwards.
    """
    rng = random.Random(seed)
    events, t, eid = [], 0.0, 0
    while True:
        t += rng.expovariate(rate)
        if t >= n_seconds:
            break
        r = rng.random()
        if r < straggler_fraction:
            delay = rng.uniform(20, 60)
        elif r < straggler_fraction + 0.09:
            delay = rng.uniform(2, 8)
        else:
            delay = rng.expovariate(2.0)          # mean 0.5 s
        arrival = t + delay
        if outage and outage[0] <= t < outage[1]:
            arrival = max(arrival, outage[2] + rng.expovariate(10.0))
        events.append(Event(round(arrival, 6), round(t, 6), "all",
                            round(rng.uniform(10, 30), 2), eid))
        eid += 1
    return sorted(events)


def accuracy(result: dict, truth: dict) -> float:
    """Fraction of true windows whose count is exactly right."""
    return sum(result.get(k) == v for k, v in truth.items()) / len(truth)


def mean_abs_error(result: dict, truth: dict) -> float:
    """Mean absolute count error per true window."""
    return sum(abs(result.get(k, 0) - v) for k, v in truth.items()) / len(truth)


def median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2


if __name__ == "__main__":
    events = generate_events()
    tumbling = Tumbling(10.0)
    truth = event_time_truth(events, tumbling)
    proc = processing_time_windows(events, tumbling)
    op = run_event_time(events, tumbling, max_delay=5.0)
    emitted = {(r.key, r.window): r for r in op.results}
    inversions = sum(1 for a, b in zip(events, events[1:]) if b.event_time < a.event_time)
    print(f"{len(events)} events over 120 s; {inversions} arrive after a later-stamped event\n")

    print("Tumbling 10 s windows: event time (watermark delay 5 s, drop late) vs processing time\n")
    print(f"{'window':<12}{'truth':>7}{'event-time':>12}{'emitted at':>12}{'processing-time':>17}")
    for key, window in sorted(truth)[:8]:
        r = emitted.get((key, window))
        at = f"{r.emitted_at:.1f}" if r else "never"
        print(f"[{window[0]:>3.0f},{window[1]:>4.0f})  {truth[(key, window)]:>7}"
              f"{r.count if r else 0:>12}{at:>12}{proc.get((key, window), 0):>17}")
    print(f"\nMean count error per window: event-time {mean_abs_error(op.final(), truth):.1f}, "
          f"processing-time {mean_abs_error(proc, truth):.1f}; "
          f"{len(op.dropped)} of {len(events)} events dropped as late")

    print("\nWatermark delay: completeness versus latency (tumbling 10 s, drop late)\n")
    print(f"{'max delay (s)':>14}{'late events':>13}{'counted':>9}{'windows exact':>15}"
          f"{'median wait after end (s)':>27}")
    for delay in (0, 0.5, 1, 2, 5, 10, 30, 60):
        op = run_event_time(events, tumbling, max_delay=delay)
        wait = median([r.emitted_at - r.window[1] for r in op.results if not r.update])
        counted = sum(op.final().values()) / len(events)
        print(f"{delay:>14}{len(op.dropped):>13}{counted:>9.1%}{accuracy(op.final(), truth):>15.0%}"
              f"{wait:>27.1f}")

    print("\nLate-event policies (tumbling 10 s, watermark delay 2 s)\n")
    print(f"{'policy':<28}{'lost':>6}{'side output':>13}{'updates':>9}{'windows exact':>15}")
    for label, kwargs in [("drop", dict(late_policy="drop")),
                          ("side output", dict(late_policy="side")),
                          ("allowed lateness 10 s", dict(allowed_lateness=10)),
                          ("allowed lateness 60 s", dict(allowed_lateness=60))]:
        op = run_event_time(events, tumbling, max_delay=2, **kwargs)
        print(f"{label:<28}{len(op.dropped):>6}{len(op.side_output):>13}{op.late_updates:>9}"
              f"{accuracy(op.final(), truth):>15.0%}")

    sliding = Sliding(10.0, 5.0)
    s_truth = event_time_truth(events, sliding)
    s_op = run_event_time(events, sliding, max_delay=5.0, allowed_lateness=60)
    print(f"\nSliding 10 s windows every 5 s: {len(s_truth)} windows, each event in 2; "
          f"event-time with 60 s allowed lateness exact for {accuracy(s_op.final(), s_truth):.0%}, "
          f"processing-time for {accuracy(processing_time_windows(events, sliding), s_truth):.0%}")
