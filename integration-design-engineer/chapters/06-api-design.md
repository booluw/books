# Chapter 6. Designing Synchronous APIs: REST, GraphQL, gRPC and SOAP

> "An API is a user interface for developers. Treat it like one."

## What you will learn

- When to use REST, GraphQL, gRPC or SOAP, and how each works.
- How to design resource-oriented REST APIs: naming, methods, status codes, errors (RFC 9457), pagination, filtering, bulk operations, long-running operations, concurrency and rate limiting.
- How to version and evolve APIs without breaking consumers.
- How to describe APIs with OpenAPI 3.x, and where Arazzo and Overlay fit.
- How to be a good API *consumer*, which is most of an integration engineer's day.

---

## 6.1 Two sides of the table

Integration engineers sit on both sides of an API:

- **As consumers**, they call APIs designed by others (Salesforce, NetSuite, Stripe, a partner's SOAP service) and must cope with their quirks.
- **As providers**, they design APIs that expose their organisation's systems to partners, mobile apps, other teams and, increasingly, AI agents.

Good providers think like consumers, and good consumers understand why providers made their choices. This chapter covers both.

---

## 6.2 Choosing an API style

| Style | Transport and format | Contract | Strengths | Weaknesses | Typical use |
|---|---|---|---|---|---|
| **REST** (HTTP + JSON) | HTTP/1.1–3, JSON | OpenAPI | Universal, cacheable, simple, tooling everywhere | Over- and under-fetching; no standard for many conventions | Public and partner APIs, SaaS, most integrations |
| **GraphQL** | HTTP (usually `POST`), JSON | GraphQL SDL schema | Client chooses fields; one round trip for nested data; strong typing; introspection | Caching is harder; query-cost control needed; errors in `200` responses; N+1 risks on the server | Front-end aggregation, product APIs (GitHub, Shopify, Linear) |
| **gRPC** | HTTP/2, Protobuf | `.proto` files | Fast, compact, streaming, code generation, deadlines | Not browser-native (needs gRPC-Web or Connect); binary is harder to debug; fewer SaaS offer it | Internal service-to-service, high-throughput, polyglot microservices |
| **SOAP** | HTTP (or JMS, SMTP), XML | WSDL + XSD | Formal contracts, WS-Security, mature enterprise tooling | Verbose, complex, declining | Banking, telecom, government, legacy ERP (NetSuite SuiteTalk SOAP, Workday SOAP) |
| **JSON-RPC** | HTTP, WebSocket, stdio; JSON | (various) | Very simple method-call model | Few conventions | Blockchain nodes, LSP, **MCP** (Chapter 18) |
| **OData** | HTTP + JSON/XML | CSDL metadata | Standard query syntax (`$filter`, `$select`, `$expand`), metadata | Complex; uncommon outside Microsoft and SAP | SAP S/4HANA, Microsoft Dynamics 365 and Dataverse |

**Rules of thumb:**

- External or partner API: **REST with OpenAPI**, unless there is a strong reason otherwise.
- Many client types needing flexible views of a rich graph: consider **GraphQL**, typically alongside REST.
- Internal high-throughput or streaming between services you control: **gRPC**.
- Consuming an older enterprise system: you will use **SOAP or OData** because the system offers nothing else.

---

## 6.3 REST in practice

Fielding's REST constraints are client–server, stateless, cacheable, uniform interface, layered system and (optionally) code on demand. In everyday usage, "REST" means **resource-oriented HTTP APIs**. Hypermedia (HATEOAS) is rarely used in practice, though links for pagination and related resources are common and useful.

### Resources and URLs

Model the *nouns* of the domain as resources, and use HTTP methods as the verbs.

```
GET    /customers                 list customers (paginated)
POST   /customers                 create a customer
GET    /customers/{id}            read one
PATCH  /customers/{id}            partial update
PUT    /customers/{id}            full replace (or create at a known ID)
DELETE /customers/{id}            delete
GET    /customers/{id}/orders     sub-collection: a customer's orders
```

Conventions (consistency matters more than which convention you pick):

- Plural nouns for collections (`/orders`); lower case; hyphens in paths (`/sales-orders`).
- One casing style for JSON fields and parameters, either `snake_case` or `camelCase`, everywhere.
- IDs are opaque strings to clients. Prefixed IDs (`cus_8f3k2`, as Stripe uses) make logs and support conversations easier.
- Avoid deep nesting beyond one level (`/customers/{id}/orders` is fine; `/customers/{id}/orders/{oid}/lines/{lid}/discounts` is not).

### Actions that are not CRUD

Real business operations do not always fit create/read/update/delete. Common options:

1. **Model the action as a resource:** `POST /orders/{id}/cancellations`, or `POST /refunds` with `{"payment_id": ...}`. This is preferred, because the action gets an ID, a status and a history.
2. **A custom-method suffix** (Google's API Improvement Proposals style): `POST /orders/{id}:cancel`.
3. **A state transition via PATCH:** `PATCH /orders/{id} {"status": "cancelled"}`. This is simple but hides business rules and side effects inside a generic update.

### Requests and responses

- Return the **created or updated resource** in the response body. It saves consumers a follow-up `GET`.
- Use **ISO 8601 / RFC 3339 UTC timestamps**, **string decimals or integer minor units for money** with a currency, and **string IDs** (Chapter 4).
- Include `created_at` and `updated_at` on every resource. They enable incremental sync.
- Use **envelopes** consistently, if at all. A common pattern is `{"data": [...], "next_cursor": "..."}` for collections and the bare object for single resources.

### Status codes

Chapter 3 lists the codes. For providers: use `201` + `Location` for creates; `202` for accepted asynchronous work; `204` for deletes; `400`/`422` for validation errors; `401` versus `403` correctly; `404` (rather than `403`) when hiding the existence of a resource; `409` for conflicts; `412` for failed preconditions; `429` with `Retry-After` for rate limits.

---

## 6.4 Errors: RFC 9457 Problem Details

Consumers need errors they can act on, both programmatically and as humans. **RFC 9457** (July 2023, superseding RFC 7807) defines a standard JSON error format with media type `application/problem+json`:

```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json

{
  "type": "https://api.acme.com/problems/validation-error",
  "title": "Your request is not valid.",
  "status": 422,
  "detail": "2 fields failed validation.",
  "instance": "/orders/requests/4f8a1c",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "errors": [
    {"pointer": "/lines/0/qty", "detail": "must be greater than or equal to 1"},
    {"pointer": "/currency", "detail": "must be one of USD, EUR, GBP"}
  ]
}
```

- `type`: a URI identifying the problem type, ideally resolving to documentation. This is what consumer code branches on.
- `title`: a short, human-readable summary of the type.
- `status`: the HTTP status, duplicated for convenience.
- `detail`: an explanation of this occurrence.
- `instance`: a URI identifying this occurrence.
- **Extension members** (such as `errors` and `trace_id` above) are allowed.

Error design rules:

- **Stable, machine-readable codes** (the `type`), separate from messages that may change or be translated.
- **Say which field failed** (JSON Pointer, RFC 6901) and why.
- **Say whether retrying could help**, implicitly through the status class or explicitly.
- **Never leak internals:** no stack traces, SQL or internal hostnames.
- **Include a correlation or trace ID** so support can find the logs.

---

## 6.5 Pagination

Never return unbounded collections. Three techniques:

| Technique | Request | Pros | Cons |
|---|---|---|---|
| **Offset / limit** | `?offset=200&limit=100` | Simple; jump to any page | Slow on large offsets; **skips or duplicates rows if data changes during paging** |
| **Page number** | `?page=3&page_size=100` | Familiar | Same problems as offset |
| **Cursor (keyset)** | `?limit=100&cursor=eyJpZCI6...` | Stable under concurrent writes; fast at any depth | No random access; cursor is opaque |

**Use cursor pagination for integration APIs.** The cursor typically encodes the sort key of the last item seen (for example `(updated_at, id)`), and the server queries `WHERE (updated_at, id) > (:t, :id) ORDER BY updated_at, id LIMIT :n`. Return the next cursor in the body (`next_cursor`), or as an RFC 8288 `Link: <...>; rel="next"` header. An empty or absent cursor means the end.

### Incremental sync: the most important query an integration makes

Most integrations need "everything that changed since last time":

```
GET /orders?updated_since=2026-10-09T13:00:00Z&sort=updated_at&limit=200
```

Pitfalls, and the provider-side remedies:

- **Clock skew and in-flight transactions:** a row committed *after* your query but stamped with an *earlier* `updated_at` will be missed forever. Consumers should overlap windows (query from `last_seen − 5 minutes`) and de-duplicate. Providers can offer a **monotonic change sequence** (a change log or sync token) instead of timestamps.
- **Ties:** many rows can share the same timestamp. Always use a compound sort key `(updated_at, id)`.
- **Deletes are invisible** to `updated_since` queries. Providers should expose **tombstones** (`GET /deleted-orders?since=...`) or soft-delete flags. Consumers that cannot see deletes need periodic full reconciliation.
- **Sync tokens:** some APIs (Microsoft Graph delta queries, Google Calendar `syncToken`) return an opaque token representing "now"; you send it back next time to get only changes. This is the most robust design.

---

## 6.6 Filtering, sorting, sparse fields and expansion

- **Filtering:** `?status=open&created_after=2026-01-01`. For complex queries, consider a small, documented filter language, a `QUERY` request (RFC 10008), or GraphQL. Avoid exposing raw SQL-like expressions (injection risk and coupling to storage).
- **Sorting:** `?sort=-created_at,id` (prefix `-` for descending).
- **Sparse fieldsets:** `?fields=id,status,total` reduces payload size.
- **Expansion:** `?expand=customer,lines.product` embeds related resources to avoid extra calls (Stripe's `expand[]` is a good model). Cap the depth.

---

## 6.7 Bulk and batch operations

Integrations move data in volume, and one-request-per-record APIs hit rate limits fast. Offer, and as a consumer look for:

- **Batch endpoints:** `POST /customers/batch` with up to *N* items, returning **per-item results** (some may succeed while others fail). Status `207 Multi-Status` or `200` with a per-item array.
- **Bulk asynchronous jobs:** submit a large file or dataset, receive a job ID, poll or receive a webhook on completion, then download results. Salesforce's **Bulk API 2.0** is the canonical example: create a job, upload CSV, close the job, poll its status, fetch successful and failed records.
- **Composite requests:** several operations in one call, sometimes transactional (Salesforce Composite API, Microsoft Graph `$batch`).

Design questions to answer: Is the batch atomic (all or nothing) or partial? How are per-item errors reported and correlated (by index or client-supplied ID)? What are the size limits?

---

## 6.8 Long-running operations

When work takes longer than a reasonable HTTP timeout (more than a few seconds), use the **asynchronous request-reply** pattern:

```http
POST /reports
→ 202 Accepted
  Location: /operations/op_123
  Retry-After: 5

GET /operations/op_123
→ 200 OK  {"status": "running", "progress": 0.4}

GET /operations/op_123
→ 200 OK  {"status": "succeeded", "result_url": "/reports/rep_9"}
```

Alternatively, accept a **callback URL** or emit a **webhook** on completion (Chapter 7). Google's AIP-151 ("Long-running operations") and Microsoft's REST API guidelines both describe this pattern in detail.

---

## 6.9 Concurrency control

Two integrations updating the same record can lose updates ("last write wins" silently). Use **optimistic concurrency**:

1. `GET /customers/42` returns `ETag: "v17"`.
2. `PATCH /customers/42` with `If-Match: "v17"`.
3. If someone else changed the record, the server responds `412 Precondition Failed`. The client re-reads, re-applies its change and retries.

Some APIs use a `version` field in the body instead of ETags. Either way, document it.

---

## 6.10 Idempotency for unsafe operations

`POST` is not idempotent. If a create call times out, the client cannot know whether it succeeded. Providers should accept an **`Idempotency-Key`** header (a client-generated unique value, typically a UUID):

- The server stores the key with the request fingerprint and the response, for a retention window (Stripe keeps keys for at least 24 hours).
- A repeat request with the same key and the same parameters returns the **stored response** without re-executing.
- A repeat with the same key but *different* parameters is rejected (`422` or `409`).
- A repeat that arrives while the first is still in progress gets `409 Conflict`; the client should retry later.

Natural alternatives: **client-generated IDs** with `PUT /orders/{client_id}` (idempotent by definition), or **unique business keys** with upsert semantics (`external_id`). Chapter 8 implements this, and [`examples/idempotent-api/`](../examples/idempotent-api/) contains runnable code.

---

## 6.11 Rate limiting and quotas

Providers protect themselves with rate limits. Consumers must respect them.

**Provider design:**

- Common algorithms: **token bucket** (allows bursts up to bucket size, refills at a steady rate), **leaky bucket**, **fixed window** and **sliding window**.
- Limit per client, per tenant, per user and per endpoint class (writes are more expensive than reads), plus daily or monthly **quotas**.
- Communicate limits: `429 Too Many Requests` with `Retry-After`, and headers showing remaining budget. The IETF `httpapi` working group's draft standardises `RateLimit-Policy` and `RateLimit` fields; many APIs still use `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset`.
- GraphQL APIs often use **query cost** limits (Shopify and GitHub calculate a points cost per query).

**Consumer behaviour:**

- Read the limit headers and throttle proactively, before you hit `429`.
- On `429`/`503`, honour `Retry-After`; otherwise back off exponentially with jitter (Chapter 8).
- Share one rate-limit budget across all workers calling the same tenant. A distributed limiter (for example, a token bucket in Redis) prevents ten workers each believing they have the full budget.
- Prefer bulk APIs and webhooks to polling.
- Know the vendor's limits. Salesforce enforces a rolling 24-hour API request allocation per org; NetSuite limits concurrent requests per account; HubSpot, Shopify and Microsoft Graph all apply different per-app and per-tenant limits.

---

## 6.12 Versioning and evolution

APIs must change without breaking consumers. First, **avoid breaking changes**: add optional fields, add endpoints, add enum values (if consumers are tolerant readers; document that you might), and accept new optional parameters. Chapter 4 lists what counts as breaking.

When a breaking change is unavoidable, version. Common strategies:

| Strategy | Example | Notes |
|---|---|---|
| **URL path** | `/v2/orders` | Most common and most visible; easy routing. |
| **Header / media type** | `Accept: application/vnd.acme.v2+json` | Cleaner URLs; harder to test in a browser. |
| **Query parameter** | `?api-version=2024-10-01` | Used by Azure. |
| **Date-based versions pinned per account** | `Stripe-Version: 2026-09-30` | Stripe's model: each account is pinned to the version it started with; the server transforms responses through "version change" modules. Excellent for consumers, expensive for providers. |

**Deprecation process:**

1. Announce early with a timeline (commonly 6–24 months for external APIs).
2. Mark deprecated operations in OpenAPI (`deprecated: true`), and send the **`Deprecation`** (RFC 9745, 2025) and **`Sunset`** (RFC 8594) response headers.
3. Track who still calls the old version (per-client analytics) and contact them directly.
4. Use brownouts (scheduled short outages of the old version) to flush out forgotten consumers.
5. Remove the old version and return `410 Gone`.

**As a consumer:** subscribe to every vendor's changelog and deprecation notices, record the API versions you use in your integration catalogue, and set calendar reminders for sunset dates. Unplanned migrations because "the vendor turned off v1" are a classic integration emergency.

---

## 6.13 Describing APIs with OpenAPI

The **OpenAPI Specification (OAS)** is the standard, machine-readable description format for HTTP APIs, governed by the OpenAPI Initiative (a Linux Foundation project). Versions:

| Version | Released | Notes |
|---|---|---|
| Swagger 2.0 | 2014 | Still found in older tooling. |
| OAS 3.0 | 2017 | Major restructure; a JSON Schema *subset*. |
| OAS 3.1 | 2021 | Full JSON Schema 2020-12 alignment; webhooks object. |
| **OAS 3.2** | **September 2025** | Hierarchical tags; `QUERY` and custom HTTP methods; better streaming (SSE, JSON Lines) and multipart; enhanced XML support; `querystring` parameter location. |

Related OpenAPI Initiative specifications:

- **Arazzo** (1.0 in 2024; **1.1 in May 2026**) describes *workflows*: sequences of API calls with data passed between them ("create customer, then create subscription with the returned customer ID"). Version 1.1 added AsyncAPI support, so one workflow can span HTTP and event-driven steps. Useful for documentation, testing and AI agents.
- **Overlay** (1.0, October 2024) describes repeatable modifications to an OpenAPI document, such as adding internal-only annotations or removing internal endpoints from a public copy.

A minimal OpenAPI 3.1 document is in [`examples/openapi/orders-api.yaml`](../examples/openapi/orders-api.yaml). Key parts:

```yaml
openapi: 3.1.0
info: {title: Orders API, version: 1.4.0}
servers: [{url: https://api.acme.com/v1}]
paths:
  /orders:
    post:
      operationId: createOrder
      parameters:
        - {name: Idempotency-Key, in: header, required: true, schema: {type: string, format: uuid}}
      requestBody:
        required: true
        content:
          application/json:
            schema: {$ref: '#/components/schemas/OrderCreate'}
      responses:
        '201': {description: Created, content: {application/json: {schema: {$ref: '#/components/schemas/Order'}}}}
        '422': {$ref: '#/components/responses/ValidationProblem'}
```

### Design-first versus code-first

- **Design-first:** write the OpenAPI document, review it with consumers, then generate stubs, mocks and SDKs. Better APIs, earlier feedback, and parallel work (consumers build against a mock).
- **Code-first:** annotate code and generate the document. Faster to start; the API tends to mirror implementation details.

For integration interfaces shared across teams or companies, **design-first is strongly preferred**. Tooling: Stoplight, Swagger Editor, Redocly, Postman and IDE plugins for editing; **Spectral** or **Redocly CLI** for linting against a style guide; Prism or Microcks for mocks; OpenAPI Generator, Kiota, Speakeasy, Stainless or Fern for SDKs; Redoc, Scalar or Swagger UI for documentation.

---

## 6.14 GraphQL essentials

GraphQL exposes a typed schema; clients send queries specifying exactly the fields they need:

```graphql
query RecentOrders($first: Int!) {
  customer(id: "cus_123") {
    name
    orders(first: $first, orderBy: {field: CREATED_AT, direction: DESC}) {
      edges { node { id total { amount currency } status } }
      pageInfo { hasNextPage endCursor }
    }
  }
}
```

Integration considerations:

- **Errors** usually come back as HTTP `200` with an `errors` array, sometimes alongside partial `data`. Check both.
- **Pagination** usually follows the Relay *connections* convention (`edges`, `node`, `pageInfo`, `endCursor`).
- **Rate limits are cost-based.** Request only what you need, and paginate nested lists.
- **Mutations** are not automatically idempotent. Look for client mutation IDs or idempotency keys.
- **Bulk operations:** Shopify offers asynchronous bulk queries that produce JSONL files, which are much better for large exports than paginating.
- **Subscriptions** (over WebSocket or SSE) provide real-time updates where supported.
- **Federation** (Apollo Federation, GraphQL Fusion) composes many services into one graph, effectively an integration layer for front ends.

---

## 6.15 gRPC essentials

Define services in Protobuf; generate clients and servers in many languages:

```protobuf
service Inventory {
  rpc GetStock(GetStockRequest) returns (StockLevel);
  rpc WatchStock(WatchStockRequest) returns (stream StockLevel);   // server streaming
}
```

- Four call types: unary, server streaming, client streaming and bidirectional streaming.
- **Deadlines** are first-class and propagate across calls. Always set them.
- **Status codes** (`OK`, `INVALID_ARGUMENT`, `NOT_FOUND`, `ALREADY_EXISTS`, `PERMISSION_DENIED`, `UNAUTHENTICATED`, `RESOURCE_EXHAUSTED`, `UNAVAILABLE`, `DEADLINE_EXCEEDED`…) map to retry decisions the same way HTTP codes do. `UNAVAILABLE` is the canonical retryable code.
- Browser and HTTP/1.1 clients need **gRPC-Web** or the **Connect** protocol. **gRPC-JSON transcoding** (Envoy, Google API gateways) exposes gRPC services as REST.
- Use `buf` for linting and breaking-change detection on `.proto` files.

---

## 6.16 SOAP essentials (for consumers)

You will mostly consume SOAP, not design it. What you need:

- The **WSDL** describes operations, messages (with XSD types), bindings (SOAP 1.1 or 1.2, document/literal style) and endpoints. Generate a client from it (Apache CXF, `wsimport`, .NET `dotnet-svcutil`, Python `zeep`).
- A request is an XML **envelope** with an optional **Header** (security tokens, addressing) and a **Body**:

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ord="urn:acme:orders:v1">
  <soapenv:Header>
    <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
      <wsse:UsernameToken><wsse:Username>svc_int</wsse:Username>
        <wsse:Password>…</wsse:Password></wsse:UsernameToken>
    </wsse:Security>
  </soapenv:Header>
  <soapenv:Body>
    <ord:GetOrder><ord:OrderId>ORD-55821</ord:OrderId></ord:GetOrder>
  </soapenv:Body>
</soapenv:Envelope>
```

- Errors are **SOAP Faults**, returned with HTTP `500` in SOAP 1.1.
- **WS-Security** may require signed or encrypted messages with X.509 certificates, and timestamps that must fall within a short window (clock skew causes failures).
- SOAP 1.1 requires a `SOAPAction` HTTP header, and some services reject requests without the exact value.
- Test with SoapUI or Postman, and keep a working sample request in your repository.

---

## 6.17 Being a good API consumer: a checklist

Before building against an API:

- [ ] Read the docs end to end: authentication, rate limits, pagination, errors, webhooks, versioning, sandbox and deprecation policy.
- [ ] Get sandbox credentials. Find out how sandbox behaviour differs from production (it always does).
- [ ] Identify the **bulk** and **incremental** mechanisms; never full-scan when you can delta-sync.
- [ ] Identify **idempotency** support for writes, and **upsert by external ID**.
- [ ] Map every error code to a handling strategy (retry, fix data, alert, ignore).
- [ ] Configure timeouts, connection pooling and retry with backoff and jitter.
- [ ] Respect rate limits proactively; share budgets across workers.
- [ ] Use a descriptive `User-Agent` and log request IDs.
- [ ] Subscribe to the provider's status page and changelog; record the API version you use.
- [ ] Wrap the API behind your own **client module or anti-corruption layer**, so vendor quirks do not leak through your codebase.

## 6.18 Being a good API provider: a checklist

- [ ] Design-first with OpenAPI; review the design with real consumers.
- [ ] Consistent naming, casing, pagination (cursor-based), errors (RFC 9457) and timestamps.
- [ ] Incremental sync support (`updated_since` with stable ordering, or sync tokens) and visible deletes.
- [ ] Idempotency keys or client IDs for creates.
- [ ] Bulk endpoints for volume.
- [ ] ETags for concurrency.
- [ ] Rate limits that are documented and communicated in headers.
- [ ] Webhooks for changes (Chapter 7).
- [ ] A versioning and deprecation policy, published.
- [ ] A sandbox with realistic data, and test helpers (for example, special card numbers that force specific errors).
- [ ] Changelog, status page and support contact.
- [ ] Security per OWASP API Security Top 10 (Chapter 10).
- [ ] Clear, precise descriptions, which AI agents now read too (Chapter 18).

---

## Summary

- REST with OpenAPI is the default for integration APIs; GraphQL, gRPC, SOAP and OData each have their place.
- Design resources, errors (RFC 9457), cursor pagination, incremental sync, bulk operations, long-running operations, concurrency control, idempotency and rate limits deliberately.
- Avoid breaking changes; when unavoidable, version and deprecate with `Deprecation` and `Sunset` headers and real communication.
- OpenAPI 3.2 (2025) is current; Arazzo 1.1 (2026) describes multi-step workflows.
- As a consumer, wrap every API behind your own client and assume it will misbehave.

## Exercises

See [`exercises/06-api-design.md`](../exercises/06-api-design.md).

## Further reading

- Arnaud Lauret, *The Design of Web APIs*, 2nd edition (Manning, 2025).
- James Higginbotham, *Principles of Web API Design* (Addison-Wesley, 2021).
- Google API Improvement Proposals (aip.dev); Microsoft REST API Guidelines (github.com/microsoft/api-guidelines); Zalando RESTful API Guidelines.
- Stripe API reference and Stripe's engineering blog posts on API versioning and idempotency.
- OpenAPI Specification 3.2.0 (spec.openapis.org).
- RFC 9457 (Problem Details), RFC 8288 (Web Linking), RFC 8594 (Sunset), RFC 9745 (Deprecation header).
