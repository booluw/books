# A log-structured merge tree (Chapter 15)

## The problem

A database must put data on disk so that it survives a crash, and must find it again quickly. Disks, both spinning and solid-state, are much faster at large sequential writes than at small random ones. A B-tree, the classic on-disk index, updates pages in place wherever the key happens to live, which means random writes.

A **log-structured merge tree** (LSM tree; O'Neil, Cheng, Gawlick and O'Neil, 1996) never updates in place. It buffers writes in memory, writes them out in large sorted batches, and tidies up later in the background. Writes become cheap and sequential; the price is paid by reads, which may need to look in several files, and by the background tidying, which rewrites the same data more than once. RocksDB, LevelDB, Cassandra, ScyllaDB, HBase and the storage layers of CockroachDB and TiKV all work this way.

This folder is a complete small LSM engine: about 500 lines of standard-library Python (plus a demonstration) that survives crashes and measures its own costs.

## Terms

- **Write-ahead log (WAL):** an append-only file. Each change is appended (and optionally `fsync`ed, forced to the physical disk) *before* it is applied in memory, so after a crash the log can be replayed.
- **Memtable:** the in-memory sorted map that holds recent writes. Here a sorted list of keys maintained with `bisect`, plus a dict.
- **Flush:** writing a full memtable to disk as a new SSTable, after which its WAL can be discarded.
- **SSTable (sorted string table):** an immutable file of key-value records sorted by key. Never modified after it is written.
- **Sparse index:** the key and file offset of every 16th record, kept in memory. A lookup binary-searches it and reads one small **block** of records.
- **Fence pointers:** each SSTable's smallest and largest key; a key outside that range cannot be in the file.
- **Bloom filter:** a bit array plus `k` hash functions that answers "possibly present" or "definitely absent". No false negatives; a tunable rate of false positives, approximately `(1 − e^(−kn/m))^k` for `n` keys in `m` bits.
- **Tombstone:** a record meaning "this key was deleted". Needed because older files cannot be edited and may still hold the old value.
- **Compaction:** merging several SSTables into one, keeping only the newest version of each key. **Size-tiered** compaction (Cassandra's default) merges a group of similar-sized tables once there are enough of them (here 4). **Levelled** compaction (RocksDB's default) is the alternative; see Limitations.
- **Write amplification (WA):** bytes written to disk divided by bytes the user wrote. Every compaction that rewrites a record adds to it.
- **Read amplification:** work per lookup: here, SSTables consulted and data blocks read from disk per `get`.
- **Space amplification:** disk used divided by live data. Overwritten values and tombstones occupy space until compaction removes them.

## How it works

| File | What it holds |
|---|---|
| `bloom.py` | `BloomFilter` (blake2b from `hashlib`, double hashing), `expected_fp_rate()`, `measure_fp_rate()` |
| `wal.py` | `WriteAheadLog`: CRC-checked records, replay that stops at a torn tail |
| `sstable.py` | `write_sstable()` and `SSTable` (sparse index, fence pointers, Bloom filter, `get`, `scan`) |
| `lsm.py` | `Memtable`, `merge_tables()`, `LSMTree`, `Stats`, and the amplification experiment |
| `test_lsm.py` | 12 unit tests |

**Write path.** `put` and `delete` append to `wal.log`, then update the memtable. At `memtable_limit` entries the memtable is flushed: the SSTable is written, the `MANIFEST` (the list of live tables, newest first) is replaced atomically with `os.replace`, and only then is the WAL emptied.

**Read path.** `get` checks the memtable, then each SSTable from newest to oldest. For each table the fence pointers and Bloom filter are checked in memory; only if both say "maybe" is a data block read. The first entry found wins, and a tombstone means "not found".

**Crash recovery.** Opening a tree loads the tables named in `MANIFEST` and replays `wal.log` into a fresh memtable. A half-written final WAL record fails its CRC (cyclic redundancy check, a checksum) and is ignored. An SSTable written just before a crash but not yet in the manifest is ignored too, and its data is still in the WAL.

**Compaction.** After each flush, `maybe_compact` looks for four adjacent tables whose sizes are within a factor of two and merges them with a k-way merge (`heapq.merge`). Merging only *adjacent* tables keeps "newer table wins" true. Tombstones are dropped only when the merge includes the oldest table, because otherwise an older value could reappear (the "resurrection" bug, which `test_tombstone_shadows_older_table_until_compacted_away` checks). The manifest switches to the new table before the inputs are deleted.

## What it shows

Bloom filter false-positive rate, 10,000 keys, 20,000 absent probes (`python3 bloom.py`):

| Bits per key | k | Measured | Formula |
|---|---|---|---|
| 2 | 1 | 39.83% | 39.35% |
| 4 | 3 | 14.72% | 14.69% |
| 6 | 4 | 5.65% | 5.61% |
| 8 | 6 | 2.05% | 2.16% |
| 10 | 7 | 0.72% | 0.82% |
| 12 | 8 | 0.34% | 0.31% |
| 16 | 11 | 0.03% | 0.05% |

Each extra bit per key cuts false positives by roughly a third or more; 10 bits per key (1.25 bytes) gives under 1%.

Amplification, 20,000 writes (15% deletes) over 4,000 keys with 100-byte values and a 500-entry memtable (`python3 lsm.py`):

| Configuration | Tables | Disk KB | WA (SSTables) | WA (with WAL) | Tables consulted per get | Blocks read per get | Blocks read per missing key |
|---|---|---|---|---|---|---|---|
| No compaction, no Bloom | 38 | 1,911 | 1.03 | 2.16 | 8.42 | 8.38 | 37.86 |
| No compaction, Bloom 10 bits/key | 38 | 1,935 | 1.04 | 2.17 | 8.42 | 1.05 | 0.33 |
| Size-tiered, Bloom 10 bits/key | 5 | 962 | 2.26 | 3.38 | 3.32 | 1.00 | 0.04 |
| … then full compaction | 1 | 400 | 2.47 | 3.60 | 1.00 | 0.84 | 0.01 |

- Without compaction every byte reaches an SSTable once (WA ≈ 1), but data piles up in 38 files using almost five times the space of the live data (400 KB), and a lookup for a missing key reads a block from nearly every file.
- Bloom filters fix most of the read cost without compaction: 38 → 0.33 block reads per miss, which is 38 tables × 0.8%.
- Size-tiered compaction more than doubles the write amplification and in return cuts files from 38 to 5, space by half, and tables consulted per get from 8.4 to 3.3.
- A full compaction leaves one table holding exactly the live data; deleted keys and their tombstones are gone.
- The WAL adds about 1.1 to WA: every byte is written once to the log and once to an SSTable.

## Run it

```bash
python3 bloom.py           # false-positive rate versus bits per key
python3 lsm.py             # write and read amplification, before and after compaction
python3 -m unittest -v     # 12 tests, a few seconds
```

Standard-library Python 3 only. Files go in temporary directories that are removed afterwards. All workloads are seeded.

## Experiments to try

Start a Python shell in this folder, then `import os, tempfile; from lsm import *; d = tempfile.mkdtemp()`. A useful probe for misses is `misses = [f"user:{j:05d}-missing" for j in range(2000)]`.

1. **Tune the Bloom filter.** `t = LSMTree(os.path.join(d, "b5"), memtable_limit=500, bloom_bits_per_key=5); run_workload(t); t.flush(); read_cost(t, misses)`. With 5 bits per key and 5 tables you read about 0.46 blocks per miss (about 9% per table); with 20 bits per key, essentially 0. Memory per key versus disk reads per miss is the trade.
2. **Change the tier size.** Repeat with `tier_threshold=2`, `4` and `8`. You get 3, 5 and 10 tables with write amplification of 4.34, 2.26 and 1.62. Merging more eagerly costs writes and saves reads.
3. **Change the memtable size.** `memtable_limit=100` gives write amplification of 3.57 and 6 tables; `memtable_limit=2000` gives 1.23 and 2 tables. Bigger memtables mean fewer, larger flushes and less compaction, at the cost of memory and a longer WAL replay after a crash.
4. **Crash it yourself.** Put 250 keys with `memtable_limit=100`, call `t.crash()`, reopen with `LSMTree(same_dir, memtable_limit=100)` and check `t.recovered` (50) and the data. Then append a few junk bytes to `wal.log` before reopening: replay stops cleanly at the torn record.
5. **Delete-heavy workloads.** `run_workload(t, delete_fraction=0.5)` with `compaction=None`, then compare `t.disk_bytes()` before and after `t.compact_all()`: about 1,290 KB shrinks to about 230 KB. Tombstones and dead values are space amplification until compaction removes them.
6. **Pay for durability.** Time 2,000 puts with `sync=True` (an `fsync` per write) against the default. On the machine used to write this, 3.1 s against 0.02 s: more than 100 times slower. This is why real engines use **group commit**, one `fsync` for a batch of writes.
7. **Break the safety rule.** In `_compact`, change `drop_tombstones=bottom` to `drop_tombstones=True` and run the tests. The resurrection test fails: a deleted key comes back.
8. **Coarser index.** Use `index_interval=128` and instrument `SSTable._read` to sum bytes read. Each lookup now scans eight times as many bytes; the index uses an eighth of the memory.

## Limitations

- Size-tiered only. **Levelled compaction** (LevelDB, RocksDB) keeps each level a single sorted run ten times bigger than the last; it has lower read and space amplification and higher write amplification (often 10–30).
- Data blocks are not compressed or cached, and "a block read" is a stand-in for a disk I/O: the operating system's page cache will make these reads fast in practice.
- One thread, no concurrency control, and compaction runs inline instead of in the background. No snapshots or sequence numbers, so no multi-version reads.
- The WAL is only `fsync`ed with `sync=True`, and directory entries are never `fsync`ed, which a production engine must also do for a newly created file to survive a power cut.
- Keys and values are strings and every SSTable is read fully into memory when opened to load its index.

## Chapter

Chapter 15 (storage engines: logs, LSM trees, B-trees, Bloom filters and amplification).
