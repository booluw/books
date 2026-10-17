# Chapter 9. The FDE Technical Toolkit

> "You won't choose the stack. You'll have to be productive in whatever stack you find."

## What you will learn

- The technical skills FDEs use most, and why breadth matters more than in most engineering roles.
- The languages, data tools, integration patterns, infrastructure and AI tooling that recur across engagements.
- How to become productive in an unfamiliar customer environment in days.
- How to build fast without building badly: prototypes that can grow up.
- How to set up a portable personal toolkit.

---

## 9.1 The shape of FDE technical skill

A product engineer typically goes deep in one stack: the company's own. An FDE is dropped into whatever the customer runs: a bank's mainframe extracts, a hospital's HL7 feeds, a manufacturer's SAP system, a start-up's Postgres and Kubernetes. They must also be fluent in their own company's product.

The resulting shape is sometimes called **T-shaped**: broad, working knowledge across many technologies (the horizontal bar) and genuine depth in one or two (the vertical stroke). Many FDE job descriptions ask for strong general software engineering, plus data engineering, plus some combination of cloud infrastructure and, from 2024, applied AI.

The most important technical skill is not any particular technology. It is **getting productive quickly in an unfamiliar environment**: reading unknown code, finding the data, understanding the constraints, and shipping something that works within days.

## 9.2 Languages

| Language | Why FDEs use it | Typical tasks |
|---|---|---|
| **Python** | The lingua franca of data and AI work; huge library ecosystem; fast to prototype | Data pipelines, scripts, API services, LLM applications, notebooks |
| **SQL** | Enterprise data lives in relational databases and warehouses | Profiling, joins, transformations, reports, debugging |
| **TypeScript / JavaScript** | Most user interfaces; many integration services; serverless functions | Front ends, browser extensions, Node services |
| **Shell (bash)** | Every server, container and CI pipeline | Automation, glue, diagnosis |
| **Java / C# / Go** | Common in enterprise back ends and in some vendor platforms | Reading and extending customer systems; high-throughput services |

You don't need to be expert in all of them. You need to **read** all of them confidently, and **write** Python and SQL fluently. Palantir's FDE interviews, for example, typically allow candidates their choice of mainstream language for coding rounds, but the job itself requires switching.

## 9.3 Data skills

Most FDE work starts with data: finding it, getting access, understanding it and moving it (Chapter 10 goes deep). Core skills:

- **SQL** beyond basics: window functions, common table expressions (CTEs), query plans and indexing, so you can query large tables without hurting a production database.
- **Data modelling:** entities, relationships, keys, normalisation versus denormalisation, slowly changing dimensions.
- **Dataframes:** pandas or Polars in Python, for quick analysis and transformation.
- **File formats:** CSV (and its many dialects), JSON, Parquet, Excel (yes, constantly), XML, fixed-width mainframe files.
- **Warehouses and lakes:** Snowflake, Databricks, BigQuery, Redshift, Synapse/Fabric. Know how to query them and how they are billed.
- **Pipelines:** batch versus streaming; orchestration tools (Airflow, Dagster, dbt for SQL transformations); change data capture (CDC).
- **Data quality:** profiling, validation, deduplication and record linkage. See [`examples/data-profiler/`](../examples/data-profiler/) and [`examples/record-linkage/`](../examples/record-linkage/).

## 9.4 Integration skills

FDEs connect their product to the customer's systems. The companion book [*The Integration Design Engineer*](../../integration-design-engineer/) covers this in depth. The essentials:

- **HTTP APIs:** REST conventions, pagination, rate limits, retries with backoff, idempotency.
- **Authentication:** OAuth 2.0 flows, API keys, service accounts, mutual TLS, single sign-on with SAML or OpenID Connect.
- **Events and messaging:** webhooks, queues and streams (Kafka, cloud queues), at-least-once delivery and deduplication.
- **Enterprise systems:** ERP (SAP, Oracle), CRM (Salesforce, Dynamics), ITSM (ServiceNow), HR (Workday), and sector systems (Epic and Cerner in healthcare, Guidewire in insurance, core banking platforms). Each has its own API style, data model and quirks.
- **File-based integration:** SFTP drops, scheduled exports. Unfashionable, still everywhere.
- **Integration platforms:** iPaaS tools such as MuleSoft, Boomi and Workato, which customers may require you to use.

## 9.5 Infrastructure and operations

Deployments must run somewhere, securely and reliably:

- **Cloud fundamentals** on at least one of AWS, Azure or Google Cloud: identity and access management (IAM), networking (VPCs, private endpoints, security groups), storage, managed databases, serverless functions.
- **Containers:** Docker; enough Kubernetes to deploy, debug and read manifests.
- **Infrastructure as code:** Terraform or the cloud's own tools, so environments are reproducible and reviewable by the customer's platform team.
- **CI/CD:** building, testing and deploying through the customer's pipelines (GitHub Actions, GitLab, Azure DevOps, Jenkins).
- **Networking:** DNS, TLS certificates, proxies, firewalls, VPNs. In enterprises, a surprising share of "the integration doesn't work" turns out to be a firewall rule or a proxy that rewrites TLS.
- **Observability:** logs, metrics and traces; dashboards and alerts (Chapter 15).
- **Restricted environments:** on-premises servers, air-gapped networks and sovereign clouds (Chapter 14).

## 9.6 Applied AI skills *(as of October 2026)*

From 2024, most new FDE roles involve deploying AI systems. The core skills (Chapters 12 and 13 go deep):

- **Model APIs:** calling hosted models (Anthropic, OpenAI, Google, open-weight models via cloud providers); streaming; structured output; tool use; cost and latency management.
- **Prompt and context engineering:** writing clear instructions, providing examples, assembling the right context from documents and data.
- **Retrieval:** chunking documents, keyword and vector search, hybrid ranking, permission-aware retrieval. See [`examples/permission-aware-retrieval/`](../examples/permission-aware-retrieval/).
- **Agents and tools:** letting models call functions and APIs; the **Model Context Protocol (MCP)**, an open standard introduced by Anthropic in November 2024 for connecting models to tools and data, now widely supported; guardrails and approvals ([`examples/agent-guardrails/`](../examples/agent-guardrails/)).
- **Evaluation:** building test sets, graders and regression suites ([`examples/llm-eval-harness/`](../examples/llm-eval-harness/)).
- **AI-assisted development:** coding assistants and agents (Claude Code, GitHub Copilot, Cursor and others) are now standard tools for FDEs themselves, multiplying how much one engineer can build in a week. Know your customer's policy on using them with their code and data before you do.

## 9.7 Product fluency

The FDE's own company's product is part of the toolkit, and deep fluency in it is a differentiator:

- **Know the extension points** (Chapter 11): configuration, APIs, SDKs, plugins, functions, connectors.
- **Know the limits:** scale limits, unsupported cases, known bugs. Better you than the customer.
- **Know the roadmap:** what's coming, so you don't build something the product will ship next quarter.
- **Know the people:** which product engineer owns which component, so you can ask the right person directly.

## 9.8 Getting productive in a new environment

The first week on a new engagement has a predictable shape. A checklist:

**Day 1–2: access and orientation**

- Accounts, laptop or virtual desktop, VPN, email, chat, ticketing system, code repositories.
- Read the architecture documentation that exists (and note what doesn't).
- Find the people: platform owner, DBA, security contact, the engineer who knows where the bodies are buried.
- Learn the change process: how code gets to production, who approves, what the release windows are.

**Day 2–4: find the data and systems**

- Run read-only queries against the systems in scope; profile the data (Chapter 10).
- Trace one real case end to end through the systems.
- Identify the environments (development, test, staging, production) and which you may use.

**Day 3–5: ship something small**

- A script, report or tool that helps someone with a real problem. It proves your access works end to end and starts building trust (Chapter 7).

### Reading unfamiliar code quickly

- Start from entry points (main functions, HTTP routes, scheduled jobs) and the data model, not from the top of the file tree.
- Use search across the repository for domain terms the users mentioned.
- Run it locally if you can; use a debugger to follow one request.
- Read the tests: they show intended behaviour.
- Ask an AI coding assistant to summarise modules, if policy allows. Verify what it says.
- Keep notes as you go; they become the handover documentation later.

## 9.9 Prototype fast, without building badly

FDEs are expected to move quickly. But prototypes have a habit of becoming production systems. The challenge is to build fast in a way that can grow up, rather than fast in a way that must be thrown away (and usually isn't).

| Do from day one (cheap now, expensive later) | Defer safely |
|---|---|
| Version control for everything, including configuration and prompts | Elaborate abstractions and frameworks |
| Secrets in a secret manager, never in code | Horizontal scaling |
| Basic logging with request IDs | Polished UI |
| A small automated test suite, including an evaluation set for AI | Full test coverage |
| Infrastructure as code for anything you deploy | Multi-region failover |
| A README: how to run it, how it works, who owns it | Comprehensive documentation |
| Respecting the customer's access controls | Performance optimisation |

The left column is cheap to do at the start and very expensive to retrofit. It is also exactly what the customer's security and platform teams will check before production (Chapters 14 and 15).

### Notebook to service

Many FDE prototypes start in a notebook (Jupyter or a platform equivalent). That's fine for exploration. Once something works, move the logic into a module with functions and tests, and have the notebook call it. Production systems should not depend on a notebook run by hand.

## 9.10 A portable personal toolkit

Experienced FDEs carry a toolkit between engagements:

- **Snippets and scripts:** data profiling, CSV cleaning, API pagination, retry wrappers, evaluation runners. (The examples in this book are a starting point.)
- **Templates:** success plans, weekly updates, handover packs (the [`templates/`](../templates/) folder).
- **Checklists:** first-week onboarding, production readiness, security questionnaires (Appendix C).
- **A reference library:** notes on enterprise systems you've integrated with (SAP's quirks, ServiceNow's API, the particular way a given hospital system encodes dates).
- **A personal environment that works offline:** some customers' networks block package registries, so carry what you need, with the customer's permission (Chapter 14).

Two cautions:

- **Never carry customer data or code between engagements.** Your toolkit contains generic tools and knowledge, never one customer's assets. This is both a contractual and an ethical line.
- **Contribute toolkit pieces back to the product** when they're generic enough (Chapter 16). A snippet every FDE copies is a feature waiting to be built.

---

## Summary

- FDEs need broad, working fluency across stacks plus depth in one or two. The meta-skill is becoming productive fast in an unfamiliar environment.
- Core languages: Python and SQL fluently; read TypeScript, Java/C#/Go and shell confidently.
- Data, integration, infrastructure and (since 2024) applied AI skills recur in almost every engagement.
- Know your own product deeply: extension points, limits, roadmap and people.
- Follow a first-week routine: access, people, data, an end-to-end trace, and a small shipped win.
- Prototype fast, but do the cheap-now, expensive-later things from day one: version control, secrets management, logging, tests, infrastructure as code, a README.
- Carry a portable toolkit, but never carry customer data or code between engagements.

## Exercises

See [`exercises/09-toolkit.md`](../exercises/09-toolkit.md).

## Further reading

- Martin Kleppmann, *Designing Data-Intensive Applications* (2017; 2nd edition with Chris Riccomini, O'Reilly, March 2026).
- Michael Feathers, *Working Effectively with Legacy Code* (2004).
- Chip Huyen, *AI Engineering* (2025).
- Model Context Protocol documentation (modelcontextprotocol.io).
- The companion book in this repository, [*The Integration Design Engineer*](../../integration-design-engineer/).
