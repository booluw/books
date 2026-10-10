# Chapter 1. What an Integration Design Engineer Is

> "Every system is someone else's legacy system."
> (common saying among integration engineers)

## What you will learn

- What "integration" means in software and why organisations pay specialists to do it.
- What an Integration Design Engineer is responsible for, and how the role differs from neighbouring roles.
- The job titles this role hides behind, and how to read a job posting.
- What a typical week looks like, and the problems you will spend most of your time on.
- The core skills of the role, which the rest of the book teaches.

---

## 1.1 The problem integration solves

Picture a mid-sized online retailer. It uses:

- **Shopify** for its storefront.
- **Stripe** to take payments.
- **NetSuite**, an ERP (Enterprise Resource Planning system), for accounting and inventory.
- A **third-party logistics (3PL) warehouse** that ships orders and exposes an SFTP server and an old SOAP API.
- **Salesforce** for its sales and customer-service team.
- **Snowflake** as its data warehouse, for reporting.
- **Okta** for employee identity.
- **Zendesk** for support tickets.
- An **AI support agent** that answers customer questions.

When a customer clicks *Buy*, a chain of things must happen:

1. Stripe captures the payment.
2. The order is recorded in NetSuite so revenue, tax and inventory are correct.
3. The 3PL receives a pick-and-pack instruction.
4. When the 3PL ships, a tracking number flows back to Shopify so the customer gets an email.
5. Salesforce shows the order on the customer's record so a sales rep can see it.
6. Snowflake receives the data for the finance dashboard.
7. If the customer later asks the AI agent "Where's my order?", the agent needs live, permissioned access to the order and the shipment status.

No vendor sells this chain. Each system has its own data model, its own API style, its own rate limits, its own authentication scheme and its own failure modes. Somebody has to design how they connect. That design must answer questions such as:

- Which system is the **source of truth** for each piece of data? Is the customer's address owned by Shopify or by Salesforce?
- Should the warehouse be told about the order **immediately** (an event) or in a **batch** every 15 minutes?
- What happens if NetSuite is down for maintenance when the order arrives? Is the order lost, delayed, or duplicated?
- What if the same webhook arrives twice? Will the customer be shipped two parcels?
- How does a field called `province_code` in Shopify become `state` in NetSuite and `ShipToState` in the 3PL's XML?
- Who is alerted at 3 a.m. when orders stop flowing, and how do they replay the ones that failed?
- How do we prove to an auditor that card data never touched our servers?

**Integration** is the discipline of answering those questions and then building, testing and operating the result. An **Integration Design Engineer** is the engineer who owns that discipline: they design the connections between systems, and usually build and run them too.

### Why it is a specialism

Most software engineers build *one* system and control both its code and its database. Integration engineers work in the spaces *between* systems, where:

- **You control almost nothing.** The systems on either side belong to vendors, partners or other teams. You cannot change their APIs, their uptime or their release schedules.
- **Failure is normal.** Networks drop packets, partners rotate certificates without warning, and APIs throttle you during their peak hours. In a distributed system, partial failure is the default state, not the exception.
- **Semantics matter more than syntax.** Moving JSON from A to B is easy. Knowing that "customer" in the CRM means a *company*, while "customer" in the billing system means a *paying account*, and that the two do not map one-to-one, is the hard part.
- **Mistakes are expensive and visible.** A bug in a reporting screen annoys a user. A bug in an order integration ships goods that were never paid for, double-charges customers, or files the wrong tax.
- **The work outlives the people.** An integration built today will run for ten years, maintained by people who were not in the room when it was designed.

These conditions call for a distinct skill set: distributed-systems reliability, data modelling and transformation, security and identity, deep knowledge of specific platforms, and above all the ability to elicit and document requirements from people in different departments.

---

## 1.2 A working definition

> **An Integration Design Engineer designs, builds and operates the interfaces and data flows that let independent software systems work together, so that business processes spanning those systems are correct, reliable, secure, observable and maintainable.**

Each word in the definition matters:

| Term | Meaning in practice |
|---|---|
| *Designs* | Chooses the integration style, the pattern, the contract, the data mapping and the error-handling strategy, and writes them down. |
| *Builds* | Writes code, configures an iPaaS flow, or both. Few roles are pure design. |
| *Operates* | Monitors the flows, handles failures, replays messages, and responds to incidents. |
| *Interfaces* | APIs, event channels, files and database views: the contracts between systems. |
| *Data flows* | The movement and transformation of business data across systems. |
| *Independent systems* | Systems with their own owners, lifecycles and data models. |
| *Business processes* | The real goal. Nobody wants "an integration"; they want "order to cash" or "hire to retire" to work. |
| *Correct, reliable…* | The non-functional requirements this book keeps returning to. |

---

## 1.3 The many names of the role

Job titles in integration are messy. The same work appears under many names, and the same name can mean different work. Here are the titles you will see, grouped by what the job usually involves *(as observed in postings through 2026)*.

### Hands-on build roles

| Title | Typical focus |
|---|---|
| **Integration Engineer / Integrations Engineer** | Building and maintaining connections between internal systems or between a product and third parties. The most common title. |
| **Integration Developer** | Same as above, often platform-specific: "MuleSoft Developer", "Boomi Developer", "Workato Developer", "SAP CPI Developer". |
| **API Engineer / API Developer** | Designing and building APIs that others integrate *with*. |
| **Software Engineer, Integrations** | At a SaaS company, building the product's native integrations (for example, "Sync with Salesforce" or "Connect to Slack"). |
| **Data Integration Engineer / ETL Developer** | Moving data in bulk into warehouses and lakes (see Chapter 9). |
| **EDI Analyst / EDI Developer** | Business-to-business document exchange with trading partners (see Chapter 13). |
| **HL7 / FHIR Interface Analyst or Engineer** | Healthcare integration (see Chapter 13). |

### Design and architecture roles

| Title | Typical focus |
|---|---|
| **Integration Architect / Enterprise Integration Architect** | Sets integration strategy, standards and patterns across an organisation; chooses platforms; reviews designs. |
| **Solutions Architect** (integration-heavy) | Designs end-to-end solutions, often for a specific product or customer. |
| **API Architect / API Product Manager** | Owns API standards, governance and the API portfolio as a product. |
| **Integration Design Engineer** | Where the title is used in software, it usually sits between engineer and architect: a senior engineer who owns the *design* of integrations and leads their delivery. |

### Customer-facing roles

| Title | Typical focus |
|---|---|
| **Solutions Engineer / Sales Engineer** | Pre-sales: demonstrates how a product integrates with a prospect's systems. |
| **Implementation Engineer / Onboarding Engineer** | Post-sales: connects a newly purchased product to the customer's systems. |
| **Technical Account Manager / Integration Consultant** | Ongoing advice to customers. |
| **Forward Deployed Engineer** | Embedded with a customer to make a product, increasingly an AI product, work inside the customer's environment. Most of that work is integration. |

### The other meanings of the title

In aerospace, defence, automotive and electronics, "Integration Design Engineer" and "Design Integration Engineer" usually describe mechanical or electrical work. Examples include Rohde & Schwarz's *Integration Design Engineer* (assembly drawings and electrical diagrams in Siemens NX) and Shield AI's spatial integration roles (installing and routing subsystems in aircraft). In semiconductors, a "Physical Design Integration Engineer" works on chip timing and layout. **If a posting mentions CAD, GD&T, harnesses, tolerance stacks or tape-out, it is not the role this book describes.**

### How to read a job posting

Ignore the title and look for these signals:

- **Technologies named:** REST, SOAP, Kafka, MuleSoft, Boomi, Workato, Azure Logic Apps, SAP Integration Suite or Salesforce APIs mean software integration.
- **Verb balance:** "design, define standards, review" points to architecture. "Develop, configure, maintain, support" points to engineering. "Demo, scope, onboard" points to customer-facing work.
- **Who you serve:** internal IT and business teams (enterprise integration), the company's own product and customers (product integrations), or external customers (solutions/implementation).
- **On-call:** if the posting mentions production support, you will operate what you build.

---

## 1.4 Three flavours of the job

Most integration jobs fall into one of three settings. They share the same fundamentals but feel different day to day.

### Flavour 1: Enterprise (internal) integration

You work for a company that *uses* software: a bank, a retailer, a hospital, a manufacturer, a government agency. Your customers are internal departments. You connect the company's purchased and in-house systems: ERP to CRM, HR to identity, e-commerce to warehouse.

- **Typical tools:** an iPaaS or ESB (MuleSoft, Boomi, Azure Integration Services, SAP Integration Suite, Informatica, IBM App Connect), API gateways, message brokers, managed file transfer.
- **Typical challenges:** legacy systems, many stakeholders, change control, audit and compliance, long project timelines.
- **Typical org:** an "Integration Competency Centre", "Integration Centre of Excellence" or "Center for Enablement" (C4E) inside IT.

### Flavour 2: Product (customer-facing) integration

You work for a software company, usually B2B SaaS, whose product must connect to the tools its customers already use. Examples: an HR product that syncs with fifty payroll systems, a sales tool that writes back to Salesforce and HubSpot, an AI assistant that reads from Google Drive and Jira.

- **Typical tools:** your product's own codebase, OAuth flows, third-party APIs, webhooks, queues, and sometimes an embedded iPaaS (Paragon, Prismatic, Workato Embedded) or a unified API (Merge, Apideck, Unified.to).
- **Typical challenges:** scale (thousands of customer tenants), variety (dozens of target systems), API rate limits and deprecations, multi-tenant security, and integration as a sales feature.
- **Typical org:** an "Integrations" or "Ecosystem" team within engineering.

### Flavour 3: Services and consulting

You work for a systems integrator (Accenture, Deloitte, Capgemini, Infosys, a boutique Salesforce or SAP partner) or for a vendor's professional-services team. You deliver integration projects for clients.

- **Typical tools:** whatever the client has.
- **Typical challenges:** fixed scope and deadlines, rapid learning of new domains, handing over to the client's team, documentation as a deliverable.
- **Typical org:** project teams, with certifications often required by the partner programme.

---

## 1.5 What the Integration Design Engineer actually does

The work cycles through six activities. Later chapters cover each in depth.

### 1. Discover and understand

- Interview business stakeholders to learn the process: "When does an order count as *confirmed*? What happens when it is cancelled after shipping?"
- Read the documentation of every system involved and probe its API in a sandbox.
- Inventory existing integrations. There are always more than anyone thinks.
- Identify the **system of record** for each data entity.
- Capture **non-functional requirements** (NFRs): volume, latency, availability, security, retention and audit.

### 2. Design

- Choose an **integration style**: request/response API, event, message queue, batch file or database replication (Chapter 5).
- Choose **patterns**: publish/subscribe, content-based router, aggregator, saga, outbox (Chapters 5 and 8).
- Define **contracts**: OpenAPI and AsyncAPI documents, schemas and file layouts (Chapters 6 and 7).
- Write the **data mapping specification**: field-by-field transformation rules, code-value translations and default values (Chapter 4).
- Design **error handling**: retries, dead-letter queues, alerts and the human workflow for fixing bad data (Chapter 8).
- Design **security**: authentication, authorisation, secrets, encryption and data minimisation (Chapter 10).
- Write it all up in an **integration design document** and get it reviewed (Chapter 14, plus the template in [`templates/`](../templates/)).

### 3. Build

- Implement flows in code or in an iPaaS.
- Build connectors, transformations and orchestration.
- Write infrastructure as code for queues, gateways and secrets.

### 4. Test

- Unit-test transformations, contract-test interfaces, run end-to-end tests against partner sandboxes, and load-test (Chapter 15).

### 5. Deploy and operate

- Release through CI/CD, monitor dashboards and alerts, handle incidents, replay failed messages and reconcile data between systems (Chapter 16).

### 6. Govern and improve

- Maintain the catalogue of integrations and APIs, enforce standards, plan deprecations and migrations, reduce technical debt, and mentor others (Chapter 17).

### A realistic week

Here is a composite week for a mid-level integration engineer at a SaaS company *(illustrative)*:

| Day | Activities |
|---|---|
| Monday | Stand-up. Triage overnight alerts: 312 HubSpot sync failures, all `429 Too Many Requests` from one large tenant. Adjust that tenant's concurrency limit and open a ticket to add adaptive rate limiting. |
| Tuesday | Discovery call with product and a design-partner customer about a new NetSuite integration. Draft the field mapping in a spreadsheet. Prototype the OAuth 2.0 flow against a NetSuite sandbox. |
| Wednesday | Write the design doc: sync direction, conflict resolution, initial backfill strategy, rate-limit budget and failure modes. Review a teammate's pull request for a Slack integration. |
| Thursday | Microsoft announces deprecation of an API version you use, with removal in nine months. Estimate the migration and add it to the roadmap. Pair with support to debug a customer's "missing contacts", caused by a custom field type the mapping did not handle. |
| Friday | Design review with the architect. Merge the rate-limiting fix behind a feature flag. Update the runbook. On-call handover. |

Notice the mix: reading other people's documentation, talking to people, writing, coding and firefighting. Pure coding is perhaps 30–50% of the time.

---

## 1.6 The neighbours: how this role relates to others

| Role | Overlap | Difference |
|---|---|---|
| **Backend engineer** | Writes services and APIs. | Owns one system; integration engineers own the seams *between* systems and work mostly with systems they do not control. |
| **Data engineer** | Moves data, builds pipelines. | Focuses on analytics: batch, warehouses and modelling for reporting. Integration engineers focus on operational flows that drive business processes in near real time. The line is blurring (Chapter 9). |
| **Platform / DevOps / SRE** | Operates infrastructure, cares about reliability. | Runs the platform; the integration engineer runs the flows on it. |
| **Solutions architect** | Designs end-to-end. | Broader and less hands-on; may not build or operate. |
| **Business / systems analyst** | Gathers requirements, writes mapping specs. | Usually does not build or operate; the integration engineer turns analysis into running systems. |
| **Security engineer** | Cares about authentication and data protection. | Sets policy; the integration engineer applies it to every connection. |
| **Salesforce, SAP or ServiceNow developer** | Builds on one platform, often including its integrations. | Platform-centric; the integration engineer is cross-platform. |

---

## 1.7 The skills map

The rest of the book is organised around the skills below. Use the table to assess yourself now, and again when you finish the book. Chapter 19 turns it into a learning plan.

| Area | Junior (0–2 years) | Mid (2–5 years) | Senior / Lead (5+ years) |
|---|---|---|---|
| **HTTP and networking** (Ch. 3) | Makes and debugs API calls; knows status codes. | Diagnoses TLS, DNS, proxy and timeout problems. | Designs network topology for hybrid integration (private links, VPNs, egress control). |
| **Data and transformation** (Ch. 4) | Maps JSON to JSON; handles dates. | Handles XML/XSD, CSV quirks, character encodings and canonical models. | Designs enterprise canonical models and schema-evolution policy. |
| **Patterns** (Ch. 5) | Knows request/response and pub/sub. | Applies EIP patterns deliberately. | Chooses styles and patterns across a portfolio and justifies the trade-offs. |
| **API design** (Ch. 6) | Consumes APIs well. | Designs REST APIs with OpenAPI; pagination, errors and versioning. | Sets API standards and governance; designs for external developers. |
| **Async and events** (Ch. 7) | Uses a queue. | Designs topics, consumer groups, ordering and webhooks. | Designs event-driven architectures and event catalogues. |
| **Reliability** (Ch. 8) | Adds retries. | Designs idempotency, DLQs, the outbox pattern and reconciliation. | Defines SLOs, failure-mode analysis and saga designs. |
| **Data integration** (Ch. 9) | Runs a sync job. | Builds CDC and ELT pipelines. | Designs data-movement strategy and MDM. |
| **Security** (Ch. 10) | Uses API keys and OAuth client credentials safely. | Implements OAuth flows, mTLS, webhook signatures and secret rotation. | Threat-models integrations; designs for compliance (PCI, HIPAA, GDPR). |
| **Platforms** (Ch. 11–12) | Productive in one iPaaS or one enterprise app. | Productive in two or three; knows their limits. | Leads platform selection and build-vs-buy decisions. |
| **Industry standards** (Ch. 13) | Knows they exist. | Works fluently with one (EDI, FHIR, ISO 20022…). | Domain authority. |
| **Design process** (Ch. 14) | Follows a design doc. | Writes design docs and mapping specs. | Runs discovery, facilitates design reviews, mentors. |
| **Testing** (Ch. 15) | Unit tests mappings. | Contract tests and sandbox automation. | Test strategy for an integration portfolio. |
| **Operations** (Ch. 16) | Reads logs and replays failures. | Builds dashboards, alerts and runbooks; uses tracing. | Owns SLOs and incident management for the integration estate. |
| **Architecture** (Ch. 17) | Understands the landscape. | Contributes to standards. | Owns integration architecture and governance. |
| **Communication** | Writes clear tickets. | Explains trade-offs to non-engineers; manages a partner. | Negotiates with vendors; aligns executives. |

---

## 1.8 Where the field is heading *(as of October 2026)*

A few forces are reshaping the role. Chapters 11, 17 and 18 discuss them in detail.

1. **Consolidation of integration platforms.** Salesforce owns MuleSoft (2018) and completed its roughly $8 billion acquisition of Informatica in November 2025. IBM completed its roughly $11 billion acquisition of Confluent, the main commercial company behind Apache Kafka, on 17 March 2026. Integration is becoming a strategic layer inside larger platforms.
2. **The end of on-premises integration servers.** SAP Process Orchestration mainstream maintenance ends on 31 December 2027, and Microsoft BizTalk Server 2020, the final BizTalk version, leaves mainstream support in April 2028. Many organisations are migrating to cloud integration (SAP Integration Suite, Azure Logic Apps and others). Migration projects are a large source of integration work through the late 2020s.
3. **Event streaming goes mainstream.** Apache Kafka 4.0 removed ZooKeeper entirely, and Kafka 4.2 (early 2026) made "Queues for Kafka" (share groups) production-ready, so one platform can now cover both streaming and work-queue semantics.
4. **AI agents become integration consumers.** The **Model Context Protocol (MCP)**, introduced by Anthropic in late 2024 and now hosted by the Linux Foundation's Agentic AI Foundation, gives AI agents a standard way to call tools and read data. Its 2026-07-28 revision made the protocol stateless. Google's **Agent2Agent (A2A)** protocol covers agent-to-agent communication. Postman's 2025 *State of the API* survey found that about a quarter of developers already design APIs with AI agents in mind. Integration engineers increasingly build and secure the tool layer that agents use.
5. **Standards keep maturing.** OpenAPI 3.2 shipped in September 2025, the HTTP `QUERY` method became RFC 10008 in June 2026, OAuth 2.1 is nearing completion as an IETF draft, and Arazzo 1.1 (May 2026) describes multi-step API workflows across both synchronous and asynchronous APIs.
6. **Regulatory deadlines drive projects.** Examples include SWIFT's move to ISO 20022 for cross-border payments (MT/MX coexistence ended on 22 November 2025) and the US CMS-0057-F rule requiring FHIR R4 APIs from many health payers by 1 January 2027.

The constant is that systems keep multiplying and someone must connect them well. Demand for integration skill has never been tied to one technology, which is why it has stayed a durable career from the EDI era to the agent era.

---

## Summary

- Integration is the discipline of making independent systems work together so that business processes spanning them are correct and reliable.
- An Integration Design Engineer designs, builds and operates those connections. The work happens in the seams between systems the engineer does not control.
- The role appears under many titles. Read the technologies and verbs in a posting, not its title. In hardware industries the same title means something unrelated.
- There are three main settings: enterprise, product and services.
- The core skills are HTTP, data transformation, integration patterns, API and event design, reliability, security, platform knowledge, a disciplined design process, and communication.

## Exercises

See [`exercises/01-the-role.md`](../exercises/01-the-role.md).

## Further reading

- Gregor Hohpe and Bobby Woolf, *Enterprise Integration Patterns* (Addison-Wesley, 2003). The foundational text of the field.
- Martin Kleppmann and Chris Riccomini, *Designing Data-Intensive Applications*, 2nd edition (O'Reilly, 2026). The best book on the distributed-data fundamentals under every integration.
- The job-description library in the GitLab Handbook, which includes a public Integrations Engineer ladder.
