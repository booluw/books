# Event time, watermarks and consistent snapshots (Chapter 16)

## The problem

A stream processor answers questions such as "how many payments per 10 seconds?" while the data is still arriving. Two things make that harder than it sounds.

First, events arrive **out of order**. A payment made at 12:00:03 may reach the processor after one made at 12:00:07, because it took a slower network path, sat in a phone's outbox, or was retried. If you count events by when they *arrive*, your answer depends on network weather. If you count them by when they *happened*, you must decide when you have waited long enough to publish a window's answer.

Second, a long-running job must be able to **checkpoint**: save a consistent picture of its state while messages are still flowing between its parts, so it can restart after a failure without losing or double-counting anything.

This folder implements both: event-time windows with watermarks and late-data handling (`windows.py`), and the Chandy–Lamport snapshot algorithm (`snapshot.py`) that underlies Apache Flink's checkpoints.

## Terms

- **Event time:** when something happened, stamped at the source. **Processing time:** when the stream processor sees it.
- **Window:** a finite slice of an endless stream over which to aggregate. **Tumbling** windows are fixed-size and do not overlap (`[0,10)`, `[10,20)`, …). **Sliding** windows have a size and a slide; with size 10 s and slide 5 s each event belongs to two windows.
- **Watermark:** the processor's running claim that "no more events with event time earlier than *W* will arrive". When the watermark passes a window's end, the window is emitted. A **bounded-out-of-orderness** watermark is *W* = (largest event time seen) − (maximum expected delay). It is a heuristic, not a guarantee.
- **Late event:** an event that arrives after the watermark has passed the end of its window. It can be **dropped**, sent to a **side output** (a separate stream for someone to inspect or reconcile), or, within an **allowed lateness**, used to **update** the already-emitted window.
- **Completeness versus latency:** waiting longer before emitting makes results more complete and later. The watermark delay is the dial.
- **Global snapshot:** the state of every process and every channel at one consistent moment. A **consistent cut** is a snapshot in which every message recorded as received was also recorded as sent.
- **FIFO channel:** first in, first out; messages on one channel arrive in the order they were sent (TCP connections are FIFO).
- **Marker:** the control message Chandy–Lamport sends along each channel to separate messages before the snapshot from messages after it. Flink calls them **barriers**.

## How it works

| File | What it holds |
|---|---|
| `windows.py` | `Event`, `Tumbling`, `Sliding`, `BoundedOutOfOrderness`, `WindowOperator`, `run_event_time()`, `event_time_truth()`, `processing_time_windows()`, `generate_events()` |
| `snapshot.py` | `Bank` (processes, FIFO channels, seeded scheduler, marker handling), `run_snapshot()`, `naive_snapshot()` |
| `test_stream.py` | 13 unit tests |

**The workload.** `generate_events()` produces about 20 events a second for 120 s. Most arrive within a second; 9% take 2–8 s; 1% are stragglers that take 20–60 s. In addition, the ingestion pipeline is down from 40 s to 50 s: events from that period are held and delivered in a burst at 56 s, *after* fresh events from 50 s onwards have already started flowing. Of 2,355 events, 1,088 arrive after an event with a later timestamp.

**The window operator.** For each event, in arrival order, `WindowOperator.process` checks the event against the current watermark, adds it to every window it belongs to that is still open (or within allowed lateness), then advances the watermark and emits every window whose end it has passed. `finish()` moves the watermark to infinity at the end of the stream.

**Chandy–Lamport.** `Bank` holds three processes with 1,000 each and a FIFO queue for each of the six ordered pairs. A seeded scheduler alternates between random transfers and random deliveries. At a random moment a random process starts the snapshot; traffic continues while markers propagate. Each process records its balance when it first sees a marker (or starts the snapshot), records each other incoming channel until that channel's marker arrives, and forwards markers on all its outgoing channels.

## What it shows

Tumbling 10 s windows, watermark delay 5 s, late events dropped (`python3 windows.py`):

| Window | True count | Event-time result | Emitted at (s) | Processing-time count |
|---|---|---|---|---|
| [0, 10) | 187 | 184 | 15.4 | 168 |
| [10, 20) | 202 | 198 | 25.2 | 201 |
| [20, 30) | 211 | 206 | 35.1 | 203 |
| [30, 40) | 188 | 187 | 50.3 | 191 |
| [40, 50) | 192 | 0 | never | 21 |
| [50, 60) | 190 | 184 | 65.4 | 357 |
| [60, 70) | 204 | 201 | 75.2 | 208 |

- Processing-time windows are simple and immediate but answer "what arrived when", not "what happened when": the outage shows up as a dip to 21 followed by a spike to 357, although the real traffic was flat.
- Event-time windows are close to the truth, except for [40, 50). Fresh events from after 50 s pushed the watermark past 50 before the backlog was released at 56 s, so the whole backlog was late and dropped. The watermark was a guess, and the guess was wrong.

Watermark delay against completeness and latency (drop late events):

| Max delay (s) | Late events | Events counted | Windows exactly right | Median wait after window end (s) |
|---|---|---|---|---|
| 0 | 354 | 85.0% | 8% | 0.3 |
| 1 | 295 | 87.5% | 8% | 1.2 |
| 2 | 273 | 88.4% | 8% | 2.3 |
| 5 | 227 | 90.4% | 8% | 5.3 |
| 10 | 24 | 99.0% | 17% | 10.3 |
| 30 | 9 | 99.6% | 42% | 30.4 |
| 60 | 0 | 100.0% | 100% | 60.3 |

Late-event policies with a 2 s watermark delay:

| Policy | Events lost | Side output | Updates emitted | Windows exactly right |
|---|---|---|---|---|
| Drop | 273 | 0 | 0 | 8% |
| Side output | 0 | 273 | 0 | 8% |
| Allowed lateness 10 s | 24 | 0 | 248 | 17% |
| Allowed lateness 60 s | 0 | 0 | 272 | 100% |

A short watermark delay with generous allowed lateness gives the best of both: a fast first answer and a correct final one, at the cost of keeping window state for longer and downstream consumers having to handle updates.

Chandy–Lamport snapshots, 1,000 seeded runs each (`python3 snapshot.py`):

| Method | Totals not equal to 3,000 | Worst error |
|---|---|---|
| Chandy–Lamport, FIFO channels | 0 | 0 |
| Chandy–Lamport, channels that reorder | 974 | 2,193 |
| Naive: read each balance in turn, ignore channels | 998 | 1,632 |

The algorithm conserves money in every run and every snapshot is a consistent cut; the tests also check that each recorded channel holds exactly the messages sent before the sender's cut and received after the receiver's. Remove FIFO ordering, or skip the markers, and the snapshot almost never adds up.

## Run it

```bash
python3 windows.py         # windows, watermark trade-off, late-data policies
python3 snapshot.py        # one snapshot in detail, then 3,000 randomised runs
python3 -m unittest -v     # 13 tests, under a second
```

Standard-library Python 3 only; every run is seeded.

## Experiments to try

Start a Python shell in this folder with `from windows import *`.

1. **Release the backlog first.** `ev = generate_events(outage=(40, 50, 50.5))`, then `run_event_time(ev, Tumbling(10), 5).final()[("all", (40.0, 50.0))]`. The backlog now arrives before fresh data moves the watermark on, and the window counts 186 of its 192 events instead of 0. Whether data is "late" depends on the order things arrive, not only on how old they are.
2. **No outage.** `generate_events(outage=None)`: with a 5 s watermark the mean error per window is 3.8 for event time and 7.25 for processing time. Without dramatic failures the difference is smaller, but it never goes away.
3. **More stragglers.** Set `straggler_fraction=0.05` and rerun the watermark-delay sweep (copy the loop from the bottom of `windows.py`). How much delay do you now need for 99% of events?
4. **Sliding windows.** Replace `Tumbling(10)` with `Sliding(60, 10)`: each event now updates six windows. Count `len(op.results)` and compare state size and late updates.
5. **Per-source watermarks.** Give events a `key` per source (`"phone"`, `"web"`) and make one source much slower. A single watermark for all sources either waits for the slowest or drops its data. Flink takes the minimum watermark across input partitions; sketch how you would add that.
6. **Break the snapshot.** In `snapshot.py`, change `Bank._record` so it also records the channel the marker arrived on (drop the `if c != skip_channel` test). Run the tests: money after the marker is counted twice.
7. **Reordering channels.** `run_snapshot(seed, fifo=False)` for a few seeds, and print `bank.trace` to find a marker that overtook a transfer. A transfer sent before the cut but delivered after an overtaking marker is counted nowhere; one sent after the cut but delivered before the marker is counted twice.
8. **More processes.** `run_snapshot(seed, n=6)`: the snapshot still conserves money. Count markers sent (`n × (n − 1)`): the cost of the algorithm grows with the number of channels.

## Limitations

- One operator, one key by default, and watermarks generated per event. Real engines generate watermarks periodically, per input partition, and propagate the minimum through a graph of operators, with **idle-source** detection so a quiet partition does not stall everything.
- Windows are emitted as whole results. Updates are not paired with **retractions** (messages that cancel the previous result), which downstream sums need to avoid double counting.
- No session windows (windows that close after a gap in activity) and no triggers other than the watermark.
- The snapshot is of a toy bank with integer balances. Flink's barrier alignment additionally blocks or buffers input channels so that operator state lines up with barriers, and stores the snapshot durably; here it lives in memory.

## Chapter

Chapter 16 (stream processing: event time, windows, watermarks, late data, and consistent checkpoints).
