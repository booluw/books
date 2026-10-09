"""A teaching-sized, MCP-style tool server (Chapter 18), standard library only.

It speaks JSON-RPC 2.0 over HTTP POST and implements the two methods at the heart
of MCP tool use, `tools/list` and `tools/call`, using MCP's result shapes
(`tools` with `inputSchema`; `content` + `structuredContent` + `isError`).

It is deliberately simplified so the *integration* lessons stand out. For real
servers use an official MCP SDK, which implements the full, current specification
(transport details, discovery, OAuth protected-resource metadata, extensions).

Integration lessons demonstrated:
  * Intent-level tools with precise descriptions and schemas (not raw API passthrough).
  * Per-USER authorisation enforced in the tool layer: a customer can only see their own orders.
  * Stateless request handling: any instance behind a load balancer can serve any request.
  * Idempotent writes: start_return is keyed on (order, sku), so agent retries are harmless.
  * Concise, structured results and instructive errors that help the model recover.
  * Per-user rate limiting and an audit log of every tool call.
"""
from __future__ import annotations

import json
import re
import time
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------------------
# Fake systems of record (stand-ins for Shopify / NetSuite / a 3PL)
# ---------------------------------------------------------------------------
ORDERS = {
    "ORD-10001": {"customer": "cus_alice", "status": "shipped", "carrier": "DHL",
                  "tracking": "JD014600006281234567", "lines": [{"sku": "TSHIRT-M", "qty": 2}],
                  "placed_at": "2026-10-01T10:15:00Z"},
    "ORD-10002": {"customer": "cus_alice", "status": "processing", "carrier": None, "tracking": None,
                  "lines": [{"sku": "CAP-01", "qty": 1}], "placed_at": "2026-10-07T18:02:00Z"},
    "ORD-20001": {"customer": "cus_bob", "status": "delivered", "carrier": "UPS",
                  "tracking": "1Z999AA10123456784", "lines": [{"sku": "MUG-1", "qty": 1}],
                  "placed_at": "2026-09-20T08:00:00Z"},
}
RETURNS: dict[tuple[str, str], dict] = {}

# Access tokens -> user. In production these are OAuth access tokens issued for this
# server's audience, validated per request (signature, issuer, audience, expiry, scopes).
TOKENS = {"token-alice": "cus_alice", "token-bob": "cus_bob"}

AUDIT_LOG: list[dict] = []
RATE_LIMIT_PER_MINUTE = 30
_calls: dict[str, list[float]] = defaultdict(list)

ORDER_ID_PATTERN = r"^ORD-\d{5}$"

TOOLS = [
    {
        "name": "get_order_status",
        "description": (
            "Get the current fulfilment status of ONE of the signed-in customer's orders, including "
            "carrier and tracking number when shipped. Use when the customer asks where an order is. "
            "Read-only."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"order_id": {"type": "string", "pattern": ORDER_ID_PATTERN,
                                        "description": "Order id, e.g. ORD-10001"}},
            "required": ["order_id"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True},
    },
    {
        "name": "list_recent_orders",
        "description": "List the signed-in customer's most recent orders (id, date, status). Read-only.",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5}},
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True},
    },
    {
        "name": "start_return",
        "description": (
            "Start a return for one item of a delivered or shipped order belonging to the signed-in customer. "
            "Creates a return request only; it does NOT issue a refund. Safe to retry: calling again for "
            "the same order and SKU returns the existing return."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "pattern": ORDER_ID_PATTERN},
                "sku": {"type": "string"},
                "reason": {"type": "string", "enum": ["wrong_size", "damaged", "not_as_described", "other"]},
            },
            "required": ["order_id", "sku", "reason"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
    },
]


class ToolError(Exception):
    """An error the model should see and can act on (returned with isError=true)."""


def _owned_order(user: str, order_id: str) -> dict:
    if not re.match(ORDER_ID_PATTERN, order_id or ""):
        raise ToolError(f"'{order_id}' is not a valid order id. Order ids look like ORD-10001.")
    order = ORDERS.get(order_id)
    # Same message for "missing" and "not yours", so the tool cannot be used to probe other
    # customers' order ids (avoids Broken Object Level Authorization, OWASP API1).
    if order is None or order["customer"] != user:
        raise ToolError(f"No order {order_id} found for this customer. Use list_recent_orders to see valid ids.")
    return order


def get_order_status(user: str, args: dict) -> dict:
    order = _owned_order(user, args.get("order_id"))
    result = {"order_id": args["order_id"], "status": order["status"]}
    if order["tracking"]:
        result |= {"carrier": order["carrier"], "tracking_number": order["tracking"]}
    return result


def list_recent_orders(user: str, args: dict) -> dict:
    limit = min(max(int(args.get("limit", 5)), 1), 10)
    mine = sorted(((oid, o) for oid, o in ORDERS.items() if o["customer"] == user),
                  key=lambda item: item[1]["placed_at"], reverse=True)[:limit]
    return {"orders": [{"order_id": oid, "placed_at": o["placed_at"], "status": o["status"]} for oid, o in mine]}


def start_return(user: str, args: dict) -> dict:
    order = _owned_order(user, args.get("order_id"))
    if order["status"] not in ("shipped", "delivered"):
        raise ToolError(f"Order {args['order_id']} is '{order['status']}'; returns can start once it has shipped.")
    if args.get("sku") not in {line["sku"] for line in order["lines"]}:
        raise ToolError(f"SKU {args.get('sku')} is not on order {args['order_id']}.")
    key = (args["order_id"], args["sku"])          # idempotency key derived from the request
    if key not in RETURNS:
        RETURNS[key] = {"return_id": f"RET-{len(RETURNS) + 1:05d}", "status": "requested", "reason": args["reason"]}
        created = True
    else:
        created = False
    return {**RETURNS[key], "order_id": args["order_id"], "sku": args["sku"], "newly_created": created}


HANDLERS = {"get_order_status": get_order_status, "list_recent_orders": list_recent_orders,
            "start_return": start_return}


def rate_limited(user: str, now: float) -> bool:
    window = [t for t in _calls[user] if now - t < 60]
    _calls[user] = window
    if len(window) >= RATE_LIMIT_PER_MINUTE:
        return True
    window.append(now)
    return False


def handle_rpc(user: str, request: dict) -> dict:
    rpc_id = request.get("id")
    method = request.get("method")
    if request.get("jsonrpc") != "2.0" or not isinstance(method, str):
        return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32600, "message": "Invalid Request"}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {"tools": TOOLS}}
    if method != "tools/call":
        return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

    params = request.get("params") or {}
    name, args = params.get("name"), params.get("arguments") or {}
    if name not in HANDLERS:
        return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32602, "message": f"Unknown tool: {name}"}}
    started = time.time()
    if rate_limited(user, started):
        payload, is_error = {"error": "Rate limit reached for this user. Wait a minute before calling tools again."}, True
    else:
        try:
            payload, is_error = HANDLERS[name](user, args), False
        except ToolError as exc:
            payload, is_error = {"error": str(exc)}, True
    AUDIT_LOG.append({"ts": started, "user": user, "tool": name,
                      "args": {k: v for k, v in args.items() if k != "reason"},  # redact free text
                      "is_error": is_error, "ms": round((time.time() - started) * 1000, 2)})
    return {"jsonrpc": "2.0", "id": rpc_id, "result": {
        "content": [{"type": "text", "text": json.dumps(payload)}],
        "structuredContent": payload,
        "isError": is_error,
    }}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        auth = self.headers.get("Authorization", "")
        user = TOKENS.get(auth.removeprefix("Bearer ").strip())
        if user is None:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Bearer realm="orders-tools"')
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length > 64 * 1024:
            self.send_response(413)
            self.end_headers()
            return
        try:
            request = json.loads(self.rfile.read(length))
            response = handle_rpc(user, request)
        except json.JSONDecodeError:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        body = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def make_server(host="127.0.0.1", port=8765) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == "__main__":
    print("MCP-style tool server on http://127.0.0.1:8765 (tokens: token-alice, token-bob)")
    make_server().serve_forever()
