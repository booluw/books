"""A safe webhook receiver (Chapter 7, section 7.9), using only the standard library.

Signature scheme: the Standard Webhooks convention (standardwebhooks.com):
    headers  webhook-id, webhook-timestamp, webhook-signature
    signed   f"{webhook_id}.{timestamp}.{raw_body}"
    sig      "v1," + base64(HMAC-SHA256(secret, signed))
Several space-separated signatures may be present (secret rotation).

What it demonstrates:
  1. Verify the HMAC over the RAW body bytes, with a constant-time comparison.
  2. Reject stale or future timestamps (replay protection).
  3. Accept old and new secrets during rotation.
  4. Cap body size.
  5. De-duplicate on the webhook id.
  6. Enqueue and acknowledge fast; a worker processes asynchronously.

Run:   python receiver.py            (listens on 127.0.0.1:8080)
Send:  python send_test_webhook.py   (signs and posts a sample event)
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import queue
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_BODY_BYTES = 256 * 1024
TOLERANCE_SECONDS = 5 * 60


def sign(secret: bytes, webhook_id: str, timestamp: int, body: bytes) -> str:
    signed = webhook_id.encode() + b"." + str(timestamp).encode() + b"." + body
    digest = hmac.new(secret, signed, hashlib.sha256).digest()
    return "v1," + base64.b64encode(digest).decode()


class VerificationError(Exception):
    pass


def verify(secrets: list[bytes], headers: dict, body: bytes, now: float | None = None) -> str:
    """Return the webhook id if the request is authentic; raise VerificationError otherwise."""
    h = {k.lower(): v for k, v in headers.items()}
    webhook_id = h.get("webhook-id")
    timestamp = h.get("webhook-timestamp")
    signatures = h.get("webhook-signature", "")
    if not webhook_id or not timestamp or not signatures:
        raise VerificationError("missing webhook headers")
    try:
        ts = int(timestamp)
    except ValueError:
        raise VerificationError("bad timestamp") from None
    now = time.time() if now is None else now
    if abs(now - ts) > TOLERANCE_SECONDS:
        raise VerificationError("timestamp outside tolerance (possible replay)")
    presented = [s for s in signatures.split(" ") if s.startswith("v1,")]
    for secret in secrets:                      # old + new secret during rotation
        expected = sign(secret, webhook_id, ts, body)
        if any(hmac.compare_digest(expected, p) for p in presented):
            return webhook_id
    raise VerificationError("no valid signature")


class DedupStore:
    """Remembers processed webhook ids. Use a database table with a TTL in production."""

    def __init__(self):
        self._seen: set[str] = set()
        self._lock = threading.Lock()

    def first_time(self, webhook_id: str) -> bool:
        with self._lock:
            if webhook_id in self._seen:
                return False
            self._seen.add(webhook_id)
            return True


class WebhookApp:
    def __init__(self, secrets: list[bytes]):
        self.secrets = secrets
        self.work: queue.Queue = queue.Queue()
        self.dedup = DedupStore()
        self.processed: list[dict] = []
        self.rejected = 0

    def handle(self, headers: dict, body: bytes) -> int:
        """Return the HTTP status to send. Never does slow work inline."""
        try:
            webhook_id = verify(self.secrets, headers, body)
        except VerificationError:
            self.rejected += 1
            return 401
        try:
            event = json.loads(body)
        except json.JSONDecodeError:
            return 400
        if not self.dedup.first_time(webhook_id):
            return 200  # duplicate delivery: acknowledge, do nothing
        self.work.put(event)
        return 202

    def worker(self, stop: threading.Event) -> None:
        while not stop.is_set():
            try:
                event = self.work.get(timeout=0.1)
            except queue.Empty:
                continue
            # Real systems: fetch current state from the provider (thin-event pattern),
            # apply idempotently, and dead-letter after N failures.
            self.processed.append(event)
            self.work.task_done()


def make_handler(app: WebhookApp):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802 (http.server naming)
            length = int(self.headers.get("Content-Length", "0"))
            if length > MAX_BODY_BYTES:
                self.send_response(413)
                self.end_headers()
                return
            raw = self.rfile.read(length)          # keep the RAW bytes for the HMAC
            status = app.handle(dict(self.headers), raw)
            self.send_response(status)
            self.end_headers()

        def log_message(self, fmt, *args):  # keep test output quiet; log structured data in real code
            pass

    return Handler


def serve(app: WebhookApp, host="127.0.0.1", port=8080):
    server = ThreadingHTTPServer((host, port), make_handler(app))
    stop = threading.Event()
    threading.Thread(target=app.worker, args=(stop,), daemon=True).start()
    return server, stop


if __name__ == "__main__":
    application = WebhookApp([b"whsec_demo_secret"])
    srv, _ = serve(application)
    print("Listening on http://127.0.0.1:8080 (Ctrl+C to stop)")
    srv.serve_forever()
