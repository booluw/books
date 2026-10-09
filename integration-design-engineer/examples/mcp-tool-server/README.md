# An MCP-style tool server (Chapter 18)

`server.py` is a teaching-sized server that speaks JSON-RPC 2.0 over HTTP and implements MCP's `tools/list` and `tools/call`, using MCP result shapes (`content`, `structuredContent`, `isError`). It exposes three **intent-level** tools for a customer-support agent: `get_order_status`, `list_recent_orders` and `start_return`.

What to look at:

- **Per-user authorisation in the tool layer.** The bearer token identifies the customer, and every tool checks ownership. A prompt-injected request for another customer's order fails, with the same message as "not found", so IDs cannot be probed.
- **Idempotent write.** `start_return` is keyed on `(order_id, sku)`; agent retries return the existing return.
- **Instructive errors** the model can recover from ("Order ids look like ORD-10001").
- **Stateless handling**, so any instance can serve any request (as in the 2026-07-28 MCP revision).
- **Rate limit per user** and an **audit log** that redacts free text.

```bash
python3 server.py      # http://127.0.0.1:8765, tokens: token-alice, token-bob
curl -s localhost:8765 -H 'Authorization: Bearer token-alice' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_recent_orders","arguments":{}}}'
python3 -m unittest -v
```

> This is not a full MCP implementation: it omits transport negotiation, discovery, OAuth protected-resource metadata and extensions. Build real servers with an official MCP SDK, and apply these integration lessons inside the tool handlers.
