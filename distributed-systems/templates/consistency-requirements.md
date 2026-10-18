# Consistency Requirements: <System name>

*Version: <n> · Date: <YYYY-MM-DD> · Author(s): <names> · Reviewers: <names> · Related design doc: <link>*

## How to use this template

- **Purpose:** decide, for **each piece of data and each operation on it**, what guarantee it needs, what it does during a network partition, what latency it can afford, and how concurrent updates are resolved. A system rarely needs one consistency model for everything: a bank balance, a "like" count, a user's own profile and a leader-election record need different guarantees. Giving each what it needs, and no more, is most of the craft ([Chapter 1 §1.8](../chapters/01-introduction.md)).
- **When:** early in design, before choosing a database; and whenever a new kind of data or a new operation appears.
- **Owner:** the engineer writing the design doc, together with the product owner. The "during a partition" column is a **product decision**: whether users see an error or possibly stale data is not something engineers should decide by accident ([Chapter 4 §4.8](../chapters/04-models-and-impossibility.md)).
- **Sign-off:** the design reviewers and the product owner.

Background reading: [Chapter 4](../chapters/04-models-and-impossibility.md) (CAP, PACELC, CALM), [Chapter 8](../chapters/08-consistency-models.md) (the models), [Chapter 9](../chapters/09-distributed-transactions.md) (isolation levels and anomalies), [Chapter 10](../chapters/10-crdts.md) (convergent data types) and [Chapter 3](../chapters/03-time-and-order.md) (clocks and conflict resolution).

*Fill in one row per (data item, operation). Then check the database's actual guarantees at the settings you'll use; defaults are often weaker than people assume ([Chapter 8 §8.11](../chapters/08-consistency-models.md), [Chapter 20 §20.8](../chapters/20-databases-in-practice.md)).*

---

## 1. Vocabulary for the columns

| Column | Choose from | Reference |
|---|---|---|
| **Model needed** | Strict serializability · serializable · snapshot isolation · linearizable · sequential · causal · session guarantees (read-your-writes, monotonic reads, monotonic writes, writes-follow-reads) · bounded staleness (≤ x s) · eventual · strong eventual (CRDT) | [Ch. 8](../chapters/08-consistency-models.md), [Ch. 9](../chapters/09-distributed-transactions.md) |
| **Invariant protected** | The application rule that breaks if the model is weaker, in plain language | [Ch. 5 §5.3](../chapters/05-formal-reasoning.md) |
| **During a partition** | **Refuse** (error or wait: CP) · **serve stale** reads (AP) · **accept and reconcile** writes (AP, needs conflict resolution) · **degrade** (read-only, cached, default) | [Ch. 4 §4.5](../chapters/04-models-and-impossibility.md) |
| **Latency budget** | p99 target for the operation, and how many cross-zone or cross-region round trips that allows ([Appendix C](../appendices/C-numbers.md)) | [Ch. 1 §1.6](../chapters/01-introduction.md) |
| **PACELC** | Partition: **A** or **C**; Else: **L** (answer locally) or **C** (wait for replicas) | [Ch. 4 §4.6](../chapters/04-models-and-impossibility.md) |
| **Conflict resolution** | None needed (single writer or consensus) · last write wins (accepts silent loss) · keep siblings (application or user merges) · CRDT merge · custom deterministic merge · avoid by routing to a home leader | [Ch. 6 §6.4](../chapters/06-replication.md), [Ch. 10](../chapters/10-crdts.md) |
| **Monotonic (CALM)?** | **Yes**: output only grows as input grows (set union, max, grow-only counter, "has anyone said yes?"); can run coordination-free. **No**: depends on absence or a threshold ("no one has booked this seat", "stock ≥ 0"); needs coordination or escrow | [Ch. 4 §4.7](../chapters/04-models-and-impossibility.md), [Ch. 10 §10.5](../chapters/10-crdts.md) |
| **Mechanism** | How the guarantee will be implemented (consensus write, read index, quorum r + w > n with read repair, leader read, session token, CRDT, idempotency key, fencing token, TTL) | [Ch. 6](../chapters/06-replication.md), [Ch. 11](../chapters/11-consensus.md) |

## 2. Questions to ask for each row

1. **What invariant breaks** if two clients see different values, or one sees an old value? If you can't name one, a weaker model is probably fine.
2. **Who notices staleness?** Users notice their *own* stale data far more than other people's: read-your-writes and monotonic reads often matter more than global freshness ([Chapter 6 §6.3](../chapters/06-replication.md)).
3. **Is the decision monotonic?** If yes, CRDTs or coordination-free designs work. If no, you need consensus, a single owner, escrow or compensation.
4. **What happens during a partition?** Refuse, serve stale, or accept and reconcile? Which side of the partition keeps working?
5. **What does the strong option cost** in round trips and latency normally (PACELC's E branch), not just during partitions?
6. **Are there cross-channel effects?** A user who updates something and then tells a friend through another channel needs causality across channels, or linearizability ([Chapter 8 §8.3](../chapters/08-consistency-models.md)).
7. **Do caches sit in front?** A cache gives bounded staleness at best; don't cache data whose staleness breaks an invariant ([Chapter 18 §18.3](../chapters/18-caching-and-load-balancing.md)).
8. **What isolation level do multi-object operations run at,** and does it allow write skew ([Chapter 9 §9.2](../chapters/09-distributed-transactions.md))?

## 3. Worksheet

| # | Data item | Operation | Invariant protected | Model needed | During a partition | Latency budget (p99) | PACELC | Conflict resolution | Monotonic? | Mechanism |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | | |
| 2 | | | | | | | | | | |
| 3 | | | | | | | | | | |

## 4. What the chosen system actually provides

| Data store / setting | Documented guarantee at our settings | Default if different | Jepsen findings (version, date) | Gap versus worksheet | Action |
|---|---|---|---|---|---|
| | | | | | |

## 5. Decisions and open questions

| # | Decision or question | Owner | Resolution |
|---|---|---|---|
| | | | |

---

## Worked examples

*Fictional. Tailspin Toys runs an online shop and a ticketing site in two regions (Europe and North America), each with three availability zones. One cross-region round trip is about 80 ms; one cross-zone round trip about 1 ms.*

| # | Data item | Operation | Invariant protected | Model needed | During a partition | Latency budget (p99) | PACELC | Conflict resolution | Monotonic? | Mechanism |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Seat inventory (ticketing) | Book seat | A seat is sold at most once | Linearizable per seat (or serializable transaction over seat and order) | **Refuse** on the minority side: "try again" is better than selling a seat twice | 300 ms | P: C; E: C | None: single writer per seat via consensus | **No**: "seat not yet booked" depends on absence | Conditional write (compare-and-set) on a consensus-replicated row in the seat's home region; idempotency key per booking attempt; hold with TTL during checkout |
| 2 | Account balance (gift cards) | Debit | Balance never negative; money conserved | Strict serializability | Refuse | 250 ms | P: C; E: C | None | **No**: threshold check | Serializable transaction in a single region's consensus database; transfers between users via saga with idempotent steps ([Ch. 9 §9.8](../chapters/09-distributed-transactions.md)) |
| 3 | Product stock (shop) | Decrement on order | Don't oversell beyond a small, compensable margin | Escrow per region, linearizable within a region | Each region sells from its own allowance; refuses when allowance is exhausted | 150 ms | P: A (within allowance); E: L | None within a region; rebalancing allowance needs coordination | No, but made locally checkable by escrow | Bounded counter: stock split into per-region allowances; borrowing more needs a cross-region transaction ([Ch. 10 §10.5](../chapters/10-crdts.md)) |
| 4 | Shopping cart | Add / remove item | An item a user added doesn't silently vanish | Strong eventual consistency + read-your-writes | Accept writes on both sides; merge later | 50 ms | P: A; E: L | OR-Set CRDT (add wins) | Add: yes; remove: handled by observed-remove tags | OR-Set per cart replicated multi-leader; session token for read-your-writes |
| 5 | User profile and settings | Update / read own profile | User sees their own change immediately | Read-your-writes + monotonic reads | Serve possibly stale reads to others; route the owner's reads to the leader or a replica that has their last write | 100 ms | P: A (reads); E: L | Single home leader per user; LWW acceptable for display name | Yes (overwrite of own data) | Single-leader per user; client carries last-write log position; replicas below it redirect |
| 6 | Product reviews and replies | Post / read | A reply is never shown without the review it answers | Causal | Serve and accept locally | 100 ms | P: A; E: L | Each post immutable; ordering by causal metadata | Yes (append-only) | Causal metadata (HLC + dependency) on each post; replica shows a post only after its dependency ([Ch. 8 §8.5](../chapters/08-consistency-models.md)) |
| 7 | "Likes" and view counts | Increment / read | None strict; approximately right | Eventual (strong eventual with CRDT) | Accept locally | 20 ms | P: A; E: L | PN-Counter CRDT | Yes | Per-region G-Counters merged by gossip ([Ch. 10 §10.2](../chapters/10-crdts.md)) |
| 8 | Product price | Read at checkout | Customer is charged the price shown, or told it changed | Bounded staleness ≤ 60 s for display; linearizable re-read at payment | Display stale; refuse payment if the authoritative price can't be confirmed | 50 ms display, 200 ms at payment | Display P: A, E: L; payment P: C, E: C | Single writer (pricing service) | Yes for display (versioned) | Cache with 60 s TTL and CDC invalidation for display; versioned price ID carried into checkout and re-validated |
| 9 | Leader record for the order-export job | Acquire / renew leadership | At most one exporter writes to the warehouse at a time | Linearizable | Refuse (no new leader on minority side) | 1 s | P: C; E: C | None | **No** | Lease in a consensus-based coordination service; **fencing token** checked by the warehouse ([Ch. 12 §12.5](../chapters/12-coordination.md)) |
| 10 | Feature-flag values | Read on every request | Flags change within a minute everywhere; a client never flips back to an older value | Bounded staleness ≤ 60 s + monotonic reads | Serve last known value | 1 ms (local) | P: A; E: L | Single writer, versioned | Yes (versioned, newest wins) | Local cache refreshed by watch from the flag store; version number ignored if older than cached |
| 11 | Payment request to card processor | Charge | A customer is charged at most once per order | Effectively-once processing | Retry later with the same key; never "charge again" | 2 s | — (external) | None: deduplicated | Yes (idempotent with key) | Idempotency key stored with the order in the same transaction; at-least-once delivery from outbox ([Ch. 14 §14.6](../chapters/14-communication.md)) |
| 12 | Unique usernames | Register | No two accounts share a username | Linearizable per username | Refuse registration on the minority side | 500 ms | P: C; E: C | None | **No** (checks absence) | Conditional insert on a consensus-replicated table partitioned by username |

### Commentary on the examples

- **Rows 1, 2, 9 and 12 are non-monotonic** (they depend on something being absent or under a threshold), so CALM says they need coordination. All four refuse during a partition: the product owner agreed that an error is better than a double booking, a negative balance, two exporters or duplicate usernames.
- **Row 3 shows a middle path:** escrow turns a global non-monotonic check ("total stock ≥ 0") into many local ones ("my allowance ≥ 0"), so each region stays available until its allowance runs out.
- **Rows 4, 6, 7 and 10 are monotonic or append-only** and stay available everywhere. Row 4 uses an OR-Set rather than last write wins, because LWW would silently drop concurrent additions ([Chapter 3 §3.3](../chapters/03-time-and-order.md)).
- **Row 5 shows that the owner's view is what matters:** global freshness isn't needed, but read-your-writes is, and it's cheap with a session token.
- **Row 8 splits one data item into two operations** with different guarantees: display can be stale; payment can't.
- **Row 11** isn't a consistency model on a replica at all, but the same reasoning applies: exactly-once *delivery* is impossible, so make the *effect* happen once ([Chapter 14 §14.6](../chapters/14-communication.md)).
