# Chapter 15. Testing Integrations

> "The sandbox lied."
> (every integration engineer, at least once)

## What you will learn

- Why integrations are hard to test, and how to structure a test strategy around that difficulty.
- Unit testing transformations; component testing with mocks and service virtualisation.
- Contract testing (consumer-driven contracts with Pact; schema- and specification-based checks).
- Testing against partner sandboxes, and end-to-end testing across systems.
- Testing failure paths: retries, duplicates, ordering, outages and poison messages.
- Performance, load and soak testing; chaos and resilience testing.
- Test data management, UAT and testing in production safely.

---

## 15.1 Why integration testing is hard

- **You do not own the systems.** Partner sandboxes are slow, shared, reset unexpectedly, or behave differently from production (different limits, versions and data).
- **Environments multiply:** every system has dev, test and production, and their combinations are many.
- **Asynchronous flows** make "did it work?" a question of waiting and polling.
- **Failure paths** (timeouts, duplicates, outages) are hard to provoke on demand.
- **Data dependencies:** a test needs a customer to exist in three systems with matching IDs.
- **Cost:** some partner APIs charge per call, and some actions are irreversible in sandboxes too (sending real emails, generating carrier labels).

The answer is the same as for any distributed system: **push most testing down to fast, isolated, deterministic levels**, and keep a small number of slow, realistic end-to-end tests at the top.

---

## 15.2 The integration test pyramid

```
                 ▲   Few, slow, realistic
                / \
               / E2E \          Cross-system scenarios in sandboxes / staging
              /-------\
             / Contract \       Provider–consumer compatibility (Pact, schema checks)
            /-------------\
           /  Component     \   Your integration with dependencies mocked or virtualised
          /-----------------\
         /  Unit (mappings,   \ Pure functions: transformations, validation, routing rules
        /   rules, clients)    \
       /-------------------------\   Many, fast, deterministic
```

| Level | What it verifies | Speed | Where it runs |
|---|---|---|---|
| **Unit** | Transformations, value maps, validation, error classification, idempotency key derivation | Milliseconds | Every commit |
| **Component** | The integration service as a whole (HTTP in, broker out, retries, DLQ) with mocks | Seconds | Every commit |
| **Contract** | Your expectations of a provider match what the provider actually offers | Seconds | Every commit on both sides |
| **Integration (sandbox)** | Real connectivity, authentication and behaviour of partner sandboxes | Minutes | Nightly / pre-release |
| **End-to-end** | Business scenarios across all systems | Minutes to hours | Pre-release, UAT |
| **Non-functional** | Performance, resilience, security | Hours | Scheduled / pre-release |

---

## 15.3 Unit testing transformations

Transformations are pure functions, so test them exhaustively:

- **Golden-file tests:** a directory of `input.json` / `expected.json` pairs; the test runs the mapping and compares. Adding a case means adding files, so business analysts can contribute cases.
- **Edge cases:** nulls versus absent fields; empty strings; maximum lengths and truncation; Unicode (accents, emoji, right-to-left text); time-zone boundaries and DST; currencies with 0 or 3 decimals; negative amounts; very large numbers; unexpected enum values.
- **Schema validation of outputs:** validate each output against the target schema (JSON Schema, XSD).
- **Property-based testing** (Hypothesis in Python, jqwik in Java, fast-check in TypeScript): generate random inputs and assert invariants, such as "line totals always sum to the order total", "mapping then reverse-mapping returns the original" and "output always validates".
- **Regression from production:** every production mapping defect gets an anonymised fixture and a test.

Also unit-test **error classification** ("`429` → retryable; `422` → business error"), **routing rules** and **idempotency key derivation**. See [`examples/data-mapping/`](../examples/data-mapping/) for golden-file tests.

---

## 15.4 Component testing with mocks and virtualisation

Run your integration service for real, with its external dependencies replaced:

- **HTTP mocks:** WireMock (Java, standalone or Docker), MockServer, Mountebank, Prism (serves mocks from OpenAPI), Microcks (from OpenAPI, AsyncAPI, gRPC and SOAP), `responses` / `respx` (Python), nock / MSW (Node.js).
- **Broker emulation:** Testcontainers (real Kafka, RabbitMQ, LocalStack for AWS services, Azurite for Azure Storage, emulators for Pub/Sub and Service Bus) in Docker during tests.
- **Databases:** Testcontainers with the real database engine (not an in-memory substitute that behaves differently).

**Script failure behaviour into the mocks.** This is where component tests earn their keep:

- return `503` twice, then `201`: does the retry logic work, and is the request idempotent?
- delay 30 seconds: does the timeout fire, and what happens next?
- return `429` with `Retry-After: 10`: is it honoured?
- return `401`: is the token refreshed once?
- return a malformed body: does it go to the error queue rather than crash the consumer?
- deliver the same message twice: is the effect applied once?
- deliver messages out of order: does the version check work?

**Service virtualisation** at enterprise scale (Broadcom's DevTest, Parasoft Virtualize, Tricentis, or recorded traffic replayed through WireMock) simulates complex backends such as mainframes and SAP for teams who cannot get enough sandbox access.

---

## 15.5 Contract testing

Mocks drift from reality: your mock says the partner returns `customer_id`, but they renamed it to `customerId` last month. **Contract tests** check that consumer and provider agree, without running an end-to-end environment.

### Consumer-driven contract testing (Pact)

1. The **consumer** writes tests against a Pact mock provider, recording the interactions it relies on (request → minimal expected response) into a **pact file**.
2. The pact is published to a **Pact Broker** (or PactFlow).
3. The **provider** runs **verification** in its own CI: it replays the pact's requests against the real provider code and checks the responses match.
4. `can-i-deploy` checks prevent deploying a version that would break a known consumer.

Pact works best **between teams in the same organisation** that both run CI. For HTTP, message (event) and gRPC interactions, it catches breaking changes before they reach production. It does not work with third-party SaaS providers who will not run your pacts.

### Specification-based contract testing

When the provider publishes an OpenAPI or AsyncAPI document:

- **Validate your consumer's requests and your mocks against the specification** (for example with Prism's validation proxy, or by generating mocks from the spec).
- **Bi-directional contract testing** (PactFlow) compares consumer pacts with the provider's OpenAPI document.
- **Schema-registry compatibility checks** (Confluent Schema Registry, Apicurio) reject incompatible event-schema changes at publish time.
- **Breaking-change detection in CI:** `oasdiff` or `openapi-diff` for OpenAPI, `buf breaking` for Protobuf, AsyncAPI diff tools for events.

### Provider-side: monitoring third-party contracts

For third-party SaaS APIs you cannot run contracts against:

- Run a small **"canary contract" suite** against the vendor sandbox nightly, asserting the response shapes you depend on.
- Subscribe to changelogs; pin API versions where the vendor allows.
- Validate responses at runtime and alert on schema drift (unknown fields are fine; missing required fields are not).

---

## 15.6 Sandbox integration testing

Real partner sandboxes test what nothing else can: authentication, network paths, certificates, real validation rules and real data formats.

Make them reliable:

- **Automate setup and teardown** of test data through the partner's API where possible; tag test records so that cleanup jobs can find them.
- **Isolate runs:** unique prefixes per test run to avoid collisions in shared sandboxes.
- **Wait properly for asynchronous outcomes:** poll with a timeout ("eventually" assertions), never fixed `sleep`s.
- **Know the sandbox's differences:** lower rate limits, missing features, different webhook behaviour, periodic resets (Salesforce sandbox refreshes, NetSuite sandbox refreshes). Document them in the design.
- **Use provider test helpers:** Stripe test card numbers that force specific declines; test clocks for subscriptions; carrier test tracking numbers.
- **Expect flakiness** and track it. A flaky sandbox test that is ignored is worse than no test.

---

## 15.7 End-to-end testing

End-to-end (E2E) tests run business scenarios across all systems in a staging environment: "close a deal in Salesforce staging → customer and order appear in NetSuite sandbox → ERP ID written back".

- Keep them **few** (the critical scenarios), **business-readable** (Gherkin-style Given/When/Then helps UAT), and **observable** (correlation IDs let you trace failures to the step that failed).
- Use them as **smoke tests after every deployment**: one synthetic transaction per critical flow.
- Accept that E2E tests cannot cover failure modes exhaustively; that is the job of component tests.

### Test data management

- Maintain **seed data sets** that exist consistently across systems (customers, products, tax codes) with known cross-references.
- **Anonymise** production-derived data (masking, synthetic generation) before use outside production. Personal data in test systems is a compliance breach waiting to happen.
- **Synthetic data generators** (Faker libraries, or tools such as Tonic and Gretel) create realistic but fake data.
- **Version test data** alongside tests.

---

## 15.8 Testing failure modes and resilience

Deliberately test what happens when things go wrong, both in component tests and in staging:

| Scenario | How to test | What to verify |
|---|---|---|
| Downstream outage | Stop the mock or block the network; use a chaos tool | Messages queue; circuit opens; no data loss; catch-up after recovery; alerts fire |
| Slow downstream | Inject latency (Toxiproxy, mock delays) | Timeouts fire; no thread or connection exhaustion; backpressure holds |
| Duplicates | Publish the same message twice; replay a DLQ | Effect applied once |
| Out-of-order | Publish v2 before v1 | Final state reflects v2 |
| Poison message | Publish a malformed payload | Goes to DLQ after N attempts; others keep flowing |
| Token expiry | Short-lived tokens in test | Refresh works under concurrency |
| Rate limiting | Mock returns `429` with `Retry-After` | Backoff honoured; overall throughput adapts |
| Crash mid-processing | Kill the process during processing (chaos) | Restart resumes; no lost or duplicated effects (outbox and inbox work) |
| Certificate expiry | Use an expired certificate in staging | Clear error; alert fires; runbook works |
| Large payloads | Send max-size and over-max messages | Claim check works; clear errors above limits |

**Chaos engineering** tools (Chaos Mesh and LitmusChaos for Kubernetes, AWS Fault Injection Service, Azure Chaos Studio, Gremlin, Toxiproxy for network faults) let you run such experiments systematically. Start in staging; move to carefully controlled production "game days" when mature.

---

## 15.9 Performance, load and soak testing

Integrations meet their peak on the worst possible day: Black Friday, quarter-end, open enrolment, payroll day.

- **Model the load:** average and peak rates, burst shapes (a sale starting at 09:00 produces a spike), payload size distribution, and the mix of operations.
- **Load test** the integration and its own infrastructure (brokers, databases) at 1.5–2× expected peak. Tools: k6, Gatling, JMeter, Locust; Kafka's `kafka-producer-perf-test` for brokers.
- **Respect partners:** do not load-test a partner's sandbox without permission. Use mocks with realistic latency and rate limits instead, and agree a joint performance test with the partner if needed.
- **Measure:** end-to-end latency percentiles (p50, p95, p99), throughput, consumer lag, error rates, resource saturation and **time to drain a backlog**.
- **Backlog drain test:** queue 6 hours of peak traffic (simulating a downstream outage), then release. How long does catch-up take? Does the downstream survive the catch-up surge? (Throttle it.)
- **Soak test:** run at normal load for 24–72 hours to find memory leaks, connection leaks, token-refresh bugs and log-volume problems.
- **Backfill test:** run the initial load at full size in staging to measure duration and impact.

---

## 15.10 User acceptance testing (UAT)

Business users verify the integration supports their process:

- Provide **scenario scripts** derived from the functional requirements (F-xx), including exception scenarios.
- Give users **visibility**: a way to see what the integration did (status dashboard, error queue UI) is part of what they accept.
- Include **operations acceptance**: can support staff follow the runbook to diagnose and replay a failure? Run a "fire drill".
- Record sign-off.

---

## 15.11 Testing in production, safely

Some things can only be verified in production (real partner behaviour, real data variety, real volumes):

- **Synthetic transactions:** periodically push a clearly marked test transaction through the live flow and verify the outcome (where partners allow it), or use read-only health checks.
- **Shadow mode / dark launch:** run the new integration in parallel, computing outputs without sending them (or sending to a sink), and compare with the old integration's outputs. Ideal for ESB migrations.
- **Canary releases:** route a small percentage of traffic or a few tenants to the new version first.
- **Feature flags** to switch flows on per tenant and off instantly.
- **Reconciliation** as continuous verification (Chapter 8).

---

## 15.12 Testing in iPaaS platforms

Low-code platforms complicate testing but do not exempt you from it:

- Use the platform's **test frameworks** where they exist: MuleSoft **MUnit**, SAP Cloud Integration's simulation mode, Boomi's test mode and **Boomi Test Hub**, Workato's recipe test cases, Logic Apps' Standard unit-testing support.
- Keep **transformations testable**: put complex logic in scripts or functions you can test outside the platform where possible.
- **Export flow definitions to version control** and run tests in CI through the platform's CLI or API.
- Use **separate environments** with promotion pipelines; never edit production flows directly.

---

## 15.13 A test strategy template

For each integration, document (in the IDD's testing section):

| Level | Scope | Tools | Owner | When |
|---|---|---|---|---|
| Unit | Mappings (golden files), validation, error classification | pytest / JUnit / MUnit | Integration team | Every commit |
| Component | Service with mocked APIs and real broker (Testcontainers); failure scenarios | WireMock, Testcontainers | Integration team | Every commit |
| Contract | Consumer pacts with internal Orders API; OpenAPI diff for vendor spec | Pact, oasdiff | Integration + Orders teams | Every commit |
| Sandbox | Auth, upsert, webhook signature against vendor sandboxes | Custom suite | Integration team | Nightly |
| E2E | Scenarios F-01…F-06 | Scenario runner | QA | Pre-release |
| Performance | 2× quarter-end peak; 6-hour backlog drain | k6, mocks | Integration team | Before go-live, then quarterly |
| Resilience | Outage, duplicates, crash mid-processing | Toxiproxy, chaos tooling | Integration team | Before go-live |
| UAT | Business scenarios + ops fire drill | Scripts | Sales ops, finance, support | Before go-live |
| Production verification | Smoke transaction; reconciliation | Synthetic monitor | Integration team | After each deploy; daily |

---

## Summary

- Push most testing down: exhaustive unit tests for mappings and rules; component tests with mocks that script failures.
- Use contract testing (Pact internally; specification diffs and schema registries for others) to catch breaking changes early.
- Use partner sandboxes for connectivity and real validation, knowing how they differ from production.
- Keep end-to-end tests few and business-focused; use them as post-deployment smoke tests.
- Test failure modes deliberately: outages, duplicates, ordering, crashes, rate limits and backlog drains.
- Load-test to beyond peak, including catch-up; soak-test for leaks.
- Verify in production with synthetics, shadow runs, canaries and reconciliation.

## Exercises

See [`exercises/15-testing.md`](../exercises/15-testing.md).

## Further reading

- Pact documentation (docs.pact.io) and Martin Fowler's "Contract Test" and "Consumer-Driven Contracts" articles (Ian Robinson).
- Testcontainers documentation (testcontainers.com).
- Casey Rosenthal and Nora Jones, *Chaos Engineering* (O'Reilly, 2020).
- Lisa Crispin and Janet Gregory, *Agile Testing Condensed* (2019).
