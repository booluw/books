# Exercises: Chapter 8, Reliability

## Questions

1. Classify as retryable, non-retryable or fix-then-retry: DNS failure; `422` invalid tax code; `409` duplicate external ID on create; `429`; TLS certificate expired; read timeout on `POST /payments` without an idempotency key; customer not yet synced to ERP when the order arrives.
2. Three services call each other in a chain (A→B→C). Each retries 3 times. C is down. How many requests reach C for one call to A? How would you fix this?
3. Implement a `with_retries` decorator using `examples/resilience/resilience.py` and use it around a function that calls a public API. Add a deadline.
4. Design the de-duplication key for a consumer that receives both Shopify webhooks and a nightly reconciliation feed for the same orders.
5. Draw a saga for "book flight + hotel + car" with compensations. Which step would you put last, and why?
6. Run `python examples/outbox/outbox.py`. Then modify `InventoryConsumer.handle` to remove the inbox insert. Re-run the tests and explain the failure.
7. Write a reconciliation design for Shopify → NetSuite orders: what is compared, when, the tolerance, and who gets the report.
8. During a 6-hour ERP outage, 50,000 messages queue. When the ERP comes back, how do you drain safely?

## Solutions

1. DNS failure: retryable. `422`: fix-then-retry (business error queue). `409` duplicate on create: usually means it already exists, so treat as success after confirming it matches (idempotent upsert would avoid it). `429`: retryable with `Retry-After`. Expired TLS certificate: non-retryable until fixed (alert). Timeout on non-idempotent POST: unknown outcome, so query the target first; do not blindly retry. Customer not yet synced: retryable with delay (dependency ordering), or create the dependency.
2. Each layer makes up to 3 attempts: 3 × 3 × 3 = 27 requests to C. Fix: retry at one layer only (closest to C, or at the outer durable queue), use retry budgets, circuit breakers and deadline propagation.
3. Hands-on.
4. Use a business key plus version, for example `shopify_order_id + updated_at` (or a version counter), so the same state from either source is applied once; also keep the webhook ID for exact-redelivery de-duplication.
5. Flight, hotel and car reservations each have a cancel compensation. Put the step that is hardest to compensate or most likely to fail last; for example, the non-refundable flight ticketing goes last, after hotel and car are held.
6. Without the inbox, the duplicate delivery increments the reservation twice (`reserved` becomes 4 instead of 2), so the "effectively once" test fails.
7. Example: daily at 06:00 for the previous local business day; compare counts and gross totals per currency between Shopify paid orders and NetSuite sales orders with external ID prefix `SHOP-`; tolerance 0 orders and ±0.01 per currency; list missing and extra IDs; auto-resync missing orders via the normal idempotent pipeline (max 500 per run); report to finance ops and the integration team channel.
8. Keep the circuit closed gradually (half-open trials); drain with bounded concurrency at or below the ERP's sustainable rate and its concurrency limits; prioritise newest-business-critical if needed; monitor ERP latency and error rate and back off on degradation; watch for messages exceeding max age (route to review); confirm with reconciliation afterwards.
