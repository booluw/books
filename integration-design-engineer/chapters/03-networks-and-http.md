# Chapter 3. Networks and HTTP for Integrators

> "It's always DNS." (operations folklore)
> "Except when it's TLS." (integration folklore)

## What you will learn

- The path a request takes from your integration to a partner's API, and every place it can fail.
- DNS, TCP, TLS and certificates, explained at the level you need to debug them.
- HTTP semantics: methods, status codes, headers, caching and content negotiation, including the new `QUERY` method.
- Timeouts, connection pooling, proxies, firewalls and private connectivity.
- A practical debugging toolkit.

Integration engineers spend a surprising share of their time on problems that are not in their code: a certificate expired, a firewall rule is missing, a proxy strips a header, a DNS record points to the old data centre. This chapter gives you the mental model to diagnose those problems quickly.

---

## 3.1 The journey of a request

When your integration calls `https://api.partner.com/v2/orders`, roughly this happens:

```
Your code
  → HTTP client library (connection pool, timeouts)
  → DNS resolution: api.partner.com → 203.0.113.10
  → (optional) outbound proxy / NAT gateway / egress firewall
  → TCP connection: three-way handshake to 203.0.113.10:443
  → TLS handshake: certificate validation, key exchange, (optional) client certificate
  → HTTP request sent (HTTP/1.1, HTTP/2 or HTTP/3)
  → Partner's CDN / WAF / load balancer
  → Partner's API gateway (authentication, rate limiting)
  → Partner's application
  → Response travels back the same way
```

Each arrow is a place where things can go wrong, and each produces a characteristic error:

| Stage | Typical failure | What you see |
|---|---|---|
| DNS | Record missing, stale cache, split-horizon DNS | `UnknownHostException`, `getaddrinfo ENOTFOUND`, `Name or service not known` |
| Egress | Firewall blocks the destination; proxy requires auth | Connect timeout; `407 Proxy Authentication Required` |
| TCP | Host down, port closed, wrong IP allow-listed | `Connection refused` (port closed); connect *timeout* (packets dropped) |
| TLS | Expired or untrusted certificate, hostname mismatch, protocol mismatch, missing client cert | `certificate verify failed`, `PKIX path building failed`, `handshake_failure`, `bad_certificate` |
| WAF / gateway | Request blocked, IP not allow-listed, rate limited | `403` (often an HTML page, not JSON), `429` |
| Application | Bugs, validation errors, overload | `4xx`/`5xx` with an error body; read timeouts |

The difference between **connection refused** and **connection timeout** is a useful early clue. *Refused* means a machine answered and said "nothing is listening on that port". *Timeout* means nothing answered at all, which usually indicates a firewall silently dropping packets, a wrong IP, or routing problems.

---

## 3.2 DNS

The **Domain Name System** turns names into addresses. Key record types:

| Record | Purpose |
|---|---|
| `A` / `AAAA` | Name → IPv4 / IPv6 address |
| `CNAME` | Alias of another name (common for SaaS custom domains and CDNs) |
| `MX` | Mail servers |
| `TXT` | Arbitrary text, used for domain-ownership verification and SPF/DKIM email authentication |
| `SRV` | Service location (host and port), used by some messaging systems |

Integration-relevant behaviours:

- **TTL (time to live)** controls caching. When a partner migrates to a new IP, clients keep using the old one until their cached record expires. Some runtimes, notably older JVM configurations, cache DNS *forever* unless configured otherwise. Check `networkaddress.cache.ttl` in Java.
- **Split-horizon DNS** returns different answers inside and outside a corporate network. Code that works on your laptop over VPN may fail in the cloud.
- **Private DNS zones** resolve names of private endpoints (for example AWS PrivateLink or Azure Private Link) only inside a specific virtual network.

Tools: `dig api.partner.com`, `nslookup`, `host`.

---

## 3.3 TCP, ports and connection pooling

**TCP** provides a reliable, ordered byte stream between two endpoints, each identified by an IP address and **port**. HTTPS uses port 443 by default; HTTP uses 80; SFTP 22; AMQP 5672 (5671 with TLS); Kafka typically 9092 or 9093.

Opening a TCP connection costs a network round trip (the handshake), and TLS adds one or two more. With 100 ms of latency, a fresh HTTPS connection costs 200–300 ms before a single byte of your request is sent. Therefore:

- **Reuse connections.** HTTP clients maintain a **connection pool**. Create one client per target and reuse it. Do not create a new client per request, a common bug in integration code.
- **Size the pool deliberately.** If you allow 50 concurrent requests but the pool holds 10 connections, 40 requests queue inside your process and appear as mysterious latency.
- **Mind idle-connection timeouts.** Load balancers close idle connections (AWS ALB defaults to 60 seconds; Azure Load Balancer to 4 minutes). If your pool keeps a connection longer than the server-side idle timeout, the next request on it fails with `connection reset`. Set the client's idle eviction below the shortest timeout in the path.
- **NAT port exhaustion.** Cloud NAT gateways have a limited number of source ports per destination. Integrations making very many short-lived connections to one partner can exhaust them. Pooling fixes this.

---

## 3.4 TLS and certificates

**Transport Layer Security (TLS)** encrypts the connection and authenticates the server, and optionally the client. TLS 1.2 (2008) and TLS 1.3 (RFC 8446, 2018) are current. TLS 1.0 and 1.1 are deprecated (RFC 8996) and should be refused. SSL is long dead, but people still say "SSL" when they mean TLS.

### How server authentication works

1. The server presents a **certificate chain**: its own **leaf certificate**, signed by one or more **intermediate CAs**, which chain up to a **root CA** that your client trusts.
2. Your client checks that:
   - the chain leads to a trusted root in its **trust store**;
   - every certificate is within its validity dates;
   - the hostname you connected to matches the certificate's **Subject Alternative Name (SAN)**;
   - nothing has been revoked (via OCSP or CRLs, with varying enforcement).
3. Client and server agree on keys, and the connection is encrypted.

### Common certificate failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `unable to get local issuer certificate` / `PKIX path building failed` | The server did not send its intermediate certificate, or your trust store lacks the root (common with corporate or private CAs). | Partner fixes their chain; or add the private CA to your trust store. |
| `certificate has expired` | Exactly what it says. | Partner renews. Monitor partner certificate expiry yourself (Chapter 16). |
| `hostname mismatch` | You connected by IP, or by a name not in the SAN. | Use the correct hostname. |
| Works in browser, fails in code | Browsers fetch missing intermediates automatically ("AIA chasing"); most libraries do not. | Partner must serve the full chain. |
| Works locally, fails in container | Container image lacks a CA bundle (e.g. minimal base images). | Install `ca-certificates`. |

> **Never "fix" a TLS error by disabling certificate verification** (`verify=False`, `-k`, `InsecureSkipVerify`). It turns encryption into theatre: anyone on the path can impersonate the partner. Fix the trust store instead.

Certificate lifetimes are shrinking. The CA/Browser Forum approved a schedule in 2025 that reduces maximum public TLS certificate validity in steps, to 200 days from March 2026, 100 days from March 2027 and 47 days from March 2029. Manual renewal processes will fail. Automate certificate management (ACME, cloud certificate managers) and alert on expiry.

### Mutual TLS (mTLS)

In **mutual TLS**, the *client* also presents a certificate, which the server validates. mTLS is common in B2B integration, banking and open-banking APIs, and inside service meshes. As the integrator you will:

- generate a private key and a **Certificate Signing Request (CSR)**;
- send the CSR to the partner (or to a CA they trust) to be signed;
- configure your client with the signed certificate and key, often packaged as a PKCS#12 (`.p12`/`.pfx`) file or as PEM files;
- track the expiry date and rotate before it lapses. **mTLS certificate expiry is one of the most common causes of B2B integration outages.**

Chapter 10 covers mTLS as an authentication mechanism.

### Certificate pinning

Some partners ask you to **pin** their certificate or public key, accepting only that exact key. Pinning blocks some attacks but breaks your integration whenever the partner rotates certificates. Prefer pinning a CA or intermediate, and agree a rotation process in advance.

---

## 3.5 HTTP: the protocol you will live in

HTTP semantics are defined in **RFC 9110** (2022), with caching in RFC 9111, HTTP/1.1 in RFC 9112, HTTP/2 in RFC 9113 and HTTP/3 in RFC 9114. Read RFC 9110 once. It answers many arguments about what a method or status code "should" do.

### Anatomy of a request and response

```http
POST /v2/orders HTTP/1.1
Host: api.partner.com
Authorization: Bearer eyJhbGciOi...
Content-Type: application/json
Accept: application/json
Idempotency-Key: 7c9e6679-7425-40de-944b-e07fc1f90ae7
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
Content-Length: 87

{"customer_id":"C-1001","lines":[{"sku":"TSHIRT-M","qty":2}],"currency":"USD"}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /v2/orders/ORD-55821
RateLimit-Policy: "default";q=100;w=60
RateLimit: "default";r=97;t=41
X-Request-Id: 9f1c2d7e

{"id":"ORD-55821","status":"pending","created_at":"2026-10-09T14:03:11Z"}
```

### Methods and their guarantees

Two properties defined in RFC 9110 drive integration design:

- **Safe:** the method does not change server state (read-only).
- **Idempotent:** sending the same request once or many times has the same effect on the server as sending it once.

| Method | Safe | Idempotent | Typical use |
|---|---|---|---|
| `GET` | Yes | Yes | Read a resource or collection |
| `HEAD` | Yes | Yes | Like GET but headers only |
| `OPTIONS` | Yes | Yes | Discover capabilities; CORS preflight |
| `QUERY` | Yes | Yes | Read with a request body (complex queries). New in RFC 10008 (June 2026) |
| `PUT` | No | Yes | Replace a resource at a known URL |
| `DELETE` | No | Yes | Remove a resource |
| `POST` | No | **No** | Create a resource, or trigger a process |
| `PATCH` | No | **Not necessarily** | Partially update a resource |

Why this matters: **a client may safely retry an idempotent request after a timeout.** If a `PUT` times out you can resend it. If a `POST /payments` times out you *do not know* whether the payment happened, and blindly retrying might charge twice. The standard remedy is an **idempotency key** (Chapter 8). An IETF draft standardises the `Idempotency-Key` header; it was at draft-07 in October 2025 and had not become an RFC as of October 2026, but Stripe, Adyen, PayPal and many others already use the pattern.

**The `QUERY` method** solves a long-standing gap. Complex searches do not fit in a URL (URLs over a few thousand characters break in proxies), so APIs have used `POST /search`, which loses the "safe and idempotent" guarantees and therefore cacheability and automatic retry. `QUERY` carries a body but is defined as safe and idempotent. Expect support in servers, clients, gateways and OpenAPI tooling (OpenAPI 3.2 already allows it) to grow through 2026–2027. Check that every hop supports it before you rely on it.

### Status codes

Status codes form classes. Your integration logic should branch on them deliberately.

| Code | Meaning | Integration handling |
|---|---|---|
| `200 OK` | Success with body | Process. |
| `201 Created` | Resource created; `Location` header points to it | Store the new ID. |
| `202 Accepted` | Accepted for asynchronous processing | Poll the status URL or wait for a callback (Chapter 6). |
| `204 No Content` | Success, no body | Do not try to parse a body. |
| `301`/`308` | Moved permanently | Update your configuration; `308` preserves the method and body. |
| `302`/`307` | Temporary redirect | `307` preserves the method and body; `302` may turn POST into GET in some clients. |
| `304 Not Modified` | Conditional GET: your cached copy is current | Use the cache. |
| `400 Bad Request` | Malformed request | **Do not retry.** Fix the data; route to an error queue. |
| `401 Unauthorized` | Missing or invalid credentials | Refresh the token *once*, then retry; if it still fails, alert. |
| `403 Forbidden` | Authenticated but not allowed | Do not retry; check scopes, permissions and IP allow-lists. |
| `404 Not Found` | Resource does not exist | Depends on context: maybe it was deleted, or maybe it has not replicated yet. |
| `405 Method Not Allowed` | Wrong method | Bug in your code. |
| `408 Request Timeout` | Server gave up waiting for your request | Retryable. |
| `409 Conflict` | State conflict, e.g. a duplicate or a version mismatch | Usually business logic: fetch the current state and decide. |
| `410 Gone` | Permanently removed (often a retired API version) | Migrate. |
| `412 Precondition Failed` | `If-Match` ETag did not match (optimistic locking) | Re-read, re-apply, retry. |
| `413 Content Too Large` | Payload too big | Split into batches. |
| `415 Unsupported Media Type` | Wrong `Content-Type` | Fix the header. |
| `422 Unprocessable Content` | Well-formed but semantically invalid | Do not retry; route to error handling. |
| `429 Too Many Requests` | Rate limited | Retry after `Retry-After`, with backoff. |
| `500 Internal Server Error` | Server bug | Retry a few times (for idempotent operations), then dead-letter. |
| `502 Bad Gateway` / `503 Service Unavailable` / `504 Gateway Timeout` | Upstream or overload problems | Retry with backoff; honour `Retry-After`. |

Rules of thumb:

- **4xx means "the request is wrong; resending it unchanged will fail again"**, except for `408`, `429`, sometimes `409` and `423`, and a `401` after a token refresh.
- **5xx means "the server failed; trying again later may work"**, *if* the operation is idempotent or protected by an idempotency key.
- **Never trust the status code alone.** Some APIs return `200 OK` with `{"success": false, "error": "..."}` in the body, notably older SOAP-style and some legacy JSON APIs. Inspect the body as well.

### Headers you must know

| Header | Purpose |
|---|---|
| `Content-Type` / `Accept` | Media type of the body you send / want back (`application/json`, `application/xml`, `text/csv`, `application/problem+json`). |
| `Content-Encoding` / `Accept-Encoding` | Compression (`gzip`, `br`, `zstd`). |
| `Authorization` | Credentials (`Bearer <token>`, `Basic <base64>`). |
| `ETag` / `If-Match` / `If-None-Match` | Versioning for caching and optimistic concurrency. |
| `Last-Modified` / `If-Modified-Since` | Time-based conditional requests. |
| `Cache-Control` | Caching directives. |
| `Location` | URL of a created resource or a redirect target. |
| `Retry-After` | Seconds, or an HTTP date, to wait before retrying (with `429`/`503`). |
| `RateLimit` / `RateLimit-Policy` | Standardised rate-limit information from the IETF `httpapi` working group draft. Many APIs still use vendor headers such as `X-RateLimit-Remaining`. |
| `Idempotency-Key` | De-duplicates unsafe requests (Chapter 8). |
| `traceparent` / `tracestate` | W3C Trace Context for distributed tracing (Chapter 16). |
| `X-Request-Id` / `X-Correlation-Id` | Non-standard but common request identifiers. Log them and quote them to partners' support teams. |
| `User-Agent` | Identify your integration (`acme-netsuite-sync/2.3 (+ops@acme.com)`), which helps partners contact you. |
| `Forwarded` / `X-Forwarded-For` | Original client information through proxies. |

Header names are case-insensitive. HTTP/2 and HTTP/3 send them in lower case. Do not write code that depends on capitalisation.

### Content negotiation and media types

`Accept: application/json` asks for JSON. Some APIs use **vendor media types** for versioning, such as `Accept: application/vnd.github+json`. A `406 Not Acceptable` means the server cannot produce what you asked for. Error bodies should use **`application/problem+json`** as defined by **RFC 9457** (Problem Details for HTTP APIs, which replaced RFC 7807 in 2023). Chapter 6 covers error design.

### Caching and conditional requests

Caching cuts load and latency, and conditional requests make polling cheap:

```http
GET /v2/products/123
If-None-Match: "a1b2c3"

HTTP/1.1 304 Not Modified
```

**Optimistic concurrency** prevents lost updates when two integrations edit the same record:

```http
PUT /v2/customers/42
If-Match: "v17"
...
HTTP/1.1 412 Precondition Failed      ← someone else updated it; re-read and merge
```

### HTTP versions

| Version | Key traits | Integration implications |
|---|---|---|
| HTTP/1.1 | Text, one request at a time per connection | Needs several connections for concurrency. |
| HTTP/2 | Binary, multiplexed streams over one connection, header compression | One connection carries many concurrent requests; gRPC requires it. |
| HTTP/3 | HTTP over QUIC (UDP), faster handshakes, no TCP head-of-line blocking | Mostly transparent; some corporate firewalls block UDP 443, and clients fall back. |

### Streaming responses

- **Chunked transfer** and **Server-Sent Events (SSE)** (`text/event-stream`) stream server-to-client over HTTP. SSE is widely used for LLM token streaming and in MCP's Streamable HTTP transport.
- **WebSockets** provide full-duplex messaging after an HTTP upgrade.
- **JSON Lines / NDJSON** (`application/jsonl`) streams one JSON object per line for bulk exports. OpenAPI 3.2 added first-class support for describing sequential and streaming media types.

---

## 3.6 Timeouts: the most important setting you will configure

Most HTTP libraries default to *no* timeout or a very long one. An integration without timeouts will eventually hang forever, holding threads and connections until the whole process stalls. Configure these explicitly:

| Timeout | What it bounds | Typical value |
|---|---|---|
| **DNS / connect timeout** | Establishing the TCP (and TLS) connection | 2–5 s |
| **Read / socket timeout** | Waiting between bytes of the response | Depends on the API's p99 latency; often 10–30 s |
| **Total / request deadline** | The whole call, including retries | Must fit inside *your* caller's deadline |
| **Pool acquisition timeout** | Waiting for a free pooled connection | 1–5 s; a breach signals saturation |

**Deadline propagation:** if your API promises to answer within 10 seconds and calls a partner, the partner call (with retries) must finish in well under 10 seconds, leaving time for your own work. gRPC propagates deadlines automatically. With HTTP you must compute the remaining budget yourself. Chapter 8 returns to timeouts, retries and budgets.

**What happens after a timeout?** A read timeout does *not* mean the server did nothing. The request may have completed, with only the response lost. That ambiguity is why idempotency is central to integration design.

---

## 3.7 Proxies, gateways, firewalls and private connectivity

Corporate and cloud networks put intermediaries in the path:

- **Forward (egress) proxies** sit between your integration and the internet, often to enforce allow-lists or inspect traffic. Configure clients with `HTTPS_PROXY` / `NO_PROXY` or the library's equivalent. **TLS-inspecting proxies** re-sign traffic with a corporate CA, so that CA must be in your trust store, and mTLS to partners usually needs a proxy bypass.
- **Reverse proxies and load balancers** (NGINX, Envoy, HAProxy, cloud load balancers) sit in front of servers.
- **API gateways** (Chapter 11) add authentication, rate limiting, transformation and analytics.
- **Web Application Firewalls (WAFs)** block suspicious traffic. They occasionally block legitimate payloads, for example XML that resembles an injection attack, and typically return an HTML `403` page rather than the API's JSON error.
- **IP allow-listing:** many partners only accept traffic from known IP addresses. Cloud workloads have changing IPs by default, so route integration egress through a **NAT gateway with a static IP**, or an iPaaS that publishes its egress IPs. Document these IPs. They are part of your interface contract.
- **Private connectivity** keeps traffic off the public internet: site-to-site **VPN** (IPsec), dedicated circuits (AWS Direct Connect, Azure ExpressRoute, Google Cloud Interconnect) and **private endpoints** (AWS PrivateLink, Azure Private Link, Google Private Service Connect). Hybrid integrations, where a cloud iPaaS reaches an on-premises SAP system, use these or an **on-premises agent**: a small runtime installed inside the private network that makes *outbound* connections to the cloud platform, so no inbound firewall ports need opening. Boomi Atoms, the Azure on-premises data gateway, SAP Cloud Connector and Workato on-prem agents all work this way.

---

## 3.8 Other transport protocols you will meet

| Protocol | Use | Notes |
|---|---|---|
| **SFTP** (SSH File Transfer) | Batch file exchange, the most common B2B file transport | Key-based authentication; watch out for host-key changes. Do not confuse it with FTPS. |
| **FTPS** | FTP over TLS | Firewall-unfriendly (separate data channels); legacy. |
| **AS2** (RFC 4130) | EDI over HTTP(S) with S/MIME signing and encryption and signed receipts (MDNs) | Retail and supply chain. AS4 (an OASIS ebMS profile) is used in European e-invoicing and energy. |
| **AMQP 0-9-1** | RabbitMQ's native protocol | |
| **AMQP 1.0** (ISO/IEC 19464) | Azure Service Bus, ActiveMQ Artemis, Solace, IBM MQ | A different protocol from 0-9-1 despite the name. |
| **MQTT** | Lightweight pub/sub for IoT | Brokers include HiveMQ, EMQX and Mosquitto. |
| **Kafka protocol** | Kafka clients ↔ brokers | Binary, over TCP. |
| **SMTP / IMAP** | Email-based integrations (still common for orders and invoices) | Parsing attachments is real-world integration work. |
| **JDBC / ODBC** | Direct database connections | Shared-database integration (Chapter 5). |
| **gRPC** | RPC over HTTP/2 | Chapter 6. |

---

## 3.9 A debugging toolkit

When an integration fails, work up the stack: DNS, then TCP, then TLS, then HTTP, then application.

```bash
# 1. DNS: does the name resolve, and to what?
dig +short api.partner.com

# 2. TCP: can we reach the port at all?
nc -vz api.partner.com 443            # or: telnet api.partner.com 443

# 3. TLS: what certificate does the server present? Is the chain complete?
openssl s_client -connect api.partner.com:443 -servername api.partner.com -showcerts </dev/null
# Check expiry dates:
openssl s_client -connect api.partner.com:443 -servername api.partner.com </dev/null 2>/dev/null \
  | openssl x509 -noout -dates -subject -issuer

# With a client certificate (mTLS):
openssl s_client -connect api.partner.com:443 -cert client.crt -key client.key

# 4. HTTP: full request/response with timing
curl -v https://api.partner.com/health
curl -sS -o /dev/null -w 'dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total}\n' https://api.partner.com/health

# 5. From *inside* the runtime environment (container, iPaaS agent host), not just your laptop.
```

Other essential tools:

- **Postman, Insomnia, Bruno or HTTPie** for exploring APIs interactively.
- **mitmproxy, Charles or Fiddler** to inspect traffic from a client you do not control.
- **Wireshark / tcpdump** for packet-level problems.
- **jq** for slicing JSON on the command line; **xmllint** for XML.
- **Request bins** (webhook.site, or a self-hosted equivalent) to see exactly what a webhook sender transmits.
- **The partner's status page.** Check it before debugging for an hour.

### A diagnostic checklist

1. Did it ever work? What changed (our deploy, their deploy, certificates, credentials, network, data)?
2. Does it fail for all requests or some? All tenants or one?
3. Can I reproduce it with `curl` from the same network location?
4. What do the partner's logs say? Give them the request ID and the exact timestamp in UTC.
5. Is the partner's status page reporting an incident?

---

## Summary

- Know every hop a request takes and the error each hop produces.
- DNS caching, connection pooling and idle timeouts cause many "random" failures.
- Understand certificate chains and mTLS; never disable verification; monitor expiry.
- Learn HTTP semantics from RFC 9110: safe and idempotent methods, status-code classes, conditional requests. The new `QUERY` method (RFC 10008) gives safe, retryable complex reads.
- Always set connect, read and total timeouts. A timeout leaves the outcome unknown, which is why idempotency matters.
- Plan egress IPs, proxies and private connectivity early. They are part of the contract.

## Exercises

See [`exercises/03-networks-and-http.md`](../exercises/03-networks-and-http.md).

## Further reading

- RFC 9110, *HTTP Semantics* (2022).
- RFC 10008, *The HTTP QUERY Method* (2026).
- RFC 8446, *TLS 1.3* (2018).
- Ilya Grigorik, *High Performance Browser Networking* (O'Reilly, 2013; free online at hpbn.co). Its networking chapters are excellent.
- Julia Evans's zines on networking, DNS and HTTP (wizardzines.com).
