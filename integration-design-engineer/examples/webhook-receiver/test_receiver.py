import json
import threading
import time
import unittest
import urllib.error
import urllib.request

from receiver import TOLERANCE_SECONDS, VerificationError, WebhookApp, serve, sign, verify

OLD, NEW = b"old-secret", b"new-secret"


def signed_headers(secret, body, webhook_id="msg_1", ts=None):
    ts = int(time.time()) if ts is None else ts
    return {"webhook-id": webhook_id, "webhook-timestamp": str(ts),
            "webhook-signature": sign(secret, webhook_id, ts, body)}


class VerifyTests(unittest.TestCase):
    body = b'{"type":"order.paid"}'

    def test_valid_signature(self):
        self.assertEqual(verify([NEW], signed_headers(NEW, self.body), self.body), "msg_1")

    def test_tampered_body_rejected(self):
        headers = signed_headers(NEW, self.body)
        with self.assertRaises(VerificationError):
            verify([NEW], headers, b'{"type":"order.refunded"}')

    def test_reserialised_json_breaks_signature(self):
        # Why you must verify the RAW bytes: re-serialising changes whitespace/key order.
        headers = signed_headers(NEW, self.body)
        reserialised = json.dumps(json.loads(self.body)).encode()
        self.assertNotEqual(reserialised, self.body)
        with self.assertRaises(VerificationError):
            verify([NEW], headers, reserialised)

    def test_stale_timestamp_rejected(self):
        old_ts = int(time.time()) - TOLERANCE_SECONDS - 1
        with self.assertRaises(VerificationError):
            verify([NEW], signed_headers(NEW, self.body, ts=old_ts), self.body)

    def test_rotation_accepts_old_and_new_secrets(self):
        self.assertEqual(verify([NEW, OLD], signed_headers(OLD, self.body), self.body), "msg_1")
        self.assertEqual(verify([NEW, OLD], signed_headers(NEW, self.body), self.body), "msg_1")

    def test_missing_headers_rejected(self):
        with self.assertRaises(VerificationError):
            verify([NEW], {}, self.body)


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = WebhookApp([NEW, OLD])
        cls.server, cls.stop = serve(cls.app, port=0)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.stop.set()
        cls.server.shutdown()

    def post(self, body, headers):
        request = urllib.request.Request(f"http://127.0.0.1:{self.port}/hook", data=body,
                                         method="POST", headers=headers)
        try:
            with urllib.request.urlopen(request) as response:
                return response.status
        except urllib.error.HTTPError as err:
            return err.code

    def test_end_to_end_with_duplicate(self):
        body = b'{"type":"order.paid","data":{"order_id":"ORD-1"}}'
        headers = signed_headers(NEW, body, webhook_id="msg_e2e")
        self.assertEqual(self.post(body, headers), 202)
        self.assertEqual(self.post(body, headers), 200)  # duplicate acknowledged, not re-queued
        self.app.work.join()
        orders = [e["data"]["order_id"] for e in self.app.processed]
        self.assertEqual(orders.count("ORD-1"), 1)

    def test_bad_signature_is_401(self):
        body = b'{"type":"x"}'
        headers = signed_headers(b"wrong", body, webhook_id="msg_bad")
        self.assertEqual(self.post(body, headers), 401)

    def test_oversized_body_is_413(self):
        body = b"x" * (256 * 1024 + 1)
        self.assertEqual(self.post(body, signed_headers(NEW, body, webhook_id="msg_big")), 413)


if __name__ == "__main__":
    unittest.main()
