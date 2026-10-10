# Exercises: Chapter 7, Asynchronous and Event-Driven Integration

## Questions

1. For each, choose queue, topic + subscriptions, or log, and a product: (a) distribute 1 million image-resize jobs; (b) notify CRM, ERP and analytics of new customers; (c) retain 30 days of clickstream for replay by new consumers.
2. An SQS consumer takes up to 90 seconds per message; the visibility timeout is 30 seconds. What happens? Fix it.
3. A Kafka topic has 6 partitions and a consumer group of 10 instances. How many are active? What changes with Kafka 4.2 share groups?
4. Events for order 123 arrive as v3, v1, v2. Describe two consumer designs that end in the correct state.
5. Write a CloudEvents JSON envelope for `CustomerAddressChanged` with a thin payload. Then a fat one. When would you use each?
6. Run `examples/webhook-receiver`. Modify the sender to sign with a timestamp 10 minutes in the past. What status do you get, and why?
7. A SaaS provider retries webhooks for 3 days, then disables the endpoint. Your receiver was down for 4 days. What do you do to recover, and what do you change?
8. Why is "send the event to Kafka inside the HTTP request handler after saving to the database" risky? What is the fix?

## Solutions

1. (a) Queue: SQS, RabbitMQ or Service Bus queues, with competing consumers. (b) Topic + subscriptions: SNS→SQS, EventBridge, Service Bus topics or Kafka. (c) Log: Kafka, Kinesis or Event Hubs, with 30-day retention.
2. The message becomes visible again after 30 s and a second consumer processes it concurrently: duplicate work and possibly duplicate side effects. Fix: set the visibility timeout above worst-case processing (for example 180 s), or extend it periodically while working, and make processing idempotent.
3. Six active; four idle (classic consumer groups cap parallelism at the partition count). Share groups let many consumers cooperatively read the same partitions with per-record acknowledgement, so all ten can work.
4. (a) Version check: store the last applied version per order and ignore events with a lower or equal version (v3 applied; v1 and v2 ignored). (b) Thin events with fetch-latest: on any event, fetch the current order from the source and apply that state.
5. Thin: `data: {"customer_id": "C-1", "version": 12}`. Fat: `data` includes the full new address and version. Thin when consumers vary, privacy matters, or ordering is a concern. Fat when consumers need to work without calling back (offline, high volume, source capacity limits).
6. `401`: the timestamp is outside the 5-minute tolerance, so it is treated as a possible replay.
7. Recover: run reconciliation against the provider's list API for the outage window (by `updated_at`), re-enable the endpoint, and replay through the same idempotent pipeline. Change: alert on webhook-receiver downtime and non-2xx rates, alert when the provider disables the endpoint (if it notifies), and schedule regular reconciliation.
8. The dual-write problem: a crash between the database commit and the send loses the event (or vice versa). Fix: transactional outbox (or CDC on the outbox table).
