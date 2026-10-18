# Distributed Systems

### How Computers Cooperate, Fail and Agree: Foundations, Formal Reasoning, Building Blocks and Real Systems

*First edition, October 2026*

---

## About this book

Almost every system you use is distributed. A web page is assembled by dozens of services. A bank transfer passes through several data centres. A chat message is copied to servers on three continents before it reaches a friend's phone. A large AI model is trained across tens of thousands of GPUs that must stay in step.

A **distributed system** is a set of computers that communicate over a network and coordinate to appear, to their users, as one system. Building them is hard for three reasons that this book returns to again and again:

1. **Partial failure.** Some parts fail while others keep running, and the parts that are running often can't tell what has failed.
2. **Unreliable communication.** Messages are delayed, lost, duplicated and reordered, and a slow message looks exactly like a lost one.
3. **No shared clock.** Each machine has its own idea of the time, so "what happened first?" is a surprisingly deep question.

This book explains how engineers build reliable systems from unreliable parts. It assumes you can program and have built software that runs on one machine. It does **not** assume you know what a quorum is, why "exactly-once delivery" is a contested phrase, or how Raft keeps a log consistent across five servers while two of them crash. Every term is defined when it first appears, and every technique is introduced by the problem it solves.

### What makes this book different

- **Formal depth, made approachable.** Distributed systems fail in ways that testing alone rarely finds. The book teaches you to reason about correctness with invariants, proof sketches and model checking. It includes TLA+ specifications checked with the TLC model checker, and a small model checker written in Python that you can read in an afternoon.
- **Principles *and* real systems.** Part IVa teaches vendor-neutral building blocks. Part IVb takes the systems you'll actually meet (Kafka, Cassandra, DynamoDB, Spanner, CockroachDB, FoundationDB, ZooKeeper, etcd, Flink, Kubernetes) and maps each back to the principles.
- **Runnable simulations.** Every major idea has a simulation you can run, break and measure: clocks, quorums, gossip, CRDTs, Raft, two-phase commit, sagas, retry storms, an LSM tree, watermarks and deterministic simulation testing.
- **Practical exercises only.** Exercises ask you to build, run, break, measure or debug something. Chapters where that doesn't fit don't have filler questions.

### Who this book is for

- Software engineers moving from single-service applications to systems that span machines, regions or clouds.
- Backend, platform, data and infrastructure engineers who want the foundations behind the tools they use.
- Engineers preparing for system design interviews who want understanding, not memorised diagrams.
- Technical leaders who review designs and need to ask the right questions.

### Companion books

- [*The Integration Design Engineer*](../integration-design-engineer/): connecting systems with APIs and events, at the level of integration patterns.
- [*Forward Deployed Engineering*](../forward-deployed-engineering/): deploying systems inside customer environments.

---

## How to read this book

| If you are… | Read |
|---|---|
| New to distributed systems | Parts I–III in order, then IVa and V; dip into IVb as you meet the systems |
| An experienced backend engineer | Chapters 3, 4, 5, 8, 11 and 12, then Parts IVa and V |
| Interested mainly in correctness | Chapters 4, 5, 8, 11, 12 and 23, with the `model-checker`, `tla`, `raft` and `linearizability-checker` examples |
| Choosing or operating a database or queue | Chapters 6–9, 15, 20 and 21 |
| Preparing for system design interviews | Chapters 1, 6, 7, 14, 17, 18 and Appendix E |

Formal sections are marked **◆ Formal**. You can skip them on a first reading and still follow the rest of the book; return to them when you want to know *why* something is true.

Folders:

- [`chapters/`](chapters/): the main text.
- [`examples/`](examples/): runnable, tested standard-library Python simulations, plus TLA+ specifications.
- [`exercises/`](exercises/): hands-on exercises with solutions, for chapters where hands-on work fits.
- [`templates/`](templates/): design doc, failure-mode analysis, consistency requirements, capacity estimation and postmortem.
- [`diagrams/`](diagrams/): Mermaid diagrams.
- [`appendices/`](appendices/): glossary, bibliography of classic papers, numbers to know, design-review checklists and a system design interview bank.

---

## Table of contents

### Part I: Foundations

1. [What a Distributed System Is, and Why We Build Them](chapters/01-introduction.md)
2. [Networks, Failures and Failure Detection](chapters/02-networks-and-failure.md)
3. [Time, Clocks and the Ordering of Events](chapters/03-time-and-order.md)
4. [System Models and Impossibility Results](chapters/04-models-and-impossibility.md)
5. [Reasoning About Correctness: Invariants, TLA+ and Model Checking](chapters/05-formal-reasoning.md)

### Part II: Data Across Machines

6. [Replication](chapters/06-replication.md)
7. [Partitioning](chapters/07-partitioning.md)
8. [Consistency Models](chapters/08-consistency-models.md)
9. [Transactions Across Machines](chapters/09-distributed-transactions.md)
10. [CRDTs and Convergent Data](chapters/10-crdts.md)

### Part III: Agreement

11. [Consensus: Paxos and Raft](chapters/11-consensus.md)
12. [Coordination: Leases, Locks, Leader Election and Membership](chapters/12-coordination.md)
13. [Byzantine Fault Tolerance](chapters/13-byzantine-fault-tolerance.md)

### Part IVa: Building Blocks

14. [Communication: RPC, Messaging, Logs and Delivery Guarantees](chapters/14-communication.md)
15. [Storage Engines](chapters/15-storage-engines.md)
16. [Batch and Stream Processing](chapters/16-batch-and-stream.md)
17. [Resilience: Timeouts, Retries, Backpressure and Overload](chapters/17-resilience.md)
18. [Caching, Load Balancing and Content Delivery](chapters/18-caching-and-load-balancing.md)
19. [Service Architecture: Microservices, Discovery and Meshes](chapters/19-service-architecture.md)

### Part IVb: Real Systems

20. [Distributed Databases in Practice](chapters/20-databases-in-practice.md)
21. [Coordination, Streaming and Orchestration Systems in Practice](chapters/21-infrastructure-in-practice.md)

### Part V: Operating and Verifying

22. [Observability and Debugging](chapters/22-observability.md)
23. [Testing Distributed Systems](chapters/23-testing.md)
24. [Learning from Outages](chapters/24-outages.md)
25. [Distributed Systems for AI](chapters/25-ai-infrastructure.md)

### Appendices

- A. [Glossary](appendices/A-glossary.md)
- B. [Bibliography and Classic Papers](appendices/B-bibliography.md)
- C. [Numbers Every Engineer Should Know](appendices/C-numbers.md)
- D. [Design Review Checklists](appendices/D-checklists.md)
- E. [System Design Interviews](appendices/E-system-design-interviews.md)

### Supporting material

- [Examples](examples/README.md) · [Exercises](exercises/README.md) · [Templates](templates/README.md) · [Diagrams](diagrams/README.md)

---

## Currency of information

The principles in Parts I–III have been stable for decades. Product details in Parts IVb and V (versions, features, defaults, cloud services) change often, and were checked in **October 2026**. They are marked *(as of October 2026)* where it matters.
