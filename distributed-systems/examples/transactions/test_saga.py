import random
import unittest

from saga import Order, OrchestratorCrash, Saga, Shop

ORDER = Order("A", "widget", 2, 40)


def assert_all_or_nothing(test, shop, order, outcome, start_stock=5, context=""):
    """Completed: every effect exactly once. Compensated: no effect remains."""
    if outcome == "completed":
        test.assertEqual(shop.inventory.stock[order.sku], start_stock - order.qty, context)
        test.assertEqual(shop.payments.net_charged(order.id), order.amount, context)
        test.assertIn(order.id, shop.shipping.bookings, context)
    else:
        test.assertEqual(outcome, "compensated", context)
        test.assertEqual(shop.inventory.stock[order.sku], start_stock, context)
        test.assertEqual(shop.payments.net_charged(order.id), 0, context)
        test.assertNotIn(order.id, shop.shipping.bookings, context)
        test.assertNotIn(order.id, shop.inventory.reservations, context)


class SagaTests(unittest.TestCase):
    def test_happy_path_completes(self):
        shop = Shop.create()
        saga = Saga(shop, ORDER)
        self.assertEqual(saga.run(), "completed")
        assert_all_or_nothing(self, shop, ORDER, "completed")
        self.assertEqual(shop.payments.charges("A"), 1)

    def test_business_failure_at_each_step_is_fully_compensated(self):
        failures = {
            "reserve_stock": dict(stock={"widget": 1}),
            "charge_card": dict(card_limit=10),
            "book_shipping": dict(capacity=0),
        }
        for step, settings in failures.items():
            with self.subTest(step):
                shop = Shop.create(**settings)
                start = shop.inventory.stock["widget"]
                saga = Saga(shop, ORDER)
                self.assertEqual(saga.run(), "compensated")
                assert_all_or_nothing(self, shop, ORDER, "compensated", start_stock=start)
                undone = [r[1] for r in saga.log if r[0] == "compensated"]
                done = [r[1] for r in saga.log if r[0] == "done"]
                self.assertEqual(undone, list(reversed(done)))   # reverse order

    def test_unknown_outcome_is_compensated_too(self):
        # The charge happens every time but its response is always lost.
        shop = Shop.create()
        shop.payments.lose_response = 1.0
        saga = Saga(shop, ORDER, compensation_attempts=1)
        outcome = saga.run()
        self.assertEqual(shop.payments.charges("A"), 1)          # 4 attempts, one charge
        self.assertEqual(shop.payments.calls, 4 + 1)
        compensating = next(r for r in saga.log if r[0] == "compensating")
        self.assertIn("charge_card", compensating[1])            # possibly-done step undone
        # The refund's response is lost too, so with one attempt it is stuck:
        self.assertIsNone(outcome)
        self.assertEqual(saga.log[-1], ("stuck", "charge_card"))
        shop.payments.lose_response = 0.0
        # ...and a later retry with the same idempotency key finishes the job.
        saga.compensation_attempts = 5
        self.assertEqual(saga.resume(), "compensated")
        assert_all_or_nothing(self, shop, ORDER, "compensated")

    def test_exponential_backoff(self):
        shop = Shop.create()
        shop.inventory.fail_before = 1.0
        saga = Saga(shop, ORDER, max_attempts=4, compensation_attempts=1)
        self.assertIsNone(saga.run())          # inventory unreachable: stuck, not finished
        self.assertAlmostEqual(saga.backoff_waited, 0.1 + 0.2 + 0.4)
        self.assertEqual(saga.log[-1], ("stuck", "reserve_stock"))

    def test_randomised_failures_end_all_done_or_fully_compensated(self):
        outcomes = {"completed": 0, "compensated": 0}
        for seed in range(400):
            rng = random.Random(seed)
            shop = Shop.create(seed=seed, card_limit=rng.choice([1000, 1000, 10]),
                               capacity=rng.choice([10, 10, 0]),
                               fail_before=rng.uniform(0, 0.4),
                               lose_response=rng.uniform(0, 0.4))
            saga = Saga(shop, ORDER, max_attempts=rng.randint(1, 5))
            outcome = saga.run()
            assert_all_or_nothing(self, shop, ORDER, outcome, context=f"seed {seed}")
            self.assertLessEqual(shop.payments.charges("A"), 1, f"seed {seed}")
            outcomes[outcome] += 1
        self.assertGreater(min(outcomes.values()), 100)

    def test_idempotent_retries_never_double_charge_but_naive_retries_do(self):
        double = {True: 0, False: 0}
        for seed in range(200):
            for idempotent in (True, False):
                shop = Shop.create(seed=seed, lose_response=0.4, idempotent_payments=idempotent)
                Saga(shop, ORDER).run()
                if shop.payments.charges("A") > 1:
                    double[idempotent] += 1
        self.assertEqual(double[True], 0)
        self.assertGreater(double[False], 20)

    def test_orchestrator_crash_at_every_log_position_then_resume(self):
        for capacity in (10, 0):
            reference = Saga(Shop.create(capacity=capacity), ORDER)
            expected = reference.run()
            for crash_at in range(1, len(reference.log) + 1):
                shop = Shop.create(capacity=capacity)
                saga = Saga(shop, ORDER, crash_before_record=crash_at)
                with self.assertRaises(OrchestratorCrash):
                    saga.run()
                self.assertEqual(saga.resume(), expected, f"{capacity}/{crash_at}")
                assert_all_or_nothing(self, shop, ORDER, expected)
                self.assertLessEqual(shop.payments.charges("A"), 1)

    def test_intermediate_states_are_visible_to_other_readers(self):
        shop = Shop.create(capacity=0)
        seen_charged = []
        for _ in Saga(shop, ORDER).execute():
            seen_charged.append(shop.payments.net_charged("A"))   # a concurrent reader
        self.assertIn(40, seen_charged)       # the reader saw a charge...
        self.assertEqual(seen_charged[-1], 0)  # ...for an order that never happened

    def test_interleaved_sagas_lose_a_sale(self):
        shop = Shop.create(stock={"widget": 2}, capacity=0)
        a = Saga(shop, Order("A", "widget", 2, 40))
        b = Saga(shop, Order("B", "widget", 1, 20))
        steps_a, steps_b = a.execute(), b.execute()
        next(steps_a)                          # A reserves both widgets
        self.assertEqual(b.run(), "compensated")   # B sees no stock and gives up
        for _ in steps_a:
            pass
        self.assertEqual(a.outcome, "compensated")
        self.assertEqual(shop.inventory.stock["widget"], 2)   # the stock B wanted is back


if __name__ == "__main__":
    unittest.main()
