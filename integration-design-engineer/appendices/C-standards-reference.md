# Appendix C. Standards and Specifications Reference

Status as checked in **October 2026**. "Draft" means an IETF Internet-Draft or equivalent work in progress: do not treat it as final.

## Web and HTTP

| Standard | Identifier | Status / version | Notes |
|---|---|---|---|
| HTTP Semantics | RFC 9110 | 2022 | Methods, status codes, headers |
| HTTP Caching | RFC 9111 | 2022 | |
| HTTP/1.1, /2, /3 | RFC 9112, 9113, 9114 | 2022 | |
| HTTP QUERY method | **RFC 10008** | June 2026, Proposed Standard | Safe, idempotent request with body |
| Problem Details for HTTP APIs | RFC 9457 | 2023 (obsoletes RFC 7807) | `application/problem+json` |
| Web Linking | RFC 8288 | 2017 | `Link` header, `rel="next"` |
| Sunset header | RFC 8594 | 2019 | |
| Deprecation header | RFC 9745 | March 2025 | |
| HTTP Message Signatures | RFC 9421 | 2024 | |
| Idempotency-Key header | draft-ietf-httpapi-idempotency-key-header | Draft (‑07, Oct 2025) | Widely implemented pattern |
| RateLimit header fields | draft-ietf-httpapi-ratelimit-headers | Draft | Many APIs use `X-RateLimit-*` |
| JSON | RFC 8259 | 2017 | |
| JSON Merge Patch / JSON Patch | RFC 7396 / RFC 6902 | | |
| JSON Pointer | RFC 6901 | | |
| JSON Schema | Draft 2020-12 | Current | Used by OpenAPI 3.1+ |
| Date/time on the internet | RFC 3339 | | ISO 8601 profile |
| UUIDs | RFC 9562 | 2024 | Includes UUIDv7 |
| CSV | RFC 4180 | Informational | |
| TLS 1.3 / deprecate TLS 1.0–1.1 | RFC 8446 / RFC 8996 | | |
| W3C Trace Context | W3C Recommendation | | `traceparent`, `tracestate` |

## API and event description

| Specification | Current version | Notes |
|---|---|---|
| OpenAPI Specification | **3.2.0** (Sept 2025); 3.1 widely supported | `QUERY` and custom methods, streaming media types, hierarchical tags |
| Arazzo | **1.1.0** (May 2026) | Workflows across OpenAPI and AsyncAPI |
| Overlay | 1.0 (Oct 2024); 1.1 in progress | Modifications to OpenAPI documents |
| AsyncAPI | **3.1.0** (2026); 3.0.0 (Dec 2023) | Event-driven API descriptions |
| CloudEvents | 1.0.x; CNCF graduated (Jan 2024) | Event envelope, protocol bindings |
| GraphQL | October 2021 spec edition (plus working drafts) | |
| gRPC / Protocol Buffers | proto3; Editions | |
| Standard Webhooks | Community specification | Webhook signing headers |

## Identity and security

| Standard | Identifier | Status |
|---|---|---|
| OAuth 2.0 | RFC 6749 / 6750 | Standard |
| OAuth 2.1 | draft-ietf-oauth-v2-1 | **Draft** (revision 16, Sept 2026) |
| OAuth 2.0 Security BCP | RFC 9700 | January 2025 |
| PKCE | RFC 7636 | |
| JWT / JWT bearer assertions | RFC 7519 / RFC 7523 | |
| Token Exchange | RFC 8693 | |
| Device Authorization Grant | RFC 8628 | |
| mTLS client auth and bound tokens | RFC 8705 | |
| DPoP | RFC 9449 | |
| PAR / RAR | RFC 9126 / RFC 9396 | |
| Authorization Server Metadata | RFC 8414 | |
| Protected Resource Metadata | RFC 9728 | 2025 |
| Resource Indicators | RFC 8707 | |
| Dynamic Client Registration | RFC 7591 | |
| OpenID Connect Core | OpenID Foundation | |
| FAPI 2.0 | OpenID Foundation | Security Profile final |
| SCIM 2.0 | RFC 7643 / 7644 | |
| SAML 2.0 | OASIS | |
| OWASP API Security Top 10 | 2023 edition | Latest edition |

## Messaging and streaming

| Technology / standard | Current (Oct 2026) | Notes |
|---|---|---|
| Apache Kafka | 4.x (4.2 early 2026) | KRaft only since 4.0; share groups GA in 4.2 |
| AMQP 0-9-1 / AMQP 1.0 | AMQP 1.0 = ISO/IEC 19464 | RabbitMQ 4.x supports both |
| MQTT | 5.0 / 3.1.1 | |
| JMS / Jakarta Messaging | Jakarta Messaging 3.x | |

## AI agent protocols

| Protocol | Current | Governance |
|---|---|---|
| Model Context Protocol | **2026-07-28** revision (stateless core, extensions) | Agentic AI Foundation (Linux Foundation) |
| Agent2Agent (A2A) | 2025– | Linux Foundation |

## B2B / EDI

| Standard | Notes |
|---|---|
| ANSI ASC X12 | Versions 004010, 005010 (HIPAA), up to 008xxx |
| UN/EDIFACT | Directories D.96A, D.01B, … D.2x |
| AS2 (RFC 4130), AS4 (OASIS ebMS 3.0 profile) | Transports |
| GS1 (GTIN, GLN, SSCC), EPCIS 2.0 | Supply chain identifiers and events |

## Healthcare

| Standard | Notes |
|---|---|
| HL7 v2.x | v2.5.1 common in the US |
| HL7 FHIR | R4 (4.0.1) in production and regulation; R5 (2023); R6 balloted January 2026 |
| US Core IG | 9.0.0 (R4-based, USCDI v6) latest; certification references specific versions |
| SMART App Launch | v2 scopes |
| CDS Hooks | |
| X12 HIPAA 005010 | 837, 835, 270/271, 276/277, 278, 834, 820 |
| CMS-0057-F | FHIR R4 payer APIs, most due 1 January 2027 |
| DICOM / DICOMweb | Imaging |

## Finance and payments

| Standard | Notes |
|---|---|
| ISO 20022 | `pain`, `pacs`, `camt`… ; SWIFT CBPR+ MT/MX coexistence ended 22 Nov 2025; structured addresses required from Nov 2026 |
| SWIFT MT | Legacy; retirement dates by category |
| NACHA ACH | US batch payments |
| ISO 8583 | Card messaging |
| FIX | Trading |
| PCI DSS | v4.0.1 (future-dated requirements mandatory from 31 March 2025) |
| FDX | US open-banking API standard |
| Berlin Group NextGenPSD2 | European open-banking APIs |

## E-invoicing

| Standard / mandate | Notes |
|---|---|
| EN 16931 (UBL 2.1 / UN/CEFACT CII syntaxes) | EU semantic standard |
| Peppol BIS Billing 3.0 | Network profile |
| Germany | Receive from 1 Jan 2025; issue from 1 Jan 2027 (>€800k turnover) / 1 Jan 2028 |
| France | Reform started 1 Sept 2026 |
| EU ViDA | Intra-EU B2B e-invoicing and digital reporting from 1 July 2030 |
