# Chapter 5. Reasoning About Correctness: Invariants, TLA+ and Model Checking

> "Writing is nature's way of letting you know how sloppy your thinking is."
> — Dick Guindon, quoted by Leslie Lamport

## What you will learn

- Why testing alone rarely finds distributed-systems bugs, and what to add.
- How to describe a system as a state machine: states, actions and behaviours.
- How to state and prove invariants, including inductive invariants, with worked examples.
- How liveness is argued, and what fairness means.
- How explicit-state model checking works, by building one in Python.
- How to write and check TLA+ specifications with the TLC model checker.
- How industry uses formal methods (Amazon, Microsoft, MongoDB, Datadog and others), and how to start on a real project.

This chapter is the most formal in the book. The rest of the book uses its vocabulary (state, action, invariant, inductive, safety, liveness, fairness, counterexample), so it's worth reading even if you skim the proofs.

---

## 5.1 Why testing isn't enough

A distributed protocol's behaviour depends on the **interleaving** of events: which message arrives first, which node crashes when, which timeout fires before which reply. The number of interleavings grows exponentially with the number of events. Conventional tests explore a tiny, biased sample of them (usually the "happy path" timing of a fast, reliable test network).

The bugs that matter most live in rare interleavings: a leader that pauses for garbage collection exactly while a new leader is elected; a message delayed across a crash and restart; a retry that arrives after the operation it repeats was compensated. These bugs:

- rarely show up in tests;
- show up in production at scale, where rare events happen daily;
- are often hard to reproduce, because the interleaving is gone by the time you investigate.

Three complementary techniques address this, in increasing order of rigour:

1. **Randomised and deterministic simulation testing** explores many interleavings with controlled randomness (Chapter 23).
2. **Model checking** explores *all* interleavings of a small model of the system, automatically.
3. **Proof** shows a property holds for all interleavings of the full (unbounded) model.

This chapter covers the last two. In practice, model checking gives the best ratio of value to effort for most engineering teams.

## 5.2 Systems as state machines

Formal reasoning starts by describing the system as a **state machine**:

- A **state** is an assignment of values to all variables: every node's local variables, plus the network (the multiset of messages in flight).
- An **initial condition** describes the possible starting states.
- **Actions** (or **transitions**) describe how one state can change into another. Each action has an **enabling condition** (when it may happen) and an **effect** (what changes). In a distributed system, typical actions are "node i sends a message", "the network delivers message m to node j", "the network drops message m", "node k crashes", "node k's timer fires".
- A **behaviour** is a sequence of states s₀, s₁, s₂, … where s₀ satisfies the initial condition and each step is either an action or a "stuttering" step in which nothing changes.

**Concurrency is modelled as nondeterminism**: at each step, *any* enabled action may happen next. The model doesn't say which. Network delay, reordering and loss all fall out naturally: a message sits in the network variable until some delivery or drop action takes it out, and any number of other actions can happen first.

### Example: a counter incremented by two processes

Two processes each run `x := x + 1` as two separate steps: read x into a local register, then write register + 1 back. State: (x, pc₁, r₁, pc₂, r₂), with program counters pc ∈ {read, write, done}.

```
Init:      x = 0, pc₁ = pc₂ = read
Read(i):   pcᵢ = read  → rᵢ' = x,      pcᵢ' = write
Write(i):  pcᵢ = write → x' = rᵢ + 1,  pcᵢ' = done
```

(A primed variable means "its value in the next state".) The behaviour Read(1), Read(2), Write(1), Write(2) ends with x = 1: the classic **lost update**. A property "when both are done, x = 2" is violated. A model checker finds this by enumerating all interleavings (there are only six here).

## 5.3 Invariants

An **invariant** is a predicate on states that is true in every reachable state. Invariants are how safety properties are stated and proved.

Examples from later chapters:

- *Election safety (Raft):* for every term t, at most one node is leader in term t.
- *Quorum intersection:* every read quorum shares at least one node with every write quorum.
- *Atomicity (two-phase commit):* it's never the case that one participant has committed while another has aborted.
- *Conservation (bank transfers):* the sum of all balances plus money in flight is constant.

### Inductive invariants

How do you prove that an invariant holds in every reachable state, when there may be infinitely many? By induction over behaviours:

1. **Base:** the invariant holds in every initial state.
2. **Step:** if the invariant holds in a state s, and some action takes s to s', then it holds in s'.

An invariant for which both steps can be proved is called **inductive**. The catch: most interesting invariants aren't inductive on their own. The step fails because there are unreachable states that satisfy the invariant but from which an action leads to a violation. You must **strengthen** the invariant by adding conjuncts that rule out those unreachable states, until the conjunction is inductive. Finding the strengthening is the creative part of a proof, and it usually reveals *why* the protocol works.

### ◆ Formal: a worked example

Consider a simple mutual-exclusion protocol with a token. Processes 1..n; a variable `holder` names the process holding the token, or is `none` while the token is in a message in flight. Each process has `pc[i] ∈ {idle, critical}`.

```
Init:     holder = 1, pc[i] = idle for all i, network = ∅
Enter(i): holder = i ∧ pc[i] = idle      → pc[i]' = critical
Exit(i):  pc[i] = critical               → pc[i]' = idle
Pass(i,j): holder = i ∧ pc[i] = idle     → holder' = none, network' = network ∪ {token→j}
Recv(j):  token→j ∈ network              → holder' = j, network' = network \ {token→j}
```

**Safety property (mutual exclusion):** `MutEx ≜ ∀ i ≠ j: ¬(pc[i] = critical ∧ pc[j] = critical)`.

Is MutEx inductive? Take a state with holder = 1, pc[2] = critical, all other processes idle, and empty network. MutEx holds. Now Enter(1) is enabled and leads to two processes in the critical section. This state is unreachable, but nothing in MutEx rules it out, so MutEx isn't inductive.

Strengthen it:

```
Inv ≜ ∧ ∀ i: pc[i] = critical ⇒ holder = i                       (only the holder is critical)
      ∧ (holder = none) ⇔ (|network| = 1)                         (exactly one token in total)
      ∧ |network| ≤ 1
```

*Base:* holder = 1, nobody critical, network empty. All three conjuncts hold.

*Step:* check each action, assuming Inv in s.
- Enter(i): requires holder = i, sets pc[i] = critical; conjunct 1 holds for i, and is unchanged for others; network unchanged.
- Exit(i): sets pc[i] = idle; conjunct 1 only gets easier.
- Pass(i, j): requires pc[i] = idle and holder = i. By conjunct 2 the network is empty; afterwards holder = none and the network has one token, so conjuncts 2 and 3 hold. Could some other process k be critical? By conjunct 1 in s, pc[k] = critical ⇒ holder = k = i, but pc[i] = idle, so no process is critical, and conjunct 1 holds vacuously with holder = none.
- Recv(j): requires the token in the network, so holder = none (conjunct 2); afterwards holder = j and the network is empty. No process was critical (conjunct 1 with holder = none), so conjunct 1 holds.

So Inv is inductive. And Inv implies MutEx: if i and j were both critical, conjunct 1 gives holder = i and holder = j, so i = j. ∎

Notice what the strengthening captured: *there is exactly one token, and only the process holding it may be critical.* That's the real reason the protocol works, and stating it precisely is the main value of the exercise, even if you never write the proof out.

## 5.4 Liveness and fairness

Liveness properties ("every request is eventually answered", "a leader is eventually elected") can't be proved by invariants alone. They need:

- a **progress measure**: something that decreases (or increases) with each relevant step and is bounded, so the good thing must happen eventually; and
- **fairness assumptions**: without them, the model allows behaviours in which the system just stutters forever, or in which an enabled action is ignored forever.

**Weak fairness** of an action A: if A is **continuously** enabled from some point on, then A eventually happens. **Strong fairness**: if A is enabled **infinitely often** (even if not continuously), it eventually happens. A message that sits in the network forever, with its delivery action continuously enabled, is delivered under weak fairness of delivery. A process that keeps retrying through a flaky link needs strong fairness to be guaranteed to get through.

In distributed systems, liveness proofs also need a timing assumption, because of FLP (Chapter 4). A typical statement: "if, after some time, messages between a majority of nodes are delivered within Δ and no further crashes occur, then a leader is elected within a bounded time". Model checkers can check liveness properties under fairness, but it's more expensive and subtler than checking invariants; most industrial use of model checking focuses on safety.

## 5.5 Explicit-state model checking

An **explicit-state model checker** enumerates every reachable state of a finite model and checks the invariant in each. The core algorithm is a breadth-first search:

```python
from collections import deque

def check(initial_states, next_states, invariant):
    """next_states(s) yields (action_name, s2). States must be hashable."""
    parent = {s: None for s in initial_states}
    queue = deque(initial_states)
    while queue:
        s = queue.popleft()
        if not invariant(s):
            return counterexample(parent, s)       # shortest path from an initial state
        for action, s2 in next_states(s):
            if s2 not in parent:
                parent[s2] = (s, action)
                queue.append(s2)
    return None                                    # invariant holds in all reachable states
```

That's genuinely most of it. Breadth-first search has a valuable property: the first violation found is reached by a **shortest** trace, so counterexamples are as short as possible, which makes them easy to understand.

### The state-explosion problem

The number of reachable states grows exponentially with the number of processes, messages and values. Model checking is feasible because of the **small-scope hypothesis** (Daniel Jackson): most bugs show up in small instances: two or three nodes, a couple of messages, values from a set of two or three. You check a small model exhaustively rather than a large one partially. Techniques to push the boundary further:

- **Symmetry reduction:** treat states that differ only by renaming nodes as the same.
- **Bounding:** limit terms, log lengths, message counts or retries.
- **Abstraction:** model only what matters to the property (a "value" can be one of {v1, v2}, not any string).
- **State hashing and disk-based storage**, as in TLC.

[`examples/model-checker/`](../examples/model-checker/) is a complete explicit-state model checker in about a hundred lines of Python. It includes models of a racy check-then-set lock (it finds the race), Peterson's mutual-exclusion algorithm (it verifies it), a lease-based lock without fencing tokens (it finds a stale write by a paused client) and with them (verified), and two-phase commit.

## 5.6 TLA+

**TLA+** is a specification language created by Leslie Lamport in the 1990s, based on the Temporal Logic of Actions. It describes systems exactly as in §5.2: variables, an initial predicate `Init`, a next-state relation `Next` (a disjunction of actions), and properties. Its main tool is **TLC**, an explicit-state model checker; there's also **Apalache**, a symbolic model checker using SMT solvers, and **TLAPS**, a proof system for machine-checked proofs.

A minimal TLA+ specification of the two-process counter from §5.2:

```tla
---------------------------- MODULE Counter ----------------------------
EXTENDS Naturals
VARIABLES x, pc, r
Procs == {1, 2}

Init == x = 0 /\ pc = [i \in Procs |-> "read"] /\ r = [i \in Procs |-> 0]

Read(i)  == /\ pc[i] = "read"
            /\ r' = [r EXCEPT ![i] = x]
            /\ pc' = [pc EXCEPT ![i] = "write"]
            /\ UNCHANGED x

Write(i) == /\ pc[i] = "write"
            /\ x' = r[i] + 1
            /\ pc' = [pc EXCEPT ![i] = "done"]
            /\ UNCHANGED r

Next == \E i \in Procs : Read(i) \/ Write(i)

AllDoneMeansTwo == (\A i \in Procs : pc[i] = "done") => x = 2
=========================================================================
```

Reading guide: `/\` is "and", `\/` is "or", `\E` is "there exists", `[r EXCEPT ![i] = x]` is "the function r with entry i replaced by x", and `UNCHANGED x` means `x' = x`. Checking `AllDoneMeansTwo` as an invariant with TLC produces a four-step counterexample: both processes read 0, then both write 1.

### What the book's specifications check

[`examples/tla/`](../examples/tla/) contains specifications you can run with TLC, each with a configuration that passes and (where instructive) one that fails:

| Specification | Property | Chapter |
|---|---|---|
| `DieHard` | A gentle first spec: TLC "finds a bug" that is actually the puzzle's solution | 5 |
| `TwoPhaseCommit` | Consistency: no participant commits while another aborts | 9 |
| `QuorumIntersection` | Read and write quorums intersect iff R + W > N | 6 |
| `LockWithFencing` | With fencing tokens checked by storage, accepted writes carry non-decreasing tokens, so a paused old lock holder can never overwrite a newer holder's write; with `UseFencing = FALSE`, TLC finds that stale write in 9 states | 12 |
| `RaftElection` | Election safety: at most one leader per term (24,139 distinct states with three servers and terms up to 3); variants that let a node vote twice, or forget its vote on restart, are refuted | 11 |

The folder's README records the exact TLC results (states found, depth) and shows counterexample traces.

### Industrial use

- **Amazon Web Services:** "How Amazon Web Services Uses Formal Methods" (Newcombe and colleagues, *Communications of the ACM*, 2015) reported using TLA+ on DynamoDB, S3, EBS and internal lock managers since 2011, finding serious bugs, some needing traces of 35 steps, that design reviews, code review and testing had missed. AWS has since described further use of formal methods and lightweight verification across services, including the S3 ShardStore work (Bornholt and colleagues, SOSP 2021).
- **Microsoft:** TLA+ for Azure Cosmos DB's consistency levels and other services; the P language for modelling and testing asynchronous systems.
- **MongoDB:** TLA+ specifications of its replication protocol and conformance checking between specification and implementation.
- **Others:** Elastic, CockroachDB, Datadog, Intel (cache coherence) and many more have published uses of TLA+ or related tools.

## 5.7 Using formal methods on a real project

You don't need to verify everything. Practical guidance:

1. **Pick the scary part.** The replication protocol, the failover logic, the lock, the cross-service workflow with compensations. Not the CRUD endpoints.
2. **Write the invariants in English first.** "An acknowledged write is never lost." "No two leaders in one term." Teams often find disagreements about the intended behaviour at this stage, which is valuable in itself.
3. **Model the design, not the code.** Abstract away everything the property doesn't depend on. A first useful spec is often under 200 lines.
4. **Model the environment's nastiness explicitly:** message loss, duplication, reordering, crashes, restarts that lose volatile state, clock jumps.
5. **Check small configurations exhaustively.** Two or three nodes, a couple of operations.
6. **Read every counterexample.** Either the design is wrong, the property is wrong, or the model is wrong. All three are useful findings.
7. **Keep the spec next to the code** and update it when the design changes. Some teams check implementation traces against the spec (trace validation) or generate tests from it.
8. **Combine with simulation testing** (Chapter 23): the model checker checks the design; deterministic simulation checks the implementation.

---

## Summary

- Distributed-systems bugs live in rare interleavings that conventional tests seldom reach. Model checking and proof explore all interleavings of a model.
- Describe the system as a state machine: states (including the network), an initial condition, and nondeterministic actions. Concurrency, loss and reordering are modelled as nondeterministic choice.
- Safety is proved with invariants. Most useful invariants must be strengthened until they're inductive, and the strengthening usually explains why the protocol works.
- Liveness needs progress arguments, fairness assumptions and (because of FLP) timing assumptions.
- Explicit-state model checking is breadth-first search over reachable states, producing shortest counterexamples. The small-scope hypothesis makes small models effective.
- TLA+ with TLC is the most widely used industrial tool; AWS, Microsoft, MongoDB and others report finding bugs that review and testing missed.
- Apply formal methods to the riskiest parts of a design, starting from invariants written in plain language.

## Exercises

See [`exercises/05-formal-reasoning.md`](../exercises/05-formal-reasoning.md).

## Further reading

- Leslie Lamport, *Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers* (Addison-Wesley, 2002; free PDF from lamport.azurewebsites.net).
- Hillel Wayne, *Practical TLA+* (Apress, 2018) and the free online guide *Learn TLA+* (learntla.com).
- Chris Newcombe et al., "How Amazon Web Services Uses Formal Methods", *Communications of the ACM* (2015).
- James Bornholt et al., "Using Lightweight Formal Methods to Validate a Key-Value Storage Node in Amazon S3", SOSP (2021).
- Daniel Jackson, *Software Abstractions: Logic, Language, and Analysis* (revised edition, MIT Press, 2012), on the small-scope hypothesis and Alloy.
- Leslie Lamport, "The TLA+ Video Course" (lamport.azurewebsites.net/video/videos.html).
- Murat Demirbas's blog *Metadata* (muratbuffalo.blogspot.com), for accessible discussions of distributed-systems papers and TLA+ models.
