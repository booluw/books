import sqlite3
import unittest

from outbox import InMemoryBroker, InventoryConsumer, OrderService, OutboxRelay


class OutboxTests(unittest.TestCase):
    def setUp(self):
        self.orders_db = sqlite3.connect(":memory:")
        self.service = OrderService(self.orders_db)
        self.broker = InMemoryBroker()
        self.relay = OutboxRelay(self.orders_db, self.broker)
        self.consumer = InventoryConsumer(sqlite3.connect(":memory:"))

    def count(self, table):
        return self.orders_db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_order_and_event_commit_together(self):
        self.service.place_order("C-1", "SKU-1", 1)
        self.assertEqual(self.count("orders"), 1)
        self.assertEqual(self.count("outbox"), 1)

    def test_crash_before_commit_leaves_neither(self):
        with self.assertRaises(RuntimeError):
            self.service.place_order("C-1", "SKU-1", 1, fail_after_insert=True)
        self.assertEqual(self.count("orders"), 0)
        self.assertEqual(self.count("outbox"), 0)

    def test_relay_publishes_each_event_and_marks_it_sent(self):
        for _ in range(3):
            self.service.place_order("C-1", "SKU-1", 1)
        self.assertEqual(self.relay.run_once(), 3)
        self.assertEqual(self.relay.run_once(), 0)
        self.assertEqual(len(self.broker.messages), 3)

    def test_relay_crash_causes_duplicate_which_inbox_absorbs(self):
        self.service.place_order("C-1", "SKU-1", 2)
        with self.assertRaises(RuntimeError):
            self.relay.run_once(crash_before_mark=True)
        self.relay.run_once()
        self.assertEqual(len(self.broker.messages), 2)       # at-least-once: duplicate published
        results = [self.consumer.handle(m) for m in self.broker.messages]
        self.assertEqual(results, [True, False])              # second one ignored
        self.assertEqual(self.consumer.reserved("SKU-1"), 2)  # effectively once

    def test_events_are_cloudevents(self):
        self.service.place_order("C-9", "SKU-9", 1)
        self.relay.run_once()
        event = self.broker.messages[0]
        for attribute in ("specversion", "id", "source", "type"):
            self.assertIn(attribute, event)


if __name__ == "__main__":
    unittest.main()
