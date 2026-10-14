# GTM Engineering

### Building the Systems That Create Revenue: Data, Signals, Automation and AI for B2B Go-to-Market

*First edition, October 2026*

---

## About this book

Every B2B company has to find the right buyers, reach them at the right moment with the right message, hand interested buyers to the right salesperson within minutes, and learn from what happened. For decades that work was done by armies of people: researchers building lists, sales development reps (SDRs) writing emails one by one, operations analysts cleaning spreadsheets.

**GTM engineering** replaces much of that manual effort with systems. A **GTM (go-to-market) engineer** builds the data pipelines, enrichment workflows, scoring models, routing rules, outbound and inbound automation, and AI agents that generate and convert pipeline. The title was coined by the data platform Clay in 2023. By 2026 it had become one of the fastest-growing roles in B2B software.

This book explains the role from first principles. It assumes you have technical ability: you can write a little code or SQL, or at least build a complex spreadsheet. It does **not** assume you know how B2B sales and marketing work. Every commercial term (ICP, MQL, pipeline coverage, CAC payback) is defined the first time it appears, and every technique is explained in terms of the business problem it solves.

### Who this book is for

- Engineers and data people who want to work closer to revenue.
- Sales ops, marketing ops and RevOps practitioners who want to become builders.
- SDRs, account executives and growth marketers who want to automate their own work and move into a technical role.
- Founders and go-to-market leaders deciding whether to hire a GTM engineer and what to expect.

### Companion book

This book builds on ideas covered in depth in [*The Integration Design Engineer*](../integration-design-engineer/), particularly APIs, webhooks, idempotency and reliability. Where a topic is covered there, this book summarises it and links across.

---

## How to read this book

| If you are… | Read |
|---|---|
| New to B2B go-to-market | Part I and Part II in order |
| An engineer moving into GTM | Chapters 1, 3, 4, 5, then Part III |
| A RevOps or sales-ops practitioner | Chapters 1, 6, then Parts III and IV |
| Hiring a GTM engineer | Chapters 1, 17, 18, 19 |
| Preparing for interviews | Chapters 1, 3, 9, 11, 19 and the exercises |

Folders:

- [`chapters/`](chapters/): the main text.
- [`examples/`](examples/): runnable, tested code (standard-library Python): ICP scoring, an enrichment waterfall, deduplication and lead-to-account matching, lead routing, email-authentication checks, safe personalisation, a signal pipeline and funnel metrics.
- [`exercises/`](exercises/): exercises with solutions per chapter.
- [`templates/`](templates/): play briefs, ICP definition, enrichment spec, routing spec, legitimate-interest assessment, stack inventory and runbook.
- [`diagrams/`](diagrams/): Mermaid diagrams.
- [`appendices/`](appendices/): glossary, metrics reference, bibliography and checklists.

---

## Table of contents

### Part I: The Role

1. [What a GTM Engineer Is](chapters/01-the-role.md)
2. [From Sales Ops to GTM Engineering: A Short History](chapters/02-history.md)

### Part II: Foundations

3. [How B2B Companies Sell: Motions, Funnels and Metrics](chapters/03-how-b2b-sells.md)
4. [ICP, TAM and Segmentation](chapters/04-icp-and-tam.md)
5. [The GTM Data Model: CRMs, Identity and Matching](chapters/05-data-model.md)
6. [The Technical Toolkit](chapters/06-technical-toolkit.md)

### Part III: Building the Machine

7. [Data Sourcing and Enrichment](chapters/07-enrichment.md)
8. [Signals and Intent](chapters/08-signals.md)
9. [Scoring, Routing and Speed-to-Lead](chapters/09-scoring-and-routing.md)
10. [Outbound Systems and Personalisation at Scale](chapters/10-outbound.md)
11. [Email Deliverability Engineering](chapters/11-deliverability.md)
12. [Inbound, Product-Led Growth and Warehouse-Native GTM](chapters/12-inbound-and-plg.md)
13. [AI Agents in Go-to-Market](chapters/13-ai-agents.md)
14. [CRM Engineering and Data Hygiene](chapters/14-crm-engineering.md)

### Part IV: Measurement, Rules and Tools

15. [Analytics, Attribution and Experimentation](chapters/15-analytics.md)
16. [Compliance, Privacy, Platform Rules and Security](chapters/16-compliance-and-security.md)
17. [The GTM Stack: Tools, Build vs Buy and Cost](chapters/17-stack.md)

### Part V: Practice and Career

18. [Working as a GTM Engineer](chapters/18-practice.md)
19. [Becoming a GTM Engineer](chapters/19-career.md)
20. [Case Studies](chapters/20-case-studies.md)

### Appendices

- A. [Glossary](appendices/A-glossary.md)
- B. [Metrics and Formulas Reference](appendices/B-metrics.md)
- C. [Bibliography and Sources](appendices/C-bibliography.md)
- D. [Checklists](appendices/D-checklists.md)

### Supporting material

- [Examples index](examples/README.md) · [Exercises index](exercises/README.md) · [Templates index](templates/README.md) · [Diagrams index](diagrams/README.md)

---

## Currency of information

The GTM tooling market changes monthly. Vendor features, prices, funding, regulations, email-provider rules and salary figures were checked in **October 2026** and are marked *(as of October 2026)*. Much of the public writing about GTM engineering comes from vendors who sell GTM tools. This book flags vendor-sourced claims as such, and prefers primary sources (regulators, mailbox providers, court filings, public job data) where they exist.

> **Not legal advice.** Chapter 16 describes laws on outreach and data protection to help you ask the right questions. Get advice from qualified counsel for your jurisdiction before running campaigns.
