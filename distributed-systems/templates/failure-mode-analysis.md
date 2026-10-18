# Failure Mode Analysis: <System name>

*Version: <n> · Date: <YYYY-MM-DD> · Author(s): <names> · Reviewers: <names> · Related design doc: <link>*

## How to use this template

- **Purpose:** list, systematically, how each component of a distributed system can fail, how you'd know, what users would experience, and what you've done about it. This is a **failure mode and effects analysis (FMEA)**, a technique from reliability engineering adapted here for software: it turns "what could go wrong?" from a brainstorm into a table that can be reviewed, prioritised and tested.
- **When:** during design review (it usually changes the design), before launch, and after every significant incident (add the failure mode that surprised you). Review it at least yearly.
- **Owner:** the team that runs the system. Write it with the on-call engineers, who know which failures actually happen.
- **Sign-off:** the design reviewers for the system, plus the owner of each dependency listed in §2.

Background reading: [Chapter 2](../chapters/02-networks-and-failure.md) (failure taxonomy and detection), [Chapter 11 §11.8](../chapters/11-consensus.md) (consensus pitfalls), [Chapter 12 §12.4](../chapters/12-coordination.md) (why leases are dangerous), [Chapter 17](../chapters/17-resilience.md) (overload and metastability), [Chapter 23](../chapters/23-testing.md) (fault injection) and [Chapter 24](../chapters/24-outages.md) (patterns from real outages).

*An FMEA is only as good as its "Test" column. A mitigation that has never been exercised is a hope, not a mitigation ([Chapter 24 §24.2](../chapters/24-outages.md)).*

---

## 1. Scope and system model

- **System and boundary:** <what's in scope; what's treated as an external dependency>
- **Failure model assumed:** <crash-recovery nodes; omission and timing faults in the network; Byzantine faults not tolerated but corruption detected by checksums; …> ([Chapter 2 §2.3](../chapters/02-networks-and-failure.md), [Chapter 4 §4.1](../chapters/04-models-and-impossibility.md))
- **Failure domains:** <hosts, racks, availability zones, regions; which components share which>
- **Largest failure we design to survive without data loss:** <e.g. one availability zone>
- **Largest failure we design to survive without unavailability:** <e.g. one node>

## 2. Components and dependencies

| Component | Instances / placement | Depends on | Shares fate with |
|---|---|---|---|
| | | | |

## 3. Rating scales

*Use the same scales across your organisation so tables can be compared. Risk priority = severity × likelihood (1–25). Some teams also rate detectability (how likely the failure is to go unnoticed); add a column if you do.*

| Score | Severity (effect on users and data) | Likelihood (per year, per system) |
|---|---|---|
| 1 | No user-visible effect | Less than once in 10 years |
| 2 | Brief, minor degradation (latency, a few retried errors) | Once in 3–10 years |
| 3 | Partial outage or noticeable degradation for some users | Once in 1–3 years |
| 4 | Full outage of a critical function, no data loss | Several times a year |
| 5 | Data loss or corruption, safety violation (two leaders, lost acknowledged write), or prolonged outage | Monthly or more often |

## 4. Failure mode table

*One row per (component, failure mode). Cover each category: crash, slow (gray failure), partition (complete, partial, asymmetric), clock, disk, overload, dependency, deployment or configuration change, operator error, and loss of the tools needed to recover. Sort by risk priority once filled.*

| # | Component | Failure mode | Detection | Effect | Sev | Lik | RPN | Mitigation | Test | Owner |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | | |
| 2 | | | | | | | | | | |

## 5. Actions

*For every row with RPN above your threshold (say 12), or severity 5 at any likelihood, record an action.*

| # | Row | Action | Owner | Due | Status |
|---|---|---|---|---|---|
| 1 | | | | | |

## 6. Residual risks accepted

| Risk | Why accepted | Who accepted | Review date |
|---|---|---|---|
| | | | |

---

## Worked example: a three-node Raft-backed coordination service

*Fictional. Contoso runs **Keystone**, an internal coordination service on three nodes (one per availability zone in one region). Keystone stores configuration, leader-election records and locks for about 40 internal services. It replicates with Raft ([Chapter 11](../chapters/11-consensus.md)), stores its log and state in an embedded copy-on-write B-tree, serves linearizable reads by default using read index, and hands out leases with fencing tokens (the key's revision) ([Chapter 12](../chapters/12-coordination.md)). Clients use a library that renews leases every 3 s for a 10 s TTL. Election timeout is randomised in 1.0–2.0 s; heartbeat interval 100 ms.*

### Scope and model (example)

- **Failure model:** crash-recovery nodes with persistent state; lossy, reordering, duplicating network with possible partial and asymmetric partitions; clocks synchronised by NTP but not trusted for safety except where noted (leases).
- **Fault tolerance:** n = 3 = 2f + 1, so f = 1. Keystone tolerates one node down. **Two nodes down, or one node isolated from two that are themselves partitioned, means no quorum: writes and linearizable reads stop.** That's a deliberate CP choice ([Chapter 4 §4.5](../chapters/04-models-and-impossibility.md)).
- **Largest failure without data loss:** one availability zone (one node); with fsync honoured, also a simultaneous restart of all three nodes.
- **Largest failure without unavailability:** one node or one zone.

### Failure mode table (example)

| # | Component | Failure mode | Detection | Effect | Sev | Lik | RPN | Mitigation | Test |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Follower node | Crash (process or host) | Leader sees missed AppendEntries acks; node health probe; `keystone_peers_up` < 3 alert | None for users; cluster now tolerates **zero** further failures | 2 | 4 | 8 | Page on any node down for > 5 min; automated host replacement; restore from snapshot plus log catch-up as a learner before promotion | Monthly: kill -9 a follower under load; verify no client errors and catch-up time |
| 2 | Leader node | Crash | Followers' election timeout; leader-change counter; client error spike | Writes and linearizable reads pause for one election (≈ 1–2 s); in-flight writes may time out with unknown outcome | 3 | 4 | 12 | Randomised election timeouts; clients retry with idempotency keys and exponential backoff with full jitter; library hides leader changes | Weekly in staging, monthly in production: kill the leader; measure unavailability window against a 3 s budget |
| 3 | Leader node | Long process pause (GC, VM migration) longer than election timeout | Leader-change counter; pause duration metric; "stepped down: higher term seen" log line | New leader elected; old leader resumes believing it leads; any write it accepts is rejected by followers (stale term), but **local reads from the old leader would be stale** | 5 | 3 | 15 | Never serve reads from local leader state: read index on every linearizable read (or leases with bounded clock drift); old leader steps down on seeing higher term ([Chapter 11 §11.6](../chapters/11-consensus.md)) | Deterministic simulation with pauses; Jepsen-style test with `SIGSTOP` on leader and linearizability checker on reads |
| 4 | Network | Partition isolating the leader (minority side) | Leader loses heartbeat acks from majority; check-quorum steps it down; clients on minority side see timeouts | Majority side elects a new leader within ≈ 2 s; minority leader can't commit; clients pinned to it fail until they re-route | 3 | 3 | 9 | Check-quorum (leader steps down if it can't reach a majority for an election timeout); client library tries all endpoints | iptables partition test in staging every release; verify no acknowledged write lost and history linearizable |
| 5 | Network | Asymmetric or partial partition: a follower can send but not receive (or reaches only one peer) | Leader-change rate alert (> 3 per 10 min); term number climbing quickly | Disrupted follower repeatedly times out and starts elections with higher terms, deposing a healthy leader: **leadership flapping**, write latency spikes | 3 | 2 | 6 | Pre-vote phase (a candidate checks it could win before incrementing its term); check-quorum; alert on term growth | Inject one-way drops with `tc`/iptables; assert ≤ 1 leader change per injected fault |
| 6 | Node disk | fsync returns error, or device acknowledges writes it hasn't persisted | fsync error counter; checksum mismatch on log read; node crash loop | If ignored, node may vote twice or lose a committed entry after restart, breaking Raft's model: **two leaders in a term or lost committed write** | 5 | 2 | 10 | Treat any fsync error as fatal (crash, recover from log and peers); checksummed log records; disks with power-loss protection; persist currentTerm and votedFor before replying ([Chapter 15 §15.2](../chapters/15-storage-engines.md)) | Fault-injecting filesystem (fsync errors, torn writes) in CI; TLA+ variant that forgets votedFor is refuted ([Chapter 5](../chapters/05-formal-reasoning.md)) |
| 7 | Node disk | Disk full (log or snapshot growth) | Disk usage alert at 70% and 85%; database-size quota alarm | Node can't append; if two nodes hit it, quorum lost: writes stop | 4 | 3 | 12 | Size quotas below the service's recommended limit (e.g. 8 GB for etcd-class stores); periodic compaction and defragmentation; reject oversized values; alert on growth rate | Fill-disk test in staging; quota-exceeded behaviour verified (read-only mode, clear error) |
| 8 | Raft log | Unbounded log growth; slow snapshot transfer to a lagging follower | Log length and snapshot duration metrics | Recovering follower can't catch up; cluster runs at f = 0 for hours | 3 | 3 | 9 | Snapshot every N entries; rate-limited InstallSnapshot; learner catch-up before voting | Restore a follower from empty at production data size; time it |
| 9 | Membership | Adding or replacing a node changes the voting set unsafely | Configuration-change audit log; peer count mismatch | Disjoint majorities possible: **two leaders**; or a new empty voter makes quorum unreachable | 5 | 2 | 10 | One-server-at-a-time changes only after the leader has committed an entry in its term; add as non-voting learner first; runbook forbids editing membership by hand | Scripted node-replacement drill quarterly; model-checked reconfiguration in the TLA+ spec |
| 10 | Whole cluster | Two of three nodes lost (zone outage during another node's maintenance) | `keystone_quorum` = 0; all writes fail | No writes or linearizable reads; clients holding leases keep acting until expiry; nothing can change (new leaders can't be elected in dependent services) | 4 | 2 | 8 | Never take a node down for maintenance while another is unhealthy (automated guard); dependent services keep last-known configuration; documented disaster-recovery procedure to rebuild from a single surviving node's data | Annual game day: stop two nodes; verify dependent services degrade as designed; practise forced recovery in staging |
| 11 | Client lease holder | Lock holder pauses or is partitioned past lease expiry, then writes to a protected resource | Fencing-token rejection counter at resources; "lease lost" client log | Without fencing: **two holders write; data corrupted**. With fencing: stale write rejected | 5 | 3 | 15 | Every lock grant returns a fencing token (revision); every protected resource rejects lower tokens; for resources that can't check, use conditional writes or idempotent operations ([Chapter 12 §12.5](../chapters/12-coordination.md)) | Model-checked lock-with-fencing spec; integration test that pauses a holder for 2× TTL and asserts its write is rejected |
| 12 | Clients | Retry storm after a leader change or brief outage (thousands of clients reconnect and retry at once) | Request rate and retry ratio spike; queue depth; p99 latency | Overload keeps the cluster slow after the trigger ends; elections time out; **metastable failure** | 4 | 3 | 12 | Client library: full-jitter backoff, retry budget (≤ 10%), reconnection jitter; server: per-client rate limits and bounded queues with load shedding ([Chapter 17 §17.9](../chapters/17-resilience.md)) | Load test: kill leader at 2× normal load; verify recovery within 30 s and amplification ≤ 1.1× |
| 13 | Clients | Misuse: services put large or fast-changing data in Keystone, or call it on every user request | Per-client request rate and value-size metrics | Coordination service becomes a bottleneck and a dependency of every request | 3 | 4 | 12 | Quotas per client; value size limit; design-review rule: control plane only, never in the request path ([Chapter 12 §12.8](../chapters/12-coordination.md)) | Quota enforcement tests; quarterly top-clients review |
| 14 | Watches | Client disconnects and resumes from a revision that has been compacted | "revision compacted" error count | Client misses changes; acts on stale configuration | 3 | 3 | 9 | Client library re-reads full state on compaction error, then resumes watch; compaction retains ≥ 1 h of history | Test: disconnect client, compact, reconnect; assert it converges |
| 15 | Clocks | NTP step backwards or fast drift on the leader | Clock-offset metric versus peers; NTP daemon alarms | Timeouts and lease durations measured wrongly if wall-clock time is used; leader leases (if enabled) unsafe | 4 | 2 | 8 | All durations on the monotonic clock; leader leases disabled unless drift is bounded and monitored; nodes exceeding max offset refuse to serve ([Chapter 3 §3.2](../chapters/03-time-and-order.md)) | Clock-skew and jump injection (`libfaketime`) in the fault-injection suite |
| 16 | Deployment | Bad binary or configuration rolled to all three nodes | Canary health; error rate; crash loop | All nodes fail together: quorum lost; correlated failure defeats replication | 5 | 3 | 15 | Roll one node at a time with health gate and automatic halt; never change all nodes' configuration at once; tested rollback ([Chapter 19 §19.8](../chapters/19-service-architecture.md), [Chapter 24 §24.10](../chapters/24-outages.md)) | Every release: canary on one follower for 24 h; rollback drill each quarter |
| 17 | TLS certificates | Peer or client certificates expire | Expiry alerts at 30, 14 and 3 days | Peers can't talk: partition of the whole cluster; clients can't connect | 5 | 2 | 10 | Automated rotation; expiry monitored independently of Keystone itself | Rotation exercised in staging monthly with short-lived certificates |
| 18 | Operations tooling | Runbooks, dashboards or access paths depend on Keystone (or on services that depend on it) | Game day reveals it | Operators can't see or fix the outage they're responding to | 4 | 2 | 8 | Out-of-band dashboards and break-glass access that don't depend on Keystone; runbook stored outside the system ([Chapter 24 §24.2](../chapters/24-outages.md)) | Annual game day performed with Keystone down |

### Actions from the example

| # | Row | Action | Owner | Due |
|---|---|---|---|---|
| 1 | 3, 11 | Add Jepsen-style test with leader pauses and a linearizability checker to the release pipeline | Keystone team | <date> |
| 2 | 11 | Audit the 40 client services: which protected resources check fencing tokens? Fix or document each | Platform architecture | <date> |
| 3 | 12 | Ship client library 4.2 with retry budget and reconnection jitter; block older versions | Keystone team | <date> |
| 4 | 16 | Enforce one-node-at-a-time rollout in the deployment tool, not just the runbook | Release engineering | <date> |

### Residual risks accepted (example)

| Risk | Why accepted | Who accepted | Review date |
|---|---|---|---|
| Loss of two zones at once makes Keystone unavailable for writes | A five-node, three-region cluster would add cross-region latency to every write; dependent services degrade safely to last-known configuration | Head of platform | <date> |
| Byzantine behaviour (a node sending wrong data deliberately) not tolerated | Single-organisation deployment; checksums and authentication cover accidental corruption and impersonation ([Chapter 13 §13.6](../chapters/13-byzantine-fault-tolerance.md)) | Security architecture | <date> |
