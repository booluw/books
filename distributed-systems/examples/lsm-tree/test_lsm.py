"""Tests for the LSM tree: Bloom filter, WAL, SSTables, recovery, compaction."""

import os
import random
import tempfile
import unittest

from bloom import BloomFilter, measure_fp_rate
from lsm import LSMTree, Memtable, merge_tables, read_cost, run_workload
from sstable import SSTable, write_sstable
from wal import WriteAheadLog


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()


class BloomTests(unittest.TestCase):
    def test_no_false_negatives(self):
        bf = BloomFilter.for_keys(5_000, 6)
        keys = [f"k{i}".encode() for i in range(5_000)]
        for k in keys:
            bf.add(k)
        self.assertTrue(all(bf.might_contain(k) for k in keys))
        self.assertTrue(all(BloomFilter.from_bytes(bf.to_bytes()).might_contain(k) for k in keys))

    def test_false_positive_rate_matches_formula(self):
        for bits_per_key in (4, 8, 12):
            measured, formula, _k = measure_fp_rate(5_000, bits_per_key, probes=20_000)
            # Within 30% of the formula, or within 0.2 percentage points for tiny rates.
            self.assertLess(abs(measured - formula), max(0.3 * formula, 0.002),
                            f"{bits_per_key} bits/key: {measured:.4f} vs {formula:.4f}")


class ComponentTests(TempDirTest):
    def test_memtable_keeps_keys_sorted(self):
        m = Memtable()
        for k in [b"c", b"a", b"b", b"a"]:
            m.put(k, k.upper())
        self.assertEqual(m.keys, [b"a", b"b", b"c"])
        self.assertEqual(list(m.scan(b"b", None)), [(b"b", b"B"), (b"c", b"C")])

    def test_wal_replay_ignores_torn_tail(self):
        path = os.path.join(self.dir, "wal.log")
        wal = WriteAheadLog(path)
        wal.append(b"a", b"1")
        wal.append(b"b", None)
        wal.close()
        with open(path, "ab") as f:
            f.write(b"\x00\x00\x00\x07\x00\x00")        # half a record: a torn write
        self.assertEqual(list(WriteAheadLog.replay(path)), [(b"a", b"1"), (b"b", None)])

    def test_sstable_sparse_index_lookup_and_tombstone(self):
        path = os.path.join(self.dir, "t.sst")
        entries = [(f"k{i:04d}".encode(), None if i % 10 == 0 else f"v{i}".encode())
                   for i in range(200)]
        write_sstable(path, entries, len(entries), index_interval=16)
        t = SSTable(path)
        self.assertEqual(len(t.index_keys), 13)            # ceil(200 / 16)
        self.assertEqual(t.get(b"k0123"), (True, b"v123"))
        self.assertEqual(t.get(b"k0120"), (True, None))    # tombstone is found, not missing
        self.assertEqual(t.get(b"k0123x")[0], False)
        self.assertEqual([k for k, _ in t.scan(b"k0195", None)],
                         [b"k0195", b"k0196", b"k0197", b"k0198", b"k0199"])

    def test_merge_prefers_newest_source(self):
        newest = [(b"a", b"new"), (b"c", None)]
        oldest = [(b"a", b"old"), (b"b", b"old"), (b"c", b"old")]
        self.assertEqual(list(merge_tables([iter(newest), iter(oldest)], False)),
                         [(b"a", b"new"), (b"b", b"old"), (b"c", None)])
        self.assertEqual(list(merge_tables([iter(newest), iter(oldest)], True)),
                         [(b"a", b"new"), (b"b", b"old")])


class LSMTreeTests(TempDirTest):
    def test_crash_recovery_from_wal(self):
        tree = LSMTree(self.dir, memtable_limit=100)
        for i in range(250):                   # two flushes and 50 entries only in memory
            tree.put(f"k{i:03d}", str(i))
        tree.delete("k007")
        tree.crash()
        reopened = LSMTree(self.dir, memtable_limit=100)
        self.assertEqual(reopened.recovered, 51)
        self.assertEqual(reopened.get("k249"), "249")
        self.assertIsNone(reopened.get("k007"))
        self.assertEqual(len(reopened.scan()), 249)
        reopened.close()

    def test_randomised_operations_match_dict_across_restarts(self):
        for seed in range(4):
            rng = random.Random(seed)
            path = os.path.join(self.dir, f"s{seed}")
            tree = LSMTree(path, memtable_limit=rng.choice([7, 20, 50]),
                           index_interval=rng.choice([1, 4, 16]), tier_threshold=3)
            ref: dict[str, str] = {}
            for step in range(3_000):
                key = f"key{rng.randrange(300):03d}"
                r = rng.random()
                if r < 0.55:
                    ref[key] = f"v{step}"
                    tree.put(key, ref[key])
                elif r < 0.75:
                    ref.pop(key, None)
                    tree.delete(key)
                elif r < 0.95:
                    self.assertEqual(tree.get(key), ref.get(key), f"seed {seed} step {step}")
                elif r < 0.98:
                    lo, hi = sorted([f"key{rng.randrange(300):03d}" for _ in range(2)])
                    self.assertEqual(tree.scan(lo, hi),
                                     sorted((k, v) for k, v in ref.items() if lo <= k < hi))
                elif r < 0.99:
                    (tree.crash if rng.random() < 0.5 else tree.close)()
                    tree = LSMTree(path, memtable_limit=tree.memtable_limit,
                                   index_interval=tree.index_interval, tier_threshold=3)
                else:
                    tree.compact_all()
            self.assertEqual(tree.scan(), sorted(ref.items()))
            tree.close()

    def test_tombstone_shadows_older_table_until_compacted_away(self):
        tree = LSMTree(self.dir, memtable_limit=1_000, compaction=None)
        tree.put("ghost", "boo")
        tree.flush()
        tree.delete("ghost")
        tree.put("other", "x")
        tree.flush()
        self.assertIsNone(tree.get("ghost"))
        tree._compact(0, 1)                    # newest table only: not the bottom
        self.assertIsNone(tree.get("ghost"), "tombstone dropped too early: data resurrected")
        tree.compact_all()
        self.assertEqual(tree.file_count(), 1)
        self.assertEqual(tree.tables[0].count, 1)   # ghost and its tombstone are gone
        tree.close()

    def test_orphan_sstable_from_crashed_compaction_is_ignored(self):
        tree = LSMTree(self.dir, memtable_limit=10, compaction=None)
        for i in range(30):
            tree.put(f"k{i:02d}", "v")
        tree.crash()
        # A crash after writing an SSTable but before the manifest names it.
        write_sstable(os.path.join(self.dir, "sst-999999.sst"), [(b"k05", b"stale")], 1)
        reopened = LSMTree(self.dir, memtable_limit=10, compaction=None)
        self.assertEqual(reopened.get("k05"), "v")
        reopened.close()

    def test_compaction_trades_write_amplification_for_read_amplification(self):
        results = {}
        for mode in (None, "size-tiered"):
            tree = LSMTree(os.path.join(self.dir, str(mode)), memtable_limit=200,
                           compaction=mode, bloom_bits_per_key=0)
            run_workload(tree, ops=6_000, keyspace=1_500, seed=3)
            tree.flush()
            misses = [f"user:{i:05d}-missing" for i in range(0, 1_500, 5)]
            results[mode] = (tree.stats.write_amplification(False), tree.file_count(),
                             read_cost(tree, misses)[1])
            tree.close()
        (wa_none, files_none, reads_none), (wa_st, files_st, reads_st) = \
            results[None], results["size-tiered"]
        self.assertLess(wa_none, 1.2)          # each byte written to an SSTable once
        self.assertGreater(wa_st, 1.5)         # compaction rewrites it
        self.assertLess(files_st, files_none / 3)
        self.assertLess(reads_st, reads_none / 3)

    def test_bloom_filters_cut_reads_for_missing_keys(self):
        costs = []
        for bits in (0, 10):
            tree = LSMTree(os.path.join(self.dir, str(bits)), memtable_limit=200,
                           compaction=None, bloom_bits_per_key=bits)
            run_workload(tree, ops=4_000, keyspace=1_000, seed=5)
            tree.flush()
            costs.append(read_cost(tree, [f"user:{i:05d}-missing" for i in range(1_000)])[1])
            tree.close()
        self.assertGreater(costs[0], 10)       # every table in range is read
        self.assertLess(costs[1], 0.5)         # ~1% false positives per table


if __name__ == "__main__":
    unittest.main()
