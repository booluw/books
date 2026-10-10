import threading
import unittest

from idempotency import PaymentsApi

BODY = {"amount": "19.99", "currency": "USD", "customer": "cus_1"}


class IdempotencyTests(unittest.TestCase):
    def test_retry_after_timeout_does_not_charge_twice(self):
        api = PaymentsApi()
        first = api.create_payment("client-a", "key-1", BODY)
        retry = api.create_payment("client-a", "key-1", BODY)    # client never saw `first`
        self.assertEqual(first.status, 201)
        self.assertEqual(retry.status, 201)
        self.assertEqual(retry.body["id"], first.body["id"])
        self.assertTrue(retry.body["idempotent_replay"])
        self.assertEqual(api.payment_count(), 1)

    def test_key_reused_with_different_body_is_rejected(self):
        api = PaymentsApi()
        api.create_payment("client-a", "key-1", BODY)
        result = api.create_payment("client-a", "key-1", {**BODY, "amount": "99.00"})
        self.assertEqual(result.status, 422)

    def test_keys_are_scoped_per_client(self):
        api = PaymentsApi()
        api.create_payment("client-a", "same-key", BODY)
        api.create_payment("client-b", "same-key", BODY)
        self.assertEqual(api.payment_count(), 2)

    def test_missing_key_is_rejected(self):
        self.assertEqual(PaymentsApi().create_payment("client-a", None, BODY).status, 400)

    def test_concurrent_duplicates_execute_once(self):
        api = PaymentsApi(work_delay=0.2)
        results = []

        def call():
            results.append(api.create_payment("client-a", "key-race", BODY).status)

        threads = [threading.Thread(target=call) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(api.executions, 1)
        self.assertEqual(sorted(results), [201, 409, 409, 409, 409])
        self.assertEqual(api.payment_count(), 1)

    def test_downstream_failure_releases_key_for_retry(self):
        api = PaymentsApi()
        failing = {**BODY, "amount": "13.13"}
        self.assertEqual(api.create_payment("client-a", "key-x", failing).status, 503)
        # The claim was released, so the same key can be retried (and fail/succeed again).
        self.assertEqual(api.create_payment("client-a", "key-x", failing).status, 503)
        self.assertEqual(api.executions, 2)


if __name__ == "__main__":
    unittest.main()
