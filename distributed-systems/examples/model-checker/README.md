# A tiny explicit-state model checker (Chapter 5)

## The problem

Concurrent and distributed algorithms fail in rare interleavings: two processes that each check a flag and then set it, a client that pauses for a few seconds at exactly the wrong moment, a coordinator that commits slightly too early. Testing samples a handful of interleavings. A **model checker** tries *all* of them, for a small configuration, and when something goes wrong it hands you the exact sequence of steps that leads there.

This folder is a model checker in about 120 lines of Python, plus seven small models. It is the same idea as TLC, the checker for TLA+ (see `../tla/` and Chapter 5), stripped to its core so you can read every line.

## Terms

- **State:** a snapshot of every variable in the system: each process's program counter, every shared flag, every message in flight. Here a state is an immutable Python `NamedTuple`, so it can be hashed and stored in a set.
- **Initial states:** the states the system may start in.
- **Next-state relation:** for a given state, every step the system *could* take next. Each step has an **action** name (for example `"P0: sets lock"`) and leads to a new state. Non-determinism (which process runs next, whether a message is lost) shows up as several successors.
- **Reachable state:** any state you can get to from an initial state by taking steps.
- **Invariant:** a predicate that must hold in every reachable state, such as "at most one process is in the critical section". An invariant is a **safety property**: it says nothing bad ever happens.
- **Liveness property:** something good eventually happens ("every request is eventually answered"). Checking liveness needs cycle detection and fairness assumptions. **It is out of scope here**; TLC does it, this checker does not.
- **Counterexample (trace):** a path from an initial state to a state that breaks an invariant.
- **Explicit-state checking:** enumerating states one by one (as here), as opposed to *symbolic* checking, which reasons about sets of states with formulas.
- **State-space explosion:** the number of reachable states grows exponentially with the number of processes and the size of each variable. That is why models are kept tiny: two clients, three participants, time up to 3.

## How it works

`checker.check(model)` runs a **breadth-first search (BFS)**:

1. Put every initial state in a queue and in the `parent` table.
2. Take a state from the front of the queue and generate its successors.
3. For each successor not yet in `parent`, record how we reached it (previous state and action), check every invariant, and add it to the queue.
4. On the first violation, walk the `parent` links back to an initial state. That is the counterexample.

Because BFS explores states in order of distance from the start, the first violation found is reached by a **shortest** trace, which makes counterexamples as easy to read as they can be. The `parent` table doubles as the seen set: hashing immutable states means each state is explored once, however many paths lead to it.

The `Result` reports `states` (distinct states discovered), `transitions` (successor edges examined), `depth` (longest shortest path), `terminal_states` (states with no successors, either finished or deadlocked) and, on failure, `violated` and `trace`.

## The models (`models.py`)

| Model | Invariant | Result | States | Shortest trace |
|---|---|---|---|---|
| `naive-mutex`: read the flag, then set it | MutualExclusion | **FAIL** | 16 (when found) | 6 steps |
| `peterson`: Peterson's algorithm, 2 processes | MutualExclusion | PASS | 20 | n/a |
| `peterson-swapped`: Peterson with `turn` written before `flag` | MutualExclusion | **FAIL** | 27 (when found) | 6 steps |
| `lease-no-fencing`: lease lock, storage accepts every write | WritesInLeaseOrder | **FAIL** | 154 (when found) | 8 steps |
| `lease-fencing`: storage rejects tokens lower than one seen | WritesInLeaseOrder | PASS | 166 | n/a |
| `two-phase-commit`: 3 participants | Atomicity | PASS | 62 | n/a |
| `two-phase-commit-majority`: coordinator commits on a majority of yes votes | Atomicity | **FAIL** | 71 (when found) | 5 steps |

For a failing model, the state count is how many states BFS had discovered when it stopped. Two-phase commit grows as expected with participants: 22, 62, 178 and 518 states for 2, 3, 4 and 5 participants (roughly ×3 per participant, since each has four local states, constrained by the coordinator).

### The naive mutex race

```
 0. Init                     pc=['idle', 'idle'] locked=False
 1. P0: wants lock           pc=['check', 'idle'] locked=False
 2. P0: sees lock free       pc=['set', 'idle'] locked=False
 3. P1: wants lock           pc=['set', 'check'] locked=False
 4. P1: sees lock free       pc=['set', 'set'] locked=False
 5. P0: sets lock            pc=['crit', 'set'] locked=True
 6. P1: sets lock            pc=['crit', 'crit'] locked=True
```

Both processes read `locked == False` before either writes it. This is a **check-then-act** (time-of-check to time-of-use) race. Real locks use an atomic test-and-set or compare-and-swap so that the check and the write are one indivisible step.

### Peterson's algorithm

Peterson (1981) gets mutual exclusion from plain reads and writes: set `flag[i] = true`, then `turn = j` (politely give way), then wait until `flag[j]` is false or `turn == i`. The checker explores all 20 reachable states and finds no violation and no deadlock. Swap the two writes and it fails in 6 steps: P1 can enter while P0 has set `turn` but not yet `flag`, and P0 then enters because P1's later write to `turn` let it through. The order of two innocent-looking assignments is the whole algorithm. (On real hardware Peterson also needs memory barriers, because CPUs reorder writes; the model assumes sequentially consistent memory.)

### The lease and the paused client

This is the scenario from Kleppmann's *Designing Data-Intensive Applications*, chapter 8. A **lease** is a lock that expires after a fixed time, so a crashed holder cannot block everyone for ever. A **fencing token** is a number that increases every time the lock server grants a lease; the storage service remembers the highest token it has accepted and rejects any lower one.

```
 0. Init                          now=0 lease_until=0 C0=idle/t0 C1=idle/t0 writes=[]
 1. C0: acquires lease (token 1)  now=0 lease_until=2 ...
 2. Clock ticks                   now=1 ...
 3. C0: checks lease: valid       now=1 ... C0=ready/t1
 4. Clock ticks                   now=2 ...           <- C0 is paused (GC, VM migration)
 5. C1: acquires lease (token 2)  now=2 lease_until=4 ...
 6. C1: checks lease: valid
 7. C1: write (token 2) accepted  writes=[2]
 8. C0: write (token 1) accepted  writes=[2, 1]       <- stale write lands last
```

C0 checked its lease and *then* paused; by the time it wrote, the lease had expired and C1 held it. No amount of checking on the client fixes this, because the pause can always fall between the check and the write. With fencing, step 8 becomes `C0: write (token 1) REJECTED` and the invariant holds in all 166 reachable states.

The invariant "storage applies writes in lease order" uses the tokens as **ghost variables** in the unfenced model: the checker can see them even though the storage ignores them.

### Two-phase commit

The model follows Lamport's TLA+ `TwoPhase` specification in spirit: participants vote yes (become *prepared*) or no (abort on their own), the coordinator commits only when all are prepared and may abort at any time before that, and participants learn the decision. Atomicity means no participant commits while another aborts. The buggy variant commits on a majority; the trace is: RM0 votes yes, RM1 votes yes, RM2 votes no, coordinator commits, RM0 commits. See `../transactions/` for a 2PC implementation with crashes and recovery logs.

## Run it

```bash
python3 models.py                                  # check every model
python3 models.py lease-no-fencing lease-fencing   # check some
python3 -m unittest -v                             # 15 tests
```

## Experiments to try

1. **Three processes.** In `models.py`, change `MODELS["naive-mutex"]` to `lambda: naive_mutex_model(3)`. The trace is still 6 steps, since only two processes are needed to collide, but the state count at the point of discovery rises from 16 to 45.
2. **Make the check atomic.** In `naive_mutex_model`, merge "sees lock free" and "sets lock" into one action that goes straight from `check` to `crit` and sets `locked=True`. The model now passes: this is test-and-set.
3. **Break Peterson differently.** In the `wait` branch, replace `(not s.flag[j] or s.turn == i)` with just `s.turn == i`. The checker still says PASS (12 states, no terminal states), yet the algorithm is now broken: processes must strictly alternate, so P0 waits for ever if P1 stops wanting the lock. That is a **liveness** failure (starvation), and a safety-only checker cannot see it. This is the clearest argument for why TLC also checks liveness.
4. **Longer leases do not help.** Call `lease_lock_model(fencing=False, lease=3, max_time=5)`. The bug is still there (9 steps, 312 states at discovery) because the pause can be any length.
5. **Fencing equal tokens.** In the fenced write, change `c.token < s.max_token_seen` to `c.token <= s.max_token_seen`. Nothing breaks here because each client writes once; think about why a client writing twice under one lease would now be rejected the second time.
6. **Grow two-phase commit.** Run `check(two_phase_commit_model(6))` and `(7)`: 1,522 and 4,502 states, roughly tripling each time. That is state-space explosion in miniature.
7. **Truncate the search.** `check(lease_lock_model(fencing=False), max_states=10)` reports `PASS (search truncated)` for a model we know is broken. A truncated search that found nothing proves nothing.

## Limitations

- Safety only. Liveness ("a process that wants the lock eventually gets it") needs cycle detection under fairness assumptions and is out of scope.
- A model is not the code. The checker proves properties of the model you wrote, for the bounds you chose (two clients, time up to 3). Bugs that need three clients or a longer run stay hidden in a smaller model; this is the **small scope hypothesis**: most bugs show up in small configurations, but not all.
- No symmetry reduction or partial-order reduction, so state counts are larger than TLC's for the same model.
- States must be immutable and hashable. A mutable list inside a state silently breaks the seen set; use tuples.
- Messages and failures are modelled only as far as each model includes them (the 2PC model abstracts messages away entirely).

## Chapter

Chapter 5 (Specifying and model checking). The lease model also appears in Chapter 8's discussion of clocks and process pauses, and the 2PC model in Chapter 9 (Transactions across services).

## References

- G. L. Peterson, "Myths About the Mutual Exclusion Problem", *Information Processing Letters* 12(3), 1981.
- L. Lamport, *Specifying Systems*, Addison-Wesley, 2002 (TLA+ and TLC; the `TwoPhase` example).
- M. Kleppmann, *Designing Data-Intensive Applications*, O'Reilly, 2017, chapter 8 (leases and fencing tokens).
- D. Jackson, *Software Abstractions*, MIT Press, 2006 (the small scope hypothesis).
