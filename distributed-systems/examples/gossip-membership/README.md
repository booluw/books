# Gossip and failure detection (Chapter 2)

## The problem

A cluster of hundreds of nodes needs to share small facts: who is a member, who has crashed, what the latest configuration is. Sending every fact from one coordinator to everyone makes that coordinator a bottleneck and a single point of failure. Having every node tell every other node costs N² messages.

**Gossip** solves the spreading problem cheaply: each round, every node talks to one random peer. Information spreads like an epidemic and reaches all N nodes in about log N rounds, even when messages are lost.

Spreading news of a crash raises the harder question: how does anyone *know* a node has crashed? Over an asynchronous network a crashed node and a slow one look the same: both are silent. A **failure detector** guesses, and every guess trades speed against mistakes. This example measures that trade-off.

## Terms

- **Gossip protocol** (epidemic protocol): nodes exchange information with randomly chosen peers in periodic **rounds**.
- **Push:** a node that knows the rumour sends it to a random peer. **Pull:** a node that does not know asks a random peer. **Push-pull:** each pair exchanges in both directions.
- **Dissemination time:** rounds until every node knows.
- **Failure detector:** a component that outputs which processes it *suspects* have crashed. It may be wrong.
- **Heartbeat:** a periodic "I am alive" message.
- **False positive:** suspecting a process that is alive. **Detection time:** how long after a real crash until it is suspected.
- **Timeout detector:** suspect a process when no heartbeat has arrived for a fixed time.
- **Phi accrual detector** (Hayashibara et al., 2004): instead of yes/no, output a suspicion level φ = −log₁₀ P(a heartbeat would arrive this late), learned from recent inter-arrival times. φ = 3 means about a 1-in-1,000 chance that a live node would be this late. Cassandra and Akka use it.
- **Gossip-style failure detection** (van Renesse, Minsky and Hayden, 1998): every node keeps a heartbeat counter for every member and gossips the whole table. A member whose counter has not risen for `t_fail` rounds is suspected.

## How it works

`gossip.py`:

| Name | What it does |
|---|---|
| `spread(n, mode, loss, seed)` | One rumour from node 0; returns informed count after each round |
| `rounds_to_spread`, `mean_rounds(n, mode, trials, loss)` | Rounds to reach everyone, single run or mean |
| `gossip_membership(n, t_fail, loss, seed, crash_round, rounds)` | Gossip heartbeat tables; one node crashes; returns `first_detected`, `all_detected` (rounds after the crash) and `false_rate` |

`detector.py`:

| Name | What it does |
|---|---|
| `heartbeat_arrivals(seed, interval, crash_at, jitter, loss, p_pause, ...)` | Arrival times of heartbeats sent every 100 ms, with delay jitter, loss and occasional sender pauses (as in garbage collection) |
| `timeout_detector(arrivals, crash_at, timeout)` | False positives and detection time for a fixed timeout |
| `PhiAccrual(window, min_std)` | `heartbeat(t)`, `phi(now)`, `stats()`, `suspect_after(threshold)` |
| `phi_detector(arrivals, crash_at, threshold)` | The same measurements for phi accrual |
| `sweep(detector, settings, seeds, **stream)` | Mean false positives per hour and detection time for several settings |

**Why log N rounds.** While few nodes know, almost every push reaches someone new, so the informed set roughly doubles each round: log₂ N rounds to inform half the cluster. Then pull takes over in push-pull: each uninformed node asks a random peer, and as most peers now know, the uninformed fraction shrinks very quickly, roughly squaring each round. Push alone is slow at the end because most pushes hit nodes that already know (Pittel, 1987: about log₂ N + ln N rounds).

## Run it

```bash
python3 gossip.py          # rumours and gossip membership, about 8 seconds
python3 detector.py        # timeout vs phi accrual
python3 -m unittest -v     # 15 tests in two files
```

Mean rounds for one rumour to reach every node (30 runs, no loss):

| N | log₂ N | Push | Pull | Push-pull |
|---|---|---|---|---|
| 16 | 4 | 7.2 | 6.2 | 4.2 |
| 64 | 6 | 11.4 | 9.2 | 6.1 |
| 256 | 8 | 14.9 | 11.4 | 7.6 |
| 1,024 | 10 | 18.3 | 14.2 | 9.2 |
| 4,096 | 12 | 21.2 | 16.1 | 10.6 |

Multiplying N by 256 (16 to 4,096) adds only 6.4 rounds to push-pull. Message loss slows it gently: for N = 1,024, push-pull takes 9.2 rounds with no loss, 10.4 at 10% loss, 11.9 at 25% and 17.7 at 50%.

Gossip-style failure detection, N = 32 (10 runs; detection in rounds after the crash):

| `t_fail` | Loss | First node detects | All nodes detect | False suspicion rate |
|---|---|---|---|---|
| 4 | 0% | 4.0 | 13.4 | 6.8% |
| 8 | 0% | 8.0 | 17.4 | 0.17% |
| 14 | 0% | 14.0 | 23.4 | 0.000% |
| 4 | 20% | 3.9 | 16.1 | 13.6% |
| 8 | 20% | 7.9 | 20.1 | 1.1% |
| 14 | 20% | 13.9 | 26.1 | 0.014% |

The gap between "first" and "all" (about 9 rounds) is how long the last heartbeat takes to gossip across 32 nodes. A `t_fail` shorter than that gossip time causes false suspicions, because fresh heartbeats have not yet reached everyone.

Heartbeat detectors (100 ms heartbeats, 1% loss, about 15 ms delay, 0.2% of heartbeats hit a 0.3–1.5 s pause; 10 runs of 10 minutes):

| Timeout | False positives per hour | Detection (ms) |
|---|---|---|
| 150 ms | 556.5 | 69 |
| 250 ms | 85.5 | 169 |
| 500 ms | 69.1 | 419 |
| 1,000 ms | 37.6 | 919 |
| 2,000 ms | 0.0 | 1,919 |

Pauses of up to 1.5 s fool every detector that reacts faster than 1.5 s: only the 2-second timeout avoids them. Phi accrual does no better here, because its normal model does not expect long pauses. Where it wins is when the network changes. With one fixed setting across three networks (no pauses):

| Mean jitter | Timeout 250 ms | Phi threshold 12 |
|---|---|---|
| 10 ms | 5.5 false/h, 155 ms detection | 5.5 false/h, 154 ms detection |
| 40 ms | 126.7 false/h, 190 ms | 0.0 false/h, 391 ms |
| 80 ms | 877.4 false/h, 254 ms | 0.6 false/h, 569 ms |

The timeout tuned for a calm network floods with false alarms on a noisy one; phi waits longer by itself.

## Experiments to try

1. **Check the log N claim.** Print `mean_rounds(n, "push-pull") / math.log2(n)` for n = 16 up to 16,384. Is the ratio settling? Repeat for push and compare with (log₂ N + ln N) / log₂ N.
2. **Increase the fanout.** Change `spread` so each node contacts `k` peers per round. How do rounds and total messages change for k = 1, 2, 4?
3. **Watch the tail.** For `spread(1024, "push", seed=1)`, the last few nodes take several rounds. Count how many messages are wasted on already-informed nodes in each round.
4. **Make pauses longer.** In `detector.py`, set `pause=(300, 5000)`. Which timeout now gives zero false positives, and what does it cost in detection time? This is why systems with long GC pauses either tune their collector or use leases with fencing (Chapter 12).
5. **Use a heavy-tailed model.** Replace the normal tail in `PhiAccrual.phi` with an exponential one, `p_later = exp(-elapsed / mean)` (Cassandra's choice). Rerun the pause scenario. Fewer false positives, slower detection?
6. **Gossip faster.** In `gossip_membership`, let each node push to two peers per round. How does the first-to-all detection gap change, and how low can `t_fail` go without false suspicions?

## Limitations

- Rounds are synchronous and every node knows every other node. Real gossip runs on unsynchronised timers with partial membership views. SWIM (described in Chapter 2) adds indirect probing and a suspicion state before declaring a node dead; Chapter 12 returns to membership.
- Messages are lost independently. Real loss is correlated: a partition drops everything between two groups.
- Heartbeats flow one way between one pair of processes, and the false-positive count treats each long gap as one event.
- No failure detector over an asynchronous network can be both complete and accurate. These detectors are *eventually* useful at best, which is exactly what consensus protocols assume (Chapter 11).
