# Appendix A. Glossary

Every term the chapters define, in alphabetical order, with a plain definition and the chapter(s) where it is covered. Facts that change over time are dated *(as of October 2026)*; Appendix B lists sources.

Jump to: [A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J](#j) · [K](#k) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [Q](#q) · [R](#r) · [S](#s) · [T](#t) · [V](#v) · [W](#w)

## A

| Term | Definition | Covered in |
|---|---|---|
| **A/B test** | See *randomised controlled trial*. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Acceptance (of deliverables)** | The agreed way, and the person, by which a deliverable is accepted under an SOW; some contracts include deemed acceptance after a number of days of silence. | [Ch. 6](../chapters/06-scoping.md) |
| **Access** | Accounts, VPN, data permissions, environments and security approvals. In enterprise engagements it is often the hidden critical path, taking longer than the build, so it is requested early and tracked like a deliverable. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 6](../chapters/06-scoping.md) |
| **Access control list (ACL)** | The list of users and groups allowed to read a resource. Permission-aware retrieval captures each document's ACL at ingestion and keeps it in sync with the source. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **ACV (annual contract value)** | The revenue from a customer contract in one year. | [Ch. 3](../chapters/03-business.md) |
| **ADKAR** | Prosci's change-management model: Awareness, Desire, Knowledge, Ability, Reinforcement. Mapping an adoption plan onto it helps when the customer's change team uses it. | [Ch. 7](../chapters/07-stakeholders.md) |
| **Adoption** | The process by which people start using a new system as part of their normal work and stop using the old way. Measured by reach, depth, retention and reliance. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 7](../chapters/07-stakeholders.md), [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **ADR (architecture decision record)** | A short, dated record of a technical decision: status, context, decision and consequences. Described by Michael Nygard in 2011; invaluable at handover. | [Ch. 8](../chapters/08-communication.md), [Ch. 11](../chapters/11-configure-extend-change.md), [Ch. 15](../chapters/15-production-and-handover.md) |
| **Agency trap** | When a product company slowly becomes a custom-development shop: each customer has its own fork, FDEs maintain one-off code and the product stagnates. | [Ch. 3](../chapters/03-business.md), [Ch. 11](../chapters/11-configure-extend-change.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Agent** | A system in which a model plans and takes a sequence of actions using tools, observing results and deciding what to do next, until a goal is reached or it stops. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **AIP (Artificial Intelligence Platform)** | Palantir's AI platform, launched in 2023 and sold through short, hands-on bootcamps. | [Ch. 2](../chapters/02-history.md) |
| **Air-gapped** | Physically disconnected from external networks. Software, models, updates and dependencies must be bundled and transferred through approved media and processes. | [Ch. 14](../chapters/14-security-and-restricted-environments.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Amber** | See *RAG status*. | [Ch. 8](../chapters/08-communication.md) |
| **Assistant (copilot)** | An AI pattern that helps a person do a task while the person makes the decision. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Audit log** | A record of every tool call, argument, result and approval (or every security-relevant event). A tamper-evident log chains entries by hash so edits are detectable. | [Ch. 12](../chapters/12-ai-deployment.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md) |

## B

| Term | Definition | Covered in |
|---|---|---|
| **Baseline** | The value of a metric before your change. Without one you cannot show impact; if none exists, measure one before deploying. | [Ch. 6](../chapters/06-scoping.md), [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Blameless post-incident review** | A written review after an incident covering timeline, impact, contributing causes and actions, focused on systems rather than individuals. | [Ch. 8](../chapters/08-communication.md), [Ch. 15](../chapters/15-production-and-handover.md) |
| **Blocker / major / minor** | Severity levels in a production readiness review. Unmet blockers mean no-go; unmet majors may proceed as conditions with an owner and due date; minors are tracked only. | [Ch. 15](../chapters/15-production-and-handover.md) |
| **Blocking** | In record linkage, comparing only records that share a cheap key (such as postcode) to avoid the quadratic cost of comparing every pair. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Blue-green deployment** | Running two production environments and switching traffic between them, allowing quick rollback of infrastructure changes. | [Ch. 15](../chapters/15-production-and-handover.md) |
| **BM25** | A classic keyword-search ranking function based on term frequency, term rarity and document length. Strong for exact terms, codes and names. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Bootcamp** | A short (days-long), intensive engagement in which vendor engineers and customer staff build working use cases on the customer's own data. Palantir's AIP go-to-market motion. | [Ch. 2](../chapters/02-history.md), [Ch. 3](../chapters/03-business.md), [Ch. 4](../chapters/04-engagement-lifecycle.md) |
| **Budget (agent)** | A cap on tool calls, tokens, spend or time per agent run, preventing runaway loops and cost. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Build alongside** | Rung 3 of the build ladder: a separate component that talks to the product only through its public APIs. | [Ch. 11](../chapters/11-configure-extend-change.md) |
| **Build-operate-transfer** | A commercial model in which the vendor builds and runs a system, then transfers it to the customer's team. | [Ch. 3](../chapters/03-business.md) |
| **Bundled (commercial model)** | FDE time included in the platform licence, often for strategic accounts. | [Ch. 3](../chapters/03-business.md) |
| **Burnout** | Chronic workplace stress that hasn't been successfully managed; the WHO's ICD-11 describes it by exhaustion, cynicism or detachment, and reduced professional effectiveness. | [Ch. 18](../chapters/18-life-as-an-fde.md) |
| **Business object** | A concept users think in (customer, policy, claim, aircraft), as opposed to a raw table. Ontologies map tables to business objects. | [Ch. 10](../chapters/10-enterprise-data.md) |

## C

| Term | Definition | Covered in |
|---|---|---|
| **CAB (change advisory board)** | A customer body that approves production changes; its schedule adds elapsed time. | [Ch. 6](../chapters/06-scoping.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **CAIQ** | The Cloud Security Alliance's Consensus Assessments Initiative Questionnaire, a standard vendor security questionnaire. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Canary release** | Sending a small percentage of traffic to a new version and comparing health before expanding. | [Ch. 15](../chapters/15-production-and-handover.md) |
| **CDC (change data capture)** | A stream of changes read from a database's log: near real-time and low load, but needs infrastructure and approval. | [Ch. 9](../chapters/09-toolkit.md), [Ch. 10](../chapters/10-enterprise-data.md) |
| **Champion** | A respected user, usually low in formal influence but supportive, who gets early access and recognition and helps peers adopt the system. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 7](../chapters/07-stakeholders.md) |
| **Change control** | The agreed process for requesting, assessing, deciding and recording scope changes (a change order where there is an SOW). | [Ch. 6](../chapters/06-scoping.md) |
| **Chunking** | Splitting documents into passages for retrieval; chunks that follow document structure usually beat fixed-size chunks. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Citation check** | Verifying that every source an AI answer cites was actually retrieved and is readable by the user. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Claude Frontier Academy** | Anthropic's $100 million programme, announced October 2026, to train 10,000 "frontier deployed engineers" at partner and customer organisations by the end of 2027 *(as of October 2026)*. | [Ch. 1](../chapters/01-the-role.md), [Ch. 2](../chapters/02-history.md), [Ch. 17](../chapters/17-running-an-fde-org.md), [Ch. 19](../chapters/19-career.md) |
| **Configuration** | Changing a product's behaviour through settings, metadata or declarative definitions, without code. Rung 1 of the build ladder. | [Ch. 11](../chapters/11-configure-extend-change.md) |
| **Consultancy drift** | An FDE organisation failure mode: bespoke code per customer and FDE headcount growing with revenue. | [Ch. 17](../chapters/17-running-an-fde-org.md) |
| **Context window** | How much text a model can consider at once, measured in tokens. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Contingency** | Explicitly named extra time in an estimate (for example for data-quality remediation), rather than padding hidden in each task. | [Ch. 6](../chapters/06-scoping.md) |
| **Contract test** | An automated test checking that a product still behaves as an extension expects (input and output shapes, error codes); run against each new product release. | [Ch. 11](../chapters/11-configure-extend-change.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Control group** | A comparison group that keeps working the old way over the same period, controlling for seasonality and other changes. | [Ch. 6](../chapters/06-scoping.md), [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Customer owner** | The named customer person (usually an operational manager) who agrees a success criterion's metric and confirms the result. | [Ch. 6](../chapters/06-scoping.md) |

## D

| Term | Definition | Covered in |
|---|---|---|
| **Data inventory** | For each data source: contents, volume, freshness, quality, sensitivity classification, legal basis and access path. | [Ch. 5](../chapters/05-discovery-and-decomposition.md) |
| **Data lineage** | A record of where each piece of data came from and what was done to it. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Data minimisation** | Using only the data needed for the purpose; a GDPR principle (Article 5) that also speeds security approval. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Data pipeline** | Code that moves data from sources, transforms it and delivers it. FDE pipelines should be idempotent, incremental where needed, observable, tested and owned. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Data profiling** | Systematically examining a dataset (row counts, nulls, distinct values, types, patterns, keys, placeholders) to learn what it really contains. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Data residency** | Keeping data within an agreed environment, region or country. | [Ch. 10](../chapters/10-enterprise-data.md), [Ch. 12](../chapters/12-ai-deployment.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Decomposition** | Turning an ambiguous goal into a structured set of sub-problems, each concrete enough to build and measure, broken down by business driver. The FDE's signature skill and a Palantir interview round. | [Ch. 5](../chapters/05-discovery-and-decomposition.md), [Ch. 19](../chapters/19-career.md) |
| **Delta** | Palantir's internal name for a forward deployed software engineer. | [Ch. 1](../chapters/01-the-role.md), [Ch. 2](../chapters/02-history.md) |
| **Deployment gap** | Everything between powerful software and a customer outcome: data, integration, problem definition, organisation, security and adoption. | [Ch. 1](../chapters/01-the-role.md), [Ch. 2](../chapters/02-history.md) |
| **Deployment strategist (Echo)** | The role paired with FDEs at Palantir that owns problem framing, stakeholder alignment, change management and the value story. | [Ch. 1](../chapters/01-the-role.md), [Ch. 2](../chapters/02-history.md), [Ch. 17](../chapters/17-running-an-fde-org.md) |
| **Dev** | Palantir's name for a product engineer: "one capability, many customers". | [Ch. 1](../chapters/01-the-role.md), [Ch. 2](../chapters/02-history.md) |
| **Difference-in-differences** | Estimating impact as the change in the pilot group minus the change in a comparison group over the same period, removing shared trends. | [Ch. 13](../chapters/13-evaluation-and-impact.md), [Ch. 20](../chapters/20-case-studies.md) |
| **DORA** | The EU's Digital Operational Resilience Act for financial entities, applying from January 2025. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **DPIA (data protection impact assessment)** | The GDPR / UK GDPR assessment required before processing personal data in ways likely to be high-risk. | [Ch. 6](../chapters/06-scoping.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md), [Ch. 15](../chapters/15-production-and-handover.md) |

## E

| Term | Definition | Covered in |
|---|---|---|
| **Echo** | Palantir's internal name for a deployment strategist. | [Ch. 1](../chapters/01-the-role.md), [Ch. 2](../chapters/02-history.md), [Ch. 17](../chapters/17-running-an-fde-org.md) |
| **Effort versus elapsed time** | Effort is engineering work in person-days; elapsed time is calendar time, dominated by waiting for access and approvals. State both. | [Ch. 6](../chapters/06-scoping.md) |
| **Embeddings** | Numeric representations of meaning used for vector search. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Engagement lifecycle** | The phases of a forward deployed engagement: qualify, discover, frame and scope, prove value, productionise, adopt, hand over, and expand and feed back. | [Ch. 4](../chapters/04-engagement-lifecycle.md) |
| **Engagement plan** | A one-page plan agreed with the sponsor: objective and criteria, scope, milestones, people, dependencies, risks and cadence. | [Ch. 4](../chapters/04-engagement-lifecycle.md) |
| **Entity resolution** | Working out which records, in one or more systems, refer to the same real-world entity. Also called record linkage or deduplication. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Error budget** | The gap between 100% and the SLO: the amount of unreliability you can tolerate. | [Ch. 15](../chapters/15-production-and-handover.md) |
| **ETL / ELT** | Extract, transform, load (transform before loading) versus extract, load, transform (load raw data, then transform in the warehouse). | [Ch. 10](../chapters/10-enterprise-data.md) |
| **EU AI Act** | Regulation (EU) 2024/1689: risk-based obligations for AI systems placed on the EU market or used in the EU, phased in from February 2025. | [Ch. 2](../chapters/02-history.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Eval set (evaluation set)** | A versioned collection of test cases, each with an input and a way to judge the output, built from the customer's real cases. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Evaluation** | Measuring whether an AI system works on the customer's real cases: how often it is right and how it fails. Distinct from impact measurement. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Excessive agency** | An agent having more permissions or autonomy than its task needs; an OWASP LLM risk category. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Executive brief** | A one-page document for executives: headline, results, what's next, asks and risks, written so it can be forwarded unchanged. | [Ch. 8](../chapters/08-communication.md), [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Executive sponsor** | The senior customer person with budget and authority who owns the engagement's strategic outcome. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 7](../chapters/07-stakeholders.md) |
| **Extension point** | A supported way to add custom behaviour to a product (plugins, functions, webhooks, connectors, SDKs, agent tools). Rung 2 of the build ladder. | [Ch. 3](../chapters/03-business.md), [Ch. 11](../chapters/11-configure-extend-change.md) |

## F

| Term | Definition | Covered in |
|---|---|---|
| **FDE (forward deployed engineer)** | A software engineer who works directly with a customer, often embedded, to deliver a working production solution to an important problem through their company's product, and who feeds what they learn back into the product. | [Ch. 1](../chapters/01-the-role.md) |
| **FDSE (Forward Deployed Software Engineer)** | Palantir's formal title for the FDE role. | [Ch. 1](../chapters/01-the-role.md), [Ch. 19](../chapters/19-career.md) |
| **Feature flag** | A switch that turns behaviour on per user or group without redeploying; an instant off switch for customer-specific or new behaviour. | [Ch. 11](../chapters/11-configure-extend-change.md), [Ch. 15](../chapters/15-production-and-handover.md) |
| **FedRAMP** | The US government programme authorising cloud services for federal use at Low, Moderate or High impact levels. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Fellegi–Sunter model** | The classical (1969) statistical foundation of record linkage, deriving field weights from agreement rates among matches and non-matches. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Field council** | A regular meeting where FDE leads present top field needs and product leaders decide, publicly, what to do with them. | [Ch. 16](../chapters/16-field-to-product.md) |
| **Field report** | A structured record carrying learning from a customer to the product team: problem, evidence, workaround, impact, other customers affected and a proposed generalisation. | [Ch. 8](../chapters/08-communication.md), [Ch. 16](../chapters/16-field-to-product.md) |
| **Fixed fee** | A set price for defined deliverables; overrun risk sits with the vendor. | [Ch. 6](../chapters/06-scoping.md) |
| **Fork** | A customer-specific copy or modification of the product's core that diverges from the main product. | [Ch. 3](../chapters/03-business.md), [Ch. 11](../chapters/11-configure-extend-change.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Freshness** | How recent data is; agreed in scope and monitored. | [Ch. 10](../chapters/10-enterprise-data.md), [Ch. 15](../chapters/15-production-and-handover.md) |

## G

| Term | Definition | Covered in |
|---|---|---|
| **GDPR / UK GDPR** | The EU and UK General Data Protection Regulations governing personal data: legal basis, minimisation, DPIAs, data subject rights, transfers and breach notification. | [Ch. 10](../chapters/10-enterprise-data.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Go / no-go** | The decision at the end of a production readiness review: GO, GO WITH CONDITIONS or NO-GO. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 15](../chapters/15-production-and-handover.md) |
| **Going native** | When an embedded person identifies so strongly with the host organisation that they stop representing their own. | [Ch. 7](../chapters/07-stakeholders.md) |
| **Golden record** | A single best version of an entity, assembled from matched records with rules about which source wins for each field. Also master record. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Grader** | The part of an evaluation that decides whether an output passes: exact match, rule-based, reference similarity, model-based or human. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Gross margin** | (Revenue − cost of delivering the product) ÷ revenue. FDE salaries counted as cost of revenue push it towards services levels. | [Ch. 3](../chapters/03-business.md) |

## H

| Term | Definition | Covered in |
|---|---|---|
| **Hallucination** | A model producing fluent but false or unsupported content. It can be reduced but not eliminated. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Handover** | Transferring ownership of a system (operation, change and support) from the FDE to the people who will run it long-term; proven by a period of unaided operation. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 15](../chapters/15-production-and-handover.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Handover pack** | The documents a receiving team needs: overview, architecture, access, runbooks, monitoring, quality, change, known issues, ADRs, support, ownership and training record. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 15](../chapters/15-production-and-handover.md) |
| **HIPAA** | US law governing protected health information handled by covered entities and their business associates. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **HITL (human in the loop)** | A person reviews or approves a model's output before it takes effect; placed where errors are costly or irreversible. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Hold-out set** | A portion of the eval set not used while iterating on prompts, to check for overfitting. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Hybrid search** | Retrieval that combines keyword search (such as BM25) with vector search; a common default. | [Ch. 12](../chapters/12-ai-deployment.md) |

## I

| Term | Definition | Covered in |
|---|---|---|
| **Idempotent** | Producing the same result when run more than once, so failed steps can be retried safely. | [Ch. 10](../chapters/10-enterprise-data.md), [Ch. 15](../chapters/15-production-and-handover.md) |
| **Impact measurement** | Establishing whether, and by how much, the business outcome improved because of the system. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Impact report** | The document that closes the loop on the success plan: headline, results against criteria, method, adoption, financial value, lessons and a recommendation. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 13](../chapters/13-evaluation-and-impact.md), [Ch. 15](../chapters/15-production-and-handover.md) |
| **Incident** | An unplanned event that disrupts or degrades a service, including AI quality incidents that return HTTP 200. | [Ch. 8](../chapters/08-communication.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md), [Ch. 15](../chapters/15-production-and-handover.md) |
| **Informal influencer** | Someone without formal authority whose opinion decides things: the senior analyst everyone asks, the architect always consulted. | [Ch. 7](../chapters/07-stakeholders.md) |
| **Insecure output handling** | Executing or rendering model output as code, SQL or HTML without treating it as untrusted input. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **ISO/IEC 27001 / 42001** | International standards for an information security management system and (2023) an AI management system. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |

## J

| Term | Definition | Covered in |
|---|---|---|
| **Jaro–Winkler similarity** | A string-similarity measure from 0 to 1 that tolerates typos and rewards shared prefixes; suits names. | [Ch. 10](../chapters/10-enterprise-data.md) |

## K

| Term | Definition | Covered in |
|---|---|---|
| **Kill switch** | An agreed way, and an agreed person, to shut a system down during an incident. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |

## L

| Term | Definition | Covered in |
|---|---|---|
| **Lagging / leading indicator** | A lagging indicator measures the result after the fact (cycle time, revenue); a leading indicator moves first and predicts it (usage, model accuracy). | [Ch. 6](../chapters/06-scoping.md) |
| **Land and expand** | Growing mainly through expansion inside existing customers. | [Ch. 3](../chapters/03-business.md) |
| **Later list** | The third scope list, beside in and out: ideas heard and recorded but not committed. | [Ch. 6](../chapters/06-scoping.md) |
| **Least privilege** | Granting only the permissions a person, service account or agent needs. | [Ch. 12](../chapters/12-ai-deployment.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Lethal trifecta** | Simon Willison's 2025 framing: an agent with access to private data, exposure to untrusted content and the ability to communicate externally can be tricked into leaking data. Remove at least one leg. | [Ch. 14](../chapters/14-security-and-restricted-environments.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Levenshtein distance** | The number of single-character edits needed to turn one string into another. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Lighthouse use case** | A first use case that is high value, highly feasible, quick to deliver and low risk, building credibility for harder problems. | [Ch. 5](../chapters/05-discovery-and-decomposition.md), [Ch. 17](../chapters/17-running-an-fde-org.md) |
| **LLM (large language model)** | A neural network trained on large amounts of text to predict the next token, able to follow instructions, analyse text and code, and use tools. | [Ch. 1](../chapters/01-the-role.md), [Ch. 12](../chapters/12-ai-deployment.md) |
| **LLM as judge** | Using another model call to grade outputs against a rubric; must be validated against human labels before it gates releases. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |

## M

| Term | Definition | Covered in |
|---|---|---|
| **Master data management (MDM)** | The discipline of building and maintaining golden records across an enterprise. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **MCP (Model Context Protocol)** | An open protocol, introduced by Anthropic in November 2024 and donated to the Agentic AI Foundation under the Linux Foundation in December 2025, that standardises how AI applications connect to tools and data. Servers expose tools, resources and prompts; clients discover and call them. | [Ch. 9](../chapters/09-toolkit.md), [Ch. 11](../chapters/11-configure-extend-change.md), [Ch. 12](../chapters/12-ai-deployment.md) |
| **MITRE ATLAS** | A knowledge base of adversary tactics and techniques against AI systems. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Model risk management** | A bank's governance of models (validation, monitoring, accountability); US supervisory guidance SR 11-7. Often applied to AI agents. | [Ch. 14](../chapters/14-security-and-restricted-environments.md), [Ch. 20](../chapters/20-case-studies.md) |
| **MSA (master services agreement)** | The overarching contract under which SOWs are issued. | [Ch. 6](../chapters/06-scoping.md) |

## N

| Term | Definition | Covered in |
|---|---|---|
| **NIST AI RMF** | The US National Institute of Standards and Technology's voluntary AI Risk Management Framework (2023), organised around govern, map, measure and manage, with a Generative AI Profile (2024). | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **NRR (net revenue retention)** | Revenue from an existing customer cohort this period, including expansion and net of churn and contraction, as a share of their revenue a year earlier. | [Ch. 3](../chapters/03-business.md), [Ch. 17](../chapters/17-running-an-fde-org.md) |

## O

| Term | Definition | Covered in |
|---|---|---|
| **Observability** | The ability to understand a system's internal state from its outputs: logs, metrics and traces. | [Ch. 9](../chapters/09-toolkit.md), [Ch. 15](../chapters/15-production-and-handover.md) |
| **Ontology** | In enterprise software, a model of the business's objects, their properties, relationships and the actions that can be taken on them, mapped onto raw data. Palantir Foundry's is the best-known example. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Open-weight model** | A model whose weights are published so customers can host it themselves, for example in air-gapped environments. | [Ch. 12](../chapters/12-ai-deployment.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md), [Ch. 20](../chapters/20-case-studies.md) |
| **OpenTelemetry** | The common open standard for traces, metrics and logs. | [Ch. 15](../chapters/15-production-and-handover.md) |
| **Orphan code** | Custom code with no owning team or support plan. "No orphan code" is a rule against the agency trap. | [Ch. 3](../chapters/03-business.md), [Ch. 11](../chapters/11-configure-extend-change.md) |
| **Outcome-based pricing** | Fees tied to measured outcomes such as tickets resolved or hours saved. | [Ch. 3](../chapters/03-business.md) |
| **OWASP Top 10 for LLM Applications** | OWASP's list of the most common technical risk categories in LLM systems, such as prompt injection, sensitive information disclosure and excessive agency. | [Ch. 12](../chapters/12-ai-deployment.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md) |

## P

| Term | Definition | Covered in |
|---|---|---|
| **Paid pilot (proof of value)** | A fixed-fee, time-boxed engagement with agreed success criteria, often credited against a subscription if the customer signs. | [Ch. 3](../chapters/03-business.md), [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 6](../chapters/06-scoping.md) |
| **Partner-delivered** | A model in which consultancies or partners deploy the product and vendor FDEs coach, review or certify them. | [Ch. 3](../chapters/03-business.md), [Ch. 4](../chapters/04-engagement-lifecycle.md) |
| **Permission-aware retrieval** | Retrieval that never lets a user receive an answer based on a document they may not read, using ACLs and security trimming. | [Ch. 12](../chapters/12-ai-deployment.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Personal data** | Any information relating to an identifiable person, in GDPR's definition. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Phased rollout** | Deploying team by team or site by site; doubles as a comparison design for impact measurement. | [Ch. 13](../chapters/13-evaluation-and-impact.md), [Ch. 15](../chapters/15-production-and-handover.md) |
| **Pilot purgatory** | A pilot that "succeeds" but never moves to production, usually for organisational rather than technical reasons. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 6](../chapters/06-scoping.md), [Ch. 15](../chapters/15-production-and-handover.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Placeholder value** | A value typed in the absence of a real one (`N/A`, `01/01/1900`, `9999-12-31`); treat as missing. | [Ch. 10](../chapters/10-enterprise-data.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Playbook** | The documented way an organisation runs engagements: phases, templates, checklists, examples and lessons. | [Ch. 16](../chapters/16-field-to-product.md), [Ch. 17](../chapters/17-running-an-fde-org.md) |
| **Pod** | A small cross-functional team (FDEs, a strategist, a product liaison, commercial roles) assigned to one large customer or a few related ones. | [Ch. 2](../chapters/02-history.md), [Ch. 17](../chapters/17-running-an-fde-org.md) |
| **Politics** | The ordinary process by which people with different interests, incentives and information make decisions together. | [Ch. 7](../chapters/07-stakeholders.md) |
| **Precision / recall** | Precision: of the items you flagged, the share that were right. Recall: of the true items, the share you found. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Problem decomposition canvas** | The book's template for structuring a decomposition from goal to drivers, users, data and first slice. | [Ch. 5](../chapters/05-discovery-and-decomposition.md) |
| **Product liaison** | A product manager or engineer assigned to an FDE pod or industry to read field reports and attend field reviews. | [Ch. 16](../chapters/16-field-to-product.md), [Ch. 17](../chapters/17-running-an-fde-org.md) |
| **Production readiness review (PRR)** | A structured, evidence-based check before launch that a system meets agreed standards for security, reliability, operations, recovery, quality and support. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 15](../chapters/15-production-and-handover.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Productisation rate** | The share of field-built components that become product or reusable assets. | [Ch. 3](../chapters/03-business.md), [Ch. 16](../chapters/16-field-to-product.md), [Ch. 17](../chapters/17-running-an-fde-org.md) |
| **Professional services** | Billable custom work for customers, judged on utilisation; it rarely feeds the product. | [Ch. 1](../chapters/01-the-role.md), [Ch. 3](../chapters/03-business.md) |
| **Prompt** | The input to a model: instructions, context and the user's request. The system prompt sets persistent instructions and role. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Prompt caching** | A provider discount for repeated prompt prefixes such as long system prompts. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Prompt injection** | An attack in which text the model reads contains instructions that hijack its behaviour. The most important security risk in agent systems. | [Ch. 12](../chapters/12-ai-deployment.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Pseudonymisation** | Replacing direct identifiers with consistent tokens and keeping the mapping separately. Pseudonymised data is still personal data under GDPR. | [Ch. 10](../chapters/10-enterprise-data.md) |

## Q

| Term | Definition | Covered in |
|---|---|---|
| **Quality SLO** | A service level objective for AI output quality, such as a share of sampled outputs graded correct. | [Ch. 15](../chapters/15-production-and-handover.md) |

## R

| Term | Definition | Covered in |
|---|---|---|
| **RACI** | A table assigning, for each activity, who is Responsible, Accountable, Consulted and Informed. | [Ch. 6](../chapters/06-scoping.md) |
| **RAG (retrieval-augmented generation)** | Retrieving relevant passages from a document collection and giving them to the model with the question, so answers are grounded and cited. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **RAG status** | Red (off track, needs intervention), amber (at risk, being managed), green (on track). Not to be confused with retrieval-augmented generation. | [Ch. 8](../chapters/08-communication.md), [Ch. 17](../chapters/17-running-an-fde-org.md) |
| **Randomised controlled trial (RCT)** | Assigning teams or cases at random to the new system or the old process; the gold standard for impact measurement. Also called an A/B test. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **RBAC (role-based access control)** | Granting permissions by role, mapped to the customer's identity groups. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Read replica** | A copy of a database kept in sync, safe for queries but possibly lagging. | [Ch. 8](../chapters/08-communication.md), [Ch. 10](../chapters/10-enterprise-data.md) |
| **Recall at k** | Whether the relevant passage appears in the top k retrieved results; used to evaluate retrieval separately from generation. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Record linkage** | See *entity resolution*. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Reference-class forecasting** | Estimating from the actual outcomes of similar past projects, adjusted for known differences, to correct bottom-up optimism. | [Ch. 6](../chapters/06-scoping.md) |
| **Regression (evaluation)** | A change that makes previously passing behaviour fail; eval suites run on every change to catch it. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Reranker** | A model that reorders the top retrieval candidates. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Rollback** | A tested way to return to the previous version, with decision criteria written in advance. | [Ch. 15](../chapters/15-production-and-handover.md) |
| **Rotation** | FDEs spending time on product teams, or product engineers in the field. | [Ch. 16](../chapters/16-field-to-product.md), [Ch. 17](../chapters/17-running-an-fde-org.md), [Ch. 18](../chapters/18-life-as-an-fde.md) |
| **Rubric** | Written criteria for what makes an output correct, partially correct or wrong, used by human labellers and model judges. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Rule of three** | Build it custom the first time, notice it the second, generalise it the third: three distinct customers with the same need trigger productisation. | [Ch. 3](../chapters/03-business.md), [Ch. 8](../chapters/08-communication.md), [Ch. 16](../chapters/16-field-to-product.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Runbook** | A step-by-step procedure for an operational task, written for someone unfamiliar with the system working under pressure. | [Ch. 15](../chapters/15-production-and-handover.md) |

## S

| Term | Definition | Covered in |
|---|---|---|
| **SBOM (software bill of materials)** | A list of every software component and version in a release. | [Ch. 14](../chapters/14-security-and-restricted-environments.md), [Ch. 20](../chapters/20-case-studies.md) |
| **SCIM** | System for Cross-domain Identity Management: a protocol for provisioning users and groups automatically so leavers lose access promptly. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Scope** | The agreed boundary of the work: what will be delivered, for whom, by when, and what will not. Written as in, out and later. | [Ch. 6](../chapters/06-scoping.md) |
| **Security trimming** | Filtering retrieval candidates by the user's permissions before anything reaches the model. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Semantic layer** | A layer that defines business metrics and dimensions once so every tool computes them the same way. | [Ch. 10](../chapters/10-enterprise-data.md) |
| **Services-led growth** | Andreessen Horowitz's term for AI start-ups accepting services-heavy early revenue to build data, workflows and trust. | [Ch. 3](../chapters/03-business.md) |
| **Shadow mode** | Running a new system alongside the old one, logging its outputs without using them, to gather production evidence. | [Ch. 15](../chapters/15-production-and-handover.md), [Ch. 20](../chapters/20-case-studies.md) |
| **Shadowing (field observation)** | Sitting with people while they work to see workarounds, exceptions, hidden dependencies, real timing and trust. | [Ch. 5](../chapters/05-discovery-and-decomposition.md) |
| **SIG** | The Shared Assessments Standardized Information Gathering questionnaire for vendor risk. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **SLI / SLO / SLA** | Service level indicator (a measured quantity), objective (a target for it over a period) and agreement (a contractual commitment with remedies). | [Ch. 15](../chapters/15-production-and-handover.md) |
| **Slice** | A subset of eval cases sharing a tag (claim type, language, difficulty); overall scores can hide slice regressions. | [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **SMART (+ owned, baselined)** | Specific, measurable, achievable, relevant, time-bound; forward deployment adds owned and baselined. | [Ch. 6](../chapters/06-scoping.md) |
| **SME (subject-matter expert)** | A customer expert whose knowledge defines correct behaviour; a co-designer and labeller. | [Ch. 7](../chapters/07-stakeholders.md), [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **SOC 2** | An AICPA audit report on a service organisation's controls; Type II covers operation over a period. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Solutions engineer** | A pre-sale technical role making the case for a sale through demos, proofs of concept and architecture advice. | [Ch. 1](../chapters/01-the-role.md), [Ch. 2](../chapters/02-history.md), [Ch. 19](../chapters/19-career.md) |
| **Sovereign cloud** | Cloud regions operated under national control, often with limited service and model availability. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **SOW (statement of work)** | A contractual document defining the work a supplier will do, usually under an MSA: objectives, deliverables, assumptions, acceptance, change control, commercials, IP and data handling. | [Ch. 3](../chapters/03-business.md), [Ch. 6](../chapters/06-scoping.md) |
| **SSO (single sign-on)** | Logging in through the customer's identity provider using SAML or OpenID Connect. | [Ch. 9](../chapters/09-toolkit.md), [Ch. 14](../chapters/14-security-and-restricted-environments.md) |
| **Stakeholder map** | A placement of each stakeholder by influence over the deployment and attitude towards it. | [Ch. 7](../chapters/07-stakeholders.md) |
| **STAR** | Situation, task, action, result: a structure for behavioural interview answers. | [Ch. 19](../chapters/19-career.md) |
| **Success criterion** | A measurable outcome that, if achieved, means the engagement worked; written at business-outcome, adoption and system-quality levels. | [Ch. 6](../chapters/06-scoping.md), [Ch. 13](../chapters/13-evaluation-and-impact.md) |
| **Success plan** | A two- to four-page working agreement signed by the sponsor: objective, criteria, scope, milestones, RACI, dependencies, risks, governance and sign-off. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 6](../chapters/06-scoping.md) |
| **Support tiers** | Tier 1 user questions; Tier 2 configuration, data and diagnosis; Tier 3 product defects. The FDE is not a support tier. | [Ch. 15](../chapters/15-production-and-handover.md) |

## T

| Term | Definition | Covered in |
|---|---|---|
| **T-shaped** | Broad working knowledge across many technologies plus depth in one or two. | [Ch. 9](../chapters/09-toolkit.md) |
| **Time and materials (T&M)** | The customer pays for hours or days worked; overrun risk sits with the customer. | [Ch. 6](../chapters/06-scoping.md) |
| **Time to first value** | Days from contract to first measurable outcome; predicts expansion and retention. | [Ch. 3](../chapters/03-business.md), [Ch. 17](../chapters/17-running-an-fde-org.md) |
| **Tool (tool use)** | A function the model can request the application to call, described by a name, description and input schema. Good tools are business-level, validated and bounded. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Trust equation** | Maister, Green and Galford's model: trust = (credibility + reliability + intimacy) ÷ self-orientation. | [Ch. 7](../chapters/07-stakeholders.md) |

## V

| Term | Definition | Covered in |
|---|---|---|
| **Vector search** | Finding semantically similar passages by comparing embeddings. | [Ch. 12](../chapters/12-ai-deployment.md) |
| **Vendor risk assessment** | A customer's assessment of a supplier, usually a security questionnaire plus certifications and penetration-test evidence. | [Ch. 14](../chapters/14-security-and-restricted-environments.md) |

## W

| Term | Definition | Covered in |
|---|---|---|
| **Weekly update** | The FDE's written heartbeat to the customer owner, sponsor and internal team: summary, progress against criteria, done and next, decisions, risks. | [Ch. 4](../chapters/04-engagement-lifecycle.md), [Ch. 8](../chapters/08-communication.md) |
| **Works council** | An elected employee body (notably in Germany) with legal rights to be consulted about technology that can monitor employee behaviour or performance. | [Ch. 7](../chapters/07-stakeholders.md) |

---

*197 entries. See also the companion glossaries in [*The Integration Design Engineer*](../../integration-design-engineer/appendices/A-glossary.md) and [*GTM Engineering*](../../gtm-engineering/appendices/A-glossary.md).*
