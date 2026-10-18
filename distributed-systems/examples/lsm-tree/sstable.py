"""Sorted String Tables: immutable, sorted files on disk.

An SSTable is written once, from a sorted stream of (key, value) pairs, and
never modified. Deleting a key does not edit an old file; it writes a
**tombstone** (a marker meaning "deleted") into a newer one.

File layout::

    data:   record*        record = key len (4) | value len (4, -1 = tombstone) | key | value
    index:  count (4) | (key len (4) | key | offset (8))*
    bloom:  BloomFilter.to_bytes()
    footer: index offset (8) | bloom offset (8) | entry count (8) | magic (8)

The **sparse index** holds the key and file offset of every ``interval``-th
record, not every record. To find a key we binary-search the index for the
last indexed key <= the target, read the block of records from that offset to
the next index entry and scan it. Fewer index entries mean less memory but
more bytes scanned per lookup.
"""

from __future__ import annotations

import bisect
import struct
from typing import Iterable, Iterator

from bloom import BloomFilter

RECORD = struct.Struct(">Ii")
FOOTER = struct.Struct(">QQQ8s")
MAGIC = b"LSMTABLE"
TOMBSTONE_LEN = -1


def write_sstable(path: str, entries: Iterable[tuple[bytes, bytes | None]],
                  count_hint: int, index_interval: int = 16,
                  bloom_bits_per_key: float = 10) -> int:
    """Write sorted ``entries`` to ``path``; return the file size in bytes."""
    bloom = BloomFilter.for_keys(max(1, count_hint), bloom_bits_per_key) \
        if bloom_bits_per_key > 0 else None
    index: list[tuple[bytes, int]] = []
    data = bytearray()
    count = 0
    previous = None
    for key, value in entries:
        if previous is not None and key <= previous:
            raise ValueError("SSTable entries must be strictly increasing")
        previous = key
        if count % index_interval == 0:
            index.append((key, len(data)))
        vlen = TOMBSTONE_LEN if value is None else len(value)
        data += RECORD.pack(len(key), vlen) + key + (value or b"")
        if bloom is not None:
            bloom.add(key)
        count += 1
    index_offset = len(data)
    data += struct.pack(">I", len(index))
    for key, offset in index:
        data += struct.pack(">I", len(key)) + key + struct.pack(">Q", offset)
    bloom_offset = len(data)
    data += bloom.to_bytes() if bloom is not None else b""
    data += FOOTER.pack(index_offset, bloom_offset, count, MAGIC)
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


class SSTable:
    """Read side. The index and Bloom filter are loaded into memory; data
    blocks are read from the file on demand, and each such read is counted."""

    def __init__(self, path: str):
        self.path = path
        with open(path, "rb") as f:
            raw = f.read()
        self.size = len(raw)
        index_offset, bloom_offset, self.count, magic = FOOTER.unpack_from(raw, len(raw) - FOOTER.size)
        if magic != MAGIC:
            raise ValueError(f"{path} is not an SSTable")
        self.data_end = index_offset
        n = struct.unpack_from(">I", raw, index_offset)[0]
        pos = index_offset + 4
        self.index_keys: list[bytes] = []
        self.index_offsets: list[int] = []
        for _ in range(n):
            klen = struct.unpack_from(">I", raw, pos)[0]
            self.index_keys.append(raw[pos + 4:pos + 4 + klen])
            self.index_offsets.append(struct.unpack_from(">Q", raw, pos + 4 + klen)[0])
            pos += 12 + klen
        bloom_bytes = raw[bloom_offset:len(raw) - FOOTER.size]
        self.bloom = BloomFilter.from_bytes(bloom_bytes) if bloom_bytes else None
        self.min_key = self.index_keys[0] if self.index_keys else b""
        self.max_key = self._last_key(raw) if self.index_keys else b""
        self.block_reads = 0             # data blocks read from disk

    def _last_key(self, raw: bytes) -> bytes:
        last = None
        for key, _ in self._parse(raw[self.index_offsets[-1]:self.data_end]):
            last = key
        return last

    @staticmethod
    def _parse(block: bytes) -> Iterator[tuple[bytes, bytes | None]]:
        pos = 0
        while pos < len(block):
            klen, vlen = RECORD.unpack_from(block, pos)
            pos += RECORD.size
            key = block[pos:pos + klen]
            pos += klen
            if vlen == TOMBSTONE_LEN:
                yield key, None
            else:
                yield key, block[pos:pos + vlen]
                pos += vlen

    def _read(self, start: int, end: int) -> bytes:
        self.block_reads += 1
        with open(self.path, "rb") as f:
            f.seek(start)
            return f.read(end - start)

    def may_contain(self, key: bytes) -> bool:
        """Cheap in-memory checks: key range (fence pointers) and Bloom filter."""
        if not self.index_keys or key < self.min_key or key > self.max_key:
            return False
        return self.bloom is None or self.bloom.might_contain(key)

    def get(self, key: bytes) -> tuple[bool, bytes | None]:
        """Return (found, value). ``value`` is None for a tombstone."""
        if not self.may_contain(key):
            return False, None
        i = bisect.bisect_right(self.index_keys, key) - 1
        end = self.index_offsets[i + 1] if i + 1 < len(self.index_offsets) else self.data_end
        for k, v in self._parse(self._read(self.index_offsets[i], end)):
            if k == key:
                return True, v
            if k > key:
                break
        return False, None

    def scan(self, lo: bytes | None = None, hi: bytes | None = None
             ) -> Iterator[tuple[bytes, bytes | None]]:
        """Yield entries with lo <= key < hi (tombstones included)."""
        if not self.index_keys:
            return
        i = 0 if lo is None else max(0, bisect.bisect_right(self.index_keys, lo) - 1)
        for k, v in self._parse(self._read(self.index_offsets[i], self.data_end)):
            if lo is not None and k < lo:
                continue
            if hi is not None and k >= hi:
                return
            yield k, v

    def __iter__(self):
        return self.scan()
