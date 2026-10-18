# TLA+ specifications

Five small formal specifications that go with the book. Each one describes a distributed protocol as a state machine. TLC, a model checker, then explores every reachable state of a small instance and either reports that the stated properties hold or prints a step-by-step counterexample.

| Spec | Chapter topic | What it shows |
|---|---|---|
| `DieHard.tla` | Warm-up | How TLC works, and that a "violation" is a found path |
| `TwoPhaseCommit.tla` | Atomic commit | 2PC never commits on one node and aborts on another; with fairness, it terminates |
| `QuorumIntersection.tla` | Replication and quorums | `R + W > N` makes every read see the latest write; `R + W <= N` does not |
| `LockWithFencing.tla` | Leases and distributed locks | A paused client corrupts storage unless storage checks fencing tokens |
| `RaftElection.tla` | Consensus and leader election | At most one Raft leader per term, and two ways to break that |

Results below were checked on 18 October 2026 with the TLA+ tools v1.8.0 build that prints `TLC2 Version 2026.10.15.145915 (rev: 932d35e)`, on OpenJDK 21.0.12 with 4 cores.

## What TLA+ is

**TLA+** is a language for writing precise descriptions of how a system behaves. Leslie Lamport designed it in the 1990s. The name stands for the *Temporal Logic of Actions*. A TLA+ description is called a **specification** (spec). It is mathematics, not a program: nothing compiles it into a running system. You write a spec to find design errors before, or alongside, writing the code.

The core ideas, all of which appear in `DieHard.tla`:

- **State.** An assignment of values to the spec's **variables**. In the jug puzzle the state is "the small jug holds 3 gallons, the big jug holds 2".
- **Action.** A formula that relates the current state to the next one. Unprimed variables (`big`) are the values now; primed variables (`big'`) are the values after the step. `FillBig == big' = 5 /\ small' = small` is an action.
- **Behaviour.** A sequence of states, each step taken by some action. A spec is usually written as `Spec == Init /\ [][Next]_vars`. Read it as: the first state satisfies `Init`, and every step either satisfies `Next` or leaves `vars` unchanged (a *stuttering* step, which means "nothing visible happened").
- **Nondeterminism.** `Next` is normally a disjunction (`\/`, "or") of actions, often under `\E` ("there exists"). The spec does not say which action happens next. Any of them can. This is how a spec models concurrency, message reordering, message loss, crashes and pauses: by allowing every possibility at once.

Properties come in two kinds:

- **Safety:** "something bad never happens". *No resource manager commits while another aborts. No term has two leaders.* A safety violation always has a finite counterexample: the sequence of steps that reaches the bad state.
- **Liveness:** "something good eventually happens". *Every resource manager eventually decides.* A liveness violation is an infinite behaviour in which the good thing never happens, for example the system stopping forever. Liveness only holds under **fairness** assumptions such as `WF_vars(Next)` (weak fairness), which says that if a step stays possible, one is eventually taken.

An **invariant** is a safety property that is a plain formula over one state, such as `Consistency`. It must be true in every reachable state. A **temporal property** uses temporal operators such as `<>` ("eventually") and `[]` ("always"). `Termination == <>(...)` is one.

### Model checking with TLC

**TLC** is the model checker that ships with the TLA+ tools. Given a spec and a configuration file (`.cfg`) that fixes the constants, TLC does a breadth-first search over every reachable state. It checks each invariant in each state and checks temporal properties over the whole state graph. When a check fails, TLC prints the shortest behaviour that reaches the failure (with one worker thread), labelled action by action.

TLC proves nothing about the unbounded system. It checks one **finite model**: three servers, terms up to 3, at most three writes, and so on. Two facts make this useful anyway:

- **State explosion.** The number of states grows exponentially with the number of processes, messages and counters. `RaftElection` has 24,139 distinct states with 3 servers and `MaxTerm = 3`. Raising `MaxTerm` to 4 gives 646,272 states and a run of about a minute. Removing symmetry reduction gives 143,929. A spec has to be bounded to be checkable.
- **The small-scope hypothesis.** Most design bugs show up in small instances: two clients, three nodes, two terms. Every counterexample in this folder is under 12 steps long. Experience at Amazon and elsewhere is that small models catch the bugs that matter, which is why the constants here are deliberately tiny.

To prove a property for *all* sizes, you write a proof in TLAPS, the TLA+ proof system. That is outside this book.

## Installing

You need Java 11 or newer (`java -version`).

1. **Command line.** Download `tla2tools.jar` from the releases page of the tlaplus repository, <https://github.com/tlaplus/tlaplus/releases> (the v1.8.0 release, or a nightly build). Keep it outside this repository, or put it next to these files as `./tla2tools.jar`. The folder's `.gitignore` keeps the jar, `states/` directories and TLC trace files out of git.
2. **VS Code.** Install the *TLA+* extension (publisher `tlaplus`, extension id `tlaplus.vscode-ide`). It bundles the tools. Open a `.tla` file and run **TLA+: Check model with TLC** from the command palette; it uses the `.cfg` with the same name.

## Running

Run every spec and compare each outcome with the expected one:

```bash
TLA2TOOLS=/path/to/tla2tools.jar ./run_tlc.sh
```

Run only one spec's configurations:

```bash
TLA2TOOLS=/path/to/tla2tools.jar ./run_tlc.sh RaftElection
```

The script copies the specs to a temporary directory and runs TLC there, so no `states/` directory or trace file ever lands in the repository. `WORKERS=auto` uses all cores (the default is 1, which keeps runs deterministic and counterexamples shortest). `KEEP=1` keeps the temporary directory and its full TLC logs. The script exits non-zero only if some result differs from the expectation. A configuration that is meant to fail is reported as `expected violation found`.

To run one model by hand, work in a scratch directory:

```bash
mkdir -p /tmp/tlc && cp *.tla *.cfg /tmp/tlc && cd /tmp/tlc
java -XX:+UseParallelGC -cp /path/to/tla2tools.jar tlc2.TLC \
     -workers auto -deadlock -config LockWithFencing_bad.cfg LockWithFencing.tla
```

`-deadlock` turns **off** TLC's deadlock check. These protocols are allowed to stop. A finished two-phase commit, for example, has no further steps, and by default TLC would report that state as a deadlock.

## The specs and the results observed

| Spec and config | Checks | Expected | Observed (generated / distinct states, search depth, time) |
|---|---|---|---|
| `DieHard.tla` + `DieHard.cfg` | `TypeOK`, `NotSolved` (the big jug never holds 4) | violation | Invariant `NotSolved` violated; 73 / 14, depth 7, 0 s. The 7-state trace is the puzzle's solution |
| `TwoPhaseCommit.tla` + `TwoPhaseCommit.cfg` (3 RMs, `FairSpec`) | `TypeOK`, `Consistency`, and the liveness property `Termination` | pass | No error; 1,146 / 288, depth 11, 0 s |
| `QuorumIntersection.tla` + `QuorumIntersection.cfg` (N=4, R=2, W=3, 3 writes) | `TypeOK`, `QuorumsIntersect`, `ReadSeesLatestWrite` | pass | No error; 3,911 / 511, depth 5, 0 s |
| `QuorumIntersection.tla` + `QuorumIntersection_bad.cfg` (N=4, R=2, W=2) | same | violation | Invariant `QuorumsIntersect` violated; 25 / 25, depth 3, 0 s |
| `LockWithFencing.tla` + `LockWithFencing.cfg` (2 clients, lease 2 ticks, clock to 6, `UseFencing = TRUE`) | `TypeOK`, `NoStaleWrite` | pass | No error; 7,335 / 4,623, depth 19, 0 s |
| `LockWithFencing.tla` + `LockWithFencing_bad.cfg` (`UseFencing = FALSE`) | same | violation | Invariant `NoStaleWrite` violated; 723 / 537, depth 9, 0 s |
| `RaftElection.tla` + `RaftElection.cfg` (3 servers, `MaxTerm = 3`, `Bug = "None"`, symmetry) | `TypeOK`, `ElectionSafety` | pass | No error; 323,516 / 24,139, depth 20, 6 s |
| `RaftElection.tla` + `RaftElection_bad.cfg` (`Bug = "VoteTwice"`) | same | violation | Invariant `ElectionSafety` violated; 31,410 / 7,058, depth 9, 1 s |
| `RaftElection.tla` + `RaftElection_forgetvote_bad.cfg` (`Bug = "ForgetVote"`) | same | violation | Invariant `ElectionSafety` violated; 60,576 / 10,906, depth 10, 2 s |

All numbers come from `run_tlc.sh` with one worker. For a run that stops at a violation, the state counts are how far the search got before it stopped. The whole suite takes about 16 seconds.

### What each spec models

- **`DieHard`.** A 3-gallon jug, a 5-gallon jug and six actions (fill, empty, pour either way). It claims `big # 4` as an invariant, and TLC's counterexample is the shortest solution: fill big, pour into small, empty small, pour, fill big, pour, which leaves 4 in the big jug.
- **`TwoPhaseCommit`.** Lamport's TwoPhase spec. Resource managers (RMs) prepare or abort on their own. The transaction manager (TM) collects `Prepared` messages and commits only when every RM is prepared; it may abort at any time before that. Messages sit in a set that only grows, which covers delay, reordering and duplication.
- **`QuorumIntersection`.** Writes go to any `W` of `N` nodes and reads ask any `R` nodes. `QuorumsIntersect` says the read quorum just used overlaps the latest write's quorum. TLC tries every possible quorum on every operation, so this covers every pair. `ReadSeesLatestWrite` is the consequence that matters: no read returns an old version.
- **`LockWithFencing`.** A lock service grants leases that expire after `LeaseDuration` ticks of a global clock. A client checks its lease, then sends its write (`StartWrite`); the write reaches storage later (`WriteArrives`). A pause is modelled by the client simply taking no steps while the clock ticks and others act. With `UseFencing`, storage rejects writes whose token is lower than the highest it has seen. `NoStaleWrite` says the accepted writes carry non-decreasing tokens: a client whose lease has been superseded can never write after the newer lease holder has. This follows Martin Kleppmann's 2016 argument.
- **`RaftElection`.** Terms, `RequestVote` broadcasts, votes, majorities, and `votedFor` and `currentTerm` kept on stable storage across `Restart`. Messages can be lost, duplicated or delayed. A ghost variable `elected` records every `<<term, server>>` that ever won, and `ElectionSafety` says no term has two winners. The spec leaves out log replication and the log up-to-date check, which election safety does not depend on.

### A counterexample, read step by step

This is the trace from `LockWithFencing_bad.cfg`, trimmed to the variables that change. It is Kleppmann's scenario, found by TLC without being told about it:

```
Error: Invariant NoStaleWrite is violated.
State 2: <Acquire(c1)>       latestToken = 1, clientExpiry[c1] = 2, clock = 0
State 3: <Tick>              clock = 1
State 4: <StartWrite(c1)>    c1 checks: clock 1 < expiry 2, lease valid; write is in flight
State 5: <Tick>              clock = 2            (c1 is paused; its lease has now expired)
State 6: <Acquire(c2)>       latestToken = 2, lockOwner = c2, leaseExpiry = 4
State 7: <StartWrite(c2)>    clientState = (c1 :> "writing" @@ c2 :> "writing")
State 8: <WriteArrives(c2)>  writeLog = <<[writer |-> c2, token |-> 2, latest |-> 2]>>
State 9: <WriteArrives(c1)>  writeLog = << [writer |-> c2, token |-> 2, latest |-> 2],
                                           [writer |-> c1, token |-> 1, latest |-> 2] >>
```

c1 did everything right: it checked its lease before writing. The pause between the check (state 4) and the write's arrival (state 9) is enough for c1's old data to overwrite c2's newer data. With `UseFencing = TRUE`, storage has seen token 2 by state 9, so it rejects c1's token-1 write and the invariant holds.

The other counterexamples, in brief:

- **`QuorumIntersection_bad.cfg`:** `Write({1, 2})` stores version 1 on nodes 1 and 2, then `Read({3, 4})` asks nodes 3 and 4, which share no node with the write. The read returns version 0 although version 1 has completed.
- **`RaftElection_bad.cfg` (`VoteTwice`):** s1 and s2 both time out into term 1 and vote for themselves. Each then receives the other's `RequestVote` and, because of the bug, grants it although it has already voted. s1 becomes leader with votes {s1, s2}, then s2 becomes leader with votes {s2, s1}: two leaders in term 1, without s3 doing anything.
- **`RaftElection_forgetvote_bad.cfg` (`ForgetVote`):** s1 and s2 start term 1. s3 votes for s1, and s1 becomes leader with {s1, s3}. s1 then restarts and, because `votedFor` was not persisted, has forgotten that it voted for itself. It grants s2's request, and s2 becomes leader with {s2, s1}: two leaders in term 1. This is why Raft writes `votedFor` to disk before answering.

## Experiments to try

Each experiment is a small edit followed by a rerun. Do them on a copy, or revert afterwards. The outcomes listed were observed with one worker.

1. **2PC: commit without waiting for every vote.** In `TwoPhaseCommit.tla`, comment out `/\ tmPrepared = RM` in `TMCommit`. TLC reports `Invariant Consistency is violated` after 4 states: `TMCommit` with nobody prepared, `RMChooseToAbort(r1)`, then `RMRcvCommitMsg(r2)`. r1 has aborted and r2 has committed.
2. **2PC: drop fairness.** In `TwoPhaseCommit.cfg`, change `SPECIFICATION FairSpec` to `SPECIFICATION Spec`. TLC reports `Temporal property Termination was violated`. The trace ends with `Stuttering`: the TM has aborted and r2 is prepared, and then the system simply stops forever. Without a fairness assumption, "do nothing" is a legal behaviour, so no liveness property can hold.
3. **Quorums: a write-heavy setting that is too small.** In `QuorumIntersection.cfg`, set `R = 1` (with `W = 3`, `N = 4`, so `R + W = N`). TLC finds `Write({1, 2, 3})` then `Read({4})`. Now try `N = 5, R = 3, W = 3`: it passes (66,121 generated, 5,151 distinct states).
4. **Fencing is not mutual exclusion.** Add `INVARIANT OnlyLatestHolderWrites` to `LockWithFencing.cfg`. This stronger property says that every accepted write comes from the *current* lease holder. Even with fencing it fails, after 7 states: c1 checks its lease, pauses, c2 acquires token 2, and c1's token-1 write arrives *before* c2 has written anything. Storage has never seen token 2, so it accepts. The data is still safe, because c1 can never write after c2 has, but the experiment shows exactly what a fencing token buys and what it does not.
5. **A longer lease does not fix it.** In `LockWithFencing_bad.cfg`, set `LeaseDuration = 4`. The violation remains (11 states): c1 just pauses for longer. No timeout value is safe against an unbounded pause.
6. **Raft: "half" is not a majority.** In `RaftElection.tla`, change `>` to `>=` in `IsMajority`. In `RaftElection.cfg`, use `Server = {s1, s2, s3, s4}` and `MaxTerm = 2`. TLC finds two leaders in term 1 after 9 states: s1 wins with {s1, s3} and s2 wins with {s2, s4}. Two halves of four servers need not overlap, which is the same arithmetic as experiment 3.
7. **Check that the model is not vacuous.** A spec that can never elect anyone satisfies `ElectionSafety` trivially. In `RaftElection.cfg`, replace `ElectionSafety` with `NoLeaderEver`. TLC "fails" after 5 states (s1 times out, s2 votes, s1 becomes leader), which proves that leaders really are elected in the model. Do this sanity check on every spec you write.
8. **Feel the state explosion.** In `RaftElection.cfg`, remove the `SYMMETRY` line: distinct states rise from 24,139 to 143,929 (1,928,953 generated, 10 s with 4 workers). Restore it and set `MaxTerm = 4`: 646,272 distinct states (10,597,829 generated, depth 26, 56 s with 4 workers).
9. **An unsolvable puzzle.** In `DieHard.tla`, replace every `5` with `6`. TLC now *passes* (6 distinct states): with jugs of 3 and 6 gallons, every reachable amount is a multiple of 3.

## Reading list

- Leslie Lamport, *Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers*, Addison-Wesley, 2002. The reference book, free from Lamport's website: <https://lamport.azurewebsites.net/tla/book.html>.
- Hillel Wayne, *Learn TLA+*, <https://learntla.com>. A practical online tutorial, and the gentlest way in.
- Chris Newcombe, Tim Rath, Fan Zhang, Bogdan Munteanu, Marc Brooker and Michael Deardeuff, "How Amazon Web Services Uses Formal Methods", *Communications of the ACM* 58(4), April 2015. Shows engineers using TLA+ on DynamoDB, S3 and other services, finding bugs whose traces were 35 steps long.
- Leslie Lamport, *The TLA+ Video Course*, <https://lamport.azurewebsites.net/video/videos.html>. The source of the DieHard and TwoPhase examples.
- Diego Ongaro and John Ousterhout, "In Search of an Understandable Consensus Algorithm", USENIX ATC 2014. Raft, with a full TLA+ spec in Ongaro's PhD thesis (Stanford, 2014).
- Martin Kleppmann, "How to do distributed locking", 8 February 2016, <https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html>.
- Jim Gray and Leslie Lamport, "Consensus on Transaction Commit", *ACM Transactions on Database Systems* 31(1), 2006. The paper behind the TwoPhase spec.
