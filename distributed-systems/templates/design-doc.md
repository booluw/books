# Design Document: <System or change name>

*Status: draft / in review / approved / superseded · Version: <n> · Date: <YYYY-MM-DD> · Author(s): <names> · Reviewers: <names> · Owning team: <team>*

## How to use this template

- **Purpose:** describe a distributed system (or a significant change to one) well enough that reviewers can find its failure modes, consistency gaps and capacity limits **before** they reach production. A design doc records decisions and the reasons for them, including the alternatives you rejected.
- **When:** before building a new service or data store, before changing replication, partitioning or consistency, before adopting a new database or queue, and before migrations. Start it as soon as you know the requirements; it's cheaper to change a document than a deployed system.
- **Owner:** the engineer leading the design writes it and keeps it current until launch.
- **Sign-off:** a design review with at least one engineer outside the team, plus the on-call owner of every dependency the design leans on. Record the decision and open issues in §17.
- **Companion documents:** [`capacity-estimate.md`](capacity-estimate.md) (§4), [`consistency-requirements.md`](consistency-requirements.md) (§8), [`failure-mode-analysis.md`](failure-mode-analysis.md) (§9) and the design-review checklists in [Appendix D](../appendices/D-checklists.md).

Background reading: [Chapter 1](../chapters/01-introduction.md) (estimation and trade-offs), [Chapter 4 §4.8](../chapters/04-models-and-impossibility.md) (using impossibility results in design), [Chapter 8 §8.11](../chapters/08-consistency-models.md) (choosing a consistency model) and [Chapter 20 §20.9](../chapters/20-databases-in-practice.md) (evaluating a database).

*Keep it as short as the system allows. A reviewer should be able to read the summary, the requirements and the "decisions" table and know what you're proposing and what it costs.*

---

## 1. Summary

*Three to five sentences: what you're building, for whom, the core design choice, and the main trade-off you're accepting.*

<…>

**Decisions at a glance**

| Decision | Choice | Main alternative rejected | Section |
|---|---|---|---|
| Partitioning | | | §6 |
| Replication | | | §7 |
| Consistency for the critical operation | | | §8 |
| Behaviour during a partition | | | §8 |
| Storage engine / database | | | §16 |

## 2. Context and problem

- **Problem:** <what is wrong or missing today, with evidence (incidents, metrics, user complaints)>
- **Users and callers:** <who calls this system, how, and from where>
- **Why now:** <what forces the decision>
- **Why distribute at all?** *Chapter 1 §1.2: scale, availability, latency, durability or organisation. Say which applies, with numbers. If one machine plus a standby would do, say so ([Chapter 1 §1.6](../chapters/01-introduction.md)).*

## 3. Requirements

### 3.1 Functional requirements

| # | Requirement | Priority (must / should / could) |
|---|---|---|
| F1 | | |
| F2 | | |

### 3.2 Non-functional requirements and service level objectives

*An SLI is a ratio of good events to all events; an SLO is a target for it over a window ([Chapter 22 §22.4](../chapters/22-observability.md)). State where each SLI is measured (client, load balancer, service).*

| SLI | Measured at | SLO (target, window) | Error budget | Notes |
|---|---|---|---|---|
| Availability: fraction of requests that succeed | | e.g. 99.95% over 30 days | 21.6 min / 30 days | |
| Latency: fraction of reads under <x> ms | | e.g. 99% under 50 ms | | |
| Latency: fraction of writes under <x> ms | | | | |
| Freshness / staleness: fraction of reads no older than <x> s | | | | |
| Durability: acknowledged writes never lost | | e.g. zero tolerated | | |

**Other constraints:** regions and data residency; recovery point objective (RPO: how much data you may lose) and recovery time objective (RTO: how long recovery may take); cost ceiling; compliance; team size and on-call capacity.

### 3.3 Out of scope

- <…>

## 4. Capacity estimate

*Summarise from [`capacity-estimate.md`](capacity-estimate.md). Show the arithmetic, not just the answer, and design for the peak in the busiest partition, not the average ([Chapter 7 §7.6](../chapters/07-partitioning.md)).*

| Quantity | Now | In 12 months | In 36 months | Assumption |
|---|---|---|---|---|
| Records / objects | | | | |
| Storage (before replication) | | | | |
| Storage (after replication, indexes, overhead) | | | | |
| Peak reads per second | | | | |
| Peak writes per second | | | | |
| Peak bandwidth in / out | | | | |
| Busiest key or partition (share of traffic) | | | | |
| Concurrent requests in flight (Little's law, L = λW) | | | | |

**Conclusion:** <one machine / primary plus replicas / partitioned; and why>

## 5. System model and assumptions

*Every guarantee holds only within a model ([Chapter 4 §4.1](../chapters/04-models-and-impossibility.md)). Write it down so reviewers can check whether the environment honours it.*

| Aspect | Assumption | What breaks if it's violated | How we check it |
|---|---|---|---|
| Timing | e.g. partially synchronous; messages usually < 10 ms, unbounded in the worst case | | |
| Process failures | e.g. crash-recovery; persistent state survives restart | | |
| Byzantine behaviour | e.g. not tolerated; checksums catch corruption ([Chapter 13 §13.6](../chapters/13-byzantine-fault-tolerance.md)) | | |
| Network | e.g. loss, duplication, reordering, partial and asymmetric partitions possible | | |
| Clocks | e.g. NTP, skew normally < 5 ms, not relied on for safety ([Chapter 3](../chapters/03-time-and-order.md)) | | |
| Storage | e.g. fsync honoured; device write caches have power-loss protection ([Chapter 15 §15.2](../chapters/15-storage-engines.md)) | | |
| Failure domains | e.g. replicas in 3 availability zones; zone loss is the largest planned failure | | |
| Maximum process pause | e.g. GC pauses up to <x> s observed | | |

## 6. Data model and partitioning

### 6.1 Entities and access patterns

| Entity | Key | Size per item | Count | Main access patterns (with rates) |
|---|---|---|---|---|
| | | | | |

### 6.2 Partitioning

*[Chapter 7](../chapters/07-partitioning.md). Choose the partition key so that the most frequent and most important transactions touch one partition.*

- **Partition key:** <…>
- **Scheme:** range / hash / compound (hash then sort) / fixed partition count / dynamic splitting
- **Number of partitions** (initial, maximum) and how they map to nodes: <…>
- **Hot keys:** <expected skew; mitigation: caching, key splitting, read replicas, adaptive capacity>
- **Secondary indexes:** local (scatter-gather reads) or global (multi-partition, often asynchronous writes)?
- **Rebalancing:** automatic or proposed-then-approved? Rate-limited how?
- **Routing:** any-node, routing tier or partition-aware client? Where is the authoritative, versioned partition map?
- **Cross-partition operations:** which operations span partitions, and how they're handled (§10).

## 7. Replication

*[Chapter 6](../chapters/06-replication.md) and [Chapter 11](../chapters/11-consensus.md).*

| Question | Answer |
|---|---|
| Architecture | single-leader / multi-leader / leaderless / consensus (Raft, Paxos) / chain |
| Replication factor and placement across failure domains | |
| Acknowledgement rule (sync, semi-sync, async, majority, w of n) | |
| Read path (leader, read index, lease, follower with bounded staleness, quorum r of n) | |
| Failover: detection, choice of new leader, fencing of the old leader | |
| Maximum acknowledged-write loss on failover (RPO) | |
| Replication lag expected and alerted on | |
| Anti-entropy (read repair, hinted handoff, Merkle-tree repair) | |
| Adding and removing replicas (snapshot + log catch-up; learners) | |

## 8. Consistency per data item and operation

*Summarise from [`consistency-requirements.md`](consistency-requirements.md). Consistency is a per-operation dial ([Chapter 4 §4.6](../chapters/04-models-and-impossibility.md)); pick the weakest model that keeps each piece of data correct ([Chapter 8 §8.11](../chapters/08-consistency-models.md)).*

| Data / operation | Model required | During a partition: refuse or serve stale? | Latency budget | PACELC (P: A/C; E: L/C) | Conflict resolution | Monotonic (CALM)? |
|---|---|---|---|---|---|---|
| | | | | | | |

**What the chosen database actually provides at the settings we use:** <isolation level, read/write concerns, consistency levels; link to documentation and any Jepsen analysis>

## 9. Failure modes

*Summarise the top risks from [`failure-mode-analysis.md`](failure-mode-analysis.md). Cover at least: node crash, slow node (gray failure), network partition (including partial and asymmetric), zone or region loss, clock skew, disk full or failing, dependency outage, overload and retry storms, bad deployment or configuration push, and loss of the coordination service.*

| # | Failure | Effect on users | Detection | Mitigation | Tested by |
|---|---|---|---|---|---|
| 1 | | | | | |

**Safety versus liveness:** under which conditions does the system deliberately stop (refuse writes, refuse reads) rather than risk a wrong answer? How is "stopped" made visible and recoverable ([Chapter 4 §4.8](../chapters/04-models-and-impossibility.md))?

## 10. Transactions, coordination and communication

- **Transactions:** single-partition only / cross-partition with 2PC over consensus groups / sagas with compensations / none. Isolation level and the anomalies it allows (write skew?) ([Chapter 9](../chapters/09-distributed-transactions.md)).
- **Locks and leader election:** for efficiency or for correctness? Which coordination service? Where are **fencing tokens** checked ([Chapter 12 §12.5](../chapters/12-coordination.md))?
- **Communication:** RPC / queue / pub-sub / replicated log. Delivery semantics and how effectively-once processing is achieved (idempotency keys, deduplication, transactional offsets, outbox) ([Chapter 14](../chapters/14-communication.md)).
- **Ordering:** what must be ordered, and by what key?
- **Schema evolution:** encoding format and compatibility rules.

## 11. Resilience and overload

*[Chapter 17](../chapters/17-resilience.md).*

| Mechanism | Setting | Rationale |
|---|---|---|
| Timeouts per dependency (from measured p99.9) | | |
| Deadline propagation | | |
| Retries: which layer, backoff, jitter, retry budget | | |
| Circuit breakers / outlier detection | | |
| Bulkheads, cells or shuffle sharding | | |
| Load shedding and admission control (bounded queues, priorities) | | |
| Graceful degradation modes | | |
| Caching: pattern, TTL, invalidation, stampede protection ([Chapter 18](../chapters/18-caching-and-load-balancing.md)) | | |

**Metastability check:** what feedback loops could keep the system overloaded after a trigger ends (retries, cold caches, failover load, backlogs)? How is each broken ([Chapter 17 §17.9](../chapters/17-resilience.md))?

## 12. Alternatives considered

| Option | Summary | Pros | Cons | Why not chosen |
|---|---|---|---|---|
| A (chosen) | | | | — |
| B | | | | |
| C: do nothing / one bigger machine | | | | |

## 13. Rollout and migration

*Old and new versions will run side by side; every step must be safe in that mixed state ([Chapter 19 §19.8](../chapters/19-service-architecture.md)).*

- **Release strategy:** canary / rolling / blue-green / feature flags. Automated canary analysis and abort criteria: <…>
- **Data migration:** expand and contract steps; backfill plan and rate limit; dual writes avoided or made safe (outbox, CDC); verification (row counts, checksums, shadow reads).
- **Compatibility:** API, message and schema changes are backward and forward compatible; rollback works with data written by the new version.
- **Configuration changes:** staged like code, never global at once ([Chapter 24 §24.10](../chapters/24-outages.md)).
- **Cut-over and rollback plan:** <steps, owners, go/no-go criteria>

| Phase | Scope | Entry criteria | Exit criteria | Rollback |
|---|---|---|---|---|
| 1 | | | | |

## 14. Observability

*[Chapter 22](../chapters/22-observability.md).*

- **SLIs and dashboards:** <links>
- **Alerts:** multi-window burn-rate alerts on SLOs; each with a runbook.
- **Metrics:** golden signals per service; per-partition and per-instance views (hot keys, gray failures); replication lag; queue depths; retry rate; fencing-token rejections; leader changes.
- **Logs:** structured, with trace IDs; protocol state transitions (became leader in term n, lease expired, stale token rejected).
- **Traces:** OpenTelemetry with context propagation across async hops; sampling strategy.
- **Out-of-band access:** monitoring and tooling don't share fate with the system ([Chapter 24](../chapters/24-outages.md)).

## 15. Testing plan

*[Chapter 23 §23.7](../chapters/23-testing.md). Match the effort to the risk.*

| Layer | Technique | Invariants / oracle | Status |
|---|---|---|---|
| Design | Model checking (TLA+ or a small model) of the riskiest protocol ([Chapter 5](../chapters/05-formal-reasoning.md)) | | |
| Logic | Property-based tests | | |
| Concurrency and faults | Deterministic simulation with many seeds | | |
| Integrated system | Fault injection with history checking (Jepsen-style) | Linearizability / isolation level | |
| Error paths | Injected errors for every handler | | |
| Recovery | Restart from cold at full scale; restore from backup; failover drill | | |
| Production | Canaries, chaos experiments, game days | Steady-state metric | |

**Invariants in plain language** (they double as test oracles and alerts):

1. <e.g. no acknowledged write is lost>
2. <e.g. at most one active writer per partition per epoch>
3. <…>

## 16. Database or infrastructure evaluation

*Complete for each candidate data store, queue or coordination service, following [Chapter 20 §20.9](../chapters/20-databases-in-practice.md). Record the version and date evaluated.*

**Candidate:** <name, version, managed or self-hosted> · **Evaluated:** <YYYY-MM-DD>

| Step | Question | Findings |
|---|---|---|
| 1. Architecture (§20.1's six questions) | Data model and partitioning | |
| | Replication | |
| | Consistency and transactions, at which settings | |
| | Time and ordering of concurrent writes | |
| | Failure behaviour during partitions and node loss | |
| | Storage engine | |
| 2. Consistency documentation | Defaults versus strongest settings; single-key versus multi-key guarantees | |
| 3. Jepsen | Is there an analysis (jepsen.io/analyses)? What was found and fixed? Which version? | |
| 4. Workload model | Key distribution, read/write ratio, transaction scope, latency budget, regions | |
| 5. Our own fault tests | Killed nodes, partitions, clock skew, full disks: what did clients see? | |
| 6. Operations | Backup and point-in-time recovery; mixed-version upgrades; rebalancing; observability; licence and support model; cost | |

**Settings we will run with** (and why): <isolation level, consistency level, write concern, replication factor, min in-sync replicas, …>

**Verdict:** <adopt / adopt with conditions / reject, and the main reason>

## 17. Open questions, risks and decisions

| # | Question or risk | Owner | Due | Resolution |
|---|---|---|---|---|
| 1 | | | | |

**Review record**

| Date | Reviewers | Outcome | Conditions |
|---|---|---|---|
| | | approved / changes requested | |

## Appendix: glossary of system-specific terms

*Define any term a new team member won't know. General terms are in [Appendix A](../appendices/A-glossary.md).*
