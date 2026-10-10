# Exercises: Chapter 3, Networks and HTTP

## Questions

1. Your integration logs `connect timed out` when calling a partner, but `curl` from your laptop works. List four possible causes, in the order you would check them.
2. Which of these may be retried automatically after a read timeout, and why? `GET /orders/1`, `PUT /orders/1`, `POST /orders`, `DELETE /orders/1`, `PATCH /orders/1 {"qty": +1}`, `QUERY /orders` (RFC 10008).
3. For each status code, choose: retry with backoff / refresh token then retry once / fix data, don't retry / business workflow / alert a human: 400, 401, 403, 404 (on a record you just created), 409, 412, 422, 429, 500 (on a `GET`), 503.
4. Run `openssl s_client -connect example.com:443 -servername example.com` and identify the leaf certificate's subject, issuer and expiry date. How many certificates are in the chain?
5. Your service's SLA is 5 seconds. It calls a partner with a 2 s read timeout and 3 attempts with jittered backoff (max 1 s between attempts). Can this breach your SLA? How would you fix it?
6. Explain why a pooled connection can fail with `connection reset` after being idle, and how to prevent it.

## Solutions

1. (1) Egress: firewall or security group in the runtime environment, or a required proxy not configured; (2) the partner's IP allow-list does not include your production egress IP (your laptop's IP may be allowed, or the VPN route differs); (3) DNS: split-horizon or private DNS resolving differently inside the runtime; (4) routing: private-link/VPN routes or NAT gateway misconfigured. Test with `nc -vz` *from the runtime itself*.
2. Safe: `GET`, `PUT`, `DELETE`, `QUERY` (idempotent by definition, assuming the server implements the semantics correctly). Not safe: `POST` (unless it carries an idempotency key) and the increment `PATCH` (not idempotent).
3. 400 fix data; 401 refresh then retry once; 403 alert a human (configuration); 404 on a just-created record: retry with backoff (likely replication lag), with a cap; 409 business workflow (re-read and decide); 412 re-read, re-apply, retry; 422 fix data; 429 retry honouring `Retry-After`; 500 on GET retry with backoff; 503 retry honouring `Retry-After`.
4. Answers vary by date. Typically two or three certificates: leaf, one intermediate, sometimes a cross-signed intermediate. The root is in your trust store and usually not sent.
5. Yes: 3 × 2 s timeouts plus up to 2 s of backoff = up to 8 s. Fix: compute a deadline (for example 4 s for the partner call, including retries); stop retrying when the remaining budget is less than one timeout; lower the per-attempt timeout based on the partner's p99; or make the operation asynchronous (202 + callback).
6. Load balancers and servers close idle connections after their own timeout (e.g. 60 s); the client still thinks the connection is usable. Set the client pool's idle eviction shorter than the smallest idle timeout in the path, enable TCP keep-alives, and retry idempotent requests once on a reset of a reused connection.
