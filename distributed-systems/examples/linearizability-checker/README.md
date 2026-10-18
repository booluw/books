# Linearizability checker (Chapters 8 and 23)

## The problem

A database's documentation says it is "strongly consistent". How would you know? You cannot see inside it while it runs. What you *can* see, from the outside, is a **history**: which client asked for what, when the request left, when the answer came back, and what the answer was. This example takes such a history for a single register (one key in a key-value store) and decides whether it is **linearizable**. If it is, the checker returns a witness order; if not, it returns how far it got before every possibility ran out.

It then generates histories from a simulated replicated register with a common bug, reads served by followers that have not caught up, and shows the checker catching it. This is, in miniature, how Jepsen tests databases (Chapter 23).

## Terms

- **Register:** the simplest storage object, one value with `read` and `write`. Here it may also support **compare-and-set (CAS)**: "if the value is `expected`, set it to `new` and say yes; otherwise change nothing and say no".
- **Invocation and response:** an operation starts when the client sends the request (*invocation*, `call`) and ends when the client receives the reply (*response*, `ret`). The operation took effect inside the system at some unknown instant in between.
- **Pending operation:** one that never got a response (the client crashed or timed out). It may or may not have taken effect.
- **History:** the list of operations with their call and return times and results. It is **well formed** when each client waits for one operation to return before invoking the next.
- **Sequential specification:** how the object behaves when operations happen one at a time. For a register, a read returns the most recent write.
- **Linearizability** (Herlihy and Wing, 1990): there is a single total order of all the operations that (1) is legal for the sequential specification and (2) respects real time: if A returned before B was invoked, A comes first. Informally, every operation appears to happen at one instant (its **linearization point**) between its call and return. Linearizability is what people usually mean by "strong consistency" for a single object.
- **Sequential consistency** (Lamport, 1979): there is a legal total order that respects each client's own **program order**, but not real time across clients. Weaker: a read may return an old value, as long as everyone agrees on one order.
- **Witness:** a legal order that proves a history is linearizable.

## How it works

`checker.check_linearizable(history)` is the **Wing & Gong** search (1993), with the memoisation from **Lowe** (2017) used by Knossos and **Porcupine**:

1. Sort the operations by invocation time.
2. Pick an operation that may go next: one invoked no later than the earliest return time among the operations not yet placed. (If some other operation returned before this one was even invoked, that one must come first.)
3. Apply it to the register's sequential specification (`history.step`). If the recorded result is impossible from the current value, try a different operation.
4. Recurse. If every completed operation has been placed, the order so far is a witness. Pending operations are placed only if a read needs them to have happened.
5. If no choice works, backtrack.

Plain backtracking is exponential: eight overlapping writes can be ordered in 40,320 ways. Lowe's observation is that what happens next depends only on **which** operations are placed and the **current value**, not on the order in which they were placed. So the checker remembers every `(set of placed operations, value)` pair it has explored and never explores one twice. The set is kept as a bitmask, so the pair is hashable.

`check_sequentially_consistent(history)` runs the same search with a different rule in step 2: an operation may go next if it is the earliest unplaced operation *of its own client*. Real time is ignored.

Linearizability checking is NP-complete in general (Gibbons and Korach, 1997). In practice, histories from real tests have limited concurrency (a handful of clients), and memoisation keeps them fast.

## Textbook histories (`histories.py`)

All start from a register holding 0.

| History | Linearizable | Sequentially consistent | What it shows |
|---|---|---|---|
| `read-after-write` | yes | yes | the easy case |
| `stale-read`: W(1) returns, then a read returns 0 | **no** | yes | a lagging follower |
| `concurrent-read-either-value` | yes | yes | reads overlapping a write may see either value |
| `new-old-inversion`: W(1) in progress; B reads 1, then C reads 0 | **no** | yes | reads must never go backwards |
| `read-from-the-future`: a read returns 1 before the write of 1 starts | **no** | yes | SC reorders across clients |
| `own-write-lost`: a client cannot read its own write | no | no | breaks program order |
| `writes-seen-in-different-orders` | no | no | no single order exists |
| `two-cas-both-succeed`: two CAS(0→x) both succeed | no | no | CAS is the basis of locks and leader election |
| `two-cas-one-fails` | yes | yes | one wins, the other fails |
| `pending-write-may-be-ignored` | yes | yes | a crashed write may never have happened |
| `pending-write-must-have-happened` | **no** | yes | once someone saw it, it happened |

The new-old inversion is the one to study. Each read alone is fine: the write is in progress, so 0 and 1 are both acceptable answers. Together they are not, because C started after B finished and saw an older value. The checker's longest legal prefix is `A:W(1), B:R()->1`; C's read of 0 cannot follow it.

```
A:W(1)    |--------------------------------------|
B:R()->1      |---|
C:R()->0              |---|
```

## Catching a real bug (`simulate.py`)

A leader and two followers hold the register. Writes and CAS go to the leader, which applies them at once and replicates each to the followers after a random lag (1 to 10 time units). Three clients each run 8 random operations (40% writes, 10% CAS, 50% reads) with network delays of 1 to 5 units each way.

- **Leader reads (correct):** every operation takes effect at one instant inside its interval on one copy, so every history is linearizable by construction. Result: **0 of 200** seeds flagged.
- **Follower reads (buggy):** a read goes to a random replica. Result: **119 of 200** seeds not linearizable (the first are seeds 2, 6, 8 and 9). **50** of those are not even sequentially consistent: a client that reads from the leader and then from a lagging follower sees time go backwards.

The 24-operation failure for seed 2 is hard to read, so `shrink()` removes operations one at a time while the history stays non-linearizable (the *shrinking* step of property-based testing). It reduces to 4 operations, a new-old inversion:

```
C1:W(4)   |-------------|
C1:W(5)                        |---------------|
C0:R()->5                        |----------|          <- served by the leader
C2:R()->4                                     |----------|   <- served by a lagging follower
```

Memoisation matters. For eight concurrent writes followed by reads that no order can explain, the search visits **3,594** nodes with memoisation and **114,641** without; for ten writes, **23,052** against **10,226,981** (about 37 seconds). A 320-operation history from eight clients checks in about 0.1 seconds, visiting 1,198 nodes.

## Run it

```bash
python3 histories.py        # every textbook history, drawn as a timeline with verdicts
python3 simulate.py         # 200 seeds each way, plus one shrunk counterexample
python3 simulate.py 1000    # more seeds
python3 -m unittest -v      # 15 tests
```

The tests compare the checker against a brute-force permutation search on 400 random seeded histories, confirm that every linearizable random history is also sequentially consistent, and pin the simulation's numbers above.

## Experiments to try

1. **Make the lag small.** In `SimConfig`, set `replication_lag=(1.0, 5.0)`. Follower reads now fail on only about 9 of 200 seeds. A bug that shows up 5% of the time in testing is a bug that shows up every day in production. Run `python3 simulate.py 2000` to see it reliably.
2. **Make the lag large.** Set `replication_lag=(1.0, 30.0)` and nearly every seed fails.
3. **Read your own writes.** Make a client read from the leader if it has written in the last 30 time units, and from a random replica otherwise. Histories still fail. Session guarantees (Chapter 8) are weaker than linearizability: other clients' writes are still missed.
4. **Turn memoisation off.** `check_linearizable(history, memo=False)` on a 320-operation simulated history still finishes (little concurrency), but on the ten-concurrent-writes history it takes tens of seconds. Concurrency, not length, is what makes checking hard.
5. **Add a pending operation.** Take `stale-read` and change the write's `ret` to `PENDING`. It becomes linearizable: the write may never have happened.
6. **Add a queue.** Write a `step` function for a FIFO queue (`enqueue`, `dequeue`), with the state as a tuple. The search code does not change: only the sequential specification does.
7. **Check many keys.** Split a multi-key history by key and check each separately. This is Porcupine's *P-compositionality*: linearizability is *local* (Herlihy and Wing), so a history is linearizable exactly when each key's sub-history is.

## Limitations

- One register only (with read, write and CAS). Other objects need their own `step` function.
- Recursive search: very long histories with high concurrency can be slow, as the problem is NP-complete. Porcupine adds further tricks (partitioning, a cache of linearized prefixes).
- The checker trusts the timestamps. In a real test, record invocation *before* sending and response *after* receiving, on one clock; never mix clocks from different machines.
- A pending operation is assumed to have taken effect at most once. Systems that retry automatically can apply it twice, and the checker would need to know that.
- Linearizability is a safety property of single objects. It says nothing about transactions across objects (that is *strict serializability*, Chapter 9) or about availability.

## Chapter

Chapter 8 (Consistency models) introduces linearizability and sequential consistency with these histories. Chapter 23 (Testing distributed systems) uses the simulation and shrinking to show how Jepsen-style testing finds stale reads.

## References

- M. Herlihy and J. Wing, "Linearizability: A Correctness Condition for Concurrent Objects", *ACM TOPLAS* 12(3), 1990.
- L. Lamport, "How to Make a Multiprocessor Computer That Correctly Executes Multiprocess Programs", *IEEE Transactions on Computers* C-28(9), 1979.
- J. Wing and C. Gong, "Testing and Verifying Concurrent Objects", *Journal of Parallel and Distributed Computing* 17(1–2), 1993.
- G. Lowe, "Testing for Linearizability", *Concurrency and Computation: Practice and Experience* 29(4), 2017.
- P. Gibbons and E. Korach, "Testing Shared Memories", *SIAM Journal on Computing* 26(4), 1997.
- A. Athalye, Porcupine, a fast linearizability checker in Go, github.com/anishathalye/porcupine (checked October 2026).
- K. Kingsbury, Jepsen and Knossos, jepsen.io (checked October 2026).
