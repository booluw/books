# Chapter 10. CRDTs and Convergent Data

> "If you can't coordinate, make the data agree with itself."

## What you will learn

- What conflict-free replicated data types (CRDTs) are, and the problem they solve.
- The mathematics that makes them work: join-semilattices, with proofs of convergence.
- State-based and operation-based CRDTs, and the delivery guarantees each needs.
- A catalogue of practical CRDTs: counters, registers, sets, maps and sequences.
- How collaborative editors use sequence CRDTs (and operational transformation).
- Garbage collection, metadata overhead and the limits of CRDTs, including the CALM theorem.
- Where CRDTs are used in production.

---

## 10.1 The problem

Chapter 6 showed that multi-leader and leaderless replication accept concurrent writes to the same data, and that resolving the resulting conflicts with last-write-wins silently loses data. Chapter 8 showed that causal consistency (the strongest model available under partitions) still allows concurrent updates to be seen in different orders.

Suppose instead the data types themselves were designed so that **concurrent updates always merge to the same result, regardless of order, without coordination**. Then replicas could accept writes independently, exchange updates whenever they can, and are guaranteed to converge. That's what a **conflict-free replicated data type (CRDT)** provides. The formal framework was published by Marc Shapiro, Nuno Preguiça, Carlos Baquero and Marek Zawirski in 2011, building on earlier work on commutative replicated data types and collaborative editing.

The guarantee is **strong eventual consistency** (Chapter 8 §8.7):

- **Eventual delivery:** every update delivered to one correct replica is eventually delivered to all.
- **Convergence (safety):** any two replicas that have received the same set of updates are in the same state.

## 10.2 A first example: counting

Three replicas each track the number of "likes" on a post. The naive approach replicates an integer: each replica increments its copy and sends the new value; receivers take... what? The maximum loses increments that happened concurrently on different replicas. The sum double-counts when the same state is sent twice.

The **G-Counter** (grow-only counter) fixes this. Each replica i keeps a vector P, where P[j] is the number of increments **originating at replica j** that i knows about.

```python
def increment(P, i):  P[i] += 1
def value(P):         return sum(P)
def merge(P, Q):      return [max(p, q) for p, q in zip(P, Q)]
```

Each replica only ever increments its own entry, so the max of each entry across replicas is exactly the total number of increments from that origin. Merging in any order, any number of times, gives the same result.

A **PN-Counter** supports decrements by keeping two G-Counters, one for increments and one for decrements, and reporting their difference.

## 10.3 ◆ Formal: why CRDTs converge

### Join-semilattices

A **partial order** ≤ on a set S is a relation that is reflexive, antisymmetric and transitive. A **join-semilattice** is a partially ordered set in which every pair of elements x, y has a **least upper bound**, called their **join** and written x ⊔ y: the smallest element that is ≥ both.

The join operation has three algebraic properties, which follow directly from the definition:

- **Commutative:** x ⊔ y = y ⊔ x.
- **Associative:** (x ⊔ y) ⊔ z = x ⊔ (y ⊔ z).
- **Idempotent:** x ⊔ x = x.

Examples: integers with max; sets with union; vectors of integers with element-wise max (the G-Counter's merge).

### State-based CRDTs (CvRDTs)

A **state-based CRDT** (also called a **convergent** replicated data type, CvRDT) is defined by:

1. a set of states S that forms a join-semilattice;
2. a **merge** function equal to the join ⊔;
3. **update** operations that are **inflationary**: for every update u and state s, s ≤ u(s). (Updates only move "up" the lattice.)

Replicas apply updates locally and periodically send their entire state to others, which merge it.

**Theorem (convergence).** If every update eventually reaches every replica (directly or via merged states), then all replicas converge to the same state: the join of all updated states.

*Proof sketch.* Consider the set of all states produced by local updates anywhere. Each replica's state is always the join of some subset of these states (true initially; preserved by local updates because they're inflationary and a replica's own previous state is included; preserved by merges because the join of two joins is the join of the union of their subsets, by associativity and commutativity). Idempotence means receiving the same state twice changes nothing. Once every replica has (transitively) received every update, each replica's state is the join of the same set, which is unique. ∎

The beauty of state-based CRDTs is how little they need from the network: messages can be lost (state is resent later), duplicated (idempotence), and reordered (commutativity and associativity). Gossip (Chapter 2) is enough.

[`examples/crdts/`](../examples/crdts/) implements G-Counter, PN-Counter, LWW-Register and OR-Set, and checks the semilattice laws and convergence with randomised tests: many replicas, random operations, random merge orders with duplicates. Across 1,000 random runs, all four CRDTs converged every time. The two naive counters show why CRDTs are needed: a counter that merges by taking the maximum always converges but loses, on average, half the increments; a counter that merges by adding converges in none of the runs, because duplicate deliveries are counted again.

### Operation-based CRDTs (CmRDTs)

An **operation-based CRDT** (also called a **commutative** replicated data type, CmRDT) sends operations rather than states. Requirements:

- operations that are concurrent must **commute** (applying them in either order gives the same state);
- the network must deliver every operation **exactly once** to every replica, in **causal order** (an operation is delivered only after the operations it depends on).

Op-based CRDTs send smaller messages, but they depend on a reliable causal broadcast layer, which is itself non-trivial. **Delta-state CRDTs** (Almeida, Shoker and Baquero, 2018) combine the advantages: they send small "deltas" that are themselves lattice states, so they tolerate loss and duplication like state-based CRDTs while keeping messages small.

## 10.4 A catalogue

### Registers

- **LWW-Register:** each write carries a timestamp (an HLC or a Lamport clock plus replica ID, for a total order); merge keeps the highest. Converges, but discards concurrent writes; use only when that's acceptable.
- **MV-Register** (multi-value): keeps all concurrent values (each tagged with a version vector); a read may return several, and the application or user resolves them. This is what Dynamo's "siblings" are.

### Sets

Sets are where CRDT design gets interesting, because "add" and "remove" don't commute: add(x) then remove(x) leaves x absent; the reverse order leaves it present.

| Set CRDT | Semantics | Mechanism | Limitation |
|---|---|---|---|
| **G-Set** | Add only | Union | No removal |
| **2P-Set** (two-phase) | Add, then remove forever | A G-Set of adds and a G-Set of removed "tombstones" | An element can't be re-added after removal |
| **LWW-Element-Set** | Latest add or remove wins | Timestamps per element | Clock-dependent; concurrent add/remove resolved arbitrarily |
| **OR-Set** (observed-remove; add-wins) | A remove only removes the adds it has *observed* | Each add creates a unique tag; remove deletes the tags it has seen | Metadata for tags |

The **OR-Set** gives intuitive semantics: if Alice adds an item to a shared shopping list while Bob, who hasn't seen her addition, removes an older copy of the same item, Alice's addition survives (add wins), because Bob's remove only covered the tag he'd observed.

```
add(e):     tag = unique id (replica, counter); S.adds += {(e, tag)}
remove(e):  S.removes += {(e, t) for (e, t) in S.adds}   # tags observed now
lookup(e):  any (e, t) in S.adds not in S.removes
merge:      adds ∪ adds',  removes ∪ removes'
```

Efficient implementations (the **optimised OR-Set**, or "ORSWOT", OR-Set without tombstones) use version vectors to avoid keeping removed tags forever.

### Maps and JSON

A **map CRDT** maps keys to nested CRDTs (a counter, a register, another map) and merges recursively. Kleppmann and Beresford (2017) defined a CRDT for JSON documents, the basis of the **Automerge** library.

### Sequences and collaborative text

Collaborative text editing needs a **sequence CRDT**: concurrent inserts and deletes at positions in a list must converge, and should preserve users' intentions (text typed together should stay together). Approaches:

- Give each character a unique, immutable **identifier** with a dense order, so inserting between two characters means generating an identifier between theirs: **Logoot**, **LSEQ** and **Treedoc**.
- Have each insertion reference the character it was inserted after, with ties between concurrent inserts broken deterministically: **RGA** (Replicated Growable Array), and the algorithm family used in **Yjs** (YATA) and Automerge.
- Deletes usually leave **tombstones** (hidden markers), so later operations that refer to deleted characters can still find their place.

Research has also addressed **interleaving**: some algorithms, when two users type words at the same position concurrently, interleave their characters ("HWeolrllod"). Kleppmann and colleagues' work on Fugue (Weidner and Kleppmann, 2023) gives algorithms with "maximal non-interleaving".

### Operational transformation

Before CRDTs, collaborative editors used **operational transformation (OT)** (Ellis and Gibbs, 1989): when an operation arrives that was generated concurrently with local operations, transform its position to account for them. Google Docs uses OT with a central server that orders operations. OT is easier with a central server; peer-to-peer OT is notoriously hard to get right (several published algorithms were later found incorrect). CRDTs need no central ordering, which suits offline-first and peer-to-peer applications.

## 10.5 Costs and limits

### Metadata

CRDTs trade coordination for metadata: version vectors, unique tags, tombstones. Sequence CRDTs may store per-character identifiers many times larger than the characters. Modern libraries (Yjs, Automerge 2.x) compress this heavily, but metadata growth is still the main engineering challenge.

### Garbage collection

Tombstones can be removed only when every replica has seen the deletion; otherwise a replica that hasn't seen it might re-introduce the element on merge. Knowing that every replica has seen something requires knowing the set of replicas and tracking their progress, which is a form of coordination. Practical systems collect garbage when replicas are known (servers) or accept bounded growth.

### Invariants CRDTs can't keep

CRDTs guarantee convergence, not application invariants. Two replicas each decrementing stock from 1 to 0 converge to −1. Two users each booking the last seat converge to two bookings. The **CALM theorem** (Chapter 4 §4.7) explains why: checking "stock ≥ 0" before decrementing is a non-monotonic decision (it depends on the absence of other decrements), so it needs coordination. Options:

- **Escrow or bounded counters:** divide the stock into per-replica allowances in advance; each replica can decrement its own allowance without coordination and must coordinate to borrow more (Balegas and colleagues, 2015).
- **Coordinate only for invariant-threatening operations:** let most operations run coordination-free and route the dangerous ones through consensus. Research on **invariant confluence** (Bailis and colleagues, 2014) gives a test for which operations need coordination.
- **Compensate:** accept the oversell and fix it in the business process (apologise, offer a voucher), as Helland and Campbell's "Building on Quicksand" (2009) argues many businesses already do.

## 10.6 CRDTs in production

| System or library | Use *(as of October 2026)* |
|---|---|
| **Riak** | Counters, sets, maps and flags as server-side data types |
| **Redis Enterprise** (Active-Active) | CRDT-based multi-region replication of Redis data types |
| **Azure Cosmos DB** | Multi-region writes with conflict resolution policies including LWW and custom merge |
| **Automerge** and **Yjs** | Libraries for collaborative and local-first applications; Yjs is widely used in collaborative editors |
| **Figma** | Its multiplayer system was inspired by CRDTs, though it uses a central server to simplify ordering |
| **Apple Notes** | Reported to use CRDTs for syncing notes |
| **SoundCloud's Roshi**, **League of Legends chat** and others | Earlier production uses of LWW-element sets and other CRDTs |

The **local-first software** movement (Kleppmann, Wiggins, van Hardenberg and McGranaghan, 2019) argues for applications that keep the primary copy of data on the user's device and sync via CRDTs, giving offline use, low latency and user ownership of data.

---

## Summary

- CRDTs are data types whose concurrent updates merge deterministically without coordination, giving strong eventual consistency.
- State-based CRDTs merge with the join of a semilattice (commutative, associative, idempotent) and use inflationary updates; they converge under any delivery order, loss or duplication, with a short proof. Op-based CRDTs need commuting operations and exactly-once causal delivery; delta-state CRDTs combine the benefits.
- Practical CRDTs include G- and PN-Counters, LWW- and MV-Registers, 2P-, LWW- and OR-Sets, maps, JSON documents and sequence CRDTs for collaborative text.
- Operational transformation is the older alternative, simplest with a central server.
- The costs are metadata and garbage collection. CRDTs can't enforce non-monotonic invariants such as "stock never negative" (CALM); use escrow, targeted coordination or compensation.

## Exercises

See [`exercises/10-crdts.md`](../exercises/10-crdts.md).

## Further reading

- Marc Shapiro, Nuno Preguiça, Carlos Baquero and Marek Zawirski, "Conflict-Free Replicated Data Types", SSS (2011), and the companion INRIA technical report "A Comprehensive Study of Convergent and Commutative Replicated Data Types" (2011).
- Paulo Sérgio Almeida, Ali Shoker and Carlos Baquero, "Delta State Replicated Data Types", *Journal of Parallel and Distributed Computing* (2018).
- Martin Kleppmann and Alastair R. Beresford, "A Conflict-Free Replicated JSON Datatype", *IEEE TPDS* (2017).
- Martin Kleppmann, Adam Wiggins, Peter van Hardenberg and Mark McGranaghan, "Local-First Software: You Own Your Data, in Spite of the Cloud", Onward! (2019).
- Matthew Weidner and Martin Kleppmann, "The Art of the Fugue: Minimizing Interleaving in Collaborative Text Editing" (arXiv, 2023).
- Peter Bailis et al., "Coordination Avoidance in Database Systems", VLDB (2015).
- Pat Helland and Dave Campbell, "Building on Quicksand", CIDR (2009).
- crdt.tech, a community index of CRDT papers and implementations.
