# Exercises: Chapter 16, Operations

## Questions

1. Define three SLIs and SLOs for an order-to-ERP integration.
2. List ten fields every integration log line should contain.
3. An integration has had zero errors for 12 hours, and the business reports missing orders. What monitoring would have caught this?
4. Write alert rules (condition, severity, recipient) for: DLQ growth, consumer lag, certificate expiry, a business error queue, and low volume.
5. Write the "replay a time window" procedure for the runbook of an integration that uses a message store and idempotent consumers.
6. Add OpenTelemetry tracing to the outbox example so a trace continues from `place_order` through the relay to the consumer. (Hint: store `traceparent` in the outbox row.)

## Solutions (outline)

1. Freshness: 95% of paid orders exist in ERP within 15 minutes (28 days). Completeness: 100% of paid orders reconcile daily, with 0 unexplained differences. Availability: 99.9% of webhook deliveries acknowledged with 2xx.
2. timestamp, level, service, flow, tenant, trace_id, correlation/message_id, entity_type and entity_id, external_system and operation, status and error_code, duration_ms, attempt.
3. Volume anomaly alerts ("orders in last hour < 30% of the same hour last week"), freshness ("latest order received > 30 min ago during trading hours"), synthetic transactions, and reconciliation.
4. Example: DLQ depth > 0 for 10 min on tier-1 flows → page integration on-call. Consumer lag age > 15 min → page. Certificate expiry < 14 days → ticket; < 3 days → page. Business error queue > 20 or oldest > 4 h → ticket to the business owner. Volume < 30% of baseline for 30 min in trading hours → page.
5. Identify the window and affected flow; confirm the fix is deployed; pause live consumption if needed; select messages from the store by time and flow; dry-run (count, sample); replay at a throttled rate through the normal pipeline (idempotency prevents duplicates); monitor errors; run reconciliation; record actions in the incident log.
6. Hands-on: inject the context when writing the outbox row, put `traceparent` into the event (or headers) when the relay publishes, and extract it in the consumer to start a child span.
