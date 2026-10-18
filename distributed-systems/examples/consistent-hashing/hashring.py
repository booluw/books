"""Consistent hashing and rendezvous hashing (Chapter 7).

To spread keys over N servers we need a function key -> server. The obvious
choice, hash(key) mod N, balances well but is unstable: when N changes, almost
every key maps to a different server, so adding one cache node empties the
whole cache, and adding one storage node moves nearly all the data.

Three placement schemes, all with the same interface (`lookup(key)`,
`add_node(node)`, `remove_node(node)`):

  ModNHashing         hash(key) mod N; moves about N/(N+1) of keys on growth
  HashRing            consistent hashing with virtual nodes; moves about 1/(N+1)
  RendezvousHashing   highest random weight; moves about 1/(N+1), no ring needed

Hashes come from hashlib, never Python's built-in hash(), which is randomised
per process. Placement must be identical on every machine and every restart.

Run `python3 hashring.py` for a demonstration.
"""
from __future__ import annotations

import bisect
import hashlib
from collections import Counter
from typing import Iterable


def stable_hash(text: str) -> int:
    """A 64-bit hash of `text` that is the same on every machine and run."""
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")


RING_SIZE = 2 ** 64


class ModNHashing:
    """Naive placement: the key goes to nodes[hash(key) mod N]."""

    def __init__(self, nodes: Iterable[str] = ()) -> None:
        self.nodes: list[str] = []
        for n in nodes:
            self.add_node(n)

    def add_node(self, node: str) -> None:
        if node in self.nodes:
            raise ValueError(f"{node} already present")
        self.nodes.append(node)

    def remove_node(self, node: str) -> None:
        self.nodes.remove(node)

    def lookup(self, key: str) -> str:
        if not self.nodes:
            raise LookupError("no nodes")
        return self.nodes[stable_hash(key) % len(self.nodes)]


class HashRing:
    """Consistent hashing (Karger et al., 1997) with virtual nodes.

    Picture the hash space 0 .. 2**64-1 bent into a circle. Each physical node
    is placed at `vnodes` pseudo-random points ("virtual nodes"); a key belongs
    to the first virtual node clockwise from the key's own hash. Adding a node
    only claims the arcs just before its new points, so only keys on those
    arcs move, and they all move to the new node.
    """

    def __init__(self, nodes: Iterable[str] = (), vnodes: int = 100) -> None:
        if vnodes < 1:
            raise ValueError("vnodes must be at least 1")
        self.vnodes = vnodes
        self._points: list[int] = []        # sorted ring positions
        self._owner: dict[int, str] = {}    # position -> physical node
        self.nodes: set[str] = set()
        for n in nodes:
            self.add_node(n)

    def _positions(self, node: str) -> list[int]:
        return [stable_hash(f"{node}#vnode{i}") for i in range(self.vnodes)]

    def add_node(self, node: str) -> None:
        if node in self.nodes:
            raise ValueError(f"{node} already present")
        self.nodes.add(node)
        for p in self._positions(node):
            if p in self._owner:            # a 64-bit collision; vanishingly rare
                continue
            self._owner[p] = node
            bisect.insort(self._points, p)

    def remove_node(self, node: str) -> None:
        self.nodes.remove(node)
        for p in self._positions(node):
            if self._owner.get(p) == node:
                del self._owner[p]
                self._points.pop(bisect.bisect_left(self._points, p))

    def lookup(self, key: str) -> str:
        if not self._points:
            raise LookupError("no nodes")
        i = bisect.bisect_right(self._points, stable_hash(key))
        return self._owner[self._points[i % len(self._points)]]   # wrap around

    def ownership(self) -> dict[str, float]:
        """Fraction of the ring each physical node owns (exact, not sampled)."""
        share: Counter[str] = Counter()
        pts = self._points
        for i, p in enumerate(pts):
            prev = pts[i - 1] if i else pts[-1] - RING_SIZE
            share[self._owner[p]] += (p - prev) / RING_SIZE
        return dict(share)


class RendezvousHashing:
    """Highest random weight hashing (Thaler and Ravishankar, 1996).

    Each node scores the key with hash(node, key); the highest score wins.
    Removing a node only affects keys it won; adding a node only steals keys
    for which it now has the highest score. Cost: O(N) hashes per lookup.
    """

    def __init__(self, nodes: Iterable[str] = ()) -> None:
        self.nodes: list[str] = []
        for n in nodes:
            self.add_node(n)

    def add_node(self, node: str) -> None:
        if node in self.nodes:
            raise ValueError(f"{node} already present")
        self.nodes.append(node)

    def remove_node(self, node: str) -> None:
        self.nodes.remove(node)

    def lookup(self, key: str) -> str:
        if not self.nodes:
            raise LookupError("no nodes")
        return max(self.nodes, key=lambda n: stable_hash(f"{n}|{key}"))


# ---------------------------------------------------------------------------
# Measurements
# ---------------------------------------------------------------------------


def make_keys(count: int, prefix: str = "key") -> list[str]:
    return [f"{prefix}-{i}" for i in range(count)]


def assignment(scheme, keys: list[str]) -> dict[str, str]:
    return {k: scheme.lookup(k) for k in keys}


def fraction_moved(before: dict[str, str], after: dict[str, str]) -> float:
    return sum(1 for k in before if before[k] != after[k]) / len(before)


def load_imbalance(scheme, keys: list[str]) -> float:
    """max load / mean load across nodes. 1.0 is perfect balance."""
    counts = Counter(scheme.lookup(k) for k in keys)
    loads = [counts.get(n, 0) for n in scheme.nodes]
    return max(loads) / (len(keys) / len(loads))


def movement_on_add(factory, n: int, keys: list[str]) -> float:
    """Fraction of keys that move when node n+1 joins n existing nodes."""
    scheme = factory([f"node-{i}" for i in range(n)])
    before = assignment(scheme, keys)
    scheme.add_node(f"node-{n}")
    return fraction_moved(before, assignment(scheme, keys))


def _demo() -> None:
    keys = make_keys(20_000)
    n = 10
    print(f"Adding an 11th node to {n} nodes ({len(keys):,} keys). Ideal movement: 1/11 = {1/11:.1%}\n")
    schemes = [
        ("mod-N hashing", ModNHashing),
        ("hash ring, 1 vnode/node", lambda ns: HashRing(ns, vnodes=1)),
        ("hash ring, 100 vnodes/node", lambda ns: HashRing(ns, vnodes=100)),
        ("rendezvous hashing", RendezvousHashing),
    ]
    for name, factory in schemes:
        print(f"  {name:<28} keys moved: {movement_on_add(factory, n, keys):6.1%}")

    print("\nRemoving one node from 10 (hash ring, 100 vnodes):")
    ring = HashRing([f"node-{i}" for i in range(n)], vnodes=100)
    before = assignment(ring, keys)
    ring.remove_node("node-3")
    after = assignment(ring, keys)
    owned = sum(1 for k in keys if before[k] == "node-3")
    print(f"  keys moved: {fraction_moved(before, after):.1%}, exactly node-3's share "
          f"({owned / len(keys):.1%}); no other key moved")

    print(f"\nLoad imbalance (max/mean keys per node), {n} nodes. "
          f"'ring share' is the exact max/mean arc owned, free of key-sampling noise:")
    for v in (1, 10, 100, 1000):
        ring = HashRing([f"node-{i}" for i in range(n)], vnodes=v)
        share = max(ring.ownership().values()) * n
        print(f"  {v:>4} vnodes per node: {load_imbalance(ring, keys):.2f}   (ring share {share:.2f})")
    print(f"  rendezvous:           "
          f"{load_imbalance(RendezvousHashing([f'node-{i}' for i in range(n)]), keys):.2f}")
    print(f"  mod-N:                "
          f"{load_imbalance(ModNHashing([f'node-{i}' for i in range(n)]), keys):.2f}")


if __name__ == "__main__":
    _demo()
