# Chapter 21. Coordination, Streaming and Orchestration Systems in Practice

> "Infrastructure is just distributed systems that other distributed systems depend on."

## What you will learn

- How Apache Kafka replicates its log, elects leaders, and provides idempotent and transactional writes, and how KRaft replaced ZooKeeper.
- How Kubernetes works as a distributed system: etcd, controllers and level-triggered reconciliation.
- How object storage (Amazon S3 and its peers) became strongly consistent, and why conditional writes made it a coordination primitive.
- How Apache Flink runs stateful stream processing in production.
- The design patterns these systems share.

Details are *as of October 2026*.

---

## 21.1 Apache Kafka

Chapter 14 introduced Kafka as a partitioned, replicated log. Here's how it works inside.

### Replication: leaders, followers and the ISR

Each partition has one **leader** broker and several **follower** replicas (replication factor typically 3). Producers write to the leader; followers fetch from it. The leader tracks the **in-sync replica set (ISR)**: followers that are caught up within a configured lag (`replica.lag.time.max.ms`).

- A producer with `acks=all` gets an acknowledgement once **every replica in the ISR** has the record.
- The **high-water mark** is the offset up to which all ISR members have replicated; consumers only read up to it, so they never see a record that could be lost on failover.
- `min.insync.replicas` (typically 2 with replication factor 3) makes the leader refuse `acks=all` writes when the ISR shrinks too far, choosing consistency over availability (Chapter 4).
- If all in-sync replicas fail, `unclean.leader.election.enable` decides whether an out-of-sync replica may become leader (availability, with data loss) or the partition stays offline (consistency). It defaults to false.

The ISR is a dynamic quorum: rather than a fixed majority, it's "all replicas that are currently keeping up", which allows a partition with replication factor 3 to keep accepting writes with only 2 (or, if allowed, 1) replicas while preserving acknowledged writes. Kafka's **leader epochs** (KIP-101) act as fencing tokens (Chapter 12 §12.5) during truncation after leader changes, fixing earlier edge cases in which replicas could diverge.

### KRaft: metadata via Raft

Kafka originally stored cluster metadata (topics, partitions, ISRs, the controller's identity) in ZooKeeper. **KRaft** (KIP-500) replaced ZooKeeper with a Raft-based quorum of **controller** nodes that store metadata in an internal, replicated metadata log; brokers follow the log. This removed a separate system to operate, and made metadata changes (such as failing over thousands of partitions) much faster. KRaft became production-ready in Kafka 3.3 (2022), and **Kafka 4.0** (March 2025) removed ZooKeeper support entirely.

### Idempotent producers and transactions

- The **idempotent producer** (default since Kafka 3.0) attaches a producer ID and a per-partition sequence number to each batch; the broker discards duplicates and detects gaps, so retries can't create duplicates within a partition.
- **Transactions** let a producer write to several partitions and commit consumer offsets **atomically**. A **transaction coordinator** runs a two-phase-commit-like protocol (Chapter 9), writing commit or abort **markers** into each partition. Consumers with `isolation.level=read_committed` skip records from aborted transactions. Combined, these give exactly-once read-process-write pipelines **within Kafka** (Chapter 14 §14.6). The transactional ID's **epoch** fences "zombie" producer instances from a previous incarnation.

### Other developments

- **Tiered storage** (KIP-405, production-ready in Kafka 3.9) offloads older log segments to object storage, decoupling retention from broker disks.
- **Share groups** ("queues for Kafka", KIP-932) add queue-like consumption, with per-message acknowledgement and multiple consumers per partition, released in early access in Kafka 4.0.
- **Diskless and object-storage-native designs:** several Kafka-compatible systems (WarpStream, acquired by Confluent in 2024; AutoMQ; others) and open proposals write directly to object storage, trading latency for much lower cross-zone replication cost.

## 21.2 Kubernetes as a distributed system

**Kubernetes** orchestrates containers across a cluster of machines. Underneath, it's a textbook application of this book's ideas.

### State in etcd

All cluster state (desired and observed) lives in **etcd** (Chapter 12), accessed only through the **API server**. Every object has a `resourceVersion` (derived from etcd's revision), used for **optimistic concurrency**: an update succeeds only if the object hasn't changed since it was read (compare-and-set). Clients **watch** resources for changes, resuming from a resource version after disconnects.

### Controllers and level-triggered reconciliation

Kubernetes doesn't execute commands like "start three containers". Users declare **desired state** ("there should be three replicas of this pod"), and **controllers** run **reconciliation loops**:

```
loop forever:
    desired  = read desired state (spec)
    observed = read actual state (status, other objects)
    if observed != desired:
        take one step toward desired
```

This design is **level-triggered** rather than **edge-triggered**: controllers act on the *current difference* between desired and observed state, not on individual change events. If a controller misses an event (it crashed, a watch disconnected), it still converges, because the next loop sees the difference. Each step is effectively idempotent. This makes the system robust to exactly the failures of Chapter 2: lost messages, crashes and restarts.

### Leader election and fencing in practice

Controllers run several replicas for availability, with one active at a time. They elect a leader using a **Lease** object in the API server (compare-and-set on the lease's holder and renew time). Because leases depend on time, a paused leader can briefly overlap with its successor (Chapter 12 §12.4); controllers mitigate this with optimistic concurrency on every write (the `resourceVersion` acts as a fencing token), so a stale leader's writes fail.

### The scheduler and kubelets

The **scheduler** assigns pods to nodes; the **kubelet** on each node makes the node's containers match the pods assigned to it, and reports status. Node heartbeats (also Lease objects) feed a failure detector: when a node stops heartbeating, its pods are eventually evicted and rescheduled, with configurable timeouts that trade detection speed against false positives, as in Chapter 2 §2.5. Workloads that must not run twice (StatefulSets) wait for confirmation that the old pod is gone, because a partitioned node may still be running it.

## 21.3 Object storage

**Object storage** (Amazon S3, Google Cloud Storage, Azure Blob Storage, and compatible systems such as MinIO and Ceph's RADOS Gateway) stores immutable blobs by key, with very high durability (S3 is designed for 99.999999999%, "eleven nines", of annual durability through replication and erasure coding across availability zones) and elastic capacity.

### From eventual to strong consistency

S3 was originally eventually consistent for overwrites and listings: a reader could get the old version of an object, or a listing that missed a new one. In December 2020, AWS made S3 **strongly consistent** for all reads, writes and listings, at no extra cost and with no performance penalty. AWS later described part of how it verified the change with formal methods and lightweight verification (Chapter 5 §5.6). Google Cloud Storage and Azure Blob Storage also provide strong consistency.

### Conditional writes as coordination

Object stores support **conditional requests**: write only if the object doesn't exist (`If-None-Match: *`), or only if its version (ETag) matches (`If-Match`). S3 added conditional writes in August 2024. These are compare-and-set operations, which means **object storage can now serve as a coordination primitive**: systems can implement leader election, locks (with the ETag as a fencing token) and atomic commits of table metadata directly on S3, without a separate database. Open table formats (Apache Iceberg, Delta Lake, Apache Hudi) commit new table versions by atomically swapping a metadata pointer, using exactly this kind of operation (or a catalogue service where it isn't available). Many new data systems (diskless Kafka variants, Turbopuffer, Neon's and others' storage layers) are built "on top of S3" for durability, accepting higher latency in exchange.

## 21.4 Apache Flink in production

Chapter 16 described Flink's checkpointing. In production:

- A **JobManager** coordinates the job (with high-availability mode using Kubernetes or ZooKeeper for leader election and checkpoint metadata); **TaskManagers** run the operators.
- **State backends** keep operator state in memory (heap) or in an embedded RocksDB instance (for state larger than memory), with checkpoints written to durable storage (usually object storage). Flink 2.0 (March 2025) introduced **disaggregated state management**, which can keep state primarily in remote storage, so that rescaling and recovery don't require copying large local state.
- **Savepoints** are manually triggered, portable checkpoints used for upgrades, rescaling and migrations.
- **Exactly-once** end to end requires replayable sources (Kafka offsets) and transactional or idempotent sinks (Chapter 16 §16.6).
- Operational concerns: checkpoint duration and size, backpressure (visible in Flink's UI as operators blocked on output), watermark lag, and state growth from windows or joins that never expire.

## 21.5 Shared patterns

Across these systems, and the databases of Chapter 20, the same few ideas recur:

| Pattern | Kafka | Kubernetes | Object storage | Flink | Chapter |
|---|---|---|---|---|---|
| Replicated log as source of truth | Partitions; KRaft metadata log | etcd (Raft) | Internal metadata | Source offsets | 6, 11, 14 |
| Consensus for metadata | KRaft | etcd | Internal | HA leader election | 11, 12 |
| Fencing tokens / epochs | Leader epochs; producer epochs | resourceVersion | ETags | Checkpoint IDs | 12 |
| Idempotency for retries | Idempotent producer | Level-triggered reconciliation | PUT of whole objects | Replay from checkpoint | 14 |
| Consistent snapshots | — | — | — | Checkpoint barriers | 16 |
| Tunable durability vs availability | acks, min ISR, unclean election | Eviction timeouts | Storage classes | Checkpoint interval | 4, 6 |
| Separating compute from storage | Tiered storage; diskless | — | The storage | Disaggregated state | 15, 20 |

Recognising these patterns makes new systems quick to understand: when you meet one, look for its log, its consensus, its fencing, its idempotency and its snapshot mechanism.

---

## Summary

- Kafka replicates partitions with leaders, followers and a dynamic in-sync replica set; acks=all with min.insync.replicas trades availability for durability; leader epochs fence stale replicas; KRaft (Raft) replaced ZooKeeper entirely in Kafka 4.0; idempotent producers and transactions give exactly-once within Kafka.
- Kubernetes stores all state in etcd, uses optimistic concurrency and watches, and converges through level-triggered reconciliation loops that tolerate lost events; leader election uses leases plus resourceVersion fencing.
- Object storage is highly durable and now strongly consistent; conditional writes make it a coordination primitive and a foundation for new data systems.
- Flink combines checkpoints, state backends and transactional sinks for exactly-once stateful streaming, with disaggregated state in 2.0.
- The same patterns recur everywhere: replicated logs, consensus for metadata, fencing, idempotency, snapshots and tunable durability.

## Exercises

See [`exercises/21-infrastructure-in-practice.md`](../exercises/21-infrastructure-in-practice.md).

## Further reading

- Apache Kafka documentation, "Design" and "Replication" sections (kafka.apache.org); KIP-101 (leader epochs), KIP-500 (KRaft), KIP-98 (exactly-once), KIP-405 (tiered storage), KIP-932 (share groups).
- Brendan Burns et al., "Borg, Omega, and Kubernetes", *ACM Queue* (2016).
- Kubernetes documentation, "Controllers" and "Leases" (kubernetes.io).
- AWS, "Amazon S3 Update – Strong Read-After-Write Consistency" (December 2020) and "Amazon S3 now supports conditional writes" (August 2024).
- Paris Carbone et al., "State Management in Apache Flink", VLDB (2017).
- Apache Flink 2.0 release announcement (flink.apache.org, March 2025).
