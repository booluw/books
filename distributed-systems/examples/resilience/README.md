# Retry storms and how to survive them (Chapter 17)

## The problem

A service is running happily at 70% of its capacity. For five seconds a burst of traffic arrives at twice its capacity. The burst ends, traffic returns to normal, and the service… stays down. Not for five seconds, but for good, until someone restarts the clients or drops traffic at the load balancer.

This is a **metastable failure**: a system with two stable states, healthy and overloaded, where a temporary trigger (the spike) pushes it into the bad state and a **sustaining effect** keeps it there after the trigger has gone. In the example the sustaining effect is retries. Every request times out, so every client retries, so the server receives three or four times the normal load, so every request times out. Bronson, Aghayev, Charapko and Zhu named and described the pattern in "Metastable Failures in Distributed Systems" (HotOS 2021), and it is behind many real outages.

This folder simulates the storm and the defences against it, so you can watch each defence work, or fail to, on identical traffic.

## Terms

- **Capacity:** the most work a server can complete per second. Here 4 workers × (1 / 0.04 s mean service time) = 100 requests/second.
- **Utilisation:** offered load divided by capacity. Queueing delay grows sharply as it approaches 100%, and above 100% the queue grows without limit.
- **Discrete-event simulation:** a simulation that jumps from one event (arrival, completion, timeout) to the next in time order, using a priority queue, instead of ticking a clock. It is fast and, with a seeded random-number generator, exactly repeatable.
- **Timeout:** how long a client waits for one **attempt** before giving up on it. The client's overall **deadline** bounds the whole **request** across all attempts.
- **Retry:** sending the request again after a failed attempt. Retries turn transient faults into successes, and turn overload into more overload.
- **Amplification:** attempts sent per logical request. Under naive retries with four attempts it approaches 4.
- **Goodput:** useful throughput, meaning requests that succeeded in time. Throughput counts work done; goodput counts work that mattered.
- **Wasted work:** attempts the server completed after the client had stopped waiting.
- **Backoff:** waiting before a retry. **Exponential backoff** doubles the wait each time, up to a cap. **Jitter** randomises the wait: **full jitter** picks uniformly between 0 and the exponential value (Marc Brooker, "Exponential Backoff and Jitter", AWS Architecture Blog, 2015).
- **Token bucket:** a counter of tokens that refills at a fixed rate up to a capacity; an action proceeds only if it can take a token. Used for rate limiting.
- **Retry budget:** a token bucket that earns a fraction of a token (here 0.1) per new request and spends a whole token per retry, so retries can never add more than about 10% load (as in Finagle and gRPC retry throttling).
- **Circuit breaker:** a client-side switch. **Closed**: calls flow and failures are counted. When the recent failure rate crosses a threshold it trips **open**: calls fail immediately without touching the server. After a cool-down it goes **half-open**, lets a few probe calls through, and closes if they succeed or re-opens if they fail.
- **Load shedding:** the server rejecting work it cannot finish in time, here by refusing new work when the queue holds 30 items, which is about 0.3 s of waiting at full speed and so less than the timeout. A fast "no" is cheaper for everyone than a slow "yes" that arrives after the caller left.
- **Deadline propagation:** sending the caller's deadline with the request so the server (and anything it calls) can skip work whose caller has already given up. gRPC does this with its deadline header.

## How it works

| File | What it holds |
|---|---|
| `components.py` | Reusable pieces with explicit time (`now`), no I/O: `backoff_delays()`, `next_backoff()`, `TokenBucket`, `RetryBudget`, `CircuitBreaker` |
| `simulation.py` | The discrete-event simulation (`Config`, `Strategy`, `simulate()`, `STRATEGIES`) and the comparison table |
| `herd.py` | A thundering-herd model of synchronised retries, to show what jitter is actually for |
| `test_resilience.py` | 15 unit tests |

The simulation draws the arrival times once from the seed, so every strategy faces exactly the same traffic. Per strategy it reports goodput among requests arriving after the spike, end-to-end p50 and p99 latency (the times within which 50% and 99% of successful requests completed) from the spike onwards, and **recovery time**: seconds after the spike until every later one-second window has at least 90% success.

Results for seed 1 (`python3 simulation.py`):

| Strategy | Goodput after spike (req/s, ideal 70) | p50 / p99 (s) | Recovery | Amplification | Wasted work |
|---|---|---|---|---|---|
| No retries | 47.0 | 0.04 / 0.47 | 15 s | 1.00 | 1,903 |
| Naive retries (immediate, 4 attempts) | 0.0 | 0.31 / 0.50 | never | 3.51 | 5,111 |
| Exponential backoff | 0.0 | 0.31 / 0.50 | never | 2.67 | 5,111 |
| Backoff + full jitter | 0.0 | 0.31 / 0.50 | never | 3.38 | 5,111 |
| Jitter + retry budget | 33.2 | 0.05 / 0.47 | 24 s | 1.06 | 2,815 |
| Jitter + circuit breaker | 67.5 | 0.05 / 0.47 | 2 s | 0.90 | 288 |
| Deadline propagation (naive retries) | 18.8 | 0.99 / 2.00 | never | 3.21 | 4,197 |
| Load shedding (naive retries) | 69.8 | 0.05 / 0.41 | 0 s | 1.27 | 3 |
| Budget + jitter + shedding + deadlines | 69.8 | 0.05 / 0.42 | 0 s | 1.02 | 3 |

What to take from it:

1. **Naive retries turn a five-second spike into a permanent outage.** Load has gone back to 70% of capacity, but amplification of 3.5 makes the offered load about 245 requests/second, and the queue grows to over 11,000 items.
2. **Backoff and jitter alone do not help here.** They change *when* retries happen, not *how many*. In an open system (new requests keep arriving whatever happens to old ones) the total extra work is what matters.
3. **Even no retries takes 15 s to recover**, because the server works through a backlog of 467 attempts whose callers have already left. Wasted work is a sustaining effect too.
4. **A retry budget caps amplification** (1.06) but does nothing about the backlog, so recovery takes 24 s.
5. **Shedding bounds the queue**, so latency stays below the timeout and almost nothing is wasted. Deadline propagation alone is not enough when retries still amplify load: the queue settles at exactly the length that makes most attempts time out.
6. **Layered defences** recover as soon as the spike ends, with amplification of 1.02.

### Where jitter does matter

`herd.py` models 200 clients that fail at the same instant against a server that accepts 10 calls per 10 ms slot:

| Policy | Calls | Calls per client | Time to drain (s) |
|---|---|---|---|
| Constant 10 ms | 2,200 | 11.0 | 0.20 |
| Exponential | 2,100 | 10.5 | 13.27 |
| Full jitter | 1,005 | 5.0 | 0.76 |
| Equal jitter | 978 | 4.9 | 0.56 |
| Decorrelated jitter | 757 | 3.8 | 0.31 |

Plain exponential backoff keeps the herd together, so every wave collides again. Jitter breaks up the herd, halving the work and finishing 17 times sooner. Use jitter to avoid synchronisation, and budgets, shedding and deadlines to limit total work.

## Run it

```bash
python3 simulation.py      # the retry-storm comparison and a success-rate timeline
python3 herd.py            # synchronised retries: why jitter exists
python3 components.py      # sample delays for each backoff policy
python3 -m unittest -v     # 15 tests, under a second
```

Everything is standard-library Python 3 and seeded: the same seed gives the same numbers on any machine.

## Experiments to try

Start a Python shell in this folder with `from simulation import *` and `from dataclasses import replace`, then:

1. **Find the tipping point.** Run `simulate(BY_NAME["naive retries"], Config(spike_end=10.4))` and then `spike_end=10.6`. A 0.4 s spike is absorbed (the queue peaks at 50 items, under one timeout's worth); a 0.6 s spike never recovers (amplification 3.4, queue over 8,600). A 0.2 s difference in the trigger flips the outcome: that cliff is the edge of the metastable region. Also try `spike_rate=110`: a mild five-second overload is absorbed.
2. **Lower the base load.** Try `Config(base_rate=10, duration=120)`, `Config(base_rate=20, duration=200)` and `Config(base_rate=30, duration=300)`. At 10 requests/second the naive system recovers 45 s after the spike; at 20, after 145 s (it must work through a backlog of nearly 2,900 abandoned attempts); at 30 it never does, because 30 × 3.5 attempts exceeds capacity. Retries are safe only with headroom for the amplification.
3. **Fewer attempts.** `simulate(replace(BY_NAME["naive retries"], max_attempts=2))`. Amplification falls to 1.84, but 1.84 × 70 is still above 100, so it still never recovers.
4. **Loosen the budget.** `simulate(BY_NAME["jitter + retry budget"], Config(budget_ratio=r))` for r = 0.15, 0.2 and 0.25. Recovery takes 29 s, then 36 s, then never: a budget protects only while it is tight.
5. **Shed later.** Run `"load shedding"` with `Config(max_queue=60)` and `max_queue=100`. Once the queue can hold more than one timeout's worth of work (100 req/s × 0.5 s = 50 items), queued requests time out, retries return, and goodput collapses (6.2 and then 0 requests/second). The combined strategy survives the same change, because deadline propagation skips expired work, but its p99 rises to the 0.5 s timeout.
6. **Make the server misbehave differently.** In `start_work`, replace the exponential service time with a heavy tail of the same 40 ms mean, `service_rng.paretovariate(2.5) * 0.024`, and compare p99 latencies.
7. **Breaker tuning.** Edit the `CircuitBreaker()` call in `simulate()` to make the breaker eager (`CircuitBreaker(min_calls=4, failure_threshold=0.25)`) and lazy (`min_calls=50`). Watch `short_circuited` in the result: an eager breaker also rejects requests the server could have served.
8. **Herd size.** In `herd.py`, try `clients=1000` and compare how completion time scales for `exponential` and `full_jitter`.

## Limitations

- One server, one queue, no network latency, and a single shared client breaker. Real systems have many hops; retries at each layer multiply (three layers each making three attempts can send 27 calls to the bottom).
- Clients form an open system with Poisson arrivals. Closed systems, where a fixed set of users waits for each response before sending the next, are self-limiting and behave differently under overload.
- Shedding by queue length is crude. Production systems use queueing time (CoDel-style), concurrency limits that adapt (such as Netflix's `concurrency-limits`), or priority-aware shedding.
- The circuit breaker counts outcomes per client population, not per endpoint or per host, and its parameters were not tuned.
- Numbers are from a toy model. They show the shape of the effects, not what your service will do.

## Chapter

Chapter 17 (resilience patterns: timeouts, retries, backoff and jitter, budgets, circuit breakers, load shedding, deadlines, and metastable failures).
