# Chapter 17. The GTM Stack: Tools, Build vs Buy and Cost

> "Every tool in the stack is a subscription, an integration, a credential and a data copy."

## What you will learn

- The categories of a modern GTM stack and leading tools in each *(as of October 2026)*.
- Reference stacks for different company stages.
- How to evaluate and buy tools, and when to build instead.
- Total cost of ownership, credit economics and stack governance.
- Market dynamics: consolidation, AI-native entrants, and vendor risk.

> Vendor names illustrate categories; this is not an endorsement. The market changes monthly. Verify capabilities, pricing and ownership before deciding.

---

## 17.1 Stack categories

| Category | Purpose | Examples |
|---|---|---|
| **CRM** | System of record for accounts, contacts, deals | Salesforce, HubSpot, Microsoft Dynamics 365, Attio, Pipedrive, Close |
| **Data / enrichment** | Company and contact data | ZoomInfo, Apollo, Cognism, Lusha, People Data Labs, Breeze Intelligence (HubSpot) |
| **Enrichment orchestration / GTM workflow** | Waterfalls, AI research, custom signals, automation | Clay, Databar, Persana, Cargo, Bitscale |
| **Email finding and verification** | Find and verify emails | Hunter, Findymail, Prospeo, LeadMagic; ZeroBounce, NeverBounce, MillionVerifier |
| **Signals and intent** | Buying signals | 6sense, Demandbase, Bombora, G2 Buyer Intent, Common Room, Unify, Warmly, UserGems, Trigify |
| **Sales engagement / sequencing** | Multi-step outreach, dialling | Outreach, Salesloft (merged with Clari, December 2025), Apollo, HubSpot Sequences; cold-email-focused: Instantly, Smartlead, Lemlist, Reply.io |
| **LinkedIn tools** | Prospecting and (risky) automation | LinkedIn Sales Navigator (official); third-party automation (Chapter 16 risks) |
| **Routing and scheduling** | Matching, assignment, booking | LeanData, Chili Piper, Default, RevenueHero |
| **Conversation and revenue intelligence** | Call recording, forecasting, deal insights | Gong, Clari/Salesloft, Avoma, Fathom |
| **Marketing automation** | Email nurture, forms, campaigns | HubSpot Marketing Hub, Marketo, Salesforce Marketing Cloud Account Engagement (Pardot), Customer.io |
| **Website identification / chat** | Visitor identification, chat | Breeze Intelligence, Dealfront, Warmly, Qualified, RB2B; (Drift is being retired) |
| **Product analytics and CDP** | Product events, identity | Segment, RudderStack, Amplitude, Mixpanel, PostHog |
| **Warehouse and modelling** | Central data, models | Snowflake, BigQuery, Databricks, Postgres; dbt |
| **Reverse ETL** | Warehouse → tools | Hightouch, Census |
| **Automation / iPaaS** | Glue workflows | Zapier, Make, n8n, Workato, Tray.ai |
| **AI agents** | Research, SDR agents, copilots | Agentforce, Breeze agents, Clay agents, Artisan, 11x, custom agents on model APIs |
| **Deliverability infrastructure** | Domains, inboxes, monitoring | Google Workspace / Microsoft 365, DNS providers, Postmaster Tools, DMARC tools, placement testers |
| **Analytics / BI** | Dashboards | Looker, Tableau, Power BI, Metabase, Hex, CRM reports |

## 17.2 Reference stacks *(illustrative)*

### Seed / early stage (founder-led sales, 1 GTM engineer or fractional)

- HubSpot (free or Starter) or Attio as CRM
- Clay for list building, enrichment and research
- Apollo for data and sequencing, *or* Instantly/Smartlead for cold email on secondary domains
- A verification tool; Google Workspace inboxes; DMARC monitoring
- Calendly or HubSpot meetings; Zapier or n8n; a spreadsheet or Metabase for metrics

Principle: **few tools, fast learning, low fixed cost.**

### Series A–B (SDR team, inbound + outbound)

- HubSpot Professional or Salesforce
- Clay (waterfalls, signals, AI research) + one primary data provider
- Outreach / Salesloft / Apollo for sequences; separate cold infrastructure if volume requires
- Chili Piper or Default for inbound routing and booking
- A signal tool or two (job changes, website, intent: only if they prove lift)
- Gong or equivalent
- Warehouse + dbt + reverse ETL starting (especially if PLG)

### Growth / enterprise

- Salesforce (often) with LeanData; enterprise data contracts (ZoomInfo or similar)
- ABM / intent platform (6sense, Demandbase)
- Warehouse-native GTM (Snowflake + dbt + Hightouch/Census)
- Governed automation (Workato or in-house services), security reviews, SSO everywhere
- GTM engineering team with an inventory, runbooks and change management

## 17.3 Evaluating tools

| Criterion | Questions |
|---|---|
| **Problem fit** | Which play or bottleneck does it improve? What metric will move? |
| **Data quality** | Bake-off on *your* ICP sample (Chapter 7) |
| **Integration** | Native CRM sync? API and webhooks? Field mapping control? Writes idempotent (upsert)? API-limit consumption? |
| **Control and safety** | Sending caps, approvals, suppression support, audit logs |
| **Security and compliance** | SOC 2, DPA, data residency, sub-processors, OAuth scopes requested |
| **Total cost** | Licence + credits + usage overages + implementation + maintenance time |
| **Lock-in and exit** | Can you export data and logic? What happens to your data at contract end? |
| **Vendor viability** | Funding, ownership changes, roadmap, support quality |

Run a **time-boxed pilot** with success criteria agreed in advance, ideally with a holdout (Chapter 15).

## 17.4 Build vs buy

| Build when | Buy when |
|---|---|
| The logic is your competitive advantage (custom signals, proprietary scoring) | It's a commodity (sequencing, calendar booking, verification) |
| Tools can't express your rules (complex routing, unusual data model) | A tool fits 80%+ of needs |
| Volume makes credit-based pricing expensive | Volume is moderate |
| You have engineering capacity to maintain it | You don't |
| Data must stay in your environment | Vendor's terms and security are acceptable |

A common pattern: **buy the platform, build the logic.** Use Clay, a sequencer and a CRM, but own the ICP model, signal definitions, scoring code and warehouse models yourself, in version control.

## 17.5 Cost and credit economics

GTM tools increasingly charge by **usage**: enrichment credits, AI actions, contacts, sends, or outcomes (HubSpot moved its Prospecting Agent to outcome-based pricing in April 2026). Manage cost like an engineer:

- **Unit economics per play:** cost per enriched contact, per sent email, per meeting held, per pipeline dollar.
- **Waterfall ordering and caching** (Chapter 7).
- **Run conditions** so expensive steps only run on qualified rows.
- **Budget alerts** per tool and per table.
- **Annual vs monthly:** commit only after usage is proven.
- **Seat audits:** remove unused seats quarterly.
- **Consolidate overlapping tools** (two intent providers reselling the same co-op data, two dialers, three enrichment contracts).

Example monthly costs for one play *(illustrative)*: 2,000 contacts × $0.12 enrichment and verification = $240; AI research $0.03 × 2,000 = $60; sending infrastructure share $150; sequencer seats share $200; human QA 6 hours × $60 = $360. Total ≈ **$1,010**. With 18 meetings held, that is about **$56 per meeting**. Compare with the expected pipeline per meeting to decide whether to scale.

## 17.6 Stack governance

- **Inventory** every tool: owner, purpose, cost, renewal date, users, integrations, data held, security review status (template: [`templates/stack-inventory.md`](../templates/stack-inventory.md)).
- **Approval process** for new tools (security, legal, data, budget).
- **Renewal calendar** reviewed 90 days ahead with usage data.
- **Data flow diagram** showing where personal data goes (needed for GDPR records and security reviews).
- **Integration-token review** quarterly (Chapter 16).

## 17.7 Market dynamics *(as of October 2026)*

- **Consolidation:** HubSpot–Clearbit (2023), Clari–Salesloft (closed December 2025) and many smaller deals. Expect bundling of data, engagement and intelligence into "revenue platforms".
- **Platforms move into agents:** Salesforce Agentforce, HubSpot Breeze agents and ZoomInfo's GTM-branded workspace products compete with AI-native start-ups.
- **Clay's growth:** valued at about $7.1 billion after a September 2026 Series D, expanding from tables into audiences, sequencing, workflows and agents. This puts it in competition with some of the tools it once integrated.
- **AI-native CRMs** (Attio and newer entrants) challenge incumbents for smaller teams.
- **Vendor risk:** acquisitions, product sunsets (Drift), breaches and pricing changes can disrupt your stack. Keep logic portable and data exportable.

---

## Summary

- A GTM stack spans CRM, data and enrichment, orchestration, verification, signals, engagement, routing, intelligence, marketing automation, product data, warehouse and reverse ETL, automation, AI agents, deliverability and BI.
- Size the stack to the stage: few tools early, governed platforms later.
- Evaluate tools on problem fit, data quality on your ICP, integration, controls, security, total cost, lock-in and viability, with pilots and holdouts.
- Buy commodity platforms; build the logic that is your advantage, in version control.
- Manage usage-based costs per play; govern the stack with an inventory, approvals, renewals, data-flow maps and token reviews.

## Exercises

See [`exercises/17-stack.md`](../exercises/17-stack.md).

## Further reading

- Vendor documentation and pricing pages (check dates).
- Sacra and analyst coverage of GTM platform consolidation.
