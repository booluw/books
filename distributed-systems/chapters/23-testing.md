# Chapter 23. Testing Distributed Systems

> "If you haven't tested it with a partition, you haven't tested it."

## What you will learn

- Why distributed systems need testing techniques beyond unit and integration tests.
- Property-based testing and invariants as test oracles.
- Fault injection: partitions, crashes, clock skew and disk faults.
- Jepsen: how black-box testing with history checking finds consistency bugs in real databases.
- Deterministic simulation testing, as pioneered by FoundationDB and adopted by others.
- Chaos engineering in production.
- How to combine model checking, simulation and fault injection into a testing strategy.

---

## 23.1 What makes testing hard

Chapter 5 explained that distributed-systems bugs live in rare interleavings. Conventional tests run on a fast, reliable local network, with no crashes, synchronised clocks and a "happy path" schedule, which is precisely the environment where those bugs don't appear. Effective testing has to:

1. **Generate adversarial conditions:** message loss, delay and reordering; partitions (complete, partial, asymmetric); crashes at awkward moments; restarts that lose volatile state; clock skew and jumps; slow and failing disks.
2. **Explore many schedules**, not one.
3. **Check correctness automatically**, because you can't eyeball thousands of runs. That needs an **oracle**: an invariant or a consistency model to check the results against.
4. **Reproduce failures**, so a bug found once can be debugged and fixed.

## 23.2 Invariants and property-based testing

**Property-based testing** (from Haskell's QuickCheck, Claessen and Hughes, 2000; Python's Hypothesis is a popular modern library) generates many random inputs and checks that a **property** holds for each. When it fails, it **shrinks** the input to a minimal counterexample.

For distributed systems, the properties are the invariants of Chapter 5 and the consistency models of Chapter 8:

- "No acknowledged write is lost."
- "The history is linearizable."
- "Replicas converge after quiescence" (CRDTs, Chapter 10).
- "The sum of balances is conserved" (Chapter 16's snapshot).
- "At most one leader per term" (Raft, Chapter 11).

Many examples in this book use this style. The CRDT tests check the semilattice laws on thousands of random states; the Raft tests run hundreds of random schedules with crashes and partitions and check four safety invariants after every step.

## 23.3 Fault injection

Inject faults at the boundaries the system depends on:

| Fault | How to inject | Tools |
|---|---|---|
| Network partition | Firewall rules (`iptables`/`nftables`), dropping traffic between nodes | Jepsen's nemeses, Toxiproxy, Chaos Mesh, tc |
| Latency, loss, reordering | Linux traffic control (`tc netem`) | Toxiproxy, Pumba, Chaos Mesh |
| Process crash / pause | `kill -9`, `SIGSTOP`/`SIGCONT` | Jepsen, chaos tools |
| Clock skew / jumps | Change system time; `libfaketime` | Jepsen's clock nemesis |
| Disk faults | Fault-injecting filesystems; `dm-flakey`; LD_PRELOAD shims returning errors for fsync | CharybdeFS, ALICE, custom |
| Dependency failure | Return errors or delays from a proxy | Toxiproxy, service-mesh fault injection |

Studies of real failures show why this matters. Yuan and colleagues ("Simple Testing Can Prevent Most Critical Failures", OSDI 2014) analysed 198 user-reported failures in Cassandra, HBase, HDFS, MapReduce and Redis, and found that most catastrophic failures were caused by incorrect handling of **non-fatal errors that were explicitly signalled in software**; in many cases, the error-handling code was trivially wrong (empty catch blocks, "TODO" comments) and simple tests of the error paths would have caught them. Testing the error paths, with injected faults, finds bugs cheaply.

## 23.4 Jepsen

**Jepsen** is a testing library and series of analyses by Kyle Kingsbury (from 2013) that has examined dozens of databases, queues and coordination services, including MongoDB, Cassandra, etcd, ZooKeeper, Redis, PostgreSQL, CockroachDB, TiDB, YugabyteDB, FaunaDB, Kafka and many more. Its approach:

1. Run the system on a cluster of real (or virtual) nodes.
2. Run **clients** that perform randomised operations concurrently, recording each operation's invocation, completion and result (or "unknown" for timeouts) as a **history**.
3. Meanwhile, a **nemesis** injects faults: partitions, crashes, pauses, clock changes, membership changes.
4. Afterwards, a **checker** analyses the history against the system's claimed consistency model: **Knossos** for linearizability, **Elle** for transactional isolation (it infers dependency graphs between transactions and finds cycles that correspond to anomalies such as lost updates, write skew or G-single).

Jepsen analyses have repeatedly found that systems didn't meet their documented guarantees: lost acknowledged writes, stale reads, split brain during partitions, and transactional anomalies. Many vendors now run Jepsen tests continuously or commission analyses. The public reports (jepsen.io/analyses) are some of the best practical education in distributed systems available.

Key lessons from Jepsen's body of work:

- **Timeouts are indeterminate:** a timed-out write may have succeeded. Checkers must allow both possibilities, and so must applications (Chapter 2 §2.1).
- **Documentation is part of the system:** many findings were mismatches between claims and behaviour.
- **Defaults matter:** weak default settings often caused anomalies users didn't expect (Chapter 20 §20.8).

[`examples/linearizability-checker/`](../examples/linearizability-checker/) is a small Knossos-style checker: it records histories from a simulated replicated register with a stale-read bug and finds non-linearizable histories.

## 23.5 Deterministic simulation testing

Fault injection on real clusters finds bugs, but slowly and not reproducibly: the schedule that caused a failure is gone. **Deterministic simulation testing (DST)** solves both problems.

The idea, pioneered by **FoundationDB** (Chapter 20 §20.6) and since adopted by TigerBeetle, Dropbox's sync engine, Antithesis (a company offering deterministic simulation of whole software stacks), and others:

1. Write (or run) the system so that **every source of non-determinism** goes through an interface the test controls: time, randomness, network, disk, thread scheduling.
2. In tests, replace those with **simulated** versions driven by a single **seeded** random number generator: a simulated clock that jumps forward, a simulated network that delays, drops, duplicates and reorders messages according to the seed, simulated disks that fail.
3. Run the whole cluster **in one process**, on one thread, as a sequence of events ordered by the simulator.
4. Check invariants continuously.
5. Run **thousands or millions of seeds** ("swarm testing", varying fault rates and configurations per seed as well).
6. When a seed fails, **replay it exactly**: the same seed always produces the same execution, so you can add logging, step through it, and verify the fix.

Because simulated time runs as fast as the CPU allows, a simulation can cover hours of "cluster time" in seconds, and rare interleavings that would take months to occur in production appear in minutes.

[`examples/deterministic-simulation/`](../examples/deterministic-simulation/) builds a miniature version: a seeded simulator with a virtual clock, a lossy network and crash injection, running a primary-backup replicated counter. The buggy version matches backup acknowledgements by counter name instead of by operation ID, so if a replication message is lost, a *later* operation's acknowledgement can wrongly release an earlier one. Results:

- Across 10,000 seeds (about 4 seconds), the invariant "no acknowledged write is lost" fails in 152 runs (1.52%). The first failing seed is 100.
- Replaying seed 100 produces the identical 93-event trace every time: the replication message for operation 1 is dropped at 11.298 ms; the acknowledgement for operation 8 releases operations 8 *and* 1 at 11.688 ms; the client is told operation 1 succeeded; the primary crashes at 48.3 ms; after failover, operation 1 is gone.
- Each ingredient is necessary: with no message loss, or no crashes, or only one client, the bug never appears in 10,000 seeds. With 0.1% message loss instead of 5%, it appears in only 10 of 2,000 seeds, which is why such bugs survive conventional testing.
- The fixed version passes all 10,000 seeds.

### Limits of simulation

- The simulation tests the code, but only the code that runs inside it; behaviour of real kernels, disks and networks that the simulator doesn't model is untested.
- Retrofitting determinism onto an existing system is hard: hidden sources of non-determinism (thread scheduling, hash-map iteration order, system time calls in libraries) must all be controlled.
- Simulations need good invariants and good fault models to find interesting bugs.

## 23.6 Chaos engineering

**Chaos engineering** experiments on **production** (or production-like) systems to build confidence in their resilience. Netflix's **Chaos Monkey** (2011) randomly terminated production instances during business hours, so engineers had to build services that tolerated instance loss. Netflix later formalised the discipline ("Principles of Chaos Engineering", 2015; Basiri and colleagues, *IEEE Software*, 2016):

1. Define **steady state** in terms of measurable business output (for example, stream starts per second).
2. **Hypothesise** that steady state will continue during the experiment.
3. Introduce real-world events: instance loss, latency, dependency failure, region evacuation.
4. Try to **disprove** the hypothesis; minimise **blast radius** (start small, with automatic abort conditions).

Cloud providers offer managed fault-injection services (AWS Fault Injection Service, Azure Chaos Studio), and **game days** (planned exercises where teams rehearse failures, such as evacuating a region) build both system and human readiness.

Chaos engineering complements, rather than replaces, pre-production testing: it finds problems with configuration, capacity, dependencies and operational procedures that only exist in production.

## 23.7 A testing strategy

| Layer | Technique | Finds | Chapter |
|---|---|---|---|
| Design | Model checking (TLA+, Python model checker) | Protocol design bugs | 5 |
| Code, logic | Unit and property-based tests with invariants | Logic errors, edge cases | 23 |
| Code, concurrency and faults | Deterministic simulation with swarm testing | Interleaving and fault-handling bugs, reproducibly | 23 |
| Integrated system | Fault injection with history checking (Jepsen-style) | Real-system consistency violations | 23 |
| Error paths | Targeted fault injection on each error handler | Mishandled exceptions | 23 |
| Production | Canaries, chaos experiments, game days | Configuration, capacity and operational failures | 19, 23 |
| Always | Observability and postmortems | Everything else, eventually | 22 |

Use the techniques that match the risk. A replication protocol deserves model checking, simulation and Jepsen-style tests; a stateless web service needs fault injection on its dependencies and good canaries.

---

## Summary

- Distributed testing must generate adversarial conditions, explore many schedules, check results with an oracle and reproduce failures.
- Property-based testing with invariants and consistency models as oracles scales test coverage; shrinking yields minimal counterexamples.
- Inject partitions, latency, crashes, pauses, clock skew and disk faults; test error paths, where most catastrophic failures originate.
- Jepsen records histories under faults and checks them for linearizability (Knossos) or transactional anomalies (Elle); its analyses have found real violations in many systems.
- Deterministic simulation controls time, randomness, network and disk with one seed, runs many seeds quickly and replays failures exactly. The book's example finds a 1.5%-of-seeds bug that needs message loss, a crash and concurrency together, and replays it identically.
- Chaos engineering tests production resilience with hypotheses, small blast radius and abort conditions.
- Combine model checking, property tests, simulation, fault injection and production experiments according to risk.

## Exercises

See [`exercises/23-testing.md`](../exercises/23-testing.md).

## Further reading

- Kyle Kingsbury, Jepsen analyses and talks (jepsen.io); Kyle Kingsbury and Peter Alvaro, "Elle: Inferring Isolation Anomalies from Experimental Observations", VLDB (2021).
- Ding Yuan et al., "Simple Testing Can Prevent Most Critical Failures", OSDI (2014).
- Will Wilson, "Testing Distributed Systems w/ Deterministic Simulation", Strange Loop (2014) talk on FoundationDB.
- TigerBeetle's documentation and blog on its simulator (VOPR) (tigerbeetle.com).
- Ali Basiri et al., "Chaos Engineering", *IEEE Software* (2016); Casey Rosenthal and Nora Jones, *Chaos Engineering* (O'Reilly, 2020).
- Koen Claessen and John Hughes, "QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs", ICFP (2000).
- Alex Groce et al., "Swarm Testing", ISSTA (2012).
