# Logical clocks (Chapter 3)

## The problem

Two servers each log an event at "10:00:00.003". Which happened first? Physical clocks on different machines disagree by milliseconds or more, so wall-clock timestamps cannot be trusted to order events, and ordering them wrongly breaks things: a reply appears before the question, a delete is applied before the insert it was meant to remove.

What we usually need is not the true time but **causality**: could event *a* have influenced event *b*? Logical clocks answer that question from the messages processes exchange, without any shared clock.

## Terms

- **Event:** something a process does: a local step, sending a message, or receiving one.
- **Happened-before** (written *a → b*, Lamport 1978): *a* comes before *b* on the same process, or *a* is the send of a message and *b* its receipt, or there is a chain of such steps from *a* to *b*.
- **Concurrent** (*a ∥ b*): neither *a → b* nor *b → a*. Neither event could have influenced the other.
- **Lamport clock:** one counter per process. Increment before each event; stamp messages with it; on receipt, jump to `max(local, received) + 1`.
- **Clock condition:** *a → b* implies *L(a) < L(b)*. Lamport clocks satisfy it. The converse does not hold.
- **Vector clock:** one counter *per process* held at every process. Entry *i* counts the events of process *i* this process has heard about. On receipt, take the element-wise maximum, then increment your own entry.
- **Vector order:** *V(a) < V(b)* when every entry of *V(a)* is ≤ the matching entry of *V(b)* and they differ. Vector clocks give an exact characterisation: *a → b* iff *V(a) < V(b)*, and *a ∥ b* iff the vectors are incomparable.
- **Hybrid logical clock (HLC):** a pair *(l, c)*, where *l* is the largest physical clock reading this process has heard of and *c* is a counter that breaks ties. HLCs satisfy the clock condition and stay close to physical time, so they can serve as timestamps in databases (CockroachDB and YugabyteDB use them).
- **Clock skew:** the difference between two machines' clocks at the same instant.

## How it works

`clocks.py`:

| Name | What it does |
|---|---|
| `LamportClock` | `tick()`, `send()`, `receive(t)` |
| `VectorClock(pid, n)` | `tick()`, `send()`, `receive(v)`; returns tuples |
| `compare(a, b)` | `"before"`, `"after"`, `"equal"` or `"concurrent"` |
| `happened_before(a, b)` | `compare(a, b) == "before"` |
| `simulate(n, steps, seed, p_send, p_local)` | A random run with reordering channels; every event records its Lamport and vector timestamps |
| `ground_truth(execution)` | Happened-before from the event graph (program-order and message edges, transitive closure), computed with no clocks at all |
| `HybridLogicalClock(physical)` | `now()`, `send()`, `receive((l, c))` |
| `simulate_hlc(n, steps, seed, max_skew, ...)` | A run where each process's physical clock is offset by up to `max_skew` from true time |

The tests compare clock verdicts against `ground_truth`, which is computed independently. That is the point of the example: the clock rules are checked against the definition, not against themselves.

## Run it

```bash
python3 clocks.py          # demo
python3 -m unittest -v     # 11 tests
```

The demo prints a 3-process run with seed 7. Of its 136 pairs of events, 80 are causally related and 56 concurrent. Lamport timestamps differ for 47 of the 56 concurrent pairs, so the Lamport order makes them *look* ordered; for example `b1` (L=1) and `a2` (L=2) are concurrent. Vector clocks classify all 136 pairs correctly. In the HLC run (skew up to ±50 units), 4 of 14 messages arrive with a physical timestamp no later than their send, an apparent violation of causality, while HLC orders all 14 correctly, and *l* never drifts more than 35 units ahead of the local physical clock.

## Experiments to try

1. **Find concurrency Lamport hides.** In `_demo()`, change the seed and count how often concurrent pairs have equal Lamport times versus different ones. Which is more common, and why does that make Lamport order dangerous for conflict detection?
2. **Break the receive rule.** In `LamportClock.receive`, drop the `+ 1` (so `self.time = max(...)`). Run the tests: which one fails, and which pair of events does it report?
3. **Forget the merge.** In `VectorClock.receive`, replace the element-wise maximum with just `self.tick()`. `test_vector_clocks_match_ground_truth_exactly` now reports pairs the vector clock calls concurrent that are actually causal.
4. **Turn up the skew.** Call `simulate_hlc(max_skew=500)` and print the largest `c`. How large does the logical counter get when one clock is far ahead? This is why production HLCs refuse messages from clocks that are too far in the future.
5. **Count the cost.** Vector clocks grow with the number of processes. Run `simulate(n=50, steps=500)` and look at one timestamp. Real systems prune entries for departed nodes or bound the vector in other ways.

## Limitations

- Processes are fixed in number; vector clocks here cannot add or remove processes. Real systems use maps keyed by node ID and prune entries.
- Channels reorder but never lose messages, and every message is delivered before the run ends.
- The HLC simulation uses fixed clock offsets; real clocks also drift and step backwards when NTP corrects them.
- Lamport timestamps are not made unique here; ties are usually broken by process ID to give a total order.
