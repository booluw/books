# Appendix A. Glossary

Terms are defined as used in this book. The chapter where a term is explained in depth is shown in brackets.

| Term | Definition |
|---|---|
| **A2A (Agent2Agent)** | Open protocol, introduced by Google in 2025 and hosted by the Linux Foundation, for agents to discover each other (Agent Cards) and exchange tasks. [18] |
| **AAIF** | Agentic AI Foundation, a Linux Foundation directed fund founded in December 2025; home of MCP. [18] |
| **ACK / NAK** | Positive / negative acknowledgement of a message, e.g. in HL7 v2 over MLLP. [13] |
| **ADR** | Architecture Decision Record: a short document recording one decision, its context and consequences. [14] |
| **Aggregator** | EIP pattern that combines related messages into one, using a correlation rule, completeness condition and aggregation strategy. [5] |
| **Anti-Corruption Layer (ACL)** | A translation layer that protects your domain model from another system's model. [17] |
| **API gateway** | Runtime component enforcing authentication, rate limits, routing and transformation for APIs. [11] |
| **API-led connectivity** | Layering of System, Process and Experience APIs, popularised by MuleSoft. [17] |
| **Arazzo** | OpenAPI Initiative specification for describing multi-step API workflows (1.1, May 2026). [6] |
| **AS2** | Applicability Statement 2 (RFC 4130): EDI over HTTP(S) with S/MIME signing, encryption and signed receipts (MDNs). [13] |
| **AsyncAPI** | Specification for describing event-driven and message-based APIs (3.0 in 2023, 3.1 in 2026). [7] |
| **At-least-once / at-most-once / exactly-once** | Delivery guarantees; integrations design for at-least-once delivery with idempotent consumers. [7] |
| **Backfill** | Initial or corrective bulk load of historical data. [14] |
| **Backpressure** | Mechanisms that slow producers or consumers to match downstream capacity. [7] |
| **BAA** | Business Associate Agreement, required under HIPAA for vendors handling PHI. [10] |
| **BAPI / RFC** | SAP's Business API function modules / Remote Function Call protocol. [12] |
| **BOLA** | Broken Object Level Authorization, OWASP API1:2023. [10] |
| **Bounded context** | DDD concept: a boundary within which a domain model is consistent. [17] |
| **Bulkhead** | Isolation of resources (pools, queues) so one failing dependency or tenant cannot exhaust all capacity. [8] |
| **C4 model** | Context, Container, Component, Code diagrams for software architecture. [14] |
| **C4E** | Center for Enablement: a central team that enables others to build integrations through platforms, assets and coaching. [17] |
| **Canonical data model** | A shared, system-neutral representation of business entities used between systems. [4] |
| **CDC** | Change Data Capture: capturing database changes as a stream of events, ideally from the transaction log. [9] |
| **Circuit breaker** | Component that stops calling a failing dependency for a cool-down period, then tests recovery. [8] |
| **Claim check** | EIP pattern: store a large payload elsewhere and pass a reference. [5] |
| **CloudEvents** | CNCF graduated specification for event metadata (`id`, `source`, `type`, `specversion`…). [7] |
| **Compensating action** | A business operation that semantically undoes a completed saga step. [8] |
| **Competing consumers** | Multiple consumers on one queue sharing the work. [5] |
| **Consumer group** | Kafka mechanism that divides a topic's partitions among consumers. [7] |
| **Consumer lag** | How far a consumer is behind the head of a stream or queue. [16] |
| **Content-based router** | EIP pattern routing messages by their content. [5] |
| **Contract testing** | Testing that a consumer's expectations match a provider's behaviour (e.g. Pact). [15] |
| **Correlation ID** | Identifier that ties related messages or log lines together. [5, 16] |
| **CQRS** | Command Query Responsibility Segregation: separate write and read models. [7] |
| **Cursor pagination** | Paging by an opaque pointer to the last item seen (keyset), stable under concurrent writes. [6] |
| **Data contract** | Agreement on schema, semantics, quality and change policy for a dataset or stream. [9] |
| **Dead-letter queue (DLQ)** | Where messages go after they cannot be processed within the retry policy. [8] |
| **Deadline propagation** | Passing the remaining time budget to downstream calls. [3, 8] |
| **Debezium** | Open-source, log-based CDC platform. [9] |
| **DPoP** | Demonstrating Proof of Possession (RFC 9449): binds OAuth tokens to a client key. [10] |
| **Dual write** | Writing to two systems (e.g. database and broker) without a shared transaction, which risks inconsistency. [8] |
| **Durable execution** | Workflow engines that persist each step so processes survive crashes (Temporal, Step Functions…). [8, 11] |
| **EDI** | Electronic Data Interchange: standard business documents exchanged between organisations (X12, EDIFACT). [13] |
| **EIP** | *Enterprise Integration Patterns* (Hohpe & Woolf, 2003) and the vocabulary it defines. [5] |
| **Embedded iPaaS** | Integration platform embedded in a SaaS product for customer-facing integrations. [11] |
| **ESB** | Enterprise Service Bus: SOA-era middleware for routing, transformation and mediation. [2, 11] |
| **ETag** | HTTP entity tag representing a resource version, used for caching and optimistic concurrency. [3, 6] |
| **ETL / ELT** | Extract-Transform-Load / Extract-Load-Transform. [9] |
| **Event** | A fact that something happened, named in the past tense. [5, 7] |
| **Event-carried state transfer** | Events containing enough state that consumers need not call back. [7] |
| **Event sourcing** | Storing state as an append-only sequence of events. [7] |
| **External ID** | A field holding another system's identifier, enabling upserts and cross-reference. [4, 12] |
| **FAPI** | Financial-grade API: OpenID Foundation high-security OAuth profile. [10, 13] |
| **FHIR** | Fast Healthcare Interoperability Resources: HL7's RESTful healthcare standard. [13] |
| **Fitness function** | Automated check that an architecture keeps a desired property. [17] |
| **Golden file** | Stored expected output used to test a transformation. [4, 15] |
| **HL7 v2** | Pipe-delimited clinical messaging standard used inside hospitals. [13] |
| **HMAC** | Hash-based Message Authentication Code, used to sign webhooks and requests. [7, 10] |
| **Idempotency key** | Client-supplied unique value that lets a server de-duplicate repeated unsafe requests. [6, 8] |
| **Idempotent** | Repeating an operation has the same effect as doing it once. [3, 8] |
| **IDoc** | SAP Intermediate Document, a structured message format for asynchronous exchange. [12] |
| **Inbox (de-duplication table)** | Table of processed message IDs written in the same transaction as their effect. [8] |
| **iPaaS** | Integration Platform as a Service. [11] |
| **ISO 20022** | Global financial messaging standard (`pain`, `pacs`, `camt`…). [13] |
| **JSON Schema** | Vocabulary for validating JSON (current: 2020-12). [4] |
| **JWT** | JSON Web Token (RFC 7519). [10] |
| **KRaft** | Kafka's built-in Raft-based metadata mode; the only mode since Kafka 4.0. [7] |
| **Lethal trifecta** | Agent risk combination: private data + untrusted content + external communication. [18] |
| **Log (stream)** | Append-only, retained, replayable sequence of messages (Kafka, Kinesis). [7] |
| **Mapping specification** | Field-by-field transformation contract between systems. [4, 14] |
| **MCP** | Model Context Protocol: open protocol connecting AI applications to tools and data. [18] |
| **MDM** | Master Data Management. [9] |
| **MDN** | Message Disposition Notification: AS2 signed receipt. [13] |
| **MFT** | Managed File Transfer. [11] |
| **MLLP** | Minimal Lower Layer Protocol, framing for HL7 v2 over TCP. [13] |
| **mTLS** | Mutual TLS: both client and server present certificates. [3, 10] |
| **NFR** | Non-functional requirement (volume, latency, availability, security…). [14] |
| **OAuth 2.0 / 2.1** | Delegated authorisation framework (RFC 6749; 2.1 is an IETF draft consolidating best practice). [10] |
| **OData** | Open Data Protocol, used by SAP and Microsoft. [6, 12] |
| **OIDC** | OpenID Connect: identity layer on OAuth 2.0. [10] |
| **OpenAPI** | Standard description format for HTTP APIs (current: 3.2, September 2025). [6] |
| **OpenTelemetry (OTel)** | Vendor-neutral standard for traces, metrics and logs. [16] |
| **Orchestration / choreography** | Central coordination vs. event-driven reaction across services. [5] |
| **Outbox (transactional)** | Writing events to a table in the same transaction as business data, then relaying them. [8] |
| **Partition** | Ordered shard of a Kafka topic; ordering is guaranteed within a partition. [7] |
| **Peppol** | International e-invoicing network and specifications. [13] |
| **PKCE** | Proof Key for Code Exchange (RFC 7636), required for OAuth authorization code clients in OAuth 2.1. [10] |
| **Poison message** | A message that fails processing every time. [8] |
| **Problem Details** | RFC 9457 error format (`application/problem+json`). [6] |
| **Publish-subscribe** | Messaging where each message goes to every subscriber. [5, 7] |
| **QHIN** | Qualified Health Information Network under TEFCA. [13] |
| **QUERY method** | HTTP method for safe, idempotent requests with a body (RFC 10008, June 2026). [3] |
| **Rate limit / quota** | Limits on request rate / total usage. [6] |
| **Reconciliation** | Periodic comparison of systems to detect and repair drift. [8] |
| **Replay** | Reprocessing stored or dead-lettered messages. [8, 16] |
| **Retry budget** | Cap on retries as a proportion of requests to prevent amplification. [8] |
| **Reverse ETL** | Syncing modelled warehouse data back into operational tools. [9] |
| **Runbook** | Operational guide for alerts and procedures. [16] |
| **Saga** | Long-running business transaction made of local steps with compensations. [8] |
| **Schema registry** | Service storing schemas and enforcing compatibility (e.g. Confluent, Apicurio). [4, 7] |
| **SCIM** | System for Cross-domain Identity Management: provisioning API standard. [10] |
| **Share group** | Kafka consumer model (KIP-932, production-ready in 4.2) with per-record acknowledgement: "Queues for Kafka". [7] |
| **SLI / SLO / SLA** | Service Level Indicator / Objective / Agreement. [16] |
| **SMART on FHIR** | OAuth/OIDC-based authorisation framework for FHIR apps. [13] |
| **SOAP / WSDL** | XML web-services protocol / its contract language. [6] |
| **Splitter** | EIP pattern breaking one message into many. [5] |
| **SSRF** | Server-Side Request Forgery, OWASP API7:2023. [10] |
| **Strangler fig** | Incremental replacement of a legacy system behind a façade. [17] |
| **System of record** | The authoritative source for a piece of data. [1, 9] |
| **TEFCA** | Trusted Exchange Framework and Common Agreement (US health data exchange). [13] |
| **Thin event** | Event carrying only identifiers; consumers fetch details. [7] |
| **Token bucket** | Rate-limiting algorithm allowing bursts up to a capacity and a steady refill rate. [6, 8] |
| **Tombstone** | Record indicating deletion (in APIs or Kafka log compaction). [6, 9] |
| **Trace context** | W3C standard (`traceparent`) for propagating distributed-trace identifiers. [16] |
| **Unified API** | One normalised API per software category across many vendors. [11] |
| **Upsert** | Update if exists, insert otherwise, by a key. [8] |
| **Value map** | Lookup table translating code values between systems. [4] |
| **VAN** | Value-Added Network for EDI. [13] |
| **Visibility timeout** | SQS period during which a received message is hidden from other consumers. [7] |
| **Webhook** | HTTP callback sent by a provider when an event occurs. [7] |
| **Wire tap** | EIP pattern copying messages to a secondary channel. [5] |
| **X12 / EDIFACT** | North American / international EDI standards. [13] |
