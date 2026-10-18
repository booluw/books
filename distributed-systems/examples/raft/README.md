# Raft in a deterministic simulator (Chapter 11)

## The problem

Five servers must agree on one sequence of commands, so that each can apply them to its own copy of a key-value store and all copies stay identical. Any server can crash and restart; messages can be delayed, lost, duplicated, reordered, or cut off by a network partition. There is no reliable clock and no way to tell a crashed server from a slow one. This is **consensus**, and **Raft** (Ongaro and Ousterhout, 2014) is the algorithm most production systems now use for it: etcd, Consul, CockroachDB, TiKV and Kafka's KRaft among them.

This folder implements Raft's core (leader election, log replication, the commit rule and a key-value state machine) and runs it inside a **deterministic discrete-event simulator** with a hostile network and a fault injector. After every single event, an independent checker verifies Raft's four safety properties. Two deliberate bugs can be switched on to show the checker catching them, and `figure8.py` replays the paper's most famous counterexample step by step.

## Terms

- **Replicated state machine:** every server applies the same commands in the same order to a deterministic program (here a key-value store), so every copy ends in the same state. Consensus is needed only to agree on the order: the **log**.
- **Log entry:** a command plus the **term** in which a leader created it. Entries are numbered by **index** from 1.
- **Term:** a number that increases with every election. It acts as a logical clock: a message from an older term is stale and is rejected; seeing a newer term makes any server step down to follower.
- **Follower, candidate, leader:** the three roles. A **follower** that hears nothing for an **election timeout** (random, 150 to 300 ms here) becomes a **candidate**, increments its term, votes for itself and requests votes. A majority (3 of 5) makes it **leader** for that term. The leader sends **heartbeats** (empty AppendEntries) every 50 ms to stop new elections.
- **Persistent state:** `currentTerm`, `votedFor` and the log must survive a crash, because a server that forgot its vote could vote twice in one term. Everything else (commit index, the state machine itself) is rebuilt after restart.
- **AppendEntries consistency check:** each AppendEntries carries the index and term of the entry *before* the new ones. A follower that lacks that entry rejects the message, and the leader retries one step earlier. Logs therefore agree up to the last matching entry.
- **Committed:** an entry is committed once the leader of its term has stored it on a majority. Committed entries are applied to the state machine and must never be lost.
- **Quorum / majority:** any two majorities of five servers share at least one server. Every safety argument in Raft rests on that overlap.
- **Safety** properties say nothing bad ever happens; **liveness** properties say something good eventually happens. Raft guarantees safety always, and liveness only when the network is well behaved for long enough (the FLP result, Chapter 10, says no deterministic algorithm can promise more).
- **Discrete-event simulation:** virtual time and a priority queue of events. Every random choice comes from one seeded generator, so any run, including one that found a bug, can be replayed exactly.
- **Nemesis:** the fault injector (Jepsen's term). Here it crashes and restarts servers and creates and heals partitions at random times.

## The safety properties (Figure 3 of the paper)

`invariants.py` keeps **ghost state** (things no real server knows, such as every commit ever observed) and checks after every event:

| Property | Meaning | How it is checked |
|---|---|---|
| **Election Safety** | at most one leader per term | remember the first leader seen for each term |
| **Log Matching** | two logs with the same term at the same index are identical up to there | for each pair of servers, find the highest index with equal terms and compare the prefixes (only when some log changed) |
| **Leader Completeness** | a committed entry is in the log of every leader of a later term | record each entry and the term in which it was first seen committed; check every current leader |
| **State Machine Safety** | no two servers apply (or commit) different entries at the same index | record the first entry committed and applied at each index |

## How the code is organised

| File | What it holds |
|---|---|
| `sim.py` | `Scheduler` (virtual clock, event queue) and `Network` (delay, loss, duplication, reordering via random delays, partitions) |
| `raft.py` | `RaftNode`: the algorithm, following the paper's Figure 2 line by line; `Storage` (persistent state); `KVStateMachine` with per-client deduplication |
| `invariants.py` | `InvariantChecker` |
| `cluster.py` | `Cluster` of five nodes, a retrying `Client`, the nemesis, `chaos_run()`, `find_bug()` and the demo |
| `figure8.py` | a hand-driven network that replays Figure 8 exactly |

Messages are frozen dataclasses: `RequestVote`, `RequestVoteReply`, `AppendEntries`, `AppendEntriesReply`, `ClientRequest`, `ClientReply`. A message handler runs atomically, so persisting state "before replying" holds automatically; real servers must `fsync` before they answer.

## Figure 8: why a leader may not commit an old entry by counting replicas

The obvious commit rule ("an entry stored on a majority is committed") is wrong. `python3 figure8.py` drives the real `RaftNode` code through the paper's schedule; the numbers in each log are entry terms:

```
(a) S1 leads term 2; entry 2 (term 2) reaches S2 only
    S1 leader  term=2  log=[1 2]     S2 follower log=[1 2]    S3, S4, S5 log=[1]
(b) S1 crashes; S5 leads term 3 (votes from S3, S4) and appends entry 2 (term 3) locally
    S5 leader  term=3  log=[1 3]
(c) S5 crashes; S1 restarts, leads term 4 (votes from S2, S3), copies entry 2 (term 2) to S3,
    appends entry 3 (term 4)
    S1 leader  term=4  log=[1 2 4]   S2 log=[1 2]   S3 log=[1 2]   <- entry 2 is on a majority
(d) S1 crashes; S5 restarts and wins term 5 with votes from S2, S3, S4
    (its last log term, 3, beats their 2 and 1), then overwrites entry 2 everywhere
    S2, S3, S4, S5 log=[1 3 5]
```

If S1 had committed entry 2 in step (c) because three servers stored it, step (d) would destroy a committed entry. With `bugs={"commit_previous_term"}` that is exactly what happens: S1 applies `put x=2` at index 2, the rest of the cluster later applies `put x=3` there, and the checker reports:

```
!! Leader Completeness: S5, leader in term 5, lacks entry 2 (term 2) committed in term 4 by S1
!! State Machine Safety: index 2 committed as term-2 entry by S1 and as term-3 entry by S5 (+7 more like it)
```

**The fix (Raft section 5.4.2):** a leader counts replicas only for entries from its *current* term. Older entries are committed indirectly, when a current-term entry after them is committed; Log Matching then guarantees the earlier ones are there too. In the correct run, S1 in step (c) shows `commit=0` despite having entry 2 on a majority, and nothing committed is ever lost. (The paper's alternative (e): if S1 had replicated entry 3 (term 4) to a majority before crashing, entries 2 and 3 would be committed and S5 could not have won term 5, because its log would not be up to date.) This is also why many implementations append a **no-op entry** when a leader is elected (`RaftConfig(noop_on_election=True)`, paper section 8): it lets the new leader commit earlier entries promptly.

## Numbers to quote

From `python3 cluster.py` and the tests (all deterministic, Python 3.13, October 2026):

- **Stable network** (delays 5 to 25 ms, no loss): over 100 seeds a leader is elected within 1,000 ms every time; over 200 seeds the median is 200 ms and the worst 533 ms. Seed 1 elects S1 at 204 ms in term 1 and commits and acknowledges 20 client commands by 1,375 ms, with 753 invariant checks.
- **Chaos** (delays 2 to 30 ms, 5% loss, 5% duplication, a crash, restart, partition or heal every 100 to 600 ms, for 5 simulated seconds): 100 seeds produce 139,830 events, each followed by a full invariant check, and 2,628 committed entries, with **0 violations**. The test suite runs 300 such seeds; a 500-seed survey also found none.
- **Recovery:** after 3 seconds of chaos, healing the network and restarting every server, the client commits 10 more commands in every one of 200 seeds (median 1.3 s, worst 3.3 s).
- **Bug `vote_without_log_check`:** caught in 277 of 500 chaos seeds, first on **seed 1**: S3 is partitioned at 654 ms and crashes at 1,136 ms, misses entries, restarts at 2,121 ms and wins term 4 with votes it should not have had. The checker reports at 2,369 ms: `Leader Completeness: S3, leader in term 4, lacks entry 3 (term 1) committed in term 1 by S1`.
- **Bug `commit_previous_term`:** much rarer under random faults, caught in only **2 of 500** seeds (**91** and 350). On seed 91, at 3,288 ms: `S3, leader in term 10, lacks entry 28 (term 4) committed in term 8 by S1`, after a burst of partitions. This is the Figure 8 schedule found by random search, and the reason the paper's authors drew the figure: a rare bug can pass hundreds of tests.

## Run it

```bash
python3 cluster.py          # stable run, 100 chaotic runs, then hunt both bugs
python3 cluster.py 500      # more chaotic runs
python3 figure8.py          # Figure 8, correct and buggy
python3 -m unittest -v      # 16 tests, about 10 seconds
```

To replay one schedule and look around:

```python
from cluster import chaos_run, Cluster
r = chaos_run(91, bugs={"commit_previous_term"})
print(r.violation); print("\n".join(r.faults))
```

## Experiments to try

1. **Hunt a bug yourself.** `find_bug("commit_previous_term", range(1000))` from `cluster.py`. How many seeds until the second hit? Raise the nemesis rate (`NemesisConfig(interval=(20.0, 150.0))` in `chaos_run`) and see whether it is found sooner.
2. **Forget the vote on restart.** In `RaftNode.restart`, add `self.storage.voted_for = None` (as if `votedFor` were not persisted). In principle this allows two leaders in one term. Run several hundred chaos seeds: the window (crash after voting, restart, second candidate in the same term) is narrow, so you may need many seeds or a targeted script in the style of `figure8.py`. Rare windows are exactly why such bugs survive in production code.
3. **Identical timeouts.** Set `RaftConfig(election_timeout=(150.0, 150.5))`. Candidates now time out together and split the vote. Measure time to first leader over 100 seeds and compare with the default (median 200 ms). Randomisation is what makes Raft's elections converge.
4. **A network slower than the timeouts.** `Cluster(seed, net=NetConfig(delay=(150.0, 300.0)))`. Safety holds (no violations), but terms climb and few commands commit: leaders are deposed before their heartbeats arrive. This is liveness depending on timing, as FLP predicts.
5. **No-op on election.** Run `figure8.py` with `RaftConfig(noop_on_election=True)` in `Figure8.__init__`. In step (c), S1 now appends a term-4 no-op immediately; how does that change which entries can commit?
6. **Batch size.** Set `max_batch=1` and compare how long a restarted follower takes to catch up after a long partition.
7. **Break the duplicate check.** In `on_append_entries`, delete the `if self.term_at(index) == entry.term: continue` lines so every AppendEntries truncates and re-appends. The unit test `test_stale_duplicate_append_does_not_truncate` fails at once. Do the chaos runs notice? Think about why a late, duplicated message is dangerous once a leader has counted a follower's acknowledgement.

## Limitations

- No membership changes, log compaction or snapshots, and no read optimisations (lease reads, ReadIndex). Reads would go through the log like writes.
- `next_index` backs up one entry at a time (with a simple hint when the follower's log is short). The paper's section 5.3 describes faster back-up.
- The client acknowledges a command once the leader applies it; a client whose leader crashes retries with the same sequence number, and the state machine applies it once. The client itself is never partitioned.
- A message handler is atomic and persistence is free. Real implementations must handle torn writes, `fsync` latency and disks that lie.
- Random testing finds bugs probabilistically. Zero violations in 500 seeds is evidence, not proof; the TLA+ specification of Raft (see `../tla/` and Chapter 5) and its model checking are the stronger argument.

## Chapter

Chapter 11 (Consensus in practice: Raft). Chapter 23 (Testing distributed systems) returns to deterministic simulation and the nemesis.

## References

- D. Ongaro and J. Ousterhout, "In Search of an Understandable Consensus Algorithm", *Proceedings of USENIX ATC*, 2014 (Figures 2, 3 and 8 are referred to above).
- D. Ongaro, *Consensus: Bridging Theory and Practice*, PhD thesis, Stanford University, 2014.
- Raft website and implementations list, raft.github.io (checked October 2026).
- K. Kingsbury, Jepsen analyses, jepsen.io (checked October 2026).
- W. Wilson, "Testing Distributed Systems w/ Deterministic Simulation", Strange Loop 2014 (FoundationDB).
