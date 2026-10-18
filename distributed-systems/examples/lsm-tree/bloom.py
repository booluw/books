"""A Bloom filter built on hashlib (Chapter 15).

A Bloom filter answers "is this key *possibly* in the set?" using a few bits
per key. It never says no to a key that was added (no false negatives), but
it sometimes says yes to a key that was not (a false positive). An LSM tree
keeps one per SSTable so that a lookup can skip files that certainly do not
hold the key, without reading them from disk.

With ``m`` bits, ``k`` hash functions and ``n`` keys, the false-positive
probability is approximately

    p = (1 - e^(-k n / m))^k

and is smallest when ``k = (m / n) ln 2``. At 10 bits per key that gives
k = 7 and p of about 0.8%.
"""

from __future__ import annotations

import hashlib
import math
import struct


class BloomFilter:
    def __init__(self, num_bits: int, num_hashes: int, bits: bytearray | None = None):
        if num_bits <= 0 or num_hashes <= 0:
            raise ValueError("a Bloom filter needs at least one bit and one hash")
        self.m = num_bits
        self.k = num_hashes
        self.bits = bits if bits is not None else bytearray((num_bits + 7) // 8)

    @classmethod
    def for_keys(cls, expected_keys: int, bits_per_key: float) -> "BloomFilter":
        """Size a filter for ``expected_keys`` keys with the optimal ``k``."""
        m = max(8, int(math.ceil(expected_keys * bits_per_key)))
        k = max(1, round(bits_per_key * math.log(2)))
        return cls(m, k)

    def _positions(self, key: bytes):
        # Double hashing (Kirsch and Mitzenmacher, 2006): two independent
        # 64-bit hashes h1, h2 simulate k hashes as h1 + i*h2.
        digest = hashlib.blake2b(key, digest_size=16).digest()
        h1, h2 = struct.unpack(">QQ", digest)
        h2 |= 1                                  # odd, so it never degenerates to 0
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, key: bytes) -> None:
        for pos in self._positions(key):
            self.bits[pos >> 3] |= 1 << (pos & 7)

    def might_contain(self, key: bytes) -> bool:
        return all(self.bits[pos >> 3] & (1 << (pos & 7)) for pos in self._positions(key))

    __contains__ = might_contain

    def to_bytes(self) -> bytes:
        return struct.pack(">QI", self.m, self.k) + bytes(self.bits)

    @classmethod
    def from_bytes(cls, data: bytes) -> "BloomFilter":
        m, k = struct.unpack_from(">QI", data)
        return cls(m, k, bytearray(data[12:12 + (m + 7) // 8]))


def expected_fp_rate(n: int, m: int, k: int) -> float:
    """The textbook approximation (1 - e^{-kn/m})^k."""
    return (1 - math.exp(-k * n / m)) ** k


def measure_fp_rate(n: int, bits_per_key: float, probes: int = 20_000) -> tuple[float, float, int]:
    """Build a filter of ``n`` keys and probe it with ``probes`` absent keys.

    Returns (measured rate, formula rate, k). Keys are deterministic strings,
    so the result is reproducible.
    """
    bf = BloomFilter.for_keys(n, bits_per_key)
    for i in range(n):
        bf.add(f"present-{i}".encode())
    false_pos = sum(bf.might_contain(f"absent-{i}".encode()) for i in range(probes))
    return false_pos / probes, expected_fp_rate(n, bf.m, bf.k), bf.k


if __name__ == "__main__":
    n = 10_000
    print(f"Bloom filter false-positive rate, {n:,} keys, 20,000 absent probes\n")
    print(f"{'bits/key':>9}{'k':>4}{'measured':>11}{'formula':>11}")
    for bpk in (2, 4, 6, 8, 10, 12, 16):
        measured, formula, k = measure_fp_rate(n, bpk)
        print(f"{bpk:>9}{k:>4}{measured:>11.4%}{formula:>11.4%}")
