import random
import unittest

from resilience import (CircuitBreaker, CircuitOpen, Outcome, Response, RetriesExhausted,
                        TokenBucket, classify, retry_call)


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def scripted(*responses):
    """Return a send() that replays the given responses (or raises given exceptions)."""
    queue = list(responses)
    calls = []

    def send():
        calls.append(1)
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    send.calls = calls
    return send


class ClassifyTests(unittest.TestCase):
    def test_classification_table(self):
        self.assertIs(classify(201, idempotent=False), Outcome.SUCCESS)
        self.assertIs(classify(400, idempotent=True), Outcome.FAIL_PERMANENT)
        self.assertIs(classify(422, idempotent=True), Outcome.FAIL_PERMANENT)
        self.assertIs(classify(401, idempotent=True), Outcome.REFRESH_AUTH)
        self.assertIs(classify(429, idempotent=False), Outcome.RETRY)
        self.assertIs(classify(503, idempotent=False), Outcome.RETRY)
        self.assertIs(classify(500, idempotent=True), Outcome.RETRY)
        # A 500 or a timeout on a non-idempotent POST has an unknown outcome:
        self.assertIs(classify(500, idempotent=False), Outcome.FAIL_PERMANENT)
        self.assertIs(classify(None, idempotent=False), Outcome.FAIL_PERMANENT)
        self.assertIs(classify(None, idempotent=True), Outcome.RETRY)


class RetryTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.kwargs = dict(sleep=self.clock.sleep, clock=self.clock, rng=random.Random(42))

    def test_succeeds_after_transient_errors(self):
        send = scripted(Response(503, {}), ConnectionError(), Response(200, {}, "ok"))
        result = retry_call(send, idempotent=True, **self.kwargs)
        self.assertEqual(result.body, "ok")
        self.assertEqual(len(send.calls), 3)

    def test_permanent_error_is_not_retried(self):
        send = scripted(Response(422, {}))
        with self.assertRaises(RetriesExhausted) as ctx:
            retry_call(send, idempotent=True, **self.kwargs)
        self.assertEqual(ctx.exception.attempts, 1)

    def test_retry_after_is_honoured(self):
        send = scripted(Response(429, {"Retry-After": "12"}), Response(200, {}))
        retry_call(send, idempotent=False, **self.kwargs)
        self.assertGreaterEqual(self.clock.now, 12)

    def test_backoff_never_exceeds_cap(self):
        send = scripted(*[Response(503, {})] * 6)
        with self.assertRaises(RetriesExhausted):
            retry_call(send, idempotent=True, max_attempts=6, base=1, cap=2, **self.kwargs)
        self.assertLessEqual(self.clock.now, 2 * 5)

    def test_deadline_stops_retries(self):
        send = scripted(*[Response(503, {"Retry-After": "10"})] * 5)
        with self.assertRaises(RetriesExhausted):
            retry_call(send, idempotent=True, deadline=15, **self.kwargs)
        self.assertLess(self.clock.now, 15)
        self.assertEqual(len(send.calls), 2)

    def test_auth_refreshed_once_only(self):
        refreshes = []
        send = scripted(Response(401, {}), Response(401, {}))
        with self.assertRaises(RetriesExhausted):
            retry_call(send, idempotent=True, refresh_auth=lambda: refreshes.append(1), **self.kwargs)
        self.assertEqual(len(refreshes), 1)


class CircuitBreakerTests(unittest.TestCase):
    def test_opens_fails_fast_then_recovers(self):
        clock = FakeClock()
        cb = CircuitBreaker(window=10, threshold=0.5, min_calls=4, cooldown=30, half_open_trials=2, clock=clock)
        for _ in range(4):
            cb.call(lambda: Response(503, {}))
        self.assertEqual(cb.state, CircuitBreaker.OPEN)
        with self.assertRaises(CircuitOpen):
            cb.call(lambda: Response(200, {}))
        clock.sleep(30)
        cb.call(lambda: Response(200, {}))
        self.assertEqual(cb.state, CircuitBreaker.HALF_OPEN)
        cb.call(lambda: Response(200, {}))
        self.assertEqual(cb.state, CircuitBreaker.CLOSED)

    def test_half_open_failure_reopens(self):
        clock = FakeClock()
        cb = CircuitBreaker(min_calls=2, threshold=0.5, cooldown=5, clock=clock)
        cb.call(lambda: Response(500, {}))
        cb.call(lambda: Response(500, {}))
        clock.sleep(5)
        cb.call(lambda: Response(500, {}))
        self.assertEqual(cb.state, CircuitBreaker.OPEN)

    def test_client_errors_do_not_open_the_circuit(self):
        cb = CircuitBreaker(min_calls=2, threshold=0.5)
        for _ in range(5):
            cb.call(lambda: Response(422, {}))
        self.assertEqual(cb.state, CircuitBreaker.CLOSED)


class TokenBucketTests(unittest.TestCase):
    def test_burst_then_steady_rate(self):
        clock = FakeClock()
        bucket = TokenBucket(rate=2, capacity=5, clock=clock)
        self.assertEqual(sum(bucket.try_acquire() for _ in range(10)), 5)  # burst of 5
        self.assertAlmostEqual(bucket.wait_time(), 0.5)
        clock.sleep(1)
        self.assertEqual(sum(bucket.try_acquire() for _ in range(10)), 2)  # 2 per second


if __name__ == "__main__":
    unittest.main()
