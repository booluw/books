# Diagrams

Mermaid diagrams. They render on GitHub and in most Markdown tools, and every one has been checked with the Mermaid CLI.

| Diagram | Chapters |
|---|---|
| [Four failures that look identical to a timeout](timeout-ambiguity.md) | 2, 14 |
| [Last write wins loses data under clock skew](lww-clock-skew.md) | 3, 6 |
| [Happened-before across three processes](happened-before.md) | 3 |
| [Single-leader replication](single-leader-replication.md) | 6 |
| [Chain replication](chain-replication.md) | 6 |
| [Partitions and their replicas across nodes](partitions-and-replicas.md) | 7 |
| [Consistent hashing ring](consistent-hashing-ring.md) | 7 |
| [Hierarchy of consistency and isolation models](consistency-hierarchy.md) | 8, 9 |
| [Two-phase commit](two-phase-commit.md) | 9 |
| [Single-decree Paxos](paxos.md) | 11 |
| [Raft server states](raft-states.md) | 11 |
| [A paused lock holder corrupts storage without fencing](lease-without-fencing.md) | 12 |
| [Log-structured merge tree](lsm-tree.md) | 15 |
| [MapReduce dataflow](mapreduce.md) | 16 |
| [Circuit breaker states](circuit-breaker.md) | 17 |
| [The metastable retry loop](metastable-failure.md) | 17, 24 |
| [Cache-aside invalidation race](cache-aside-race.md) | 18 |
| [A distributed trace as a tree of spans](trace-tree.md) | 22 |

Conventions: node labels containing punctuation are quoted, and line breaks use `<br/>`.
