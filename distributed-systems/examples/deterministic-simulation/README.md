# Deterministic simulation testing (Chapter 23)

## The problem

Distributed-systems bugs hide in **interleavings**: the particular order in which messages arrive, timers fire, packets are lost and machines crash. A bug that needs three unlikely things to coincide may never show up in unit tests or on a developer's laptop, then appear in production once a month and vanish when someone attaches a debugger. Even when a test does hit it, re-running the test usually does not, because real threads, clocks and networks never behave the same way twice.

**Deterministic simulation testing** removes the non-determinism. The system's real logic runs inside a simulated world in one thread, with a virtual clock and a simulated network, and every "random" choice (each delay, each dropped packet, each crash) comes from one pseudo-random generator started from a **seed**. One seed, one execution, exactly reproducible. Then you run the simulation with thousands or millions of seeds, checking invariants, and when one fails you replay it as often as you like.

FoundationDB was built this way from the start (Will Wilson, "Testing Distributed Systems w/ Deterministic Simulation", Strange Loop 2014), and TigerBeetle's VOPR (Viewstamped Operation Replicator) simulator runs its consensus code against simulated disks and networks around the clock. Antithesis sells the same idea for whole containers by making a hypervisor deterministic.

This folder builds a small harness, a replicated system with a deliberate rare bug, and a **swarm** runner that finds the bug, replays it exactly, and confirms the fix.

## Terms

- **Interleaving:** one possible ordering of the events in a concurrent system. The number of interleavings grows explosively with the number of events.
- **Seed:** the starting value of a pseudo-random number generator. The same seed always gives the same sequence of numbers.
- **Discrete-event simulation:** jumping from one scheduled event to the next in virtual time, using a priority queue, instead of waiting in real time. A run that represents minutes of activity takes milliseconds.
- **Invariant:** a property that must hold in every execution. Here: **no acknowledged write is lost**.
- **Primary-backup replication:** one node (the **primary**) handles writes and copies each one to a **backup** before acknowledging it. If the primary fails, the backup is promoted, which is called **failover**.
- **Failure detector:** the component that decides a node has failed. Here an oracle that promotes the backup a fixed delay after the crash.
- **Idempotent:** safe to apply more than once. Each counter stores the *set* of op ids applied to it, so a retried increment counts once.
- **Swarm testing:** varying the test *configuration* per seed (number of clients, loss rate, latency, whether to crash) as well as the schedule, so that some runs are calm and some are hostile (Groce, Zhang, Eide, Chen and Regehr, ISSTA 2012).
- **Trace:** the log of everything the simulator did. Its SHA-256 hash is a fingerprint of the whole execution.

## How it works

| File | What it holds |
|---|---|
| `sim.py` | The harness: `Simulator` (virtual clock, event heap with a tie-breaking sequence number, lossy network, trace and trace hash) and `SwarmConfig.from_seed()` |
| `primary_backup.py` | The system under test: `Node` (correct), `BuggyNode`, `Client`, `Cluster` (crash and failover), `run(seed, buggy)` and the invariant check |
| `swarm.py` | The swarm runner: search seeds, replay the first failure three times, explain it from the trace, then check the fixed version on the same seeds |
| `test_simulation.py` | 13 unit tests |

**The protocol.** A client sends `incr(op, counter)` to the primary. The primary applies it, sends `replicate` to the backup, retransmits every 30 ms until the backup's `ack` arrives, then replies `ok`. Clients retry on a 60 ms timeout, to whichever node is primary. A crash kills the primary; 50 ms later the backup is promoted and carries on alone.

**The bug.** `BuggyNode.on_ack` matches acknowledgements by *counter name* instead of *op id*. When two increments of the same counter are in flight, the backup's ack for one releases both. If the `replicate` message for the second was dropped, the primary has now stopped retransmitting it and the backup will never get it. The client has been told `ok`. When the primary later crashes, the write is gone. The bug needs concurrent writes to the same counter, a dropped message at the wrong moment and a later failover.

**Determinism.** All randomness comes from `Simulator.rng` (seeded) or `SwarmConfig.from_seed` (seeded separately). Events at equal times run in the order they were scheduled. Nothing reads the real clock, iterates over an unordered set in a way that affects behaviour, or uses threads.

## What it shows

`python3 swarm.py` (timings from the machine used to write this):

```
Buggy primary: 10,000 seeds in 4.1 s (0.41 ms per run)
Invariant 'no acknowledged write is lost' violated in 152 seeds (1.52%)
First failing seeds: [100, 210, 284, 319, 360, 614, 641, 839, 893, 947]

Replaying seed 100 three times:
 replay  trace events        trace hash  acked  lost (op, counter)
      1            93  8ca2b3092ef8398c     21  [(1, 'c0')]
      2            93  8ca2b3092ef8398c     21  [(1, 'c0')]
      3            93  8ca2b3092ef8398c     21  [(1, 'c0')]

What happened (trace lines that mention the lost op, plus crash and failover):
     11.298 RECV client0->n0 ('incr', 1, 'c0', 'client0')
     11.298 DROP n0->n1 ('replicate', 1, 'c0')
     11.688 n0 ack for op 8 on c0 releases ops [8, 1]
     12.881 RECV n0->client0 ('ok', 1)
     48.349 CRASH n0 (ops awaiting backup ack: [6, 13])
     98.349 FAILOVER n1 is primary with state {'c0': 16}
    173.823 END primary=n1 acked=21 lost=[(1, 'c0')]

Fixed primary (acks matched by op id): 10,000 seeds in 3.4 s, 0 violations
```

- The bug shows up in about 1.5% of swarm seeds; the first is **seed 100**. Every replay of seed 100 produces the same 93 trace events and the same hash.
- The trace tells the whole story in seven lines: op 1's replication is dropped, the ack for op 8 (same counter) wrongly releases op 1, the client is told `ok`, the primary crashes 36 ms later, and the backup takes over without op 1.
- The fix (match acks by op id) passes all 10,000 seeds, including seed 100.
- Each ingredient is necessary. Across 10,000 seeds the buggy version never fails with message loss turned off, never fails without a crash, and never fails with a single client. A test suite that runs only "realistic" calm conditions would never find it.

## Run it

```bash
python3 swarm.py                    # search 10,000 seeds, replay the first failure, check the fix
python3 swarm.py --seeds 2000       # a quicker search
python3 swarm.py --seed 100         # the full trace of one run
python3 swarm.py --seed 100 --fixed # the same seed with the corrected primary
python3 -m unittest -v              # 13 tests, about 2 seconds
```

Standard-library Python 3 only.

## Experiments to try

Start a Python shell in this folder with `from dataclasses import replace; from primary_backup import run; from sim import SwarmConfig`.

1. **Remove one ingredient at a time.** Count failures over 10,000 seeds with `replace(SwarmConfig.from_seed(s), drop_rate=0.0)`, then `crash_primary=False`, then `clients=1`, passing each as `config=` to `run(s, config=...)`. Each gives 0 failures: the bug needs loss, a failover and concurrency together.
2. **Which configurations find it?** Group the 152 failing swarm seeds by `SwarmConfig.from_seed(s).drop_rate`: 74 had 2% loss, 49 had 1%, 23 had 0.5%, 6 had 0.1%, and none of the 3,275 loss-free seeds failed. A single hand-written configuration is a bet on one point in that space: `SwarmConfig()` with 5% loss fails in 409 of 2,000 seeds, but the same with `drop_rate=0.001` fails in only 10. Swarm testing spreads runs across configurations so that one unlucky choice of parameters does not hide a bug.
3. **Break determinism on purpose.** In `Client.start`, replace `self.sim.rng.uniform(0, 20)` with `random.uniform(0, 20)` from the global, unseeded `random` module (add `import random` at the top). Run `python3 swarm.py --seed 100` three times: the trace hashes now differ and the failure comes and goes. This is what testing without a simulator is like.
4. **Another kind of non-determinism.** Make `Simulator.schedule` push `(time, action, args)` without the sequence number. Equal-time events now compare their actions, which Python cannot order, and the run crashes. Real harnesses must make every tie-break explicit.
5. **Add an invariant.** Check after each failover, not only at the end, that the new primary holds every acknowledged op. The violation is then reported at the failover (98 ms for seed 100) instead of at the end of the run, which makes traces shorter.
6. **Plant your own bug.** In `Node.on_incr`, reply `ok` before replicating when the backup is "probably fine" (say, if the last ack arrived less than 5 ms ago). How many seeds does the swarm need to find it?
7. **Shrink the failure.** Write a loop that, for a failing seed, tries smaller configurations (fewer clients, fewer ops) with the same seed and keeps the smallest that still fails. This is **test-case minimisation**, which tools such as Hypothesis do automatically.

## Limitations

- The system under test is written for the simulator. Real deterministic simulation runs the production code, which means every source of non-determinism (clock, network, disk, threads, random numbers) must go through an interface the simulator can replace. That design discipline is the hard part, and why FoundationDB and TigerBeetle built it in from day one.
- No disk faults (torn writes, lost fsyncs, corruption), no clock skew and no network partitions with healing; production simulators inject all of these.
- The failure detector is an oracle and only the primary ever crashes, and nodes never restart. A real failover needs fencing so that a slow old primary cannot keep acknowledging writes.
- Random search finds bugs that are rare, not ones that are astronomically rare. Coverage-guided search (Antithesis) and model checking (TLA+) complement it.

## Chapter

Chapter 23 (testing distributed systems: deterministic simulation, fault injection, swarm testing and reproducible failures).
