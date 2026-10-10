# The Integration Design Engineer

### A Field Guide to Connecting Systems: APIs, Events, Data, Platforms, and the Career Built Around Them

*First edition, October 2026*

---

## About this book

Nearly every organisation runs dozens to hundreds of software systems: a CRM, an ERP, a billing platform, a data warehouse, an identity provider, a ticketing tool, partner portals, mobile apps, and now AI agents. None of these systems is useful alone. Orders must reach the warehouse, invoices must reach accounting, a new hire in HR must get a laptop and a login, and a payment in a bank must show up in the ledger. The work of making systems exchange data and trigger each other reliably, securely and in a way the organisation can maintain is **integration**. The person who designs that work is the **Integration Design Engineer**.

This book explains the role from first principles. It assumes you can program and know roughly what an HTTP request or a database is. It does not assume you have done integration work. Each chapter defines its terms, explains why a technique exists before showing how to use it, and ends with a summary and exercises.

### Who this book is for

- Software engineers moving into integration, platform or API work.
- Analysts, administrators and consultants (Salesforce, SAP, ServiceNow and similar) who want an engineering foundation.
- Engineering students choosing a specialisation.
- Engineering managers and architects who hire or lead integration teams.

### A note on the job title

"Integration Design Engineer" is used inconsistently across the industry. In aerospace, defence and electronics, postings with that exact title often mean *physical* integration: CAD, packaging and harness routing. **This book covers the software meaning**, which appears under titles such as Integration Engineer, Integration Developer, Integrations Engineer, API Engineer, Integration Architect, Solutions/Implementation Engineer and iPaaS Developer. [Chapter 1](chapters/01-the-role.md) maps the title landscape so you can read any job posting and know which role it means.

---

## How to read this book

| If you are… | Read |
|---|---|
| New to the field | Part I and Part II in order, then skim the rest |
| A developer who already builds APIs | Chapters 1, 5, 7, 8, 14 and 17 first |
| Preparing for interviews | Chapters 1, 8, 14 and 19, plus the exercises |
| Choosing a platform | Chapters 11 and 17 |
| Working in a regulated industry | Chapters 10 and 13 |

Folders in this book:

- [`chapters/`](chapters/): the main text.
- [`diagrams/`](diagrams/): Mermaid diagrams (they render on GitHub and in most Markdown viewers).
- [`examples/`](examples/): runnable code, written in standard-library Python where possible, plus OpenAPI and AsyncAPI documents.
- [`exercises/`](exercises/): exercises per chapter with worked solutions.
- [`templates/`](templates/): design-document, mapping-specification, runbook and review-checklist templates you can copy into real work.
- [`appendices/`](appendices/): glossary, bibliography, standards reference and checklists.

---

## Table of contents

### Part I: The Role

1. [What an Integration Design Engineer Is](chapters/01-the-role.md)
2. [A Short History of Integration](chapters/02-history.md)

### Part II: Foundations

3. [Networks and HTTP for Integrators](chapters/03-networks-and-http.md)
4. [Data Formats, Schemas and Transformation](chapters/04-data-formats-and-transformation.md)
5. [Integration Styles and Enterprise Integration Patterns](chapters/05-integration-styles-and-patterns.md)

### Part III: Designing Interfaces

6. [Designing Synchronous APIs: REST, GraphQL, gRPC and SOAP](chapters/06-api-design.md)
7. [Asynchronous and Event-Driven Integration](chapters/07-async-and-events.md)
8. [Reliability: Designing for Failure](chapters/08-reliability.md)
9. [Data Integration: ETL, ELT, CDC and Streaming](chapters/09-data-integration.md)
10. [Security, Identity and Compliance](chapters/10-security.md)

### Part IV: Platforms and Ecosystems

11. [Integration Platforms: ESB, iPaaS, API Management and Embedded Integration](chapters/11-platforms.md)
12. [Integrating Enterprise Applications](chapters/12-enterprise-applications.md)
13. [Industry Standards: EDI, Healthcare, Finance and More](chapters/13-industry-standards.md)

### Part V: Practice

14. [The Integration Design Process](chapters/14-design-process.md)
15. [Testing Integrations](chapters/15-testing.md)
16. [Deploying, Observing and Operating Integrations](chapters/16-operations.md)
17. [Integration Architecture and Governance](chapters/17-architecture-and-governance.md)
18. [AI Agents and the Future of Integration](chapters/18-ai-and-the-future.md)

### Part VI: The Career

19. [Becoming an Integration Design Engineer](chapters/19-career.md)
20. [Case Studies](chapters/20-case-studies.md)

### Appendices

- A. [Glossary](appendices/A-glossary.md)
- B. [Bibliography and Further Reading](appendices/B-bibliography.md)
- C. [Standards and Specifications Reference](appendices/C-standards-reference.md)
- D. [Checklists](appendices/D-checklists.md)

### Supporting material

- [Examples index](examples/README.md)
- [Exercises index](exercises/README.md)
- [Diagrams index](diagrams/README.md)
- [Templates index](templates/README.md)

---

## Currency of information

Integration changes quickly. Version numbers, standards status, vendor ownership, market reports and salary figures were checked in **October 2026** and are dated in the text. Facts that are likely to change are marked *(as of October 2026)*. Always confirm them against the primary source listed in [Appendix B](appendices/B-bibliography.md) before you rely on them.
