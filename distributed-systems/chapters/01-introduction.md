# Chapter 1. What a Distributed System Is, and Why We Build Them

> "A distributed system is one in which the failure of a computer you didn't even know existed can render your own computer unusable."
> — Leslie Lamport, email to colleagues, 1987

## What you will learn

- A working definition of a distributed system, and what makes one different from a program on one machine.
- The reasons we accept the difficulty: scale, availability, latency, durability and organisation.
- The fallacies of distributed computing, and why each is still a source of bugs.
- The vocabulary used throughout the book: nodes, messages, replicas, partitions, faults, failures, safety and liveness.
- How to estimate with back-of-the-envelope numbers before you design.
- The shape of the rest of the book.

---

## 1.1 A definition

A **distributed system** is a collection of independent computers, called **nodes**, that communicate only by sending **messages** over a network and that coordinate to provide a service. Three properties distinguish it from a program running on one machine:

1. **Concurrency.** Nodes run at the same time, independently. There is no single thread of control.
2. **No global clock.** Each node has its own clock, and clocks disagree. There's no reliable way for two nodes to agree on exactly what time it is (Chapter 3).
3. **Independent failure.** Nodes, and the network links between them, fail independently. One node can crash while the others continue. This is called **partial failure**, and it is the defining difficulty of the field.

On a single computer, failure is usually total: if the power goes, everything stops, and when it comes back the program starts again from a known state. In a distributed system, some things fail while others don't, and the survivors often can't tell what failed. Did the other node crash, or is it just slow? Did my message arrive and the reply get lost, or did my message never arrive? Every technique in this book is, in some way, an answer to this uncertainty.

### Examples you already use

- **A web search:** your query fans out to thousands of machines, each holding a slice of the index; their answers are merged in a fraction of a second.
- **A payment:** a card network, the merchant's processor, your bank and the merchant's bank exchange messages; each keeps its own records, which must eventually agree.
- **A cloud database** such as Amazon DynamoDB or Google Cloud Spanner: data is copied across machines and data centres, so it survives the loss of any one of them.
- **A collaborative editor:** several people type into the same document at once, and everyone ends up seeing the same text.
- **Training a large AI model:** thousands of GPUs each compute part of the work and exchange results many times a second (Chapter 25).

## 1.2 Why we build them

Distributed systems are harder to build, test and operate than single-machine systems. We accept that cost for five reasons.

| Reason | What it means | Example |
|---|---|---|
| **Scale** | One machine can't hold the data or handle the load | A social network's billions of posts; millions of requests per second |
| **Availability** | The service must keep working when machines fail | A payment system that must not go down when one server dies |
| **Latency** | Users are far apart; light in fibre takes time | Serving European users from Europe and Asian users from Asia |
| **Durability** | Data must survive the loss of a disk, a machine or a building | Copies of every bank record in several data centres |
| **Organisation** | Many teams must ship independently | Hundreds of services owned by different teams (Chapter 19) |

### Scale up or scale out

You can make a system handle more load in two ways:

- **Scale up (vertical scaling):** buy a bigger machine. Simpler; no distributed-systems problems. In 2026 a single server can have hundreds of CPU cores and several terabytes of memory, which is enough for far more workloads than people assume.
- **Scale out (horizontal scaling):** add more machines. Unlimited in principle, but you inherit every problem in this book.

A sound rule: **don't distribute until you must.** Many systems are distributed for fashion rather than need, and pay the complexity cost without the benefit. But availability and durability usually force at least some distribution: a single machine is a single point of failure, however large it is.

## 1.3 The fallacies of distributed computing

In the 1990s, engineers at Sun Microsystems (L. Peter Deutsch, with later additions by James Gosling) listed false assumptions that programmers new to distributed systems tend to make. Thirty years later, each is still a common source of production incidents.

| Fallacy | Reality | Typical bug |
|---|---|---|
| 1. The network is reliable | Messages are lost, duplicated, delayed and reordered | No retry; or retries without idempotency, so a payment is charged twice |
| 2. Latency is zero | A round trip across a data centre takes ~0.5 ms; across an ocean, ~70–150 ms | A loop making 200 sequential remote calls |
| 3. Bandwidth is infinite | Links saturate; cross-region traffic is costly | Shipping a whole table to filter it remotely |
| 4. The network is secure | Traffic can be read or altered | Unencrypted internal traffic; trusting any caller inside the network |
| 5. Topology doesn't change | Nodes and routes come and go | Hard-coded IP addresses |
| 6. There is one administrator | Many teams and organisations control parts | Changes break a dependency you didn't know about |
| 7. Transport cost is zero | Serialisation, encryption and data transfer cost CPU and money | Chatty protocols that dominate CPU or cloud bills |
| 8. The network is homogeneous | Different hardware, software and protocols | Incompatible versions or encodings |

Add two modern fallacies:

- **Clocks are synchronised.** They aren't, and timestamps from different machines can't be compared naively (Chapter 3).
- **Failures are clean.** Real failures are often partial and slow (a "gray failure", Chapter 22): a disk that works but takes ten seconds per write, a node that answers health checks but fails real requests.

## 1.4 Core vocabulary

These terms are used throughout the book.

- **Node** (or **process**): a participant in the system: a server, a container, a process. Formal sections usually say "process".
- **Message:** data sent from one node to another over the network.
- **Client:** a node that issues requests to the system; usually not part of the system's internal protocol.
- **Replica:** a node holding a copy of some data. **Replication** keeps multiple copies (Chapter 6).
- **Partition:** this word has two meanings, and you must tell them apart from context.
  - A **data partition** (or **shard**) is a subset of the data, stored on some nodes (Chapter 7).
  - A **network partition** is a failure in which the network splits the nodes into groups that can't communicate with each other (Chapter 2).
- **Fault** versus **failure:** a **fault** is a component deviating from its specification (a disk returns an error, a node crashes). A **failure** is the *system* as a whole failing to provide its service. Fault tolerance means preventing faults from becoming failures.
- **Latency:** the time a request takes. **Throughput:** how many requests per unit time the system handles.
- **Availability:** the fraction of time (or of requests) for which the system provides its service correctly.
- **Safety** and **liveness:** the two kinds of correctness property (§1.5).

## 1.5 Safety and liveness

In 1977, Leslie Lamport proposed splitting correctness properties into two kinds. The distinction runs through this whole book.

- A **safety property** says *something bad never happens*. Examples: "two nodes never both believe they are the leader for the same term"; "a committed transaction is never lost"; "the account balance never goes negative".
- A **liveness property** says *something good eventually happens*. Examples: "every request eventually gets a response"; "if the network stabilises, a leader is eventually elected".

Why the distinction matters:

- **Safety violations are permanent and witnessed by a finite prefix of the execution.** If two leaders existed at time *t*, nothing that happens later can undo that. You can point to the moment it went wrong.
- **Liveness can only be violated by an infinite execution.** At any finite moment, the good thing might still happen later. You can never point to the moment liveness failed, only observe that it hasn't happened *yet*.

In distributed systems, there's usually a tension between the two. When the network misbehaves, a well-designed system **preserves safety and sacrifices liveness**: it stops making progress rather than doing something wrong. Consensus protocols (Chapter 11) are designed exactly this way, and the FLP impossibility result (Chapter 4) says that, in a fully asynchronous system, you can't guarantee both.

### ◆ Formal: the precise definitions

Model an execution (or **behaviour**) as an infinite sequence of states σ = s₀, s₁, s₂, …. A property is a set of behaviours.

- *P* is a **safety property** if every behaviour that violates *P* has a finite prefix such that every extension of that prefix also violates *P*. ("Once bad, always bad.")
- *P* is a **liveness property** if every finite prefix can be extended to a behaviour that satisfies *P*. ("It's never too late.")

Bowen Alpern and Fred Schneider proved in 1985 that **every property is the intersection of a safety property and a liveness property**. This is why correctness arguments in this book come in two halves: an **invariant** (a statement true in every reachable state) proves safety, and a **progress argument** under some assumption about the environment (eventually messages arrive in bounded time) proves liveness. Chapter 5 turns this into a practical method.

## 1.6 Back-of-the-envelope estimation

Before designing, estimate. A few minutes of arithmetic rules out designs that can't work and avoids distributing things that don't need to be.

### Numbers to carry in your head

The famous "latency numbers every programmer should know" were popularised by Jeff Dean at Google and Peter Norvig. Exact values change with hardware; the orders of magnitude are what matter. Approximate values for 2026-era hardware (Appendix C has a fuller table):

| Operation | Approximate time |
|---|---|
| L1 cache reference | ~1 ns |
| Main memory reference | ~100 ns |
| Read 1 MB sequentially from memory | ~10–50 µs |
| Round trip within a data centre | ~0.5 ms (often less with modern networks) |
| Random read from NVMe SSD | ~10–100 µs |
| Read 1 MB sequentially from NVMe SSD | ~0.1–0.3 ms |
| Round trip between continents (e.g. London–New York) | ~70–80 ms |
| Round trip London–Sydney | ~250–300 ms |

The speed of light in optical fibre is about 200,000 km/s (about two-thirds of its speed in a vacuum). London to New York is about 5,600 km, so a one-way trip takes at least 28 ms and a round trip at least 56 ms, before any routing or processing. **No engineering can beat this.** That's why global systems must choose between waiting for distant replicas (slow, consistent) and not waiting (fast, possibly inconsistent): the trade-off formalised in Chapter 4 as PACELC.

### A worked estimate

*A service stores user profiles. 50 million users; 2 KB per profile; 5,000 reads per second at peak and 200 writes per second. Does it need to be distributed?*

- Storage: 50 × 10⁶ × 2 KB = 100 GB. Fits comfortably in the memory of one modern server.
- Reads: 5,000 per second. A single well-indexed database server handles tens of thousands of simple reads per second.
- Writes: 200 per second. Trivial for one server.

**Conclusion:** one primary database is enough for load. You still want at least one replica in another availability zone for durability and failover (Chapter 6), and perhaps a cache (Chapter 18). You don't need sharding. The design is distributed for *availability*, not *scale*.

Now change one number: 5 billion profiles (500 TB). Storage alone forces partitioning across many machines (Chapter 7). Estimation tells you which problem you actually have.

A worksheet is in [`templates/capacity-estimate.md`](../templates/capacity-estimate.md).

## 1.7 Availability arithmetic

Availability is often stated in "nines":

| Availability | Downtime per year | Downtime per 30 days |
|---|---|---|
| 99% (two nines) | 3.65 days | 7.2 hours |
| 99.9% (three nines) | 8.77 hours | 43.2 minutes |
| 99.99% (four nines) | 52.6 minutes | 4.3 minutes |
| 99.999% (five nines) | 5.26 minutes | 26 seconds |

### Dependencies multiply

If a request must pass through *n* independent components, each with availability *a*, the request succeeds only if all of them work. The combined availability is aⁿ. Ten components at 99.9% each give 0.999¹⁰ ≈ 99.0%: two nines, from components that each had three. **Serial dependencies erode availability.** This is a quantitative argument against long synchronous call chains (Chapter 19).

### Redundancy adds

If a request can be served by any one of *n* independent replicas, it fails only if all fail. The combined availability is 1 − (1 − a)ⁿ. Two replicas at 99% each give 1 − 0.01² = 99.99%. **Parallel redundancy improves availability dramatically**, provided the failures really are independent. In practice they often aren't: replicas share a power supply, a software version, a configuration push or a bug. Correlated failure is why real systems spread replicas across **failure domains** (racks, availability zones, regions) and why the outages in Chapter 24 so often begin with one change applied everywhere at once.

## 1.8 Trade-offs, not solutions

There are almost no free lunches in distributed systems. The recurring trade-offs:

| Trade-off | One side | Other side | Chapter |
|---|---|---|---|
| Consistency vs availability (during partitions) | Every read sees the latest write | Every request gets an answer | 4, 8 |
| Consistency vs latency (normally) | Wait for distant replicas | Answer locally | 4, 6 |
| Durability vs latency | Wait for disk and replicas | Acknowledge from memory | 6, 15 |
| Coordination vs throughput | Global agreement on order | Independent, parallel progress | 10, 11 |
| Simplicity vs flexibility | One database, one service | Many specialised components | 19 |

Much of the craft is choosing the right point on each trade-off for each piece of data. A shopping cart, a bank balance, a "like" count and a leader-election record need different guarantees, and a good design gives each what it needs and no more.

## 1.9 The shape of this book

- **Part I** builds foundations: networks and failure (Chapter 2), time (3), models and impossibility (4), and formal reasoning (5).
- **Part II** covers data across machines: replication (6), partitioning (7), consistency (8), transactions (9) and convergent data types (10).
- **Part III** covers agreement: consensus (11), coordination (12) and Byzantine fault tolerance (13).
- **Part IVa** covers building blocks: communication (14), storage engines (15), batch and stream processing (16), resilience (17), caching and load balancing (18) and service architecture (19).
- **Part IVb** tours real systems (20, 21) and maps them to the principles.
- **Part V** covers operating and verifying systems: observability (22), testing (23), outages (24) and distributed systems for AI (25).

---

## Summary

- A distributed system is a set of nodes that coordinate only by messages, with concurrency, no global clock and independent (partial) failure.
- We distribute for scale, availability, latency, durability and organisational reasons. Don't distribute until you must, but availability usually forces some distribution.
- The fallacies of distributed computing (plus "clocks are synchronised" and "failures are clean") remain common sources of bugs.
- Correctness properties are safety ("nothing bad happens", proved by invariants) or liveness ("something good eventually happens", proved by progress arguments). Every property is an intersection of the two.
- Estimate before you design. The speed of light sets hard limits on global latency.
- Serial dependencies multiply unavailability; independent redundancy multiplies availability, but real failures are often correlated.
- Distributed design is a series of trade-offs; choose the right guarantee for each piece of data.

## Exercises

See [`exercises/01-introduction.md`](../exercises/01-introduction.md).

## Further reading

- Leslie Lamport, "Proving the Correctness of Multiprocess Programs", *IEEE Transactions on Software Engineering* (1977), where safety and liveness were introduced.
- Bowen Alpern and Fred B. Schneider, "Defining Liveness", *Information Processing Letters* (1985).
- Arnon Rotem-Gal-Oz, "Fallacies of Distributed Computing Explained" (2006).
- Martin Kleppmann and Chris Riccomini, *Designing Data-Intensive Applications* (2nd edition, O'Reilly, 2026).
- Maarten van Steen and Andrew S. Tanenbaum, *Distributed Systems* (4th edition, 2023; free PDF at distributed-systems.net).
- Jeff Dean, "Designs, Lessons and Advice from Building Large Distributed Systems" (LADIS keynote, 2009).
