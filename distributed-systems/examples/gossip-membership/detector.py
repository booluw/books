"""Heartbeat failure detectors: fixed timeout and phi accrual (Chapter 2).

A monitored process sends a heartbeat every `interval` milliseconds. The
monitor cannot see a crash; it can only notice that heartbeats have stopped
arriving. But a heartbeat can also be late because the network is slow, a
packet was lost, or the sender paused for garbage collection. So every
detector trades two things:

  detection time    how long after a real crash until we suspect it
  false positives   how often we suspect a process that is actually alive

A short timeout detects quickly and suspects wrongly often; a long timeout
rarely errs but leaves a dead node in service for longer. No setting wins on
both, which is the practical face of the impossibility results in Chapter 2.

Two detectors:

  timeout_detector   suspect when no heartbeat for `timeout` ms
  phi_detector       phi accrual (Hayashibara et al., 2004, used by Cassandra
                     and Akka): learn the distribution of inter-arrival times
                     and output a suspicion level phi = -log10(P(a heartbeat
                     would arrive this late)); suspect when phi > threshold

Both are evaluated on the same simulated heartbeat stream so they can be
compared fairly. Run `python3 detector.py` for a demonstration.
"""
from __future__ import annotations

import math
import random
import statistics
from collections import deque
from dataclasses import dataclass


def heartbeat_arrivals(seed: int = 0, interval: float = 100.0, crash_at: float = 600_000.0,
                       base_delay: float = 5.0, jitter: float = 10.0, loss: float = 0.01,
                       p_pause: float = 0.002, pause: tuple[float, float] = (300.0, 1500.0)) -> list[float]:
    """Arrival times (ms) at the monitor of heartbeats sent until `crash_at`.

    Each heartbeat is lost with probability `loss`. Otherwise it takes
    base_delay plus an exponential jitter (mean `jitter`). With probability
    `p_pause` the sender stalls, as in a garbage-collection pause, delaying
    that heartbeat and the ones queued behind it by a random pause length.
    """
    rng = random.Random(seed)
    arrivals = []
    stall_until = 0.0
    t = 0.0
    while t < crash_at:
        if rng.random() < p_pause:
            stall_until = t + rng.uniform(*pause)
        send = max(t, stall_until)
        if send < crash_at and rng.random() >= loss:
            arrivals.append(send + base_delay + rng.expovariate(1 / jitter))
        t += interval
    return sorted(arrivals)


@dataclass
class DetectorResult:
    false_positives: int      # times a live process was suspected
    detection_ms: float       # time from crash to (lasting) suspicion
    heartbeats: int

    @property
    def false_per_hour(self) -> float:
        hours = self.heartbeats * 0.1 / 3600     # assumes the 100 ms default interval
        return self.false_positives / hours


def timeout_detector(arrivals: list[float], crash_at: float, timeout: float) -> DetectorResult:
    """Suspect whenever `timeout` ms pass without a heartbeat.

    A false positive is a gap between two heartbeats longer than the timeout
    (the process was alive, since a later heartbeat arrived). Detection time
    is when the last heartbeat plus the timeout runs out, measured from the crash.
    """
    false = sum(1 for a, b in zip(arrivals, arrivals[1:]) if b - a > timeout)
    detect = max(0.0, arrivals[-1] + timeout - crash_at)
    return DetectorResult(false, detect, len(arrivals))


def tail_z(threshold: float) -> float:
    """The z for which a normal variable exceeds mean + z * std with probability 10**-threshold.

    Solved by bisection: the standard library's NormalDist.inv_cdf cannot
    reach far into the tail because 1 - 10**-12 rounds badly in floating point.
    """
    target = 10 ** -threshold
    lo, hi = -10.0, 40.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if 0.5 * math.erfc(mid / math.sqrt(2)) > target:
            lo = mid
        else:
            hi = mid
    return hi


class PhiAccrual:
    """Phi accrual suspicion level from a sliding window of inter-arrival times.

    Inter-arrival times are modelled as normal with the window's mean and
    standard deviation (with a floor on the deviation, as Akka does, so a
    very regular stream does not make phi explode at the first late beat).
    Running sums keep each update O(1).
    """

    def __init__(self, window: int = 100, min_std: float = 20.0) -> None:
        self.intervals: deque[float] = deque()
        self.window = window
        self.min_std = min_std
        self.last: float | None = None
        self._sum = 0.0
        self._sumsq = 0.0

    def heartbeat(self, t: float) -> None:
        if self.last is not None:
            x = t - self.last
            self.intervals.append(x)
            self._sum += x
            self._sumsq += x * x
            if len(self.intervals) > self.window:
                old = self.intervals.popleft()
                self._sum -= old
                self._sumsq -= old * old
        self.last = t

    def stats(self) -> tuple[float, float]:
        """(mean, standard deviation) of the window, the deviation floored at min_std."""
        k = len(self.intervals)
        mean = self._sum / k
        var = max(0.0, self._sumsq / k - mean * mean)
        return mean, max(math.sqrt(var), self.min_std)

    def phi(self, now: float) -> float:
        """-log10 of the probability that the next heartbeat comes even later than now."""
        if self.last is None or not self.intervals:
            return 0.0
        mean, std = self.stats()
        p_later = 0.5 * math.erfc((now - self.last - mean) / (std * math.sqrt(2)))
        return -math.log10(max(p_later, 1e-300))

    def suspect_after(self, threshold: float, z: float | None = None) -> float:
        """Elapsed time since the last heartbeat at which phi crosses `threshold`.

        Pass a precomputed `z = tail_z(threshold)` to avoid recomputing it.
        """
        mean, std = self.stats()
        return mean + (tail_z(threshold) if z is None else z) * std


def phi_detector(arrivals: list[float], crash_at: float, threshold: float,
                 window: int = 100, min_std: float = 20.0) -> DetectorResult:
    """Evaluate phi accrual with the given threshold on an arrival stream."""
    fd = PhiAccrual(window, min_std)
    z = tail_z(threshold)
    false = 0
    for a, b in zip(arrivals, arrivals[1:]):
        fd.heartbeat(a)
        if len(fd.intervals) >= 2 and b - a > fd.suspect_after(threshold, z):
            false += 1
    fd.heartbeat(arrivals[-1])
    detect = max(0.0, arrivals[-1] + fd.suspect_after(threshold, z) - crash_at)
    return DetectorResult(false, detect, len(arrivals))


def sweep(detector, settings, seeds=range(10), **stream) -> list[tuple[float, float, float]]:
    """(setting, mean false positives per hour, mean detection ms) for each setting."""
    streams = [heartbeat_arrivals(seed=s, **stream) for s in seeds]
    crash = stream.get("crash_at", 600_000.0)
    out = []
    for x in settings:
        rs = [detector(a, crash, x) for a in streams]
        out.append((x, statistics.mean(r.false_per_hour for r in rs),
                    statistics.mean(r.detection_ms for r in rs)))
    return out


def _demo() -> None:
    print("Heartbeats every 100 ms for 10 minutes; 1% loss, ~15 ms delay, occasional")
    print("0.3-1.5 s pauses (0.2% of beats). Means over 10 runs.\n")
    print("Fixed timeout:")
    print(f"  {'timeout ms':>10} {'false/hour':>11} {'detect ms':>10}")
    for t, fp, det in sweep(timeout_detector, (150, 250, 500, 1000, 2000)):
        print(f"  {t:>10} {fp:>11.1f} {det:>10.0f}")
    print("\nPhi accrual:")
    print(f"  {'threshold':>10} {'false/hour':>11} {'detect ms':>10}")
    for t, fp, det in sweep(phi_detector, (1, 3, 5, 8, 12)):
        print(f"  {t:>10} {fp:>11.1f} {det:>10.0f}")

    print("\nOne setting, three networks (no pauses; mean delay jitter 10, 40, 80 ms):")
    print(f"  {'jitter':>6} {'timeout 250 ms':>22} {'phi threshold 12':>24}")
    for jitter in (10, 40, 80):
        [(_, tf, td)] = sweep(timeout_detector, (250,), jitter=jitter, p_pause=0)
        [(_, pf, pd)] = sweep(phi_detector, (12,), jitter=jitter, p_pause=0)
        print(f"  {jitter:>6} {tf:>8.1f}/h, {td:>4.0f} ms detect {pf:>8.1f}/h, {pd:>4.0f} ms detect")
    print("  The fixed timeout floods with false positives as jitter grows; phi adapts by")
    print("  waiting longer on a noisier network.")

    print("\nA phi trace after the last heartbeat (window learned from a calm stream):")
    fd = PhiAccrual()
    for a in heartbeat_arrivals(seed=1, crash_at=60_000, p_pause=0):
        fd.heartbeat(a)
    for dt in (50, 100, 150, 200, 300, 500):
        print(f"  {dt:>4} ms since last heartbeat: phi = {fd.phi(fd.last + dt):6.2f}")


if __name__ == "__main__":
    _demo()
