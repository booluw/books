# Exercises: Chapter 6, API Design

## Questions

1. Redesign these endpoints in resource-oriented REST: `POST /getCustomer`, `POST /createOrder`, `GET /deleteOrder?id=5`, `POST /orders/5/doCancel`.
2. Why is offset pagination unsafe for an integration that syncs a table receiving frequent inserts? Show what cursor pagination's SQL looks like.
3. A consumer uses `GET /orders?updated_since=<last run start>`. Name three ways it can miss changes, and a fix for each.
4. Write an RFC 9457 problem-details response for "SKU ABC-1 is discontinued" on line 3 of an order.
5. Design the idempotency behaviour for `POST /refunds`. What happens on (a) a retry with the same key and body, (b) the same key with a different amount, (c) a retry while the first request is still processing?
6. You must rename `customerName` to `customer_name` in a public API with 40 consumers. Describe the full process.
7. Extend `examples/openapi/orders-api.yaml` with a `POST /orders/batch` operation that accepts up to 100 orders and returns per-item results. Lint it with Redocly.
8. When would you choose GraphQL over REST for an integration API? When gRPC?

## Solutions

1. `GET /customers/{id}`; `POST /orders`; `DELETE /orders/5`; `POST /orders/5/cancellations` (or `POST /orders/5:cancel`).
2. New rows inserted before the current offset shift later rows, so pages skip or repeat records. Cursor (keyset): `SELECT … WHERE (updated_at, id) > (:last_ts, :last_id) ORDER BY updated_at, id LIMIT :n`.
3. Clock skew or late-committing transactions stamp rows earlier than the watermark: overlap the window and de-duplicate, or use a monotonic change sequence or sync token. Ties at the same timestamp across a page boundary: use a compound cursor `(updated_at, id)`. Deletes are invisible: tombstone endpoint or soft-delete flag, plus periodic reconciliation.
4.
```json
{"type": "https://api.example.com/problems/sku-discontinued",
 "title": "A requested product is no longer available.",
 "status": 422,
 "detail": "SKU ABC-1 was discontinued on 2026-09-30.",
 "errors": [{"pointer": "/lines/2/sku", "detail": "ABC-1 is discontinued"}]}
```
(JSON Pointer is zero-based: line 3 is `/lines/2`.)
5. (a) Return the stored response, with no second refund. (b) `422`: key reused with different parameters. (c) `409`: in progress; the client retries later with the same key.
6. Add `customer_name` alongside `customerName` (both returned and accepted) → document and mark `customerName` deprecated → announce with timeline → send `Deprecation`/`Sunset` headers on responses that use the old field → monitor which clients still send or rely on it → contact them → remove in the next major version (or after the sunset date).
7. Hands-on; check that per-item results correlate by index or client-supplied ID and that partial success is documented.
8. GraphQL: many client types needing flexible, nested views of a rich graph (front ends, partner apps), with cost-based limits. gRPC: internal high-throughput, low-latency or streaming service-to-service calls between services you control.
