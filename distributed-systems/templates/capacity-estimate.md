# Capacity Estimate: <System name>

*Version: <n> · Date: <YYYY-MM-DD> · Author: <name> · Related design doc: <link>*

## How to use this template

- **Purpose:** estimate, in a few minutes of arithmetic, how much storage, request throughput, bandwidth, concurrency and availability a system needs, so you can rule out designs that can't work and avoid distributing systems that don't need it. The answers are orders of magnitude, not forecasts; their value is in telling you *which problem you actually have* ([Chapter 1 §1.6](../chapters/01-introduction.md)).
- **When:** before choosing an architecture or database; at each capacity review (say quarterly); whenever traffic or data assumptions change by more than about 2×.
- **Owner:** the engineer writing the design doc.
- **Sign-off:** none formally, but every number needs a stated assumption so a reviewer can challenge it.

Background reading: [Chapter 1 §1.6–1.7](../chapters/01-introduction.md) (estimation and availability arithmetic), [Chapter 7 §7.6](../chapters/07-partitioning.md) (skew), [Chapter 11 §11.2](../chapters/11-consensus.md) (quorums), [Chapter 17 §17.7](../chapters/17-resilience.md) (Little's law and utilisation). Reference numbers are in [Appendix C](../appendices/C-numbers.md).

*Rules of thumb: round aggressively (powers of ten are fine); write units on every number; design for the peak in the busiest partition, not the average; keep headroom (run below about 70% utilisation, because latency rises steeply above that).*

---

## 1. Assumptions

| # | Assumption | Value | Source or reasoning |
|---|---|---|---|
| A1 | Users / devices / tenants | | |
| A2 | Active fraction per day | | |
| A3 | Operations per active user per day (reads, writes) | | |
| A4 | Peak-to-average ratio | e.g. 2–5× (diurnal); 10×+ for launches or events | |
| A5 | Item size (average, 99th percentile) | | |
| A6 | Retention period | | |
| A7 | Growth per year | | |
| A8 | Replication factor | | |
| A9 | Skew: share of traffic on the busiest key or partition | | |

## 2. Formulas

| Quantity | Formula | Notes |
|---|---|---|
| Average QPS | operations per day ÷ 86,400 | 1 day = 86,400 s ≈ 10⁵ s |
| Peak QPS | average QPS × peak-to-average ratio | |
| Raw storage | items × item size | Plus growth × years retained |
| Stored bytes | raw storage × replication factor × overhead | Overhead: indexes, MVCC versions, compaction headroom (often 1.3–2×; see [Chapter 15 §15.6](../chapters/15-storage-engines.md)) |
| Bandwidth | QPS × bytes per request (or response) | Convert bytes to bits (× 8) for network links |
| Replication bandwidth | write QPS × item size × (replication factor − 1) | Cross-zone and cross-region traffic is often billed |
| Concurrency (Little's law) | L = λ × W | In-flight requests = arrival rate × time in system ([Ch. 17 §17.7](../chapters/17-resilience.md)) |
| Utilisation | ρ = λ ÷ capacity | Keep ρ ≲ 0.7 |
| Time in system (M/M/1) | W = S ÷ (1 − ρ) | S = service time; at ρ = 0.9, W = 10S |
| Nodes needed | peak load ÷ (capacity per node × target utilisation) | Then add N + 1 or N + 2 for failures and maintenance |
| Serial availability | A = a₁ × a₂ × … × aₙ | Every dependency must work ([Ch. 1 §1.7](../chapters/01-introduction.md)) |
| Parallel availability | A = 1 − (1 − a)ⁿ | Any one of n independent replicas suffices; assumes independence |
| Downtime allowed | (1 − A) × period | 30 days = 43,200 min |
| Crash-tolerant quorum | n = 2f + 1; quorum = f + 1 | Tolerates f crashed or unreachable nodes ([Ch. 11 §11.2](../chapters/11-consensus.md)) |
| Byzantine quorum | n = 3f + 1; quorum = 2f + 1 | [Ch. 13 §13.2](../chapters/13-byzantine-fault-tolerance.md) |
| Leaderless quorum overlap | r + w > n | Reads see the latest completed write ([Ch. 6 §6.5](../chapters/06-replication.md)) |
| Tail amplification | P(slow) = 1 − (1 − p)ᵏ | Fan-out to k partitions, each slow with probability p ([Ch. 7 §7.7](../chapters/07-partitioning.md)) |
| Retry amplification | (r + 1)ᵈ | r retries per layer, d layers ([Ch. 17 §17.3](../chapters/17-resilience.md)) |
| Speed-of-light round trip | 2 × distance ÷ 200,000 km/s | Lower bound; real paths are longer ([Ch. 1 §1.6](../chapters/01-introduction.md)) |

## 3. Storage

| Line | Calculation | Result |
|---|---|---|
| Items now | | |
| Raw storage now | | |
| Raw storage in 3 years | | |
| With replication and overhead | | |
| Per node, at <n> nodes | | |
| Fits in one machine's memory / disk? | | |

## 4. Request rates

| Line | Calculation | Result |
|---|---|---|
| Reads per day | | |
| Average read QPS | | |
| Peak read QPS | | |
| Writes per day | | |
| Average write QPS | | |
| Peak write QPS | | |
| Busiest partition's peak (skew) | | |
| Cache hit rate assumed; load reaching the database | | |

## 5. Bandwidth

| Line | Calculation | Result |
|---|---|---|
| Ingress at peak | | |
| Egress at peak | | |
| Replication traffic (cross-zone, cross-region) | | |

## 6. Concurrency and utilisation

| Line | Calculation | Result |
|---|---|---|
| Latency per request (W) | | |
| In-flight requests (L = λW) | | |
| Workers, threads or connections needed | | |
| Utilisation per node at peak | | |
| Utilisation after losing one node (or zone) | | |

## 7. Availability budget

| Component on the critical path | Availability (measured or SLA) | Serial or redundant? |
|---|---|---|
| | | |
| **Composed availability** | | |
| **Target (SLO)** | | |
| **Gap and what closes it** | | |

## 8. Quorum and replica sizing

| Question | Answer |
|---|---|
| Failures to tolerate without losing writes (f) | |
| Failure model (crash or Byzantine) | |
| Nodes needed (2f + 1 or 3f + 1) | |
| Failure domains to spread across (one replica per domain) | |
| Leaderless: n, w, r, and is r + w > n? | |
| Write latency implied (round trips to a quorum across zones or regions) | |

## 9. Conclusion

*One paragraph: single machine, primary plus replicas, or partitioned? Which resource is the binding constraint (storage, write throughput, a hot key, latency, availability)? What would change the answer?*

<…>

---

## Worked example 1: user profiles (from Chapter 1)

*A service stores user profiles. 50 million users; 2 KB per profile; 5,000 reads per second at peak and 200 writes per second. Does it need to be distributed? ([Chapter 1 §1.6](../chapters/01-introduction.md))*

| Line | Calculation | Result |
|---|---|---|
| Raw storage | 50 × 10⁶ × 2 KB = 100 × 10⁶ KB | **100 GB** |
| With 3 replicas and 1.5× overhead | 100 GB × 3 × 1.5 | 450 GB across all replicas; **150 GB per replica** |
| Fits in one server? | A 2026-era server has hundreds of GB to several TB of memory | **Yes**, even in memory |
| Peak reads | Given | 5,000 /s: one well-indexed database handles tens of thousands of simple reads per second |
| Peak writes | Given | 200 /s: trivial for one server |
| Read bandwidth | 5,000 /s × 2 KB | 10 MB/s ≈ 80 Mbit/s |
| Replication bandwidth | 200 /s × 2 KB × 2 followers | 0.8 MB/s ≈ 6.4 Mbit/s |
| Concurrency at 5 ms per read | L = 5,000 × 0.005 | 25 reads in flight |

**Conclusion:** one primary database is enough for load. Add at least one replica in another availability zone for durability and failover ([Chapter 6](../chapters/06-replication.md)), perhaps a cache ([Chapter 18](../chapters/18-caching-and-load-balancing.md)). No sharding. The design is distributed for *availability*, not *scale*.

**Change one number:** 5 billion profiles of 100 KB each (with photos and history) is 5 × 10⁹ × 100 KB = **500 TB**. Storage alone now forces partitioning across many machines ([Chapter 7](../chapters/07-partitioning.md)): at, say, 10 TB usable per node and replication factor 3, that's 500 × 3 ÷ 10 = 150 nodes before headroom.

## Worked example 2: availability composition

*A checkout request calls a gateway, the checkout service, and then the cart, payment and inventory services in sequence. Each is 99.9% available. The payment service depends on one of two independent payment processors, each 99% available.*

| Line | Calculation | Result |
|---|---|---|
| Payment processors (redundant) | 1 − (1 − 0.99)² = 1 − 0.0001 | 99.99% |
| Payment service including processors | 0.999 × 0.9999 | ≈ 99.89% |
| Whole chain (five services in series, payment as above) | 0.999⁴ × 0.9989 | ≈ 99.49% |
| Downtime per 30 days | (1 − 0.9949) × 43,200 min | ≈ 220 min (≈ 3.7 h) |

**Conclusion:** the chain can't meet a 99.9% SLO (43 min per 30 days). Options: make cart and inventory checks asynchronous or cached (removing them from the serial path), degrade gracefully when optional services fail, or raise each component's availability ([Chapter 19 §19.4](../chapters/19-service-architecture.md)). And remember that the redundancy calculation assumes independent failures; two processors behind the same network link aren't independent.

## Worked example 3: quorum and concurrency for a coordination service

*A lock service must survive the loss of any one availability zone, in a region with three zones, without losing acknowledged writes. Clients make 2,000 lock operations per second at peak; each takes 4 ms (one cross-zone round trip of about 1 ms to a majority, plus an fsync of about 2–3 ms).*

| Line | Calculation | Result |
|---|---|---|
| Failures to tolerate | One zone, one node per zone | f = 1 |
| Nodes needed (crash model) | 2f + 1 | **3**, one per zone; quorum = 2 |
| Would 4 nodes help? | Quorum of 4 is 3; still tolerates only 1 failure | No: cost without tolerance ([Ch. 11 §11.2](../chapters/11-consensus.md)) |
| To tolerate zone loss *plus* a node in maintenance | f = 2 → 2f + 1 | 5 nodes (2 + 2 + 1 across three zones) |
| In-flight operations (Little's law) | 2,000 /s × 0.004 s | 8 |
| Leader utilisation if it can commit 10,000 small ops/s (batched) | 2,000 ÷ 10,000 | ρ = 0.2: comfortable headroom |

## Worked example 4: utilisation and latency headroom

*A service's instances each handle 500 requests per second at most (service time 2 ms). Peak load is 6,000 requests per second.*

| Line | Calculation | Result |
|---|---|---|
| Instances at 100% utilisation | 6,000 ÷ 500 | 12 |
| Instances at ρ = 0.7 | 6,000 ÷ (500 × 0.7) | 17.1 → **18** |
| Mean time in system at ρ = 0.7 (M/M/1) | 2 ms ÷ (1 − 0.7) | ≈ 6.7 ms |
| After losing one zone (one third of 18 → 12 left) | ρ = 6,000 ÷ (12 × 500) | ρ = 1.0: **overloaded** |
| Instances to survive a zone loss at ρ ≤ 0.8 | 6,000 ÷ (500 × 0.8) = 15 surviving → 15 × 3/2 | **23** (round up to 24 for even spread) |

**Conclusion:** sizing for the average, or even the peak without failures, leaves no room to lose a zone. The last 10–20% of capacity costs enormous latency, and a small loss of capacity can tip a busy system into overload ([Chapter 17 §17.7](../chapters/17-resilience.md)).
