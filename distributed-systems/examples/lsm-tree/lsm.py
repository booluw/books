"""A small log-structured merge tree (LSM tree) storage engine (Chapter 15).

Writes go to a write-ahead log (for durability) and an in-memory sorted
**memtable**. When the memtable is full it is **flushed** to a new immutable
**SSTable** file. Reads check the memtable, then SSTables from newest to
oldest; the first entry found wins. Over time the files pile up, so
**compaction** merges several into one, keeping only the newest version of
each key and dropping tombstones when it is safe.

The design trades write cost for read cost: writes are sequential appends
(fast), while reads may have to look in several files. Bloom filters and
compaction claw the read cost back. RocksDB, LevelDB, Cassandra, ScyllaDB
and HBase are all built this way.

Directory layout::

    MANIFEST          JSON: the live SSTables, newest first (replaced atomically)
    wal.log           the write-ahead log for the current memtable
    sst-000001.sst    SSTable files
"""

from __future__ import annotations

import bisect
import heapq
import json
import os
from dataclasses import dataclass

from sstable import SSTable, write_sstable
from wal import WriteAheadLog


class Memtable:
    """A sorted map kept as a sorted key list (bisect) plus a dict.

    Real engines use a skip list or a balanced tree; a sorted list with
    ``bisect.insort`` has the same interface and is easy to read.
    """

    def __init__(self):
        self.keys: list[bytes] = []
        self.values: dict[bytes, bytes | None] = {}

    def put(self, key: bytes, value: bytes | None) -> None:
        if key not in self.values:
            bisect.insort(self.keys, key)
        self.values[key] = value

    def get(self, key: bytes) -> tuple[bool, bytes | None]:
        if key in self.values:
            return True, self.values[key]
        return False, None

    def scan(self, lo: bytes | None, hi: bytes | None):
        start = 0 if lo is None else bisect.bisect_left(self.keys, lo)
        end = len(self.keys) if hi is None else bisect.bisect_left(self.keys, hi)
        for key in self.keys[start:end]:
            yield key, self.values[key]

    def __len__(self):
        return len(self.keys)


@dataclass
class Stats:
    user_bytes: int = 0          # bytes of keys and values the caller asked us to store
    wal_bytes: int = 0           # bytes appended to the write-ahead log
    flush_bytes: int = 0         # bytes of SSTables written by flushes
    compaction_bytes: int = 0    # bytes of SSTables written by compactions
    gets: int = 0
    tables_consulted: int = 0    # SSTables whose in-memory filter/fences were checked
    block_reads: int = 0         # data blocks read from SSTable files
    flushes: int = 0
    compactions: int = 0

    def write_amplification(self, include_wal: bool = True) -> float:
        written = self.flush_bytes + self.compaction_bytes + (self.wal_bytes if include_wal else 0)
        return written / self.user_bytes if self.user_bytes else 0.0


def merge_tables(sources, drop_tombstones: bool):
    """K-way merge of sorted sources, ordered newest first.

    Each source yields (key, value) in key order. For each key the entry from
    the newest source wins. Tombstones are dropped only when the output will
    be the oldest data in the tree, because only then can no older version of
    the key be hiding underneath.
    """
    tagged = [((key, rank, value) for key, value in src) for rank, src in enumerate(sources)]
    last = None
    for key, _rank, value in heapq.merge(*tagged, key=lambda t: (t[0], t[1])):
        if key == last:
            continue                     # an older version of a key already emitted
        last = key
        if value is None and drop_tombstones:
            continue
        yield key, value


class LSMTree:
    def __init__(self, directory: str, memtable_limit: int = 1000,
                 bloom_bits_per_key: float = 10, index_interval: int = 16,
                 compaction: str | None = "size-tiered", tier_threshold: int = 4,
                 sync: bool = False):
        self.dir = directory
        self.memtable_limit = memtable_limit
        self.bloom_bits_per_key = bloom_bits_per_key
        self.index_interval = index_interval
        self.compaction = compaction
        self.tier_threshold = tier_threshold
        self.stats = Stats()
        os.makedirs(directory, exist_ok=True)
        self._load_manifest()
        self.memtable = Memtable()
        self.recovered = 0
        for key, value in WriteAheadLog.replay(self._path("wal.log")):
            self.memtable.put(key, value)          # crash recovery
            self.recovered += 1
        self.wal = WriteAheadLog(self._path("wal.log"), sync=sync)

    # ---- files ------------------------------------------------------------
    def _path(self, name: str) -> str:
        return os.path.join(self.dir, name)

    def _load_manifest(self) -> None:
        try:
            with open(self._path("MANIFEST")) as f:
                manifest = json.load(f)
        except FileNotFoundError:
            manifest = {"tables": [], "next_id": 1}
        self.next_id = manifest["next_id"]
        self.tables = [SSTable(self._path(name)) for name in manifest["tables"]]

    def _save_manifest(self) -> None:
        manifest = {"tables": [os.path.basename(t.path) for t in self.tables],
                    "next_id": self.next_id}
        tmp = self._path("MANIFEST.tmp")
        with open(tmp, "w") as f:
            json.dump(manifest, f)
        os.replace(tmp, self._path("MANIFEST"))     # atomic on POSIX and Windows

    def _new_table_path(self) -> str:
        name = f"sst-{self.next_id:06d}.sst"
        self.next_id += 1
        return self._path(name)

    # ---- writes -----------------------------------------------------------
    def put(self, key: str, value: str) -> None:
        self._write(key.encode(), value.encode())

    def delete(self, key: str) -> None:
        self._write(key.encode(), None)

    def _write(self, key: bytes, value: bytes | None) -> None:
        self.stats.user_bytes += len(key) + (len(value) if value else 0)
        before = self.wal.bytes_written
        self.wal.append(key, value)                 # 1. durable first
        self.stats.wal_bytes += self.wal.bytes_written - before
        self.memtable.put(key, value)               # 2. then visible
        if len(self.memtable) >= self.memtable_limit:
            self.flush()

    def flush(self) -> None:
        """Write the memtable to a new SSTable, then start an empty WAL."""
        if not len(self.memtable):
            return
        path = self._new_table_path()
        size = write_sstable(path, self.memtable.scan(None, None), len(self.memtable),
                             self.index_interval, self.bloom_bits_per_key)
        self.stats.flush_bytes += size
        self.stats.flushes += 1
        self.tables.insert(0, SSTable(path))        # newest first
        self._save_manifest()                       # the table is now live ...
        self.wal.reset()                            # ... so the log can go
        self.memtable = Memtable()
        if self.compaction == "size-tiered":
            self.maybe_compact()

    # ---- compaction -------------------------------------------------------
    def _compact(self, start: int, end: int) -> None:
        """Merge the adjacent tables self.tables[start:end] into one."""
        victims = self.tables[start:end]
        bottom = end == len(self.tables)            # includes the oldest table?
        path = self._new_table_path()
        merged = list(merge_tables([iter(t) for t in victims], drop_tombstones=bottom))
        if merged:
            size = write_sstable(path, merged, len(merged), self.index_interval,
                                 self.bloom_bits_per_key)
            self.stats.compaction_bytes += size
            replacement = [SSTable(path)]
        else:
            replacement = []
        self.tables[start:end] = replacement
        self._save_manifest()                       # switch over atomically ...
        for t in victims:                           # ... then delete the inputs
            os.remove(t.path)
        self.stats.compactions += 1

    def maybe_compact(self) -> None:
        """Size-tiered compaction: merge runs of ``tier_threshold`` adjacent
        tables of similar size (each within 2x of the run's smallest)."""
        while True:
            run = self._find_similar_run()
            if run is None:
                return
            self._compact(*run)

    def _find_similar_run(self):
        n = len(self.tables)
        for start in range(n):
            smallest = self.tables[start].size
            end = start + 1
            while end < n:
                size = self.tables[end].size
                if not (smallest / 2 <= size <= smallest * 2):
                    break
                smallest = min(smallest, size)
                end += 1
                if end - start >= self.tier_threshold:
                    return start, end
        return None

    def compact_all(self) -> None:
        """Major compaction: flush, then merge every table into one."""
        self.flush()
        if self.tables:
            self._compact(0, len(self.tables))

    # ---- reads ------------------------------------------------------------
    def get(self, key: str) -> str | None:
        k = key.encode()
        self.stats.gets += 1
        found, value = self.memtable.get(k)
        if not found:
            for table in self.tables:               # newest to oldest
                self.stats.tables_consulted += 1
                before = table.block_reads
                found, value = table.get(k)
                self.stats.block_reads += table.block_reads - before
                if found:
                    break
        return value.decode() if found and value is not None else None

    def scan(self, lo: str | None = None, hi: str | None = None) -> list[tuple[str, str]]:
        """All live (key, value) pairs with lo <= key < hi, in key order."""
        blo = lo.encode() if lo is not None else None
        bhi = hi.encode() if hi is not None else None
        sources = [self.memtable.scan(blo, bhi)] + [t.scan(blo, bhi) for t in self.tables]
        return [(k.decode(), v.decode()) for k, v in merge_tables(sources, drop_tombstones=True)]

    # ---- lifecycle --------------------------------------------------------
    def close(self) -> None:
        """Clean shutdown: the WAL already holds the memtable, so just close."""
        self.wal.close()

    def crash(self) -> None:
        """Simulate a process crash: drop the memtable without flushing it."""
        self.wal.close()
        self.memtable = Memtable()

    def file_count(self) -> int:
        return len(self.tables)

    def disk_bytes(self) -> int:
        return sum(t.size for t in self.tables)


# ---------------------------------------------------------------------------
# Demonstration: write amplification versus read amplification
# ---------------------------------------------------------------------------

def run_workload(tree: LSMTree, ops: int = 20_000, keyspace: int = 4_000,
                 delete_fraction: float = 0.15, value_size: int = 100, seed: int = 7) -> dict:
    """Apply a seeded random mix of puts and deletes; return the reference dict."""
    import random
    rng = random.Random(seed)
    reference: dict[str, str] = {}
    for i in range(ops):
        key = f"user:{rng.randrange(keyspace):05d}"
        if rng.random() < delete_fraction:
            tree.delete(key)
            reference.pop(key, None)
        else:
            value = f"{i:08d}".ljust(value_size, "x")
            tree.put(key, value)
            reference[key] = value
    return reference


def read_cost(tree: LSMTree, keys: list[str]) -> tuple[float, float]:
    """Average (SSTables consulted, data blocks read) per get over ``keys``."""
    before = (tree.stats.tables_consulted, tree.stats.block_reads)
    for key in keys:
        tree.get(key)
    n = len(keys)
    return ((tree.stats.tables_consulted - before[0]) / n,
            (tree.stats.block_reads - before[1]) / n)


def amplification_experiment(directory: str, seed: int = 7) -> list[dict]:
    """Load the same workload under several configurations and measure costs."""
    import random
    rng = random.Random(seed + 1)
    present_probe = [f"user:{rng.randrange(4_000):05d}" for _ in range(2_000)]
    absent_probe = [f"user:{rng.randrange(4_000):05d}-missing" for _ in range(2_000)]
    rows = []

    def measure(label: str, tree: LSMTree, reference: dict) -> None:
        assert all(tree.get(k) == reference.get(k) for k in present_probe[:200])
        present = read_cost(tree, present_probe)
        absent = read_cost(tree, absent_probe)
        rows.append(dict(label=label, tables=tree.file_count(),
                         disk_kb=tree.disk_bytes() / 1024,
                         wa_sst=tree.stats.write_amplification(include_wal=False),
                         wa_all=tree.stats.write_amplification(include_wal=True),
                         present_tables=present[0], present_reads=present[1],
                         absent_reads=absent[1]))

    configs = [("no compaction, no Bloom", dict(compaction=None, bloom_bits_per_key=0)),
               ("no compaction, Bloom 10 bits/key", dict(compaction=None)),
               ("size-tiered, Bloom 10 bits/key", dict(compaction="size-tiered"))]
    for i, (label, kwargs) in enumerate(configs):
        tree = LSMTree(os.path.join(directory, f"run{i}"), memtable_limit=500, **kwargs)
        reference = run_workload(tree, seed=seed)
        tree.flush()
        measure(label, tree, reference)
        if kwargs["compaction"] is not None:
            tree.compact_all()
            measure("  ... then full compaction", tree, reference)
        tree.close()
    return rows


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        rows = amplification_experiment(tmp)
    print("20,000 writes (15% deletes) over 4,000 keys, 100-byte values, memtable 500 entries\n")
    head = (f"{'configuration':<34}{'tables':>7}{'disk KB':>9}{'WA sst':>8}{'WA +wal':>8}"
            f"{'tables/get':>11}{'reads/get':>10}{'reads/miss':>11}")
    print(head)
    print("-" * len(head))
    for r in rows:
        print(f"{r['label']:<34}{r['tables']:>7}{r['disk_kb']:>9.0f}{r['wa_sst']:>8.2f}"
              f"{r['wa_all']:>8.2f}{r['present_tables']:>11.2f}{r['present_reads']:>10.2f}"
              f"{r['absent_reads']:>11.2f}")
    print("\nWA: write amplification = bytes written to disk / bytes the user wrote")
    print("tables/get: SSTables consulted per get of an existing-or-deleted key")
    print("reads/get, reads/miss: data blocks read from disk per get (key in range / absent key)")
