# Appendix D. Checklists

Copy these into tickets, pull-request templates or review agendas.

## D.1 New-system discovery checklist (Chapter 12)

- [ ] APIs available (REST / SOAP / GraphQL / OData / files / events); strategic vs legacy; deprecation dates
- [ ] Authentication options; integration-user licensing; IP restrictions; certificates
- [ ] Rate limits, concurrency limits, payload limits, daily allocations, and how they are reported (headers)
- [ ] Change detection: webhooks, events/CDC, `updated_since`, sync tokens, deletes/tombstones
- [ ] Bulk import/export mechanisms
- [ ] Upsert / external ID support; idempotency keys
- [ ] Customisation: custom fields/objects; runtime metadata discovery
- [ ] In-platform automation fired by API writes (triggers, workflows, validation rules)
- [ ] Sandboxes: availability, refresh behaviour, differences from production
- [ ] Release cadence and API versioning policy
- [ ] Status page, changelog, support contacts
- [ ] Known traps (forums, community, vendor known issues)

## D.2 Integration design review checklist (Chapter 14)

**Scope and requirements**
- [ ] One-paragraph frame (event, outcome, timeliness, value, current state)
- [ ] Scenarios cover exceptions: cancellations, amendments, partial, merges, deletes, duplicates, test data
- [ ] Measurable NFRs: volume and peak, latency, availability, ordering, consistency, security, audit, recoverability, supportability, cost
- [ ] System of record defined per entity (and per field where shared)

**Design**
- [ ] Style and patterns named; options and trade-offs recorded (ADRs)
- [ ] Contracts written (OpenAPI / AsyncAPI / file spec) and versioned
- [ ] Mapping specification reviewed with business owners, with real samples
- [ ] Key/identity strategy (external IDs, cross-reference)

**Reliability**
- [ ] Timeouts on every call; nested correctly
- [ ] Error classification table; retries only for transient errors on idempotent operations; backoff with jitter; single retry layer
- [ ] Every write idempotent (upsert, idempotency key, inbox); de-dup key and retention defined
- [ ] Behaviour during target outage of 1 hour and 3 days
- [ ] Circuit breaker / consumer pause
- [ ] DLQ + business error queue; owners; alerts; replay procedure
- [ ] No dual writes (outbox or durable workflow)
- [ ] Compensations for multi-step processes
- [ ] Ordering assumptions explicit; out-of-order and duplicate handling
- [ ] Reconciliation designed
- [ ] Backfill isolated from real-time traffic

**Security**
- [ ] Data classification; minimisation
- [ ] Least-privilege identities and scopes; separate identity per integration
- [ ] Secrets in a manager; rotation without downtime; expiry inventory
- [ ] TLS everywhere; mTLS/message encryption where required
- [ ] Logging redaction; payload retention limits
- [ ] SSRF and unsafe-consumption defences where URLs or partner data are involved
- [ ] Threat model (STRIDE at trust boundaries)
- [ ] Compliance: DPA/BAA, residency, audit

**Operations**
- [ ] Metrics, logs, traces; trace propagation through messages; business-key search
- [ ] Business signals monitored (volume, freshness, completeness)
- [ ] Alerts routed by ownership; SLOs agreed
- [ ] Runbook written and rehearsed
- [ ] Environments wired correctly; CI/CD; IaC; rollback plan
- [ ] Owner and catalogue entry

## D.3 Webhook consumer checklist (Chapter 7)

- [ ] HTTPS endpoint; body size cap
- [ ] Signature verified over raw bytes, constant-time compare
- [ ] Timestamp tolerance; replay protection
- [ ] Old + new secrets accepted during rotation
- [ ] Persist/enqueue then return 2xx within seconds
- [ ] De-duplicate on event ID (and business key + version)
- [ ] Ordering not assumed (versions or fetch-latest)
- [ ] Periodic reconciliation for missed events
- [ ] Alerts on signature failures, non-2xx rates, provider endpoint disablement

## D.4 Webhook provider checklist (Chapter 7)

- [ ] Signed payloads; event ID, type, timestamp, API version
- [ ] Retries with exponential backoff over hours/days; endpoint disable + notification
- [ ] Delivery logs, manual redelivery, replay API
- [ ] Event-type subscriptions
- [ ] SSRF protections (private IP blocking, DNS rebinding, egress proxy)
- [ ] Documented in OpenAPI `webhooks` or AsyncAPI

## D.5 API provider checklist (Chapter 6)

- [ ] Design-first OpenAPI; linted against style guide
- [ ] Consistent naming and casing; string IDs; RFC 3339 timestamps; decimal-string or minor-unit money with currency
- [ ] RFC 9457 errors with stable types and field pointers
- [ ] Cursor pagination; max page size
- [ ] Incremental sync with stable ordering; visible deletes
- [ ] Idempotency keys on creates
- [ ] ETag / If-Match concurrency
- [ ] Bulk/batch endpoints with per-item results
- [ ] Long-running operations (202 + status)
- [ ] Documented rate limits with headers and Retry-After
- [ ] Versioning and deprecation policy; Deprecation/Sunset headers
- [ ] Sandbox and test helpers; changelog; status page
- [ ] OWASP API Top 10 controls
- [ ] Agent-friendly descriptions (Chapter 18)

## D.6 Go-live checklist (Chapters 15 and 16)

- [ ] All test levels passed, including failure modes and peak load
- [ ] UAT and operations fire drill signed off
- [ ] Production credentials issued, stored and inventoried with expiry dates
- [ ] Firewall rules, allow-lists, DNS and certificates in place (both directions)
- [ ] Dashboards and alerts live; on-call informed
- [ ] Backfill plan executed or scheduled; matching reviewed
- [ ] Feature flag / gradual rollout plan; rollback plan rehearsed
- [ ] Partners informed of go-live time and contacts
- [ ] Hypercare period staffed
- [ ] Catalogue entry, design doc and runbook published

## D.7 Decommissioning checklist (Chapter 16)

- [ ] No traffic for an agreed period (logs and metrics checked)
- [ ] Consumers and partners notified
- [ ] Flows disabled, then removed
- [ ] Credentials revoked; secrets deleted
- [ ] Webhook registrations removed at providers
- [ ] Firewall rules, allow-listed IPs and partner certificates removed
- [ ] Queues, topics, subscriptions and storage deleted (after retention obligations)
- [ ] Catalogue updated; documentation archived

## D.8 Agent tool (MCP server) checklist (Chapter 18)

- [ ] Intent-level tools; precise descriptions including side effects and limits
- [ ] Strict input schemas; server-side validation
- [ ] Concise, structured results; pagination
- [ ] Instructive error messages
- [ ] Per-user authorisation; no token passthrough
- [ ] Idempotent writes; human approval for consequential actions
- [ ] Rate limits and budgets per user/session
- [ ] Audit log of every call (redacted)
- [ ] Lethal-trifecta review
- [ ] Allow-listed and versioned servers; gateway policies
