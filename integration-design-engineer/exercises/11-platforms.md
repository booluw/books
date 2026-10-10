# Exercises: Chapter 11, Platforms

## Questions

1. Your company runs SAP S/4HANA, Salesforce, Workday and 120 SaaS tools, with an integration team of five and many business analysts. Outline a platform strategy.
2. A SaaS start-up needs integrations with 25 HRIS systems to read employee lists. Compare building, an embedded iPaaS and a unified API.
3. Write 10 evaluation criteria for an iPaaS proof of concept, each with how you would measure it.
4. List five risks of uncontrolled Zapier or Power Automate use, and a guardrail for each.
5. Plan the first three months of a BizTalk-to-Azure migration with 150 interfaces.
6. What is the difference between an API gateway and a service mesh? When would you use both?

## Solutions

1. Example: an iPaaS with strong SAP and Salesforce connectors (or SAP Integration Suite for SAP-centric flows plus a general iPaaS) for application integration; API management in front of system APIs; an event broker for high-volume events; governed citizen automation (Power Automate or Workato) with connector allow-lists; a catalogue; templates; and a C4E model so analysts build within guardrails.
2. Build: deep control but 25 connectors to maintain. Embedded iPaaS: customers configure, but per-connection pricing and work still needed per target. Unified API: one integration covers the category quickly; check custom-field support, data storage and residency, sync freshness, cost. For "read employee lists", a unified HRIS API is usually the fastest fit; build in-house later for the top 2–3 systems if depth is needed.
3. Example: time to build the reference flow (hours); quality of the Salesforce bulk/CDC connector (features covered); local dev and Git support (yes/no, demo); CI/CD automation (pipeline runs); error handling and replay (scenario test); observability export to OTel (demo); throughput at 2× peak (load test); hybrid agent for on-prem (deploy test); security certifications (documents); three-year TCO (model).
4. Shadow data flows → connector DLP policies. Personal credentials → service accounts. No error handling → mandatory failure notifications. Creator leaves → ownership register and periodic review. Sensitive data to unapproved apps → approved app list and data classification rules.
5. Month 1: inventory from BizTalk tracking data; classify (retire, rehost, refactor, replace); define target architecture (Logic Apps Standard, Service Bus, APIM, Integration Account for EDI), standards, CI/CD and environments. Month 2: build templates and shared components (error handling, logging, maps); migrate a pilot wave of low-risk interfaces; validate operations. Month 3: wave 2 by business domain; parallel runs for critical flows; decommission migrated ports; report progress against the support deadline (April 2028).
6. A gateway manages north–south (external client → service) traffic: auth, quotas, transformation, developer portal. A mesh manages east–west (service ↔ service) traffic: mTLS, retries, telemetry. Use both in microservice estates exposing external APIs.
