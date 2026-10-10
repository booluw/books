# Chapter 12. Integrating Enterprise Applications

> "Read the limits page first."

## What you will learn

- The integration surfaces of the enterprise applications you are most likely to meet: Salesforce, SAP, Oracle NetSuite and Fusion, Microsoft Dynamics 365 and Dataverse, Workday, ServiceNow, HubSpot, Shopify, Microsoft 365 / Graph and Google Workspace.
- For each: APIs, eventing options, bulk mechanisms, authentication, limits and known traps.
- Generic patterns that apply to any packaged application, and how to learn a new one quickly.

Enterprise applications are where business processes live. Your value as an integration engineer rises sharply when you know the major platforms' integration surfaces deeply. This chapter is a field guide to them, not a replacement for each vendor's documentation, which you must read.

> **Currency note:** API versions, limits and deprecations below were checked in October 2026. Vendors update them several times a year.

---

## 12.1 How to learn any enterprise application's integration surface

When you meet a new system, answer these questions in order. They form a reusable discovery checklist (also in [Appendix D](../appendices/D-checklists.md)):

1. **What APIs exist?** REST, SOAP, GraphQL, OData, proprietary RPC, file import/export, database access (rarely allowed for SaaS).
2. **How do I authenticate?** OAuth flows supported; integration-user licensing; IP restrictions; certificate requirements.
3. **What are the limits?** Requests per time period, concurrency, payload size, records per call, governance or "unit" models.
4. **How do I get changes out?** Webhooks, event bus, CDC, change-tracking queries, report exports.
5. **How do I load data in bulk?** Bulk APIs, import tools, file-based loaders.
6. **How do I avoid duplicates?** External ID fields, upsert operations, idempotency keys.
7. **What customisation exists?** Custom objects and fields mean the data model differs per customer. How do I discover metadata at runtime?
8. **Where can I run code inside the platform?** Triggers, scripts, extensions, and when to use them versus external middleware.
9. **What are the release and deprecation practices?** API versioning, release cadence, sandbox refreshes.
10. **What do experienced practitioners complain about?** Community forums, Stack Exchange, vendor "known issues". The traps are always documented somewhere.

---

## 12.2 Salesforce (Customer 360 / Agentforce platform)

**Integration surfaces:**

| API | Use |
|---|---|
| **REST API** | CRUD on sObjects; SOQL queries (`/query?q=SELECT…`); upsert by External ID (`PATCH /sobjects/Account/External_Id__c/ABC123`). |
| **Composite APIs** | `composite` (up to 25 subrequests, optionally all-or-none, with references between them), `composite/sobjects` collections (up to 200 records per call), `composite/graph`. |
| **Bulk API 2.0** | Asynchronous CSV-based jobs for large loads and queries (millions of records); simpler than Bulk API 1.0. |
| **SOAP API** | Enterprise and Partner WSDLs; still used by many older integrations and ETL tools. |
| **Metadata API / Tooling API** | Deploying and reading configuration, not business data. |
| **Pub/Sub API** | gRPC over HTTP/2 with Avro-encoded events: subscribe to and publish **Platform Events** and **Change Data Capture (CDC)** events, with replay IDs and client-controlled flow. Successor to the CometD-based Streaming API for most uses. |
| **Platform Events** | Custom event types you define and publish from Apex, flows or APIs; subscribers via Pub/Sub API, Apex triggers or flows. Events are retained on the event bus for 72 hours, so subscribers can replay within that window using replay IDs. |
| **Change Data Capture** | Automatic change events for selected standard and custom objects (create, update, delete, undelete), including the changed fields. |
| **Outbound Messages** | Legacy SOAP-based notifications from workflow rules; still found in older orgs. |
| **Apex callouts and Named Credentials** | Salesforce calling out to external APIs; Named and External Credentials store endpoints and authentication securely. |
| **External Services** | Import an OpenAPI description to make external APIs callable from Flow. |
| **Salesforce Connect / External Objects** | Virtualise external data (OData, cross-org or custom adapters) without copying it. |
| **Data Cloud (Data 360)** | Ingestion connectors, zero-copy data sharing with warehouses, and activation, closely tied to Informatica since 2025. |

**Authentication:** OAuth 2.0 via Connected Apps or the newer **External Client Apps**: JWT bearer flow (certificate-based, recommended for server-to-server), client credentials flow, and web server flow (authorisation code) for user-delegated access. Use a dedicated **integration user** (Salesforce provides an API-only "Salesforce Integration" user licence) with a minimal permission set.

**Limits:**

- **Daily API request allocation** per org over a rolling 24 hours. For Enterprise Edition it is 100,000 plus a per-licence amount (1,000 per Salesforce or Salesforce Platform licence; less for some other licence types), plus purchased add-ons. REST, SOAP, Bulk and Connect API calls count against it. Monitor it with the `/limits` resource or the `Sforce-Limit-Info` response header.
- **Concurrent long-running requests** (over 20 seconds) are limited, typically to 25 in production orgs.
- **Governor limits** inside Apex (SOQL queries, DML statements and CPU time per transaction) constrain triggers and code that run as a result of your API calls. An innocent bulk update can fail because a customer's trigger is not bulk-safe.

**Traps:**

- **Triggers, flows and validation rules fire on API writes.** Your integration's update can trigger automation that fails or that calls out to yet another system. Test against a sandbox with the customer's automation enabled.
- **Record locking:** parallel updates to child records lock the parent (`UNABLE_TO_LOCK_ROW`). Group updates by parent, or reduce parallelism.
- **15- versus 18-character IDs** (Chapter 4).
- **Field-level security:** the integration user cannot see fields not granted, and the API silently omits them in some contexts.
- **Sandboxes** have different limits and data; refreshes wipe integration configuration such as Named Credentials and Connected App consumer secrets in some cases.
- **Three releases per year** (Spring, Summer, Winter). Each API version is supported for years, but old versions are retired on announced schedules. Salesforce retired API versions 21.0 to 30.0 in 2025; keep integrations on recent versions.

---

## 12.3 SAP (S/4HANA, ECC and SAP's cloud portfolio)

SAP landscapes are vast and old. You will meet several generations of interfaces at once.

| Interface | Era | Description |
|---|---|---|
| **IDoc (Intermediate Document)** | 1990s– | SAP's structured message format for asynchronous document exchange (orders `ORDERS05`, invoices `INVOIC02`, materials `MATMAS05`, customers `DEBMAS07`). Transmitted via ALE/EDI ports, tRFC, files or SOAP (IDoc-XML). Status codes trace processing. Still everywhere in ECC and S/4HANA. |
| **RFC / BAPI** | 1990s– | Remote Function Calls; **BAPIs** are stable, documented business function modules (e.g. `BAPI_SALESORDER_CREATEFROMDAT2`). Called via SAP JCo (Java), NCo (.NET), PyRFC or iPaaS connectors. |
| **SOAP web services** | 2000s– | Enterprise services, often via SAP PI/PO. |
| **OData (v2 and v4)** | 2010s– | The primary API style for S/4HANA and SAP Fiori: `API_SALES_ORDER_SRV`, `API_BUSINESS_PARTNER` and hundreds more, documented on the **SAP Business Accelerator Hub** (api.sap.com). |
| **SAP Business Events / Event Mesh** | 2020s– | S/4HANA emits business events (e.g. `sap.s4.beh.salesorder.v1.SalesOrder.Created.v1`), in CloudEvents format, to SAP Event Mesh or Advanced Event Mesh (based on Solace). |
| **CDS views and SAP Datasphere / Business Data Cloud** | 2020s– | For analytical extraction (ODP-based extraction, replication flows). |

**Key concepts:**

- **Clean core:** SAP's guidance for S/4HANA (especially in its cloud editions and the RISE with SAP programme) is to keep custom code out of the ERP core and integrate through released, stable APIs and events, with extensions on **SAP BTP** (Business Technology Platform). Prefer released OData APIs and events over custom RFCs and table access.
- **SAP Integration Suite** is SAP's iPaaS, the successor to **SAP PI/PO**, whose mainstream maintenance ends on **31 December 2027**. PO-to-Integration-Suite migration is one of the biggest integration work streams of 2025–2028.
- **SAP Cloud Connector** links cloud services (BTP, Integration Suite) to on-premises SAP systems through an outbound tunnel, with fine-grained exposure of resources.
- **Business Partner model:** in S/4HANA, customers and vendors are unified as Business Partners (BP). Older interfaces built for ECC's separate customer and vendor masters need redesign.
- **Authentication:** basic auth with communication users, X.509 certificates, OAuth via SAP BTP, principal propagation for user context, and SAML.

**Traps:**

- Leading zeros in material and customer numbers (`000000000000012345`). Conversion exits (`ALPHA`) add and strip them inconsistently across interfaces.
- Date formats (`YYYYMMDD`), and OData v2 dates as `/Date(…)/`.
- Units of measure have internal versus external codes.
- IDoc segments and qualifiers carry meaning that only the mapping documentation explains.
- Locked records and update tasks: asynchronous posting means "success" from a BAPI may precede the actual database commit. Call `BAPI_TRANSACTION_COMMIT`, and understand the logical unit of work.
- Transports and client-specific configuration differ between DEV, QA and PRD systems.

---

## 12.4 Oracle NetSuite

| Interface | Notes |
|---|---|
| **SuiteTalk REST web services** | Record API (CRUD, upsert via `externalId`), **SuiteQL** queries via REST, asynchronous requests. OAuth 2.0 (authorisation code, client credentials with certificate / M2M). The strategic API. |
| **SuiteTalk SOAP web services** | Long the dominant NetSuite API. **2025.2 is the last planned SOAP endpoint; from 2027.1 only the 2025.2 endpoint is supported; SOAP is removed in 2028.2.** All new integrations should use REST with OAuth 2.0. Migration from SOAP is a major work item for NetSuite integrations through 2028. |
| **RESTlets** | Custom REST endpoints written in SuiteScript, deployed inside NetSuite. Flexible; widely used by iPaaS connectors (Celigo, for example). |
| **SuiteScript** (2.1) | User event scripts, scheduled scripts and map/reduce scripts inside NetSuite; `N/https` for outbound calls. |
| **Saved searches and SuiteAnalytics** | Exporting data; SuiteAnalytics Connect for ODBC/JDBC read access. |
| **CSV import** | For bulk loads. |

**Limits:** NetSuite governs **concurrency** (concurrent web-service requests per account, depending on service tier and SuiteCloud Plus licences) and **governance units** for scripts. Exceeding concurrency returns errors that must be retried with backoff.

**Traps:** record-type differences (sales order versus cash sale versus invoice); subsidiaries and multi-currency in OneWorld accounts; item types (inventory, non-inventory, kit, assembly); custom fields named by script ID (`custbody_…`, `custcol_…`); accounting periods closing; and sandbox refresh behaviour.

---

## 12.5 Oracle Fusion Cloud Applications (ERP, HCM, SCM)

- **REST APIs** for most business objects; **SOAP web services** for many others.
- **File-Based Data Import (FBDI):** spreadsheets and templates converted to CSV, zipped, uploaded to UCM (the content server), then processed by Enterprise Scheduler (ESS) jobs. This is the standard bulk-load route for ERP.
- **HCM Data Loader (HDL)** for HR bulk loads; **HCM Extracts** for outbound HR data.
- **BI Publisher reports** as an outbound extract mechanism (often scheduled and delivered to SFTP).
- **Business events** for selected objects, subscribed via Oracle Integration (OIC).
- Oracle Integration (OIC) provides adapters that hide much of this complexity.

---

## 12.6 Microsoft Dynamics 365 and Dataverse

- **Dataverse Web API** (OData v4) for Dynamics 365 Sales, Customer Service, Field Service and Power Apps: CRUD, `$batch`, upsert by **alternate keys**, `$filter`, `$expand`, and change tracking (`Prefer: odata.track-changes` delta links).
- **Dynamics 365 Finance & Supply Chain Management** (formerly AX): OData data entities, the **Data Management Framework** (DMF) for bulk packages, the **Recurring Integrations** API, business events (to Service Bus, Event Grid, HTTPS or Power Automate), and dual-write to Dataverse.
- **Plugins and webhooks** in Dataverse; **Azure Service Bus integration** for publishing execution context.
- **Virtual tables** for virtualising external data.
- **Authentication:** Microsoft Entra ID OAuth 2.0 (client credentials with an **application user** in Dataverse, or delegated). Certificates or federated credentials preferred over client secrets.
- **Limits:** service-protection API limits per user (requests, execution time and concurrency within a sliding window) return `429` with `Retry-After`; plus entitlement-based request allocations per licence.

---

## 12.7 Workday (HCM, Financials)

- **Workday Web Services (SOAP):** comprehensive, versioned (twice-yearly releases); the backbone of most Workday integrations.
- **Workday REST APIs:** a growing set, plus **Workday Extend** for custom apps.
- **Reports-as-a-Service (RaaS):** custom reports exposed as REST/SOAP endpoints returning XML, JSON or CSV. A very common way to extract data with exactly the fields needed.
- **Enterprise Interface Builder (EIB):** spreadsheet-based inbound and outbound integrations built within Workday.
- **Workday Studio:** an Eclipse-based IDE for complex integrations running on Workday's cloud.
- **Cloud Connect** packaged integrations (payroll, benefits providers).
- **Integration System Users (ISUs)** with security groups; OAuth 2.0 via API clients; X.509 for some flows.
- **Effective dating** is central: HR data changes have effective dates, and future-dated changes, retroactive corrections and rescinded transactions must be handled. Incremental extracts use "transaction log" queries with effective-from and entry-moment ranges.

---

## 12.8 ServiceNow

- **Table API** (REST CRUD on any table), **Import Set API** (staging tables with transform maps, good for inbound integrations with mapping inside ServiceNow), **Aggregate API**, **Attachment API**, **Batch API**.
- **Scripted REST APIs** for custom endpoints.
- **IntegrationHub** with **spokes** (prebuilt connectors) and Flow Designer; **Stream Connect** (Kafka) for event streaming.
- **MID Server:** an on-premises agent for reaching internal systems (discovery, orchestration, integrations).
- **Outbound REST messages** and **business rules** for event-driven outbound calls.
- **Authentication:** basic, OAuth 2.0, mutual auth; integration users with roles.
- **Traps:** business rules firing on API writes; ACLs silently filtering fields; `sys_id` versus display values (`sysparm_display_value`); rate-limit rules configured per instance.

---

## 12.9 Other platforms you will meet often

| Platform | Key integration facts |
|---|---|
| **HubSpot** | REST APIs (CRM objects, associations v4), webhooks via apps, OAuth for public apps, private-app tokens for single portals; rate limits per app and per account with burst and daily caps; search API has its own lower limits. |
| **Shopify** | The **GraphQL Admin API** is the primary API. The REST Admin API has been **legacy since 1 October 2024**, and **new public apps must use GraphQL only since 1 April 2025**. Cost-based rate limits; bulk operations (asynchronous JSONL exports and imports); webhooks (HTTP, Amazon EventBridge or Google Pub/Sub delivery); quarterly API versions (`2026-10`). |
| **Microsoft Graph** | Unified REST API for Microsoft 365 and Entra ID: users, groups, mail, calendar, Teams, SharePoint and OneDrive. `$batch`; **delta queries** for change tracking; **change notifications** (webhooks, or via Event Hubs or Event Grid) with subscription renewal; throttling (`429`) by service. |
| **Google Workspace** | Admin SDK, Gmail, Calendar (`syncToken` incremental sync, push notifications via channels), Drive (changes API); domain-wide delegation for service accounts (to be used with great care and minimal scopes). |
| **Stripe** | The reference REST API: idempotency keys, expansion, cursor pagination, date-based versioning, signed webhooks with retries for up to 3 days, test-mode clocks. |
| **Zendesk, Jira / Atlassian, Slack, GitHub** | REST (plus GraphQL for GitHub), webhooks or event subscriptions, OAuth apps, cursor pagination, documented rate limits. |
| **Snowflake / BigQuery / Databricks** | SQL APIs, bulk loading (COPY, Snowpipe, Storage Write API), external tables, data sharing; frequently both source and target of integrations. |

---

## 12.10 Generic patterns for packaged applications

1. **Use the platform's upsert by external ID** for idempotent writes, and store the other system's ID in it.
2. **Prefer events or change tracking** (Salesforce CDC, Graph delta queries, Dataverse change tracking, S/4HANA business events) over polling with timestamps; fall back to incremental polling with overlap and de-duplication.
3. **Use bulk interfaces for volume** (Salesforce Bulk API 2.0, Oracle FBDI, Dynamics DMF, Shopify bulk operations, NetSuite CSV import). Never loop a single-record API over a million rows.
4. **Respect in-platform automation:** your writes trigger customer-specific logic. Test against realistic sandboxes.
5. **Discover metadata at runtime** in product integrations: custom fields, picklist values and required fields differ per customer (Salesforce `describe`, NetSuite metadata catalogue, Dataverse `EntityDefinitions`).
6. **Budget API limits** across all integrations sharing an org or tenant. One rogue integration can exhaust the daily allocation for all of them. Monitor usage centrally.
7. **Isolate in-platform code from integration logic:** keep heavy transformation in middleware unless the platform clearly benefits from in-platform scripts; but use in-platform events and triggers to *signal* changes.
8. **Plan for vendor release cycles:** test in preview sandboxes before each major release (Salesforce three times a year, Workday twice a year, Microsoft in waves, SAP cloud quarterly).
9. **Track deprecations** (NetSuite SOAP by 2028.2, Shopify REST, retired Salesforce API versions) in your integration catalogue with target dates.

---

## Summary

- Each enterprise platform offers multiple generations of interfaces. Learn which are strategic, which are legacy, and which are being removed.
- Use upserts by external ID, bulk APIs, and event or change-tracking mechanisms; avoid naive polling and per-record loops.
- Read limits and in-platform automation behaviour first; they cause most surprises.
- Track vendor release and deprecation calendars as part of operating integrations.

## Exercises

See [`exercises/12-enterprise-applications.md`](../exercises/12-enterprise-applications.md).

## Further reading

- Salesforce *Integration Patterns and Practices* (developer.salesforce.com) and the *Salesforce Developer Limits and Allocations Quick Reference*.
- SAP Business Accelerator Hub (api.sap.com) and SAP's *Integration Solution Advisory Methodology*.
- Oracle NetSuite *SOAP Web Services To REST Web Services Upgrade Guide*.
- Microsoft Learn: Dataverse Web API; Microsoft Graph throttling and delta query guidance.
- Workday Community: Integration documentation (requires customer or partner access).
