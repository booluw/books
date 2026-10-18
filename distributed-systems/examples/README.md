# Examples

Runnable companions to the chapters. Every Python example uses **only the standard library** (Python 3.11 or later; tested with 3.13 in October 2026), so there is nothing to install. Networks, clocks, crashes and message loss are simulated, and every simulation is seeded, so a run with the same seed always gives the same result. That makes a surprising result something you can rerun, print and debug, rather than a flaky one-off.

Each folder has a README that explains the problem, defines the terms it uses, shows how to run it, lists **experiments to try** (concrete things to change and measure) and states its limitations. The exception is `tla/`, which holds TLA+ specifications rather than Python.

| Folder | Chapter | What it teaches |
|---|---|---|
| [`gossip-membership/`](gossip-membership/) | 2 | Push, pull and push-pull gossip with message loss; rounds to reach every node grow as log N; gossip-style membership; heartbeat timeout and phi accrual failure detectors, and the trade-off between detection time and false positives |
| [`logical-clocks/`](logical-clocks/) | 3 | Lamport and vector clocks on random message-passing runs, checked against happened-before computed from the event graph; why Lamport order cannot detect concurrency; hybrid logical clocks under clock skew |
| [`model-checker/`](model-checker/) | 5 | A small explicit-state model checker in Python: breadth-first search of every reachable state, invariant checking and shortest counterexample traces |
| [`tla/`](tla/) | 5 | TLA+ specifications checked with the TLC model checker: Die Hard warm-up, quorum intersection, two-phase commit, Raft leader election and locks with fencing tokens, plus deliberately broken configurations whose counterexamples TLC prints |
| [`quorum-store/`](quorum-store/) | 6 | A leaderless replicated key-value store with N, R and W; crashes, late delivery and read repair; brute-force proof that quorums intersect iff R + W > N; stale-read rates on either side of that line |
| [`consistent-hashing/`](consistent-hashing/) | 7 | Hash rings with virtual nodes, rendezvous hashing and mod-N hashing compared: fraction of keys moved when a node joins or leaves, and load imbalance against the number of virtual nodes |
| [`linearizability-checker/`](linearizability-checker/) | 8, 23 | Checking whether a concurrent history of operations is linearizable, with histories that pass and fail and a simulated store that produces both |
| [`transactions/`](transactions/) | 9 | Two-phase commit across participants, and sagas with compensating actions |
| [`crdts/`](crdts/) | 10 | G-Counter, PN-Counter, LWW-Register and add-wins OR-Set; randomised tests of the semilattice laws (commutative, associative, idempotent) and convergence; the lost updates of a naive counter |
| [`raft/`](raft/) | 11 | Raft leader election and log replication in a simulated cluster with crashes and partitions |
| [`lsm-tree/`](lsm-tree/) | 15 | A log-structured merge tree: write-ahead log, memtable, sorted string tables, Bloom filters, compaction and crash recovery |
| [`stream-windows/`](stream-windows/) | 16 | Event-time windows, watermarks and late data; the Chandy–Lamport consistent snapshot algorithm |
| [`resilience/`](resilience/) | 17 | Timeouts, retries with exponential backoff and jitter, circuit breakers, and how naive retries turn a brief overload into a retry storm |
| [`deterministic-simulation/`](deterministic-simulation/) | 23 | Deterministic simulation testing: running a distributed system on a seeded simulated network and clock so that any failure found can be replayed exactly |

## Run every test

From the repository root:

```bash
python3 distributed-systems/examples/run_all_tests.py
```

The runner finds every folder with `test_*.py` files and runs them with `unittest`. Each folder also runs on its own: `cd` into it and run `python3 -m unittest -v`.

`tla/` has no Python tests. Checking its specifications needs **Java** (11 or later) and **`tla2tools.jar`**, the TLA+ tools distribution that contains TLC, downloaded from the TLA+ project's GitHub releases. Its README explains how to run TLC on each specification.

## Demos

Each Python module has a demonstration that prints something worth looking at. Run it from inside the folder:

| Folder | Demo |
|---|---|
| `gossip-membership/` | `python3 gossip.py` and `python3 detector.py` |
| `logical-clocks/` | `python3 clocks.py` |
| `quorum-store/` | `python3 quorum.py` |
| `consistent-hashing/` | `python3 hashring.py` |
| `crdts/` | `python3 crdts.py` |
| Other folders | See the folder's README |

## A note on production use

These examples teach mechanisms, not products. They leave out what real systems spend most of their code on: persistence and fsync, real networking, security, configuration changes, upgrades, observability and years of hardening against failures nobody predicted. Use them to understand and to experiment, and use them as test oracles or starting points, not as components to deploy.
