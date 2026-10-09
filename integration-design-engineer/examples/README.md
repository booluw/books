# Examples

Runnable companions to the chapters. All Python examples use **only the standard library** (Python 3.11+; tested with 3.13), so there is nothing to install.

| Folder | Chapter | What it shows |
|---|---|---|
| [`data-mapping/`](data-mapping/) | 4, 15 | A field mapping with decimal money, currency minor units, local business dates, Unicode normalisation, truncation warnings and error codes, tested with **golden files** |
| [`resilience/`](resilience/) | 8 | Error classification, retries with exponential backoff and full jitter, `Retry-After`, deadlines, a **circuit breaker** and a **token-bucket** rate limiter, tested with a fake clock |
| [`idempotent-api/`](idempotent-api/) | 6, 8 | Provider-side **idempotency keys**: atomic claim, request fingerprinting, replayed responses, concurrent duplicates and release on failure |
| [`outbox/`](outbox/) | 8 | The **transactional outbox** and an **inbox** consumer with SQLite: a relay crash produces a duplicate that the inbox absorbs |
| [`webhook-receiver/`](webhook-receiver/) | 7, 10 | A webhook receiver: HMAC over the raw body (Standard Webhooks headers), replay window, secret rotation, size cap, de-duplication, fast acknowledgement |
| [`openapi/`](openapi/) | 6 | An integration-grade **OpenAPI 3.1** document: cursor pagination, incremental sync, tombstones, idempotency keys, ETags, RFC 9457 errors, webhooks. Lints clean with Redocly CLI (apart from the expected `example.com` warnings) |
| [`asyncapi/`](asyncapi/) | 7 | An **AsyncAPI 3.1** document for Kafka events with CloudEvents headers. Validates with the AsyncAPI CLI |
| [`mcp-tool-server/`](mcp-tool-server/) | 18 | An **MCP-style tool server** (JSON-RPC `tools/list` and `tools/call`) with per-user authorisation, idempotent writes, instructive errors, rate limiting and audit logging |

## Run every test

```bash
cd integration-design-engineer/examples
python3 run_all_tests.py
```

## Validate the API documents (optional, needs Node.js)

```bash
npx @redocly/cli lint openapi/orders-api.yaml
npx @asyncapi/cli validate asyncapi/order-events.yaml
```

## A note on production use

These examples teach patterns. They leave out things production code needs, such as persistent storage with retention jobs, structured logging, metrics, tracing, configuration and secrets management. For MCP, use an official SDK, which implements the full current specification.
