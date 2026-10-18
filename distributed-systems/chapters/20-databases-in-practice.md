# Chapter 20. Distributed Databases in Practice

> "Every database is a set of trade-offs that somebody chose for you. Read the trade-offs before the benchmarks."

## What you will learn

- How widely used distributed databases are built, mapped back to the principles of Parts I–IVa.
- Dynamo-style stores: Amazon DynamoDB, Apache Cassandra and ScyllaDB.
- Globally consistent SQL databases: Google Spanner, CockroachDB, YugabyteDB and TiDB.
- FoundationDB and its approach to correctness.
- Cloud-native designs that disaggregate storage: Amazon Aurora and Aurora DSQL.
- MongoDB's replication and consistency controls.
- A method for evaluating any distributed database.

Product details are *as of October 2026*; versions, defaults and licences change. The principles behind them change much more slowly.

---

## 20.1 How to read this chapter

For each system, the same questions:

1. **Data model and partitioning** (Chapter 7): how is data split, and by what key?
2. **Replication** (Chapter 6): leader-based, leaderless or consensus? Synchronous or asynchronous?
3. **Consistency and transactions** (Chapters 8 and 9): what's guaranteed, at which settings?
4. **Time and ordering** (Chapter 3): how are concurrent writes ordered?
5. **Failure behaviour** (Chapters 2 and 4): what happens during a partition or node loss?
6. **Storage engine** (Chapter 15).

| System | Partitioning | Replication | Strongest default guarantee | Ordering |
|---|---|---|---|---|
| DynamoDB | Hash (+ sort key) | Multi-Paxos per partition (3 AZs) | Strongly consistent reads optional; transactions | Leader per partition |
| Cassandra | Consistent hashing (vnodes) | Leaderless, tunable quorums | Per-query consistency level; LWT via Paxos | LWW timestamps |
| Spanner | Range (splits) | Paxos groups | Strict serializability | TrueTime |
| CockroachDB | Range | Raft per range | Serializable | Hybrid logical clocks |
| FoundationDB | Range | Custom (logs + storage) | Strict serializability | Central sequencer |
| Aurora (PostgreSQL/MySQL) | None (single writer) | Quorum storage (6 copies, 3 AZs) | The engine's isolation | Single writer |
| MongoDB | Hash or range (sharded) | Raft-like replica sets | Configurable (majority, linearizable reads) | Primary per shard |

## 20.2 Amazon DynamoDB

The 2007 **Dynamo** paper (DeCandia and colleagues) described an internal, leaderless, eventually consistent key-value store for Amazon's shopping cart: consistent hashing with virtual nodes, sloppy quorums with hinted handoff, vector clocks for conflict detection (siblings resolved by the application), Merkle-tree anti-entropy and gossip membership. It became the template for Cassandra, Riak and Voldemort.

**DynamoDB** (launched 2012) shares the name but not the design. Its 2022 paper (Elhemali and colleagues, USENIX ATC) describes:

- **Partitioning** by hash of the partition key, with an optional sort key for ordered items within a partition; partitions split by size and by load ("split for heat").
- **Replication** of each partition across three availability zones using **Multi-Paxos**, with a leader that serves writes and strongly consistent reads.
- **Reads:** eventually consistent by default (any replica, half the cost), strongly consistent on request (the leader).
- **Transactions** (since 2018) across items and tables, using a timestamp-based protocol with transaction coordinators, providing serializable isolation (Idziorek and colleagues, USENIX ATC 2023).
- **Global tables:** multi-region, multi-leader replication with last-writer-wins conflict resolution; in 2025 AWS added a **multi-region strong consistency** option for global tables *(as of October 2026)*.
- **Admission control and adaptive capacity** to handle hot partitions (Chapter 7 §7.6).

Mapping: Paxos-replicated partitions (Chapter 11) inside, hash partitioning (Chapter 7), and an explicit choice between latency and consistency per read (PACELC, Chapter 4).

## 20.3 Apache Cassandra and ScyllaDB

**Cassandra** (originally from Facebook, 2008; Apache project since 2009) combines Dynamo's distribution with Bigtable's data model:

- **Partitioning:** consistent hashing on the partition key, with virtual nodes; clustering columns sort rows within a partition.
- **Replication:** leaderless; the replication factor (often 3 per data centre) and **consistency level** per query: `ONE`, `QUORUM`, `LOCAL_QUORUM`, `ALL` and others. `QUORUM` reads and writes satisfy r + w > n (Chapter 6 §6.5), with the caveats listed there.
- **Conflict resolution:** last-write-wins per cell by timestamp (Chapter 3 §3.3).
- **Lightweight transactions (LWT):** compare-and-set via a Paxos round per operation, for linearizable conditional updates on one partition, at several times the latency of a normal write.
- **Anti-entropy:** read repair, hinted handoff and scheduled **repair** with Merkle trees; operators must run repair regularly, or deleted data can reappear when tombstones are purged before every replica has seen them (the "zombie data" problem, governed by `gc_grace_seconds`).
- **Storage:** an LSM tree with size-tiered, leveled, time-window and (since Cassandra 5.0, 2024) unified compaction; storage-attached secondary indexes (SAI) and vector search arrived in 5.0.
- **Accord:** a leaderless consensus protocol (Elliott Smith and colleagues) bringing multi-partition, strictly serializable ACID transactions to Cassandra. As of mid-2026 it was in the 6.0 alpha releases, not yet in a generally available version.

**ScyllaDB** is a Cassandra-compatible reimplementation in C++ using a shard-per-core architecture (each CPU core owns a slice of data, avoiding locks), and has moved metadata and topology management to Raft. Both systems suit very high write throughput with simple access patterns known in advance.

## 20.4 Google Spanner

**Spanner** (Corbett and colleagues, OSDI 2012) was the first system to provide **externally consistent** (strictly serializable) transactions at global scale:

- **Partitioning:** data is split into ranges ("splits") of a sorted key space, moved and resplit automatically.
- **Replication:** each split is replicated by a **Paxos group** (typically 3 or 5 replicas, possibly across regions), with a long-lived leader holding a lease.
- **Transactions:** read-write transactions use two-phase locking at the leaders and two-phase commit across Paxos groups (Chapter 9 §9.5), so the coordinator and participants are fault-tolerant groups, not single machines.
- **Time:** TrueTime with commit wait (Chapter 3 §3.8) assigns timestamps that respect real time, enabling **lock-free snapshot reads** at any timestamp across the whole database.
- **SQL** with a relational schema (added and documented in later papers, 2017).

Cloud Spanner is Google's public offering. Its design shows that strong global consistency is achievable, at the cost of specialised clock infrastructure and cross-region latency for writes (PACELC's "else consistency" branch).

## 20.5 CockroachDB, YugabyteDB and TiDB

These systems bring Spanner's architecture to environments without TrueTime.

### CockroachDB

- **Ranges** of the sorted key space (512 MiB by default), each replicated by **Raft** (Multi-Raft, Chapter 11 §11.7), with a **leaseholder** that serves reads.
- **Transactions:** serializable by default (read committed is also available since 2024), using MVCC with **hybrid logical clocks** (Chapter 3 §3.7). Because clocks aren't tightly bounded, each transaction has an **uncertainty interval** (the configured maximum clock offset, 500 ms by default): a read that encounters a value written inside the interval can't tell whether it happened before the read, so the transaction restarts at a later timestamp (or refreshes its reads). Nodes whose clocks drift beyond the maximum offset shut themselves down rather than risk anomalies. The design guarantees serializability and, for transactions touching overlapping keys, linearizability; the docs describe the precise guarantee.
- **Parallel commits** reduce the latency of distributed transactions to roughly one round of consensus by writing a "staging" transaction record in parallel with the intents.
- **Storage:** Pebble, a RocksDB-inspired LSM engine written in Go.
- **Licence:** since late 2024, CockroachDB is distributed only under its proprietary enterprise licence (with a free tier for small businesses), having retired the open-source core edition.

### YugabyteDB

Reuses PostgreSQL's query layer on top of DocDB, a distributed document store with Raft-replicated tablets and HLC-based MVCC, storing data in a modified RocksDB. Supports serializable, snapshot and read-committed isolation.

### TiDB

A MySQL-compatible SQL layer over **TiKV**, a Raft-replicated key-value store (Multi-Raft over RocksDB). Transactions follow Google's **Percolator** model (Chapter 9 §9.6), with timestamps from a centralised **timestamp oracle** in the Placement Driver, avoiding clock assumptions at the cost of a round trip for each timestamp (batched in practice). A columnar replica (TiFlash) serves analytics from the same data.

## 20.6 FoundationDB

**FoundationDB** (acquired by Apple in 2015, open-sourced in 2018; SIGMOD 2021 paper by Zhou and colleagues) is an ordered key-value store with **strictly serializable** multi-key transactions, designed as a foundation for building other data models ("layers") on top. Apple runs it at very large scale, including for CloudKit, and Snowflake uses it for metadata.

Its architecture separates concerns:

- a **sequencer** hands out commit versions (a central timestamp oracle);
- **proxies** and **resolvers** perform optimistic concurrency control: a transaction reads at a snapshot version, and at commit, resolvers check whether any key it read was written by a transaction that committed after its read version; if so, it aborts;
- **log servers** make commits durable (replicated logs); **storage servers** apply them and serve reads.

Rather than recovering failed components individually, the transaction system **recovers as a whole**: on a failure, a new generation of the transaction subsystem is recruited, quickly, using the logs.

FoundationDB is famous for its testing: the whole database runs inside a **deterministic simulator** (Flow, a C++ actor extension) with simulated network, disks and clocks, injecting faults across enormous numbers of simulated hours. Its developers credit this with finding almost all bugs before release. Chapter 23 explains deterministic simulation; [`examples/deterministic-simulation/`](../examples/deterministic-simulation/) is a miniature version.

## 20.7 Amazon Aurora and Aurora DSQL

**Aurora** (Verbitski and colleagues, SIGMOD 2017) keeps the familiar single-writer MySQL or PostgreSQL engine but replaces its storage with a distributed service, built on the principle that **"the log is the database"**:

- The database engine sends only **redo log records** to storage, not full pages, cutting network traffic.
- Storage is divided into 10 GB segments, each replicated **six times across three availability zones**. Writes need a **quorum of 4 of 6**; reads need 3 of 6 (r + w = 7 > 6, Chapter 6). This tolerates the loss of a whole availability zone plus one more node without losing data, and the loss of an AZ without losing write availability.
- Storage nodes materialise pages from the log in the background.
- Read replicas share the same storage, so replica lag is typically tens of milliseconds.

**Aurora DSQL** (announced December 2024, generally available in 2025) goes further: a PostgreSQL-compatible, serverless, distributed SQL database with **active-active multi-region** clusters. AWS's descriptions emphasise optimistic concurrency control with **snapshot isolation** (equivalent to PostgreSQL's repeatable read), no locks, read-only transactions that avoid cross-region round trips, write transactions that pay cross-region latency only at commit, and precise time from Amazon's time sync infrastructure to order transactions. Applications must be ready to retry transactions that abort on conflicts.

## 20.8 MongoDB

- **Replica sets:** a primary and secondaries, with an election protocol derived from Raft (protocol version 1). Writes go to the primary and replicate via an operation log (oplog).
- **Write concern** controls acknowledgement: `w: 1` (primary only) or `w: "majority"` (the default since MongoDB 5.0). Only majority-acknowledged writes are guaranteed to survive failover.
- **Read concern** controls what reads see: `local`, `majority` (only majority-committed data), `linearizable` (confirms the primary is still primary before returning) and `snapshot`.
- **Causally consistent sessions** provide read-your-writes and monotonic reads across secondaries (Chapter 8 §8.6).
- **Sharding** by hash or range of a shard key, with `mongos` routers and config servers.
- **Multi-document transactions** (replica sets since 4.0, sharded clusters since 4.2), with snapshot isolation.

Jepsen analyses (2017 and 2020) found that MongoDB's guarantees depend heavily on the read and write concerns chosen, and that some weaker defaults allowed anomalies users might not expect; the 2020 analysis of 4.2.6 found transactional anomalies even at strong settings, which MongoDB addressed. The lesson generalises: **know the settings you run with.**

## 20.9 A method for evaluating any distributed database

1. **Find the paper or architecture document** and answer the six questions in §20.1.
2. **Read the consistency documentation carefully**, noting defaults versus strongest settings, and what's guaranteed for single-key versus multi-key operations.
3. **Check for a Jepsen analysis** (jepsen.io/analyses) and read what was found and fixed.
4. **Model your workload:** key distribution (hot keys?), read/write ratio, transaction scope (single partition or many?), latency budget and regions.
5. **Test failure behaviour yourself:** kill nodes, partition the network, skew clocks, fill disks. Measure what clients see.
6. **Check operations:** backup and point-in-time recovery, upgrades with mixed versions, rebalancing, observability, and the licence and support model.

The [`templates/design-doc.md`](../templates/design-doc.md) template includes a section for recording this evaluation.

---

## Summary

- Each database is a combination of the book's building blocks. Map partitioning, replication, consistency, ordering, failure behaviour and storage before comparing features.
- DynamoDB: hash partitions replicated by Multi-Paxos across three AZs, optional strong reads, transactions, and multi-region global tables.
- Cassandra and ScyllaDB: Dynamo-style leaderless replication with tunable consistency, LWW conflict resolution, Paxos-based lightweight transactions, and (in development) Accord for full transactions.
- Spanner: Paxos groups, 2PC across groups and TrueTime for global strict serializability. CockroachDB, YugabyteDB and TiDB adapt the design with Raft, HLCs with uncertainty intervals, or a timestamp oracle.
- FoundationDB: a central sequencer with optimistic concurrency control, strict serializability, whole-system recovery and pioneering deterministic simulation testing.
- Aurora: "the log is the database", with 4-of-6 quorum storage across three AZs; Aurora DSQL adds active-active multi-region SQL with optimistic snapshot isolation.
- MongoDB: Raft-like replica sets with write and read concerns that determine the guarantees you actually get.
- Evaluate with papers, documentation, Jepsen reports, workload modelling and your own fault testing.

## Exercises

See [`exercises/20-databases-in-practice.md`](../exercises/20-databases-in-practice.md).

## Further reading

- Mostafa Elhemali et al., "Amazon DynamoDB: A Scalable, Predictably Performant, and Fully Managed NoSQL Database Service", USENIX ATC (2022); Joseph Idziorek et al., "Distributed Transactions at Scale in Amazon DynamoDB", USENIX ATC (2023).
- Avinash Lakshman and Prashant Malik, "Cassandra: A Decentralized Structured Storage System", *ACM SIGOPS OSR* (2010).
- James C. Corbett et al., "Spanner: Google's Globally-Distributed Database", OSDI (2012); David F. Bacon et al., "Spanner: Becoming a SQL System", SIGMOD (2017).
- Rebecca Taft et al., "CockroachDB: The Resilient Geo-Distributed SQL Database", SIGMOD (2020).
- Jingyu Zhou et al., "FoundationDB: A Distributed Unbundled Transactional Key Value Store", SIGMOD (2021).
- Alexandre Verbitski et al., "Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases", SIGMOD (2017).
- Marc Brooker, "DSQL Vignettes" blog series on Aurora DSQL's design (brooker.co.za, 2024–2025).
- Jepsen analyses (jepsen.io/analyses).
