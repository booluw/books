# Chapter 2. A Short History of Integration

> "Those who cannot remember the past are condemned to re-implement it in YAML."
> (with apologies to George Santayana)

## What you will learn

- How integration evolved from tape files to AI agents, and what problem each generation solved.
- Why ideas from the 1990s (hubs, canonical models, message queues) keep returning under new names.
- Which legacy technologies you are still likely to meet in production, and why they persist.

Understanding the history is practical. Most organisations run a *geological* stack: a 1990s EDI translator, a 2000s ESB, 2010s REST microservices, a 2020s iPaaS and a 2026 MCP server, all live at the same time. You will integrate with all of them.

---

## 2.1 Era 0: Sneakernet and batch files (1960s–1980s)

Early business computing ran on mainframes. Integration meant one program writing a file, often a fixed-width record layout on tape, and another program reading it in an overnight batch run. Someone physically carried the tape between machines: the "sneakernet".

What survives today:

- **Fixed-width and delimited flat files.** Banks, insurers, payroll providers and governments still exchange them, now over SFTP instead of tape.
- **The batch window.** "The nightly job" is still a common integration pattern, because it is simple, cheap and easy to audit.
- **COBOL copybooks.** These define record layouts on mainframes. If you integrate with a bank's core system you may be handed a copybook and asked to parse EBCDIC-encoded files (Chapter 4).

**The lesson:** file transfer is the oldest integration style and still one of the most robust. Files are durable, inspectable and replayable. Do not dismiss them.

---

## 2.2 Era 1: EDI, business-to-business integration (1960s–1990s)

Electronic Data Interchange (EDI) began in the transport industry in the 1960s and was standardised in the late 1970s and 1980s:

- **ANSI ASC X12** (1979) in North America: transaction sets such as **850** (Purchase Order), **810** (Invoice) and **856** (Advance Ship Notice).
- **UN/EDIFACT** (1987) internationally: messages such as **ORDERS**, **INVOIC** and **DESADV**.

Companies exchanged EDI documents through **Value-Added Networks (VANs)**, private networks that acted as mailboxes. Later, the internet protocol **AS2** (RFC 4130, 2005) let trading partners exchange documents directly over HTTP with signatures and receipts.

EDI is not dead. It is the backbone of retail, logistics, automotive and healthcare claims. Large retailers require suppliers to be "EDI-compliant" as a condition of doing business. Chapter 13 covers EDI in depth.

**The lesson:** standard *business documents*, rather than standard function calls, made cross-company integration possible. The same idea reappears in FHIR resources, ISO 20022 messages and CloudEvents.

---

## 2.3 Era 2: Remote procedure calls and distributed objects (1980s–1990s)

Programmers wanted to call a function on another computer as if it were local. This led to:

- **Sun RPC / ONC RPC** (1980s).
- **DCE RPC** and Microsoft's **DCOM**.
- **CORBA** (Common Object Request Broker Architecture, 1991), an ambitious cross-language distributed-object standard.
- **Java RMI** (1997).

These technologies hid the network behind a function call. That turned out to be dangerous. In 1994, Peter Deutsch and others at Sun Microsystems listed the **Fallacies of Distributed Computing**, assumptions programmers wrongly make:

1. The network is reliable.
2. Latency is zero.
3. Bandwidth is infinite.
4. The network is secure.
5. Topology doesn't change.
6. There is one administrator.
7. Transport cost is zero.
8. The network is homogeneous.

Every integration bug you will ever debug traces back to one of these eight assumptions. Memorise them.

**The lesson:** making remote calls *look* local hides failure modes that must be designed for. Modern RPC frameworks such as gRPC (Chapter 6) make the network explicit with deadlines, status codes and streaming.

---

## 2.4 Era 3: Message-oriented middleware (1990s)

To decouple systems in time, vendors built **message queues**:

- **IBM MQSeries** (1993), now **IBM MQ**, still running in a very large share of the world's banks.
- **TIBCO Rendezvous** (publish/subscribe for trading floors).
- **Microsoft MSMQ**.
- The **Java Message Service (JMS)** API (1998), a standard interface to such systems.

A sender puts a message on a queue, and the receiver takes it off whenever it is ready. If the receiver is down, messages wait. This **store-and-forward** model gives *temporal decoupling*: the sender and receiver need not be running at the same moment.

**The lesson:** asynchronous messaging is the foundation of reliable integration. Chapter 7 is built on these ideas.

---

## 2.5 Era 4: Enterprise Application Integration (EAI) and the hub (late 1990s–early 2000s)

Companies bought packaged applications: SAP R/3, PeopleSoft, Siebel and Oracle E-Business Suite. Connecting *n* applications point-to-point needs up to *n(n−1)/2* connections. With 20 systems that is 190 interfaces, each custom-built, each a maintenance burden. This is the **point-to-point spaghetti** problem.

**EAI** products (TIBCO, webMethods, SeeBeyond, Vitria, BEA, IBM WebSphere Message Broker, Microsoft BizTalk Server from 2000) introduced the **hub-and-spoke** model:

- Every application connects once, to a central **hub**, through an **adapter**.
- The hub transforms messages into and out of a **canonical data model**, a shared enterprise-wide representation of entities such as "Customer" and "Order".
- The hub **routes** messages based on content and rules.

With a hub, *n* systems need *n* connections, not *n²*.

The downsides became clear over time. The hub became a bottleneck, a single point of failure, and an organisational bottleneck too: one central team had to change it for everybody. Canonical models grew into enormous compromises that pleased no one.

In 2003, Gregor Hohpe and Bobby Woolf published ***Enterprise Integration Patterns*** (EIP), cataloguing 65 patterns for messaging-based integration: Message Channel, Content-Based Router, Splitter, Aggregator, Dead Letter Channel and more. The vocabulary is still the lingua franca of the field, and frameworks such as Apache Camel (2007), Spring Integration and MuleSoft implement it directly. Chapter 5 teaches it.

**The lesson:** centralisation reduces connection count but concentrates risk and organisational load. Every generation since has tried to balance central governance against decentralised delivery.

---

## 2.6 Era 5: SOA, web services and the ESB (2000s)

The web made HTTP and XML universal. **Service-Oriented Architecture (SOA)** proposed that applications expose business capabilities as reusable **services** with formal contracts. The technology stack was **SOAP web services**:

- **XML** for data, described by **XSD** (XML Schema).
- **SOAP** (Simple Object Access Protocol) envelopes, sent over HTTP.
- **WSDL** (Web Services Description Language) for the contract.
- **UDDI** for service discovery (it largely failed).
- The **WS-\*** family: WS-Security, WS-ReliableMessaging, WS-AtomicTransaction, WS-Addressing and many more.

The **Enterprise Service Bus (ESB)** was SOA's middleware: a distributed evolution of the EAI hub offering routing, transformation, protocol mediation and orchestration (via **BPEL**, the Business Process Execution Language). Major ESBs included IBM WebSphere ESB / Integration Bus (now **IBM App Connect Enterprise**), Oracle Service Bus, TIBCO BusinessWorks, Software AG webMethods, SAP Process Integration (later **SAP PI/PO**), Microsoft BizTalk, and open-source options such as Mule ESB (2006, the origin of MuleSoft), Apache ServiceMix and WSO2.

What went right: formal contracts, strong typing, and serious security and reliability standards. Banks, telecoms and governments still run SOAP services, and you *will* consume them.

What went wrong: complexity. WS-\* specifications were hard to implement consistently. ESBs accumulated business logic and became monoliths, and many SOA programmes delivered governance bureaucracy rather than agility.

**The lesson:** contracts and standards are valuable, but heavyweight tooling and centralised logic slow everyone down. "Smart endpoints, dumb pipes" (below) was the reaction.

---

## 2.7 Era 6: REST, web APIs and the API economy (mid-2000s–2010s)

In his 2000 doctoral dissertation, Roy Fielding described **REST** (Representational State Transfer), the architectural style of the web itself: resources identified by URLs, manipulated through a uniform interface (HTTP methods), with stateless interactions and hypermedia. In practice, "REST API" came to mean *JSON over HTTP with resource-oriented URLs*.

Milestones:

- **2000:** Salesforce and eBay launch web APIs.
- **2006:** Amazon Web Services launches S3 and SQS with web APIs.
- **2006–2010:** Twitter, Facebook and Google Maps APIs create the "mashup" era. JSON overtakes XML.
- **2007:** **OAuth 1.0** lets users grant apps access without sharing passwords. **OAuth 2.0** follows as RFC 6749 in 2012.
- **2010:** Stripe launches with a developer-first API, setting a new bar for API design, documentation and idempotency.
- **2011:** Swagger is created; it is donated in **2015** to the Linux Foundation's new **OpenAPI Initiative** and becomes the **OpenAPI Specification**.
- **2015:** Facebook releases **GraphQL**; Google releases **gRPC**.
- **2010s:** API management platforms appear: Apigee (acquired by Google in 2016), Mashery, 3scale (Red Hat), Kong and Azure API Management.

The "API economy" framed APIs as products. Companies such as Twilio, Stripe and Plaid built businesses whose product *is* an API.

**The lesson:** simple, well-documented, self-service interfaces beat powerful but complex ones. Developer experience is a design requirement.

---

## 2.8 Era 7: Microservices, cloud and "smart endpoints, dumb pipes" (2010s)

Netflix, Amazon and others split monoliths into **microservices**, small services owned by small teams, communicating over APIs and events. Martin Fowler and James Lewis's 2014 article on microservices popularised the principle **"smart endpoints and dumb pipes"**: put the logic in the services, and keep the transport simple (HTTP, a plain message broker) rather than in an ESB.

Related developments:

- **Apache Kafka** (open-sourced by LinkedIn in 2011, an Apache top-level project in 2012) introduced the **distributed commit log**: a durable, replayable, partitioned stream of events. It became the backbone of **event-driven architecture** and **event streaming**. Confluent was founded in 2014 by Kafka's creators.
- **Cloud messaging services:** Amazon SQS/SNS, Azure Service Bus and Event Hubs, Google Pub/Sub.
- **Containers and Kubernetes** (2014) changed how integration runtimes are deployed.
- **Service meshes** (Istio, Linkerd) moved retries, mTLS and observability into infrastructure.
- **Serverless** (AWS Lambda, 2014) made event-triggered glue code cheap.

Microservices multiplied the number of integrations *inside* each company. Every service-to-service call is an integration with the same fallacies.

**The lesson:** distributing ownership speeds teams up but multiplies interfaces. Contracts, observability and reliability patterns became everyone's job, not only the integration team's.

---

## 2.9 Era 8: SaaS sprawl and iPaaS (2010s–2020s)

Companies moved from a few large on-premises suites to hundreds of SaaS applications. A typical mid-sized company now uses well over a hundred SaaS products. These apps live on the internet, expose REST APIs and webhooks, and are bought by individual departments.

**Integration Platform as a Service (iPaaS)** emerged to connect them: cloud-hosted integration with prebuilt connectors, visual flow designers, and managed runtime and monitoring. Key vendors (detailed in Chapter 11) include MuleSoft Anypoint Platform (acquired by Salesforce in 2018), Boomi, Workato, Informatica (acquired by Salesforce, closed November 2025), SnapLogic, Jitterbit, Celigo, Tray.ai, SAP Integration Suite, Microsoft Azure Integration Services, and cloud-native services from AWS and Google. Citizen-integrator tools (Zapier, Make, n8n, Power Automate) let non-engineers build simple automations.

MuleSoft popularised **API-led connectivity**: layering *System APIs* (wrapping systems of record), *Process APIs* (orchestrating business logic) and *Experience APIs* (shaping data for each consumer). Chapter 17 evaluates it.

Two newer categories serve SaaS companies building *customer-facing* integrations:

- **Embedded iPaaS** (Paragon, Prismatic, Workato Embedded, Tray Embedded), which puts an integration builder or marketplace inside your product.
- **Unified APIs** (Merge, Apideck, Unified.to, Kombo, Finch), which offer one normalised API per software category (HRIS, CRM, accounting) across dozens of vendors.

**The lesson:** connectors and managed operations are commodities now. The scarce skills are design, semantics, governance and operating at scale.

---

## 2.10 Era 9: Event streaming and data-in-motion (late 2010s–2020s)

The lines between operational integration and analytics blurred:

- **Change Data Capture (CDC)** tools (Debezium, launched by Red Hat in 2016; Oracle GoldenGate; Fivetran HVR; AWS DMS) turn database changes into event streams.
- **Stream processing** (Kafka Streams, Apache Flink, ksqlDB) transforms events in flight.
- **ELT** (Extract, Load, Transform) with Fivetran, Airbyte and dbt moved transformation into cloud warehouses (Snowflake, BigQuery, Databricks).
- **Reverse ETL** (Hightouch, Census) pushes warehouse data back into operational tools.
- **Kafka 4.0 (March 2025)** removed ZooKeeper in favour of KRaft, and **Kafka 4.2** (early 2026) made share groups ("Queues for Kafka") production-ready.
- **IBM acquired Confluent** (closed 17 March 2026), signalling that streaming is now core enterprise infrastructure.

Chapter 9 covers this data-integration world.

---

## 2.11 Era 10: Agents and the tool layer (2024–present)

Large language models (LLMs) gained the ability to call tools. Every AI assistant that can "check your calendar" or "file a ticket" is an integration consumer. In November 2024 Anthropic introduced the **Model Context Protocol (MCP)**, an open protocol for connecting AI applications to tools and data. MCP spread quickly across AI clients and developer tools. In December 2025 Anthropic donated it to the Linux Foundation's newly formed **Agentic AI Foundation** (co-founded with Block and OpenAI). At that point there were more than 10,000 active public MCP servers. Google's **Agent2Agent (A2A)** protocol (April 2025, also donated to the Linux Foundation) addresses communication *between* agents.

This era raises old integration questions in new forms:

- **Contracts:** tool descriptions must be precise enough for a model to use correctly.
- **Security:** an agent acting for a user needs delegated, least-privilege authorisation, which brings OAuth back to the centre.
- **Reliability:** an agent may retry a tool call or call it in a loop, so idempotency and rate limits matter more than ever.
- **Governance:** which tools may which agents use, and how are their actions audited?

Chapter 18 covers agent integration.

---

## 2.12 Patterns that keep coming back

| Old idea | Modern form |
|---|---|
| Batch file transfer | Bulk APIs, SFTP drops, data-lake landing zones, Parquet exports |
| EDI standard documents | FHIR resources, ISO 20022 messages, CloudEvents, unified-API schemas |
| Message queue (MQSeries, JMS) | SQS, Azure Service Bus, RabbitMQ, Kafka share groups |
| EAI hub and adapters | iPaaS and its connectors |
| Canonical data model | Unified APIs, enterprise event schemas, data contracts |
| ESB mediation | API gateways, service meshes, event brokers with routing rules |
| WSDL / XSD contracts | OpenAPI, AsyncAPI, Protobuf, JSON Schema |
| BPEL orchestration | Workflow engines (Temporal, AWS Step Functions, Camunda), iPaaS recipes, sagas |
| UDDI registry | API catalogues and developer portals (Backstage, API hubs), MCP registries |
| CORBA "make remote look local" | Auto-generated SDKs, and its lessons in gRPC deadlines |

When someone presents a "new" integration product, ask which of these ideas it repackages and what it does differently. The answer is usually a better developer experience, a better operating model or better economics. Those are real improvements, but the underlying trade-offs are the same.

---

## Summary

- Integration has moved through files, EDI, RPC, message queues, EAI hubs, SOA/ESB, REST APIs, microservices, iPaaS, streaming and AI agents.
- Each era solved the previous era's main pain and created new ones.
- Legacy technologies persist because they work and because replacing them is costly. Expect to meet all of them.
- The Fallacies of Distributed Computing and the Enterprise Integration Patterns are timeless. Learn them first.

## Exercises

See [`exercises/02-history.md`](../exercises/02-history.md).

## Further reading

- Peter Deutsch et al., "The Eight Fallacies of Distributed Computing" (Sun Microsystems, 1994).
- Roy T. Fielding, *Architectural Styles and the Design of Network-based Software Architectures* (PhD dissertation, UC Irvine, 2000), Chapter 5.
- James Lewis and Martin Fowler, "Microservices" (martinfowler.com, 2014).
- Jay Kreps, "The Log: What every software engineer should know about real-time data's unifying abstraction" (LinkedIn Engineering, 2013).
