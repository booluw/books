"""A leaderless replicated key-value store with read and write quorums (Chapter 6).

Dynamo-style stores (Amazon Dynamo, Cassandra, Riak) keep N copies of each key
and have no leader. A client writes to all N replicas but waits for only W
acknowledgements; it reads from replicas and waits for only R replies, taking
the reply with the newest version. The rule of thumb:

    R + W > N   every read quorum overlaps every write quorum, so a read
                always reaches at least one replica holding the latest
                acknowledged write;
    R + W <= N  quorums can miss each other, and reads can be stale.

This module simulates such a store, one key-value map per replica, with:

  * versions as (timestamp, writer) pairs, highest wins (last-writer-wins);
  * replicas that crash and recover (keeping their data) at random;
  * writes that reach the acknowledging replicas at once and the others late,
    after a random delay, or never if the replica is down;
  * optional read repair: the reader pushes the newest version to any stale
    replica it heard from.

It also contains a brute-force check of the quorum intersection property.

Run `python3 quorum.py` for a demonstration.
"""
from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field

Version = tuple[int, str]          # (timestamp, writer id); compared as tuples
NO_VERSION: Version = (0, "")


# ---------------------------------------------------------------------------
# Quorum intersection, by brute force
# ---------------------------------------------------------------------------


def quorums_intersect(n: int, r: int, w: int) -> bool:
    """True iff every R-subset of N replicas shares a member with every W-subset.

    Checks all C(n, r) * C(n, w) pairs. The book proves the closed form:
    this holds iff r + w > n (pigeonhole: |R| + |W| > n forces an overlap,
    and if r + w <= n, take R and W disjoint).
    """
    replicas = range(n)
    write_sets = [set(s) for s in itertools.combinations(replicas, w)]
    return all(not ws.isdisjoint(rs)
               for rs in itertools.combinations(replicas, r)
               for ws in write_sets)


# ---------------------------------------------------------------------------
# Replicas and the store
# ---------------------------------------------------------------------------


@dataclass
class Replica:
    rid: int
    up: bool = True
    data: dict[str, tuple[Version, object]] = field(default_factory=dict)

    def get(self, key: str) -> tuple[Version, object]:
        return self.data.get(key, (NO_VERSION, None))

    def apply(self, key: str, version: Version, value: object) -> bool:
        """Store the value if it is newer than what we hold. Returns True if stored.

        Never going backwards is what makes late, duplicated or reordered
        deliveries harmless.
        """
        if version > self.get(key)[0]:
            self.data[key] = (version, value)
            return True
        return False


@dataclass
class ReadResult:
    value: object
    version: Version
    contacted: list[int]
    repaired: list[int]


class QuorumStore:
    """N replicas, read quorum R, write quorum W.

    Time advances by one tick per client operation. `max_delay` is how many
    ticks a write may take to reach replicas that were not in its quorum.
    """

    def __init__(self, n: int = 3, r: int = 2, w: int = 2, seed: int = 0,
                 max_delay: int = 5, read_repair: bool = True) -> None:
        if not (1 <= r <= n and 1 <= w <= n):
            raise ValueError("need 1 <= R, W <= N")
        self.n, self.r, self.w = n, r, w
        self.replicas = [Replica(i) for i in range(n)]
        self.rng = random.Random(seed)
        self.max_delay = max_delay
        self.read_repair = read_repair
        self.clock = 0
        self.pending: list[tuple[int, int, str, Version, object]] = []  # (due, rid, key, ver, val)

    # -- time and failures --------------------------------------------------

    def tick(self) -> None:
        """Advance time and deliver late writes that are due."""
        self.clock += 1
        still = []
        for due, rid, key, ver, val in self.pending:
            if due > self.clock:
                still.append((due, rid, key, ver, val))
            elif self.replicas[rid].up:
                self.replicas[rid].apply(key, ver, val)
            # a write arriving at a down replica is lost (no hinted handoff here)
        self.pending = still

    def set_up(self, rid: int, up: bool) -> None:
        self.replicas[rid].up = up

    def up_replicas(self) -> list[int]:
        return [r.rid for r in self.replicas if r.up]

    # -- client operations ----------------------------------------------------

    def write(self, key: str, value: object, writer: str = "client") -> Version | None:
        """Write to every replica; succeed once W acknowledge.

        The first W up replicas to respond (a random choice) apply the write
        now; the others receive it after a random delay. Returns the version
        on success, or None if fewer than W replicas are up (the write is not
        acknowledged, though replicas that received it keep it).
        """
        self.tick()
        version: Version = (self.clock, writer)
        up = self.up_replicas()
        self.rng.shuffle(up)
        fast, slow = up[:self.w], up[self.w:]
        for rid in fast:
            self.replicas[rid].apply(key, version, value)
        for rid in slow + [r.rid for r in self.replicas if not r.up]:
            delay = self.rng.randint(1, self.max_delay)
            self.pending.append((self.clock + delay, rid, key, version, value))
        return version if len(fast) >= self.w else None

    def read(self, key: str) -> ReadResult | None:
        """Ask R up replicas (a random choice); return the newest version seen.

        Returns None if fewer than R replicas are up. With read repair on,
        contacted replicas holding an older version are sent the newest one.
        """
        self.tick()
        up = self.up_replicas()
        if len(up) < self.r:
            return None
        contacted = self.rng.sample(up, self.r)
        replies = {rid: self.replicas[rid].get(key) for rid in contacted}
        version, value = max(replies.values(), key=lambda vv: vv[0])
        repaired = []
        if self.read_repair:
            for rid, (v, _) in replies.items():
                if v < version and self.replicas[rid].apply(key, version, value):
                    repaired.append(rid)
        return ReadResult(value, version, contacted, repaired)


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------


@dataclass
class TrialStats:
    reads: int = 0
    stale: int = 0
    failed_reads: int = 0
    writes: int = 0
    failed_writes: int = 0
    repairs: int = 0

    @property
    def stale_rate(self) -> float:
        return self.stale / self.reads if self.reads else 0.0


def run_trial(n: int, r: int, w: int, seed: int, ops: int = 200, p_write: float = 0.4,
              p_fail: float = 0.05, p_recover: float = 0.3, max_delay: int = 5,
              read_repair: bool = True) -> TrialStats:
    """A random workload on one key with crashing and recovering replicas.

    A read is *stale* if it returns a version older than the latest
    acknowledged write. (A read may legitimately return something newer:
    an unacknowledged write that reached some replicas.)
    """
    rng = random.Random(seed)
    store = QuorumStore(n, r, w, seed=rng.randrange(2**32), max_delay=max_delay,
                        read_repair=read_repair)
    stats = TrialStats()
    latest_acked: Version = NO_VERSION
    for op in range(ops):
        for rep in store.replicas:            # failures and recoveries
            if rep.up and rng.random() < p_fail:
                store.set_up(rep.rid, False)
            elif not rep.up and rng.random() < p_recover:
                store.set_up(rep.rid, True)
        if rng.random() < p_write:
            stats.writes += 1
            v = store.write("x", op, writer=f"c{rng.randrange(3)}")
            if v is None:
                stats.failed_writes += 1
            else:
                latest_acked = v
        else:
            res = store.read("x")
            if res is None:
                stats.failed_reads += 1
                continue
            stats.reads += 1
            stats.repairs += len(res.repaired)
            if res.version < latest_acked:
                stats.stale += 1
    return stats


def stale_table(n: int = 3, trials: int = 100, **kw) -> dict[tuple[int, int], TrialStats]:
    """Aggregate stats for every (R, W) with 1 <= R, W <= N."""
    table = {}
    for r in range(1, n + 1):
        for w in range(1, n + 1):
            total = TrialStats()
            for seed in range(trials):
                s = run_trial(n, r, w, seed, **kw)
                for f in ("reads", "stale", "failed_reads", "writes", "failed_writes", "repairs"):
                    setattr(total, f, getattr(total, f) + getattr(s, f))
            table[(r, w)] = total
    return table


def _demo() -> None:
    print("Quorum intersection by brute force (every R-set meets every W-set?)")
    for n in (3, 5):
        for r in range(1, n + 1):
            row = "".join(" yes" if quorums_intersect(n, r, w) else "  no" for w in range(1, n + 1))
            print(f"  N={n} R={r}  W=1..{n}:{row}")

    print("\nA stale read with N=3, R=1, W=1:")
    s = QuorumStore(3, 1, 1, seed=4, max_delay=10, read_repair=False)
    v = s.write("x", "new")
    holders = [rep.rid for rep in s.replicas if rep.get("x")[0] == v]
    print(f"  write 'new' acknowledged by replica(s) {holders}; the others will hear later")
    for _ in range(8):
        res = s.read("x")
        tag = "STALE" if res.version < v else "fresh"
        print(f"  read from replica {res.contacted} -> {res.value!r:6} {tag}")

    n, trials = 3, 200
    print(f"\nStale-read rate, N={n}, {trials} random runs of 200 operations each,"
          f" replicas crash 5%/op and recover 30%/op, late delivery up to 5 ticks:")
    tables = {repair: stale_table(n, trials, read_repair=repair) for repair in (False, True)}
    for repair, table in tables.items():
        print(f"  read repair {'on' if repair else 'off'}:")
        print("        " + "".join(f"   W={w}  " for w in range(1, n + 1)))
        for r in range(1, n + 1):
            cells = []
            for w in range(1, n + 1):
                st = table[(r, w)]
                mark = "*" if r + w > n else " "
                cells.append(f"{st.stale_rate:7.2%}{mark}")
            print(f"    R={r} " + " ".join(cells))
    print("  (* marks R + W > N: no stale reads, as the intersection argument guarantees)")
    t = tables[True]
    for rw in ((2, 2), (1, 3), (3, 3)):
        st = t[rw]
        print(f"  R={rw[0]} W={rw[1]}: {st.failed_writes / st.writes:.1%} of writes and "
              f"{st.failed_reads / (st.reads + st.failed_reads):.1%} of reads failed for lack of a quorum")


if __name__ == "__main__":
    _demo()
