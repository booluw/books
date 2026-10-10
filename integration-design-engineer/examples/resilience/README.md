# Resilience building blocks (Chapter 8)

`resilience.py` contains:

- `classify(status, idempotent=…)`: maps an HTTP outcome to `SUCCESS`, `RETRY`, `REFRESH_AUTH` or `FAIL_PERMANENT`. A timeout or `500` on a **non-idempotent** call is *not* retried, because its outcome is unknown.
- `retry_call(...)`: exponential backoff with **full jitter**, honours `Retry-After`, caps attempts, respects a **deadline**, and refreshes credentials **once** on `401`.
- `CircuitBreaker`: closed → open → half-open over a sliding window of results. Client errors (4xx except 429) do not count as failures.
- `TokenBucket`: client-side rate limiting with bursts.

Clock and sleep functions are injectable, so the tests run in microseconds and are deterministic.

```bash
python3 -m unittest -v
```
