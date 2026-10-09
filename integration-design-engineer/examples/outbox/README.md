# Transactional outbox and inbox (Chapter 8)

`outbox.py` shows the fix for the **dual-write problem**:

1. `OrderService.place_order` writes the order **and** a CloudEvents-formatted event into an `outbox` table **in one transaction**.
2. `OutboxRelay.run_once` publishes unsent rows to a broker and then marks them sent. A crash between those steps republishes the row, so delivery is **at-least-once**.
3. `InventoryConsumer.handle` inserts the event ID into an `inbox` table in the **same transaction** as its effect (a non-idempotent increment), so duplicates are ignored: processing is **effectively once**.

```bash
python3 outbox.py          # demo: relay crash -> duplicate publish -> duplicate ignored
python3 -m unittest -v
```

In production the relay is a polling worker (`SELECT … FOR UPDATE SKIP LOCKED`) or a CDC connector (for example, Debezium's outbox event router), and the broker is Kafka, RabbitMQ, SQS or similar.
