"""Provider-side idempotency keys for a POST endpoint (Chapter 6 §6.10, Chapter 8 §8.4).

Rules implemented:
  * The key is claimed atomically (INSERT with a unique constraint) BEFORE the work runs,
    so two concurrent retries cannot both execute.
  * The request body is fingerprinted; reusing a key with a different body -> 422.
  * A repeat while the first request is still running -> 409 (client retries later).
  * A repeat after completion replays the stored response; the work is not re-executed.
  * Keys are scoped per client and expire after a retention window.
  * If the work fails with a server error, the claim is released so the client can retry.

The "payment" is simulated; swap execute_payment() for a real side effect.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass

RETENTION_SECONDS = 24 * 3600

SCHEMA = """
CREATE TABLE IF NOT EXISTS idempotency_keys (
    client_id TEXT NOT NULL,
    key TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    status TEXT NOT NULL,              -- 'in_progress' | 'done'
    response_status INTEGER,
    response_body TEXT,
    created_at REAL NOT NULL,
    PRIMARY KEY (client_id, key)
);
CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY, client_id TEXT, amount TEXT, currency TEXT
);
"""


@dataclass
class HttpResult:
    status: int
    body: dict


def fingerprint(body: dict) -> str:
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


class PaymentsApi:
    def __init__(self, db_path: str = ":memory:", work_delay: float = 0.0):
        self.db = sqlite3.connect(db_path, check_same_thread=False, isolation_level=None)
        self.db.executescript(SCHEMA)
        self.lock = threading.Lock()  # SQLite connection is shared across threads in this demo
        self.work_delay = work_delay
        self.executions = 0

    def _sql(self, sql, params=()):
        with self.lock:
            return self.db.execute(sql, params).fetchall()

    def execute_payment(self, client_id: str, body: dict) -> HttpResult:
        time.sleep(self.work_delay)             # simulate a slow downstream call
        self.executions += 1
        if body.get("amount") == "13.13":       # test hook: simulate a downstream outage
            raise ConnectionError("payment processor unavailable")
        payment_id = f"pay_{uuid.uuid4().hex[:10]}"
        self._sql("INSERT INTO payments VALUES (?, ?, ?, ?)",
                  (payment_id, client_id, body["amount"], body["currency"]))
        return HttpResult(201, {"id": payment_id, "amount": body["amount"], "currency": body["currency"]})

    def create_payment(self, client_id: str, idempotency_key: str | None, body: dict) -> HttpResult:
        if not idempotency_key:
            return HttpResult(400, {"type": "about:blank", "title": "Idempotency-Key header is required"})
        fp = fingerprint(body)
        now = time.time()
        self._sql("DELETE FROM idempotency_keys WHERE created_at < ?", (now - RETENTION_SECONDS,))
        try:
            self._sql(
                "INSERT INTO idempotency_keys (client_id, key, fingerprint, status, created_at) "
                "VALUES (?, ?, ?, 'in_progress', ?)",
                (client_id, idempotency_key, fp, now),
            )
        except sqlite3.IntegrityError:
            (stored_fp, status, resp_status, resp_body), = self._sql(
                "SELECT fingerprint, status, response_status, response_body FROM idempotency_keys "
                "WHERE client_id = ? AND key = ?", (client_id, idempotency_key))
            if stored_fp != fp:
                return HttpResult(422, {"title": "Idempotency-Key reused with a different request body"})
            if status == "in_progress":
                return HttpResult(409, {"title": "A request with this Idempotency-Key is in progress"})
            replay = json.loads(resp_body)
            replay["idempotent_replay"] = True
            return HttpResult(resp_status, replay)

        try:
            result = self.execute_payment(client_id, body)
        except ConnectionError:
            # Nothing was charged: release the claim so a retry can run the work.
            self._sql("DELETE FROM idempotency_keys WHERE client_id = ? AND key = ?", (client_id, idempotency_key))
            return HttpResult(503, {"title": "Payment processor unavailable, retry later"})
        self._sql(
            "UPDATE idempotency_keys SET status = 'done', response_status = ?, response_body = ? "
            "WHERE client_id = ? AND key = ?",
            (result.status, json.dumps(result.body), client_id, idempotency_key),
        )
        return result

    def payment_count(self) -> int:
        return self._sql("SELECT COUNT(*) FROM payments")[0][0]
