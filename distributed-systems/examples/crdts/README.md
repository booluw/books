# CRDTs (Chapter 10)

## The problem

A shopping list app works offline on two phones. A counter of page views runs in three data centres that sometimes lose contact. In both cases, replicas accept updates independently and must later reconcile. Reconciling by hand ("keep the newest copy") loses data; reconciling with a coordinator gives up the independence we wanted.

A **CRDT** is a data type designed so that reconciliation is automatic and always gives the same answer: every replica that has seen the same updates ends in the same state, whatever order the updates arrived in and however many times each arrived. This example implements four classic CRDTs, tests the algebraic laws that make them work, and shows what goes wrong with a counter that ignores those laws.

## Terms

- **CRDT** (conflict-free replicated data type; Shapiro, Preguiça, Baquero and Zawirski, 2011): a replicated data type that converges without coordination.
- **State-based CRDT** (convergent, CvRDT): replicas send each other their whole state and **merge** it. (The alternative, operation-based CRDTs, sends operations and needs reliable causal delivery instead.)
- **Join-semilattice:** a set of states with a merge (the *join*, ⊔) that is
  - **commutative:** a ⊔ b = b ⊔ a (order of arrival does not matter);
  - **associative:** (a ⊔ b) ⊔ c = a ⊔ (b ⊔ c) (grouping does not matter);
  - **idempotent:** a ⊔ a = a (duplicates do not matter).
- **Inflation:** an update that moves a state upwards, so a ⊑ update(a), where a ⊑ b means a ⊔ b = b.
- **Strong eventual consistency:** replicas that have received the same set of updates are in the same state. Semilattice merge plus inflationary updates guarantees it. The proof sketch is short: any delivery order computes the join of the same set of states, and the three laws say the join of a set does not depend on order, grouping or repetition.
- **G-Counter:** grow-only counter. One entry per replica; each replica increments only its own entry; merge takes the element-wise maximum; value is the sum.
- **PN-Counter:** two G-Counters, one for increments (P) and one for decrements (N); value is P − N.
- **LWW-Register:** last-writer-wins register. Each write carries a (timestamp, replica id) stamp; merge keeps the higher stamp.
- **OR-Set** (observed-remove set), **add-wins** variant: each add creates a unique tag; a remove deletes only the tags the remover has seen. An add concurrent with a remove has a tag the remover never saw, so the element survives.
- **Tombstone:** a record that something was removed, kept so that merging an older state does not bring it back.

## How it works

`crdts.py`:

| Name | Updates | Merge |
|---|---|---|
| `GCounter(replica)` | `increment(n)` | element-wise max |
| `PNCounter(replica)` | `increment(n)`, `decrement(n)` | merge P and N separately |
| `LWWRegister(replica)` | `set(value, timestamp)` | higher (timestamp, replica) wins |
| `ORSet(replica)` | `add(e)`, `remove(e)`, `e in s` | union of add-tags and of removed tags |
| `NaiveCounter(replica, mode)` | `increment(n)` | `"max"` or `"sum"`; **not** a CRDT |

Every type has `merge(other)` (returns a new replica and never mutates its inputs), `value`, `state()` (a canonical form for comparison), `copy()` and `fresh(replica)`.

Helpers: `random_run(cls, rng)` produces many related states from random updates and merges among three replicas; `deliver_in_random_order(states, rng, receiver, duplicates)` merges a list of states in shuffled order with duplicates; `converges(states, rng)` checks that five receivers end up identical; `merge_all(states)` joins a list.

The tests check the semilattice laws on states drawn from random runs, rather than on hand-picked examples. Laws checked on random but *related* states (states that share history, as real replicas do) catch bugs that unrelated random states miss.

## Run it

```bash
python3 crdts.py           # demo, about 2 seconds
python3 -m unittest -v     # 12 tests
```

From the demo: two partitioned replicas each count 5 page views (true total 10).

| Counter | After merging | After a duplicate delivery |
|---|---|---|
| Naive, merge = max | 5 | 5 |
| Naive, merge = sum | 10 | 15 |
| G-Counter | 10 | 10 |

Over 1,000 random workloads, all four CRDTs converged in every run (five receivers, random order, duplicates). On the same workloads the naive counter with `max` merge converged every time but lost increments in all 1,000 runs, on average 50% of the count; with `sum` merge it never converged, because duplicates are counted again.

The OR-Set demo: Alice removes "milk" while Bob, offline, re-adds it. After merging, milk is on the list (add wins). If Alice removes it again *after* seeing Bob's add, it is gone. The LWW demo: two writes with the same timestamp; both replicas pick "blue" (replica `y` beats `x`), and "red" disappears without trace.

## Experiments to try

1. **Break a law and watch the tests catch it.** Change `GCounter._join` to add counts instead of taking the maximum: idempotence fails (and so does convergence). Then make `LWWRegister._join` compare timestamps only, `other.stamp[0] > self.stamp[0]`, ignoring the replica id: commutativity fails on ties. Read the failing states the test reports.
2. **Remove-wins instead of add-wins.** Modify `ORSet` so a remove beats a concurrent add (hint: track removes per element with the tags known at removal *and* a flag). Does it still pass the semilattice tests? Which product behaviour would you want for a shopping list, and for a set of users with admin rights?
3. **Measure the tombstone cost.** Run 10,000 random add/remove operations on one `ORSet` and print `len(s.adds)`, `len(s.removes)` and `len(s.value)`. Optimised OR-Sets (Bieniusa and colleagues, 2012) use version vectors to avoid keeping removed tags for ever.
4. **Lose a write to clock skew.** Give replica `x` a clock 10 units behind replica `y`. If `x` writes *after* `y` in real time, which value wins? Compare with Chapter 3's LWW data-loss example.
5. **Build a multi-value register.** Replace LWW with a register that keeps *all* concurrent values (siblings), using version vectors from `logical-clocks/`. Check it against the same law tests.
6. **Count bytes.** A G-Counter keeps one entry per replica that has ever incremented. Simulate 1,000 short-lived replicas and look at the state size. What would you do in production?

## Limitations

- State-based only: merging whole states is simple but sends a lot of data. Delta-state CRDTs send only recent changes; operation-based CRDTs send operations.
- The OR-Set keeps tombstones for ever and the G-Counter keeps entries for departed replicas for ever; real systems need garbage collection, which needs some coordination.
- No sequence or text CRDT (RGA, Logoot, Yjs-style); these are what collaborative editors use.
- Convergence is not the same as *intent*: CRDTs guarantee all replicas agree, not that they agree on what each user wanted. LWW agreeing to discard "red" is still convergence.
