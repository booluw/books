# Chapter 13. Byzantine Fault Tolerance

> "Trust, but verify" is not an algorithm. Byzantine fault tolerance is.

## What you will learn

- What Byzantine faults are, and when (rarely, in a data centre) you need to tolerate them.
- The Byzantine Generals problem, and why tolerating f traitors needs 3f + 1 participants, with a proof.
- How digital signatures change what's possible.
- PBFT, the first practical Byzantine consensus protocol, and its modern descendants (Tendermint, HotStuff).
- How blockchains approach the same problem with proof of work and proof of stake.
- Cheaper defences against non-malicious "Byzantine" behaviour: checksums, validation and diversity.

This chapter is shorter than its neighbours: Byzantine fault tolerance matters enormously in some domains and very little in most corporate systems. It's included so you can recognise when it's needed and evaluate claims about it.

---

## 13.1 Byzantine faults

The crash model (Chapter 2 §2.3) assumes a faulty node simply stops. A **Byzantine** fault allows a node to behave **arbitrarily**: send incorrect messages, send *different* messages to different nodes (**equivocation**), pretend to have received messages it didn't, or collude with other faulty nodes. The name comes from Lamport, Shostak and Pease's 1982 paper, which framed the problem as generals of the Byzantine army, some of whom may be traitors.

Sources of Byzantine behaviour:

- **Malicious participants:** in systems spanning organisations that don't trust each other (blockchains, cross-bank settlement, some federated systems).
- **Compromised nodes:** an attacker controlling some servers.
- **Bugs and hardware faults** that cause wrong rather than missing output: memory corruption, CPU errors that silently miscompute (Google and Meta both reported **silent data corruption** from defective CPU cores in large fleets in 2021), corrupted disks.

Inside a single organisation's data centre, most systems assume nodes are honest and handle the non-malicious sources with cheaper techniques (§13.6). Full Byzantine fault tolerance is used where participants genuinely don't trust each other, or where the cost of a wrong answer is extreme (some aerospace and flight-control systems).

## 13.2 The Byzantine Generals problem

A commander sends an order (attack or retreat) to n − 1 lieutenants. Some generals, possibly including the commander, are traitors. Requirements:

1. All loyal lieutenants obey the same order.
2. If the commander is loyal, every loyal lieutenant obeys the commander's order.

### ◆ Formal: why three generals can't tolerate one traitor

With **oral messages** (messages that can be forged or altered by their sender; a traitor can claim anything about what it received), the problem is unsolvable unless n ≥ 3f + 1.

Take n = 3: commander C and lieutenants L1, L2; one traitor.

- **Scenario A:** C is loyal and orders "attack". L2 is the traitor and tells L1 "C told me retreat".
- **Scenario B:** C is the traitor. It tells L1 "attack" and tells L2 "retreat". L2, loyal, honestly reports to L1 "C told me retreat".

From L1's point of view, the two scenarios are identical: it received "attack" from C and "C said retreat" from L2. In scenario A, requirement 2 says L1 must attack. So L1 attacks in scenario B too. By the symmetric argument from L2's perspective (swapping roles), L2 must retreat in scenario B (it received "retreat" from C, and L1 says C said "attack", indistinguishable from a scenario where C is loyal and ordered retreat and L1 is the traitor). Then the loyal lieutenants L1 and L2 disagree in scenario B, violating requirement 1. ∎

The general result (Lamport, Shostak and Pease, 1982; and Pease, Shostak and Lamport, 1980) is that, with oral messages, agreement is possible if and only if n ≥ 3f + 1, by grouping the 3f + 1 nodes into three groups and simulating this three-general argument.

### Why 3f + 1, intuitively, in quorum terms

A quorum-based protocol must be able to proceed after hearing from n − f nodes (the f faulty ones may stay silent). Among those n − f, up to f may be faulty and lying. For two quorums of size n − f to intersect in at least one **honest** node, they must overlap in at least f + 1 nodes:

```
2(n − f) − n ≥ f + 1   ⇒   n ≥ 3f + 1
```

With n = 3f + 1, quorums are 2f + 1 nodes. Compare crash tolerance, where quorums of f + 1 out of 2f + 1 need only overlap in one node, because no node lies.

## 13.3 Signatures change the game

With **signed messages** (each message carries a digital signature that others can verify and no one can forge), a traitor can't misreport what an honest node said, and equivocation becomes detectable when two conflicting signed messages from the same node are compared. Lamport, Shostak and Pease showed that, with signatures, the Generals problem is solvable for any number of traitors in a synchronous system. In partially synchronous systems (the realistic model), Byzantine consensus still needs n ≥ 3f + 1 (Dwork, Lynch and Stockmeyer, 1988), but signatures make protocols simpler and cheaper.

## 13.4 PBFT

**Practical Byzantine Fault Tolerance** (Miguel Castro and Barbara Liskov, OSDI 1999) was the first Byzantine state machine replication protocol efficient enough for real use: its authors built a Byzantine-tolerant NFS file server only a few percent slower than an unreplicated one.

With n = 3f + 1 replicas, one of which is the **primary** for the current **view**:

1. **Pre-prepare:** the primary assigns a sequence number to a client request and broadcasts it.
2. **Prepare:** each replica broadcasts a prepare message agreeing to that assignment. A replica is **prepared** once it has the pre-prepare and 2f matching prepares from others. Prepared certificates from two honest replicas for the same sequence number can't name different requests, because two sets of 2f + 1 overlap in an honest replica.
3. **Commit:** each prepared replica broadcasts commit; once a replica has 2f + 1 commits, it executes the request and replies to the client.
4. The client waits for **f + 1 matching replies**, which guarantees at least one came from an honest replica.

If the primary is faulty (slow or equivocating), replicas time out and run a **view change** to the next primary, carrying forward prepared certificates so committed requests aren't lost.

PBFT's all-to-all prepare and commit phases cost O(n²) messages per request, which limits it to tens of replicas.

## 13.5 Modern BFT and blockchains

### Leader-based BFT with linear communication

- **Tendermint** (Buchman, Kwon and Milosevic, 2018) adapted PBFT-style rounds for blockchain use with rotating proposers; it's used by the Cosmos ecosystem (now as CometBFT).
- **HotStuff** (Yin and colleagues, PODC 2019) uses threshold signatures to aggregate votes so each phase needs only O(n) messages, and pipelines phases; it influenced Meta's Diem project (since discontinued) and later protocols in several blockchains.

### Nakamoto consensus

Bitcoin (Satoshi Nakamoto, 2008) solved a different version of the problem: agreement among an **open, unknown** set of participants, where anyone can join and identities are free (so voting by node count would be defeated by an attacker creating many identities, a **Sybil attack**). Its **proof of work** makes each vote (a block) cost computation; the longest (most-work) chain wins; and agreement is **probabilistic**: a block becomes exponentially less likely to be reversed as more blocks are added after it. Security assumes honest participants control a majority of computing power.

**Proof of stake** replaces computation with economic stake: validators lock up currency and lose it ("slashing") if caught equivocating. Ethereum moved from proof of work to proof of stake in September 2022 ("the Merge"); its consensus combines a BFT-style finality gadget (Casper FFG) with a fork-choice rule.

### How blockchains relate to the rest of this book

A blockchain is a replicated log (Chapter 6 §6.7) maintained by Byzantine consensus among parties that don't trust each other. For data shared within one organisation, or among parties that trust a common operator, a conventional replicated database is far cheaper and faster. The useful question to ask of any proposed blockchain system: *who are the mutually distrusting parties, and why can't they agree on a trusted operator?* If there's no good answer, you don't need Byzantine consensus.

## 13.6 Cheaper defences against arbitrary faults

Most "Byzantine" faults in a data centre are accidents, not attacks. Inexpensive techniques catch most of them:

| Technique | Catches |
|---|---|
| **End-to-end checksums** on data at rest and in transit (application-level, not just TCP's weak 16-bit checksum) | Corruption in memory, disks, networks |
| **Input validation** at every service boundary | Malformed or nonsensical data from buggy peers |
| **Assertions and invariant checks** in production code | Logic errors before they propagate |
| **Scrubbing:** periodically re-reading and verifying stored data | Latent disk errors |
| **Redundant computation** for critical results (compute twice, compare) | Silent CPU errors |
| **Diversity:** different implementations or versions | Common-mode software bugs (at considerable cost) |
| **Authentication and authorisation** between services | Compromised or impersonating peers |

Amazon S3, for example, has described pervasive checksumming and continuous verification of stored data; the 2017 S3 outage write-up and later talks on S3's durability engineering are good reading.

---

## Summary

- Byzantine faults allow arbitrary behaviour, including lying and equivocation. They arise from malice, compromise and silent hardware or software errors.
- Without signatures, agreement with f Byzantine participants needs n ≥ 3f + 1; the three-generals argument shows why one traitor among three defeats any protocol. Quorums of 2f + 1 out of 3f + 1 intersect in an honest node.
- Signatures make equivocation detectable and protocols simpler; in partial synchrony, n ≥ 3f + 1 remains necessary.
- PBFT made Byzantine state machine replication practical, at O(n²) messages; HotStuff and Tendermint reduce communication and suit blockchains.
- Nakamoto consensus handles open membership with proof of work and probabilistic finality; proof of stake uses economic penalties.
- Inside one organisation, use checksums, validation, assertions, scrubbing and authentication rather than full BFT.

## Exercises

This chapter has no exercises. The protocols it describes are worth understanding, but implementing a toy version would teach less than the consensus exercises in Chapter 11. If you want hands-on practice, extend the Chapter 11 model-checking exercise with a node that equivocates, and observe which invariants fail.

## Further reading

- Leslie Lamport, Robert Shostak and Marshall Pease, "The Byzantine Generals Problem", *ACM TOPLAS* (1982).
- Miguel Castro and Barbara Liskov, "Practical Byzantine Fault Tolerance", OSDI (1999).
- Maofan Yin et al., "HotStuff: BFT Consensus with Linearity and Responsiveness", PODC (2019).
- Ethan Buchman, Jae Kwon and Zarko Milosevic, "The Latest Gossip on BFT Consensus" (Tendermint, arXiv 2018).
- Satoshi Nakamoto, "Bitcoin: A Peer-to-Peer Electronic Cash System" (2008).
- Peter H. Hochschild et al., "Cores that Don't Count", HotOS (2021), on silent CPU errors at Google; Harish Dattatraya Dixit et al., "Silent Data Corruptions at Scale" (Meta, arXiv 2021).
