"""State-based CRDTs (Chapter 10): counters, a register and an add-wins set.

A conflict-free replicated data type (CRDT) is a data type whose replicas can
be updated independently, without coordination, and are guaranteed to
converge once they have seen the same updates, in any order and with
duplicates. State-based CRDTs (also called convergent replicated data types,
CvRDTs) get there by making the set of states a *join-semilattice*: a merge
operation that is

    commutative   merge(a, b) == merge(b, a)
    associative   merge(merge(a, b), c) == merge(a, merge(b, c))
    idempotent    merge(a, a) == a

and updates that only move a state "upwards" (inflations). Then replicas can
gossip whole states to each other any number of times, in any order, and all
end at the least upper bound of everything they have seen.

Types:

  GCounter      grow-only counter: one count per replica, merge = element-wise max
  PNCounter     counter with decrement: a pair of GCounters (P for +, N for -)
  LWWRegister   last-writer-wins register: highest (timestamp, replica) wins
  ORSet         observed-remove set, add-wins: concurrent add and remove keep the element
  NaiveCounter  NOT a CRDT: a plain integer, to show what goes wrong

Every type offers `merge(other)`, returning a new replica, `state()`, a
canonical value used to compare replicas, `value`, `copy()` and `fresh(id)`.
Run `python3 crdts.py` for a demo.
"""
from __future__ import annotations

import random
from typing import Hashable


class CRDT:
    """Shared plumbing: a replica id, a pure merge and comparison by state."""

    def __init__(self, replica: str) -> None:
        self.replica = replica

    def state(self):
        raise NotImplementedError

    def _join(self, other) -> None:
        """Join `other` into self, in place."""
        raise NotImplementedError

    def copy(self):
        """An independent copy of this replica."""
        raise NotImplementedError

    def fresh(self, replica: str):
        """A new, empty replica of the same type."""
        return type(self)(replica)

    def merge(self, other):
        """A new replica (keeping self's id) holding the join of both states."""
        result = self.copy()
        result._join(other)
        return result

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and self.state() == other.state()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.replica!r}, value={self.value!r})"


class GCounter(CRDT):
    """Grow-only counter. Each replica increments only its own entry.

    value = sum of entries. Merge takes the maximum of each entry, which is
    safe because each entry only ever grows and has a single writer.
    """

    def __init__(self, replica: str) -> None:
        super().__init__(replica)
        self.counts: dict[str, int] = {}

    def increment(self, n: int = 1) -> None:
        if n < 0:
            raise ValueError("a G-Counter cannot decrease; use a PN-Counter")
        self.counts[self.replica] = self.counts.get(self.replica, 0) + n

    @property
    def value(self) -> int:
        return sum(self.counts.values())

    def state(self):
        return tuple(sorted((r, c) for r, c in self.counts.items() if c))

    def copy(self) -> "GCounter":
        c = GCounter(self.replica)
        c.counts = dict(self.counts)
        return c

    def _join(self, other: "GCounter") -> None:
        for r, c in other.counts.items():
            self.counts[r] = max(self.counts.get(r, 0), c)


class PNCounter(CRDT):
    """Increment and decrement: value = P.value - N.value."""

    def __init__(self, replica: str) -> None:
        super().__init__(replica)
        self.p = GCounter(replica)
        self.n = GCounter(replica)

    def increment(self, n: int = 1) -> None:
        self.p.increment(n)

    def decrement(self, n: int = 1) -> None:
        self.n.increment(n)

    @property
    def value(self) -> int:
        return self.p.value - self.n.value

    def state(self):
        return (self.p.state(), self.n.state())

    def copy(self) -> "PNCounter":
        c = PNCounter(self.replica)
        c.p, c.n = self.p.copy(), self.n.copy()
        return c

    def _join(self, other: "PNCounter") -> None:
        self.p._join(other.p)
        self.n._join(other.n)


class LWWRegister(CRDT):
    """Last-writer-wins register.

    Each write is stamped (timestamp, replica id); the merge keeps the write
    with the larger stamp. The replica id breaks timestamp ties, so the order
    is total and merge is commutative. The cost: of two concurrent writes,
    one is silently discarded.
    """

    def __init__(self, replica: str) -> None:
        super().__init__(replica)
        self.stamp: tuple[int, str] = (0, "")
        self._value: object = None

    def set(self, value: object, timestamp: int) -> None:
        stamp = (timestamp, self.replica)
        if stamp > self.stamp:
            self.stamp, self._value = stamp, value

    @property
    def value(self) -> object:
        return self._value

    def state(self):
        return (self.stamp, self._value)

    def copy(self) -> "LWWRegister":
        c = LWWRegister(self.replica)
        c.stamp, c._value = self.stamp, self._value
        return c

    def _join(self, other: "LWWRegister") -> None:
        if other.stamp > self.stamp:
            self.stamp, self._value = other.stamp, other._value


class ORSet(CRDT):
    """Observed-remove set with add-wins semantics.

    Every add creates a unique tag (replica id, sequence number). An element
    is present if it has a tag that has not been removed. A remove deletes
    only the tags this replica has *observed*, so an add that happened
    concurrently (with a tag the remover never saw) survives: add wins.

    This simple version keeps removed tags for ever as tombstones; optimised
    OR-Sets use version vectors to avoid that.
    """

    def __init__(self, replica: str) -> None:
        super().__init__(replica)
        self.adds: set[tuple[Hashable, tuple[str, int]]] = set()
        self.removes: set[tuple[Hashable, tuple[str, int]]] = set()
        self.seq = 0

    def add(self, element: Hashable) -> None:
        self.seq += 1
        self.adds.add((element, (self.replica, self.seq)))

    def remove(self, element: Hashable) -> None:
        self.removes |= {(e, t) for e, t in self.adds if e == element}

    def __contains__(self, element: Hashable) -> bool:
        return element in self.value

    @property
    def value(self) -> frozenset:
        return frozenset(e for e, t in self.adds - self.removes)

    def state(self):
        return (frozenset(self.adds), frozenset(self.removes))

    def copy(self) -> "ORSet":
        c = ORSet(self.replica)
        c.adds, c.removes, c.seq = set(self.adds), set(self.removes), self.seq
        return c

    def _join(self, other: "ORSet") -> None:
        self.adds |= other.adds
        self.removes |= other.removes
        # Keep sequence numbers unique even if our own tags come back to us
        # from another replica (e.g. after a restart from a merged state).
        own = [t[1] for _, t in self.adds if t[0] == self.replica]
        self.seq = max([self.seq] + own)


class NaiveCounter(CRDT):
    """NOT a CRDT. A plain integer with a choice of bad merges.

    mode="max": take the larger value. Idempotent, but concurrent increments
                on different replicas are lost.
    mode="sum": add the values. Counts concurrent increments, but merging the
                same state twice (a duplicated message) double-counts, and
                merging back and forth inflates without bound.
    """

    def __init__(self, replica: str, mode: str = "max") -> None:
        super().__init__(replica)
        if mode not in ("max", "sum"):
            raise ValueError("mode is 'max' or 'sum'")
        self.mode = mode
        self.count = 0

    def increment(self, n: int = 1) -> None:
        self.count += n

    @property
    def value(self) -> int:
        return self.count

    def state(self):
        return self.count

    def fresh(self, replica: str) -> "NaiveCounter":
        return NaiveCounter(replica, self.mode)

    def copy(self) -> "NaiveCounter":
        c = NaiveCounter(self.replica, self.mode)
        c.count = self.count
        return c

    def _join(self, other: "NaiveCounter") -> None:
        self.count = max(self.count, other.count) if self.mode == "max" else self.count + other.count


# ---------------------------------------------------------------------------
# Random workloads, used by the demo and the tests
# ---------------------------------------------------------------------------


def random_op(replica: CRDT, rng: random.Random, clock: list[int]) -> None:
    """Apply one random update to a replica of any of the types above."""
    if isinstance(replica, (GCounter, NaiveCounter)):
        replica.increment(rng.randint(1, 3))
    elif isinstance(replica, PNCounter):
        (replica.increment if rng.random() < 0.6 else replica.decrement)(rng.randint(1, 3))
    elif isinstance(replica, LWWRegister):
        clock[0] += rng.randint(0, 2)            # timestamps can repeat across replicas
        replica.set(rng.choice("abcdef"), clock[0])
    elif isinstance(replica, ORSet):
        e = rng.choice("wxyz")
        (replica.add if rng.random() < 0.6 else replica.remove)(e)
    else:
        raise TypeError(type(replica))


def random_run(cls, rng: random.Random, n_replicas: int = 3, steps: int = 30, **kw) -> list[CRDT]:
    """Replicas that update independently and occasionally merge a peer's state.

    Returns every intermediate state, so tests have a rich supply of states
    that share history, as real replicas do.
    """
    replicas = [cls(f"r{i}", **kw) for i in range(n_replicas)]
    clock = [0]
    seen = []
    for _ in range(steps):
        i = rng.randrange(n_replicas)
        if rng.random() < 0.3:
            j = rng.randrange(n_replicas)
            replicas[i] = replicas[i].merge(replicas[j])
        else:
            random_op(replicas[i], rng, clock)
        seen.append(replicas[i].copy())
    return seen + replicas


def deliver_in_random_order(states: list[CRDT], rng: random.Random, receiver: CRDT,
                            duplicates: int = 3) -> CRDT:
    """Merge every state into `receiver` in a random order, some of them more than once."""
    msgs = states + [rng.choice(states) for _ in range(duplicates)]
    rng.shuffle(msgs)
    for m in msgs:
        receiver = receiver.merge(m)
    return receiver


def merge_all(states: list[CRDT]) -> CRDT:
    """The join of a list of states."""
    result = states[0]
    for st in states[1:]:
        result = result.merge(st)
    return result


def converges(states: list[CRDT], rng: random.Random, receivers: int = 5) -> bool:
    """Do fresh replicas that each receive all `states` (shuffled, duplicated) agree?"""
    finals = [deliver_in_random_order(states, rng, states[0].fresh(f"q{k}"))
              for k in range(receivers)]
    return all(f.state() == finals[0].state() for f in finals)


def _demo() -> None:
    print("Two replicas of a page-view counter, partitioned; each counts 5 views.\n")
    for name, make in (("naive (merge = max)", lambda r: NaiveCounter(r, "max")),
                       ("naive (merge = sum)", lambda r: NaiveCounter(r, "sum")),
                       ("G-Counter", GCounter)):
        a, b = make("A"), make("B")
        for _ in range(5):
            a.increment()
            b.increment()
        once = a.merge(b)
        twice = once.merge(b)               # the same state delivered again
        print(f"  {name:<20} after merge: {once.value:>2}   after a duplicate delivery: {twice.value:>2}"
              f"   (true total 10)")

    print("\nShopping list as an OR-Set (add wins):")
    alice, bob = ORSet("alice"), ORSet("bob")
    alice.add("milk")
    bob = bob.merge(alice)                  # both now see milk
    alice.remove("milk")                    # Alice bought it...
    bob.add("milk")                         # ...while Bob, offline, adds it again
    merged = alice.merge(bob)
    print(f"  Alice removed milk, Bob concurrently re-added it -> {sorted(merged.value)}")
    alice2 = merged.merge(alice)
    alice2.remove("milk")
    print(f"  Alice removes again after seeing Bob's add       -> {sorted(alice2.merge(bob).value)}")

    print("\nLWW register: concurrent writes at the same timestamp, replica id breaks the tie:")
    x, y = LWWRegister("x"), LWWRegister("y")
    x.set("red", 7)
    y.set("blue", 7)
    print(f"  x.merge(y) = {x.merge(y).value!r}, y.merge(x) = {y.merge(x).value!r}; "
          f"'red' is lost without a trace")

    runs = 1000
    print(f"\nConvergence: {runs} random runs per type; 5 replicas each receive every state")
    print("in a different random order, with duplicates.")
    rng = random.Random(2026)
    for cls in (GCounter, PNCounter, LWWRegister, ORSet):
        converged = sum(converges(random_run(cls, rng), rng) for _ in range(runs))
        print(f"  {cls.__name__:<12} converged in {converged:>4} of {runs} runs")

    print(f"\nThe naive counter over the same {runs} random workloads (identical seeds):")
    for mode in ("max", "sum"):
        converged = lost = 0
        lost_fraction = []
        for seed in range(runs):
            truth = merge_all(random_run(GCounter, random.Random(seed))).value
            states = random_run(NaiveCounter, random.Random(seed), mode=mode)
            converged += converges(states, random.Random(seed))
            final = merge_all(states).value
            lost += final < truth
            lost_fraction.append(max(0, truth - final) / truth)
        print(f"  merge = {mode}: converged in {converged:>4} of {runs} runs; lost increments in "
              f"{lost:>4} runs (mean {sum(lost_fraction) / runs:.0%} of the count lost)")
    print("  'max' converges, but to the wrong number: an integer cannot tell two replicas'")
    print("  increments apart. 'sum' counts them, but duplicates make replicas disagree.")


if __name__ == "__main__":
    _demo()
