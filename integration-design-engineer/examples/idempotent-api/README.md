# Provider-side idempotency keys (Chapters 6 and 8)

`idempotency.py` implements `POST /payments`-style semantics:

| Situation | Result |
|---|---|
| First request with a key | Work executes; response stored |
| Same key, same body, after completion | Stored response replayed (`idempotent_replay: true`); no second payment |
| Same key, **different** body | `422` |
| Same key while the first request is still running | `409`; client retries later |
| Downstream failure (nothing charged) | `503`, and the key claim is released so a retry can run |
| Same key from a different client | Independent (keys are scoped per client) |

The claim is an `INSERT` against a primary key **before** the work runs. That is what makes concurrent duplicates safe; the test fires five concurrent requests and checks the payment executes exactly once.

```bash
python3 -m unittest -v
```
