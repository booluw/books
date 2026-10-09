"""Transactional outbox and idempotent inbox with SQLite (Chapter 8, section 8.8).

Producer side:
    place_order() writes the order AND an outbox row in ONE transaction,
    so there is never an order without its event (or an event without its order).

Relay:
    OutboxRelay.run_once() publishes unsent outbox rows to a broker and then
    marks them sent. If it crashes between publish and mark, the row is
    published again: delivery is at-least-once.

Consumer side:
    InventoryConsumer.handle() records each event ID in an inbox table in the
    same transaction as its business effect, so duplicates have no effect:
    processing is effectively once.

The "broker" here is an in-memory list so the example runs anywhere; swap
it for Kafka, RabbitMQ or SQS without changing the pattern.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------
# Producer: order service
# --------------------------------------------------------------------------
ORDER_SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    sku TEXT NOT NULL,
    qty INTEGER NOT NULL CHECK (qty > 0),
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outbox (
    id TEXT PRIMARY KEY,               -- event id, used by consumers for de-duplication
    aggregate_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    sent_at TEXT                       -- NULL until the relay has published it
);
"""


class OrderService:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.executescript(ORDER_SCHEMA)

    def place_order(self, customer_id: str, sku: str, qty: int, *, fail_after_insert: bool = False) -> str:
        order_id = f"ORD-{uuid.uuid4().hex[:8]}"
        event = {
            "specversion": "1.0",
            "id": str(uuid.uuid4()),
            "source": "urn:example:orders",
            "type": "com.example.order.placed.v1",
            "subject": order_id,
            "time": utc_now(),
            "data": {"order_id": order_id, "customer_id": customer_id, "sku": sku, "qty": qty},
        }
        with self.db:  # one transaction: both rows commit, or neither does
            self.db.execute(
                "INSERT INTO orders (id, customer_id, sku, qty, created_at) VALUES (?, ?, ?, ?, ?)",
                (order_id, customer_id, sku, qty, utc_now()),
            )
            if fail_after_insert:
                raise RuntimeError("simulated crash before commit")
            self.db.execute(
                "INSERT INTO outbox (id, aggregate_id, event_type, payload, created_at) VALUES (?, ?, ?, ?, ?)",
                (event["id"], order_id, event["type"], json.dumps(event), utc_now()),
            )
        return order_id


class InMemoryBroker:
    def __init__(self):
        self.messages: list[dict] = []

    def publish(self, message: dict) -> None:
        self.messages.append(message)


class OutboxRelay:
    def __init__(self, db: sqlite3.Connection, broker: InMemoryBroker, batch_size: int = 100):
        self.db = db
        self.broker = broker
        self.batch_size = batch_size

    def run_once(self, *, crash_before_mark: bool = False) -> int:
        rows = self.db.execute(
            "SELECT id, payload FROM outbox WHERE sent_at IS NULL ORDER BY created_at, id LIMIT ?",
            (self.batch_size,),
        ).fetchall()
        for event_id, payload in rows:
            self.broker.publish(json.loads(payload))
            if crash_before_mark:
                raise RuntimeError("simulated relay crash after publish, before marking sent")
            with self.db:
                self.db.execute("UPDATE outbox SET sent_at = ? WHERE id = ?", (utc_now(), event_id))
        return len(rows)


# --------------------------------------------------------------------------
# Consumer: inventory service with an inbox
# --------------------------------------------------------------------------
INVENTORY_SCHEMA = """
CREATE TABLE IF NOT EXISTS stock (sku TEXT PRIMARY KEY, reserved INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS inbox (
    consumer TEXT NOT NULL,
    event_id TEXT NOT NULL,
    processed_at TEXT NOT NULL,
    PRIMARY KEY (consumer, event_id)
);
"""


class InventoryConsumer:
    NAME = "inventory-reservations"

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.executescript(INVENTORY_SCHEMA)

    def handle(self, event: dict) -> bool:
        """Apply the event once. Returns False if it was a duplicate."""
        try:
            with self.db:
                self.db.execute(
                    "INSERT INTO inbox (consumer, event_id, processed_at) VALUES (?, ?, ?)",
                    (self.NAME, event["id"], utc_now()),
                )
                data = event["data"]
                # Note: an increment is NOT naturally idempotent; the inbox makes it safe.
                self.db.execute(
                    "INSERT INTO stock (sku, reserved) VALUES (?, ?) "
                    "ON CONFLICT(sku) DO UPDATE SET reserved = reserved + excluded.reserved",
                    (data["sku"], data["qty"]),
                )
            return True
        except sqlite3.IntegrityError:
            return False  # already processed: the inbox insert hit the primary key

    def reserved(self, sku: str) -> int:
        row = self.db.execute("SELECT reserved FROM stock WHERE sku = ?", (sku,)).fetchone()
        return row[0] if row else 0


if __name__ == "__main__":
    orders_db = sqlite3.connect(":memory:")
    inventory_db = sqlite3.connect(":memory:")
    service, broker = OrderService(orders_db), InMemoryBroker()
    relay, consumer = OutboxRelay(orders_db, broker), InventoryConsumer(inventory_db)

    service.place_order("C-1", "TSHIRT-M", 2)
    try:
        relay.run_once(crash_before_mark=True)   # publishes, then "crashes"
    except RuntimeError as exc:
        print("relay:", exc)
    relay.run_once()                              # publishes the same event again
    print("messages on broker:", len(broker.messages))
    for message in broker.messages:
        print("handled" if consumer.handle(message) else "duplicate ignored", message["id"])
    print("reserved TSHIRT-M:", consumer.reserved("TSHIRT-M"))
