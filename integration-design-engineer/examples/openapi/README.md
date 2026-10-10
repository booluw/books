# Orders API: OpenAPI 3.1 example (Chapter 6)

[`orders-api.yaml`](orders-api.yaml) shows integration-friendly API design:

- **Cursor pagination** (`limit`, `cursor`, `next_cursor`).
- **Incremental sync** with `updated_since` + `sort=updated_at`, plus **tombstones** (`/order-deletions`) so deletes are visible.
- A required **`Idempotency-Key`** on creates and on the cancellation action.
- **ETag / `If-Match`** optimistic concurrency on updates (`412` on conflict); JSON Merge Patch.
- A business action modelled as a resource (`POST /orders/{id}/cancellations`).
- **RFC 9457** problem details, with JSON Pointer validation errors.
- `429`/`503` responses with `Retry-After`.
- Money as decimal strings with ISO 4217 currency; a `version` field for discarding stale events.
- A signed **webhook** (`webhooks.orderShipped`).
- OAuth 2.0 client-credentials security with read and write scopes.

```bash
npx @redocly/cli lint orders-api.yaml       # only the expected example.com warnings remain
npx @stoplight/prism-cli mock orders-api.yaml  # run a mock server
```
