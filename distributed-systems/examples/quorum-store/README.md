# Quorum store (Chapter 6)

## The problem

Keep three copies of every key so that losing a server loses no data and the store keeps answering. Without a leader, any replica can take a write, so different replicas can hold different versions of a key at the same moment. A client that writes and then reads might get back the old value.

**Quorums** limit that. A client writes to all N replicas but waits for only W of them to confirm; it reads from R replicas and keeps the newest answer. If R + W > N, every read is guaranteed to reach at least one replica that has the latest confirmed write. This example simulates such a store, shows the guarantee holding over thousands of random runs with crashes and slow networks, and shows it failing when R + W ≤ N.

## Terms

- **Replica:** a server holding a copy of the data. **N** is the number of replicas per key.
- **Leaderless replication:** any replica accepts reads and writes; there is no primary. Amazon's Dynamo (2007) made the design famous; Cassandra and Riak follow it.
- **Write quorum (W):** how many replicas must acknowledge a write before the client is told it succeeded.
- **Read quorum (R):** how many replicas must answer a read. The client keeps the reply with the highest version.
- **Acknowledged write:** a write that reached W replicas, so the client was told "done".
- **Stale read:** a read that returns a version older than the latest acknowledged write.
- **Version:** here a pair *(timestamp, writer id)*, compared as a tuple. The higher version wins: **last-writer-wins** (LWW). Ties on the timestamp are broken by writer id.
- **Read repair:** when a reader sees a replica with an old version, it sends that replica the newest one.
- **Quorum intersection:** every possible read quorum shares at least one replica with every possible write quorum.

## Why R + W > N works

A read contacts a set of R replicas and the latest acknowledged write reached a set of W replicas, both out of N. If the two sets were disjoint, together they would contain R + W > N distinct replicas, more than exist (the pigeonhole principle). So they share a replica. That replica holds the latest acknowledged write or something newer, because a replica never replaces a version with an older one (`Replica.apply`). The reader takes the maximum version it sees, so the read is not stale. Conversely, if R + W ≤ N, pick the read set and write set disjoint: the read can miss the write entirely.

`quorums_intersect(n, r, w)` checks the first claim by brute force, trying every pair of subsets, and the tests confirm it equals `r + w > n` for every N up to 7. It is the same property Chapter 6 proves, and the reason Raft and Paxos (Chapter 11) use majorities: two majorities always overlap.

## How the simulation works

`quorum.py`:

| Name | What it does |
|---|---|
| `quorums_intersect(n, r, w)` | Brute-force quorum intersection |
| `Replica` | `get(key)`, `apply(key, version, value)`; keeps the higher version |
| `QuorumStore(n, r, w, seed, max_delay, read_repair)` | `write(key, value, writer)` returns the version or `None`; `read(key)` returns a `ReadResult` or `None`; `set_up(rid, up)`; `tick()` |
| `run_trial(n, r, w, seed, ops, ...)` | A random workload with crashes and recoveries; returns `TrialStats` (reads, stale reads, failed operations, repairs) |
| `stale_table(n, trials, ...)` | `TrialStats` for every (R, W) |

Each write goes to every replica. The first W up replicas (chosen at random) apply it at once; the rest receive it 1 to `max_delay` ticks later, and a replica that is down when its copy arrives never gets it. Replicas crash with probability 5% per operation and recover with probability 30%, keeping their data. A read picks R random up replicas. An operation fails if fewer than R (or W) replicas are up.

## Run it

```bash
python3 quorum.py          # demo, about 5 seconds
python3 -m unittest -v     # 12 tests
```

Stale-read rate from the demo, N = 3, 200 random runs of 200 operations each (* means R + W > N):

| | W = 1 | W = 2 | W = 3 |
|---|---|---|---|
| R = 1 | 34.4% | 15.0% | 0%* |
| R = 2 | 10.2% (7.7% with read repair) | 0%* | 0%* |
| R = 3 | 0%* | 0%* | 0%* |

Read repair cannot help when R = 1 because the reader hears from only one replica.

Availability is the price. With R = W = 2, 5.4% of writes and 5.4% of reads failed for lack of a quorum; with W = 3 (write to all), 36.8% of writes failed, because a single crashed replica blocks every write.

## Experiments to try

1. **Find the cheapest safe setting.** Run `stale_table(5, 50)` and print stale and failed rates for N = 5. Which (R, W) pairs are safe, and which of those fails least often?
2. **Slow the network.** Set `max_delay=1` and then `max_delay=50` in `run_trial`. How does the stale rate of R = W = 1 change? This is "eventual" consistency made visible: the longer propagation takes, the longer the window of inconsistency.
3. **Turn on hinted handoff.** In `QuorumStore.tick`, writes to a down replica are dropped. Change this so they are kept in `pending` until the replica recovers. How does the stale rate for R = W = 1 change? (Real stores also let another node accept the write temporarily: a *sloppy quorum*. Can R + W > N still guarantee fresh reads then?)
4. **Break monotonicity.** Make `Replica.apply` always overwrite, even with an older version. `test_overlapping_quorums_never_read_stale` should now fail. The intersection argument needs both overlap and replicas that never go backwards.
5. **Lose a write to clock skew.** Versions here come from a single global clock. Give each writer its own clock with an offset (say writer `c0` is 10 ticks behind). Two writes in a row from `c1` then `c0`: which survives? This is why LWW with wall clocks silently drops writes, and why Riak used vector clocks and siblings (see `logical-clocks/` and `crdts/`).

## Limitations

- One key, and a global logical clock that issues versions; real coordinators use wall-clock timestamps or vector clocks.
- R + W > N guarantees a read sees the latest *acknowledged* write. It does not make the store linearizable: concurrent reads during a write in progress can disagree, and a failed write may still be visible (Chapter 8).
- No sloppy quorums, hinted handoff or Merkle-tree anti-entropy; replicas that miss a write learn it only through read repair.
- Replicas are chosen at random; real clients pick the N replicas for a key from a hash ring (see `consistent-hashing/`) and wait for the fastest responders.
