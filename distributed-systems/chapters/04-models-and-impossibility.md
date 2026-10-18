# Chapter 4. System Models and Impossibility Results

> "Impossibility results tell you where not to look."

## What you will learn

- What a system model is, and why every protocol's guarantees are only as good as its model.
- The Two Generals problem, and why no protocol can guarantee agreement over a lossy channel.
- The consensus problem, stated precisely.
- The FLP impossibility result: what it says, a proof sketch, and how real systems get around it.
- The CAP theorem: what it actually says, a proof, and the common misreadings.
- PACELC: the trade-off that matters when there is no partition.
- How to use these results as a design tool rather than as slogans.

---

## 4.1 Why models matter

A **system model** is a precise statement of what we assume about the environment a protocol runs in. It has three parts:

1. **Timing:** synchronous, partially synchronous or asynchronous (Chapter 2 §2.2).
2. **Process failures:** crash-stop, crash-recovery or Byzantine, and how many processes may fail.
3. **Communication:** reliable or lossy links; whether messages can be duplicated, reordered or forged.

Every correctness claim is relative to a model. "Raft is safe" means "Raft never violates its safety properties in an asynchronous system with crash-recovery processes and lossy, reordering, duplicating links, provided processes keep their persistent state". If a disk silently loses a supposedly persisted vote, the model is violated and the guarantee is void. Many production bugs are exactly this: the system's real behaviour stepped outside the model its protocol was proved in.

Impossibility results go the other way: they say that *in a given model*, no protocol whatsoever can achieve some goal. They're valuable because they stop you looking for a solution that doesn't exist, and they tell you which assumption you must strengthen (or which guarantee you must weaken) to make progress.

## 4.2 The Two Generals problem

Two armies, led by generals A and B, camp on hills either side of a valley held by an enemy. They win only if they attack at the same time; if only one attacks, it's destroyed. They communicate by messengers who must cross the valley and may be captured. Can they agree on an attack time?

A sends "attack at dawn". If the messenger is captured, B never knows, so A can't attack unless it hears back. B replies "agreed". But B can't be sure the reply arrived, so B won't attack unless A confirms. And so on forever.

### ◆ Formal: no finite protocol works

**Claim.** No deterministic protocol over a channel that can lose any message guarantees that both generals attack, or neither does, in every execution, while ensuring they attack when no messages are lost.

*Proof sketch.* Suppose a protocol exists. Consider an execution where all messages are delivered and both attack; it uses some finite number of messages. Take a **shortest** such execution, with k messages. Now consider the same execution but with the last message lost. The sender of the last message can't tell the difference (it receives nothing either way), so it still attacks. The receiver's decision must not depend on the last message, because otherwise in this execution it would decide differently from the sender and the protocol would fail. So the receiver also attacks without it. Then the protocol works with k − 1 messages, contradicting minimality. (For k = 0, neither general has heard anything, so they can't both have learned to attack in a coordinated way.) ∎

The practical lesson: **no amount of acknowledgements makes a lossy channel certain.** Real systems accept probabilistic or eventual agreement, use retries and idempotency until a message gets through, or make one side's action conditional on durable state that can be queried later. When your bank shows "pending", it is living with the Two Generals problem.

## 4.3 Consensus, precisely

Many problems in this book reduce to **consensus**: getting a set of processes to agree on a single value. Electing a leader, committing a transaction, deciding the next entry in a replicated log and acquiring a lock are all consensus in disguise.

Each process proposes a value; each must eventually **decide** on a value. A protocol solves consensus if:

- **Agreement:** no two correct processes decide different values. (Safety.)
- **Validity:** a decided value was proposed by some process. (Safety; rules out trivial protocols that always decide 0.)
- **Integrity:** each process decides at most once. (Safety.)
- **Termination:** every correct process eventually decides. (Liveness.)

## 4.4 The FLP impossibility result

In 1985, Michael Fischer, Nancy Lynch and Michael Paterson proved what became known as **FLP**:

> In an asynchronous system in which even **one** process may crash, no deterministic protocol solves consensus.

This is surprising. One crash. No Byzantine behaviour, no message loss (FLP even assumes reliable links). Just the possibility that one process stops, combined with no bound on message delays.

### ◆ Formal: proof sketch

The proof uses three ideas. Call a global state (the states of all processes plus the messages in transit) a **configuration**.

1. **Valence.** A configuration is **0-valent** if every possible continuation decides 0, **1-valent** if every continuation decides 1, and **bivalent** if both outcomes are still possible.

2. **A bivalent initial configuration exists.** Line up initial configurations that differ in one process's input at a time, from all-0 to all-1. The all-0 configuration is 0-valent and the all-1 is 1-valent (by validity), so somewhere two *adjacent* configurations C₀ (0-valent) and C₁ (1-valent) differ only in the input of one process p. Now consider a run where p crashes at the start. A protocol tolerating one crash must still decide, and the other processes can't tell C₀ from C₁ in that run, so they decide the same value from both. That contradicts one being 0-valent and the other 1-valent, unless one of them is actually bivalent.

3. **From any bivalent configuration, the adversary can stay bivalent.** Take a bivalent configuration C and any pending step e (process p receiving some message m). Consider all configurations reachable from C without applying e, and then applying e. The proof shows that at least one of these resulting configurations is bivalent. If not, there would be two "neighbouring" configurations, one leading to 0 after e and the other to 1, which differ by a single step of some process. A case analysis on whether that step is taken by p or by another process shows that, if p were to crash (or simply be very slow), the remaining processes couldn't distinguish the cases, contradicting the different valences.

Applying step 3 repeatedly, while making sure every pending message is eventually delivered (so the execution is "fair" and no process is actually crashed), the adversary constructs an **infinite execution that stays bivalent forever**: no process ever decides. Termination fails. ∎

### What FLP does *not* say

- It doesn't say consensus is impossible in practice. It says no protocol can *guarantee* termination in *every* asynchronous execution.
- It doesn't affect safety. Paxos and Raft never violate agreement; FLP only shows that an adversarial schedule can keep them from deciding.
- It doesn't apply if you strengthen the model.

### How real systems get around FLP

| Strengthen the model with… | Example |
|---|---|
| **Partial synchrony:** assume delays are *eventually* bounded | Paxos, Raft: safe always, live once the network behaves (Dwork, Lynch and Stockmeyer, 1988) |
| **Failure detectors** that are eventually accurate | Chandra–Toueg consensus with ◇S (Chapter 2 §2.5) |
| **Randomisation:** decide with probability 1, not deterministically | Ben-Or's protocol (1983); randomised election timeouts in Raft help in practice |
| **Synchrony** (real bounds) | Some embedded and avionics systems |

Raft's randomised election timeouts are a good illustration: in theory, an adversary that controls message timing could keep splitting the vote forever; in practice, randomisation makes repeated split votes vanishingly unlikely.

## 4.5 The CAP theorem

In 2000, Eric Brewer conjectured that a distributed data store can't simultaneously guarantee consistency, availability and partition tolerance. Seth Gilbert and Nancy Lynch proved a formal version in 2002.

### The precise statement

In Gilbert and Lynch's formalisation:

- **Consistency (C)** means **linearizability** for a read/write register: every operation appears to take effect atomically at some instant between its invocation and its response, so every read returns the most recent write (Chapter 8).
- **Availability (A)** means every request received by a **non-failed** node eventually gets a (non-error) response.
- **Partition tolerance (P)** means the system continues to meet its guarantees even when the network loses arbitrarily many messages between nodes.

**Theorem.** In an asynchronous network where messages can be lost, no read/write register implementation provides both linearizability and availability.

### ◆ Formal: proof

Suppose such an implementation exists, with at least two nodes. Partition the nodes into two non-empty groups G₁ and G₂ and drop all messages between them.

1. A client writes v₁ (different from the initial value v₀) to a node in G₁. By availability, the write completes.
2. Afterwards, a client reads from a node in G₂. By availability, the read returns.
3. No message crossed the partition, so the node in G₂ has no information about the write. Its response is the same as in an execution where the write never happened, so it returns v₀.
4. But the write completed before the read began, so linearizability requires the read to return v₁. Contradiction. ∎

### What CAP actually means

Partitions aren't optional (Chapter 2 §2.4), so "choosing CA" isn't a real option for a system that spans a network. The real statement is: **during a partition, each operation must choose between consistency and availability.**

- A **CP** choice: nodes that can't reach a quorum refuse requests (return errors or wait). Consensus-based systems such as etcd, ZooKeeper and Spanner behave this way.
- An **AP** choice: nodes keep serving from local state, accepting that reads may be stale and writes may conflict, to be reconciled later. Dynamo-style stores and DNS behave this way.

### Common misreadings

| Misreading | Correction |
|---|---|
| "Pick two of three" | Partition tolerance isn't a choice for networked systems; the choice is C or A *during a partition* |
| "This database is CP" (for everything) | The choice can differ per operation; many databases let you choose per query (e.g. consistency levels in Cassandra) |
| "AP systems are always inconsistent" | They're consistent when there's no partition; they're eventually consistent after one |
| "CAP consistency" = "ACID consistency" | Different things: CAP's C is linearizability; ACID's C is preserving application invariants (Chapter 9) |
| "CAP explains why my database is slow" | Usually not: latency in normal operation is PACELC's E-branch (§4.6) |

Brewer himself wrote a retrospective in 2012, "CAP Twelve Years Later: How the 'Rules' Have Changed", arguing for treating partitions as a mode to detect, operate in and recover from, rather than as a binary choice made at design time. Martin Kleppmann's "A Critique of the CAP Theorem" (2015) argues that the theorem is too narrow to guide most design decisions, and suggests reasoning about latency and consistency models directly.

## 4.6 PACELC

Daniel Abadi (2010, formalised in 2012) observed that CAP only describes behaviour during partitions, which are rare. The trade-off that shapes everyday performance is different:

> **If** there is a **P**artition, choose between **A**vailability and **C**onsistency; **E**lse, choose between **L**atency and **C**onsistency.

Even with a perfect network, a strongly consistent write must reach (and be acknowledged by) other replicas before it's acknowledged to the client. If the replicas are in another region, that costs at least one cross-region round trip (Chapter 1 §1.6). A system can avoid that latency only by acknowledging before replication, accepting weaker consistency.

| System *(typical configuration)* | Partition: A or C | Else: L or C |
|---|---|---|
| Dynamo-style stores (Cassandra, Riak) with low consistency levels | A | L |
| Spanner, CockroachDB, etcd | C | C |
| MongoDB (default majority writes in recent versions) | C (for majority operations) | C |
| A single-leader database with asynchronous replicas, reading from replicas | A (for replica reads) | L |

The table is a simplification; most of these systems are configurable per operation. That's the point: **consistency is a per-operation dial**, and PACELC tells you what turning it costs.

## 4.7 Other limits worth knowing

- **Byzantine agreement needs n ≥ 3f + 1** processes to tolerate f Byzantine processes (Lamport, Shostak and Pease, 1982); Chapter 13 explains why.
- **Crash-tolerant consensus needs n ≥ 2f + 1** in partial synchrony: with only 2f processes, a partition into two halves of f leaves each half unable to tell whether the other half crashed or is merely cut off (Chapter 11).
- **Coordination avoidance (CALM).** The CALM theorem (Consistency As Logical Monotonicity; Hellerstein, Alvaro and others, 2010–2019) states that a program has a consistent, coordination-free distributed implementation if and only if it is **monotonic**: if its output only grows as it learns more input, never retracting earlier conclusions. Monotonic computations (set union, counters that only increase, "has anyone voted yes?") can run without coordination; non-monotonic ones (checking that something is *absent*, such as "no one has booked this seat") need coordination. CALM explains why CRDTs work (Chapter 10) and where they can't help.
- **Lower bounds on latency.** Consensus needs at least two message delays to decide in the common case for a broad class of protocols, and Spanner-style external consistency must wait out clock uncertainty. These bounds are why geo-distributed strong consistency is always slower than local writes.

## 4.8 Using impossibility results in design

1. **Name the model.** For each component, write down the timing and failure assumptions it relies on. Review whether the environment honours them (clock bounds, fsync behaviour, network characteristics).
2. **Decide what gives during a partition.** For each operation: refuse, or serve possibly stale data? Make it a product decision, not an accident.
3. **Decide the normal-case latency budget.** If you need cross-region strong consistency, budget for the round trips, or reduce what needs it.
4. **Prefer safety over liveness.** When in doubt, stop rather than diverge, and make "stopped" visible and recoverable.
5. **Use monotonic designs where you can** (CALM), and confine coordination to the operations that need it.

The [`templates/consistency-requirements.md`](../templates/consistency-requirements.md) worksheet walks through these decisions for each piece of data.

---

## Summary

- A system model fixes assumptions about timing, failures and communication. Every guarantee is relative to a model, and many real bugs come from violating the model.
- Two Generals: no finite protocol guarantees agreement over a lossy channel.
- Consensus requires agreement, validity, integrity (safety) and termination (liveness).
- FLP: in an asynchronous system with one possible crash, no deterministic protocol guarantees consensus terminates. Real systems keep safety unconditionally and get liveness from partial synchrony, failure detectors or randomisation.
- CAP (Gilbert–Lynch): with message loss, no register is both linearizable and available. During a partition, choose consistency or availability per operation. Partition tolerance isn't optional.
- PACELC: without partitions, the everyday trade-off is latency versus consistency.
- Other limits: 2f + 1 for crash consensus, 3f + 1 for Byzantine, CALM for coordination-free computation, and latency lower bounds for geo-replication.

## Exercises

This chapter has no exercises. Its results are exercised in practice in Chapters 5, 6, 8 and 11, where you'll use a model checker to find the counterexamples these proofs predict.

## Further reading

- Michael J. Fischer, Nancy A. Lynch and Michael S. Paterson, "Impossibility of Distributed Consensus with One Faulty Process", *Journal of the ACM* (1985).
- Seth Gilbert and Nancy Lynch, "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services", *ACM SIGACT News* (2002).
- Eric Brewer, "CAP Twelve Years Later: How the 'Rules' Have Changed", *IEEE Computer* (2012).
- Daniel Abadi, "Consistency Tradeoffs in Modern Distributed Database System Design", *IEEE Computer* (2012).
- Cynthia Dwork, Nancy Lynch and Larry Stockmeyer, "Consensus in the Presence of Partial Synchrony", *Journal of the ACM* (1988).
- Joseph M. Hellerstein and Peter Alvaro, "Keeping CALM: When Distributed Consistency Is Easy", *Communications of the ACM* (2020).
- Martin Kleppmann, "A Critique of the CAP Theorem" (arXiv, 2015).
- Nancy Lynch, *Distributed Algorithms* (Morgan Kaufmann, 1996).
