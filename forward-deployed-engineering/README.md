# Forward Deployed Engineering

### Shipping Software Inside the Customer: Discovery, Delivery, Data, AI Deployment and the Feedback Loop to Product

*First edition, October 2026*

---

## About this book

Most software engineers never meet the people who use their code. A **forward deployed engineer (FDE)** does the opposite: they work inside a customer's organisation, sometimes literally on site, to make a product solve that customer's hardest problem, then carry what they learned back to the product team.

The role was pioneered at Palantir in the late 2000s, where FDEs were called **"Deltas"**. For a decade it was a Palantir curiosity. Then generative AI arrived, and enterprises discovered that powerful models do not deploy themselves. Messy data, legacy systems, security reviews, unclear success criteria and organisational politics stood between the model and the value. In 2025–2026 the FDE became one of the most sought-after roles in technology:

- OpenAI launched a **Deployment Company** (May 2026).
- AWS committed **$1 billion** to a forward deployed engineering unit (June 2026).
- Anthropic committed **$100 million** to train 10,000 "Frontier Deployed Engineers" through its Claude Frontier Academy (October 2026).
- Consultancies, AI start-ups and software vendors of every size began hiring FDEs.

This book explains the role from first principles. It assumes you can program. It does **not** assume you have worked with customers, written a statement of work, navigated a hospital's security review, or deployed an AI system into a bank. Every concept is defined on first use, and every technique is explained by the problem it solves.

### Who this book is for

- Software engineers considering a move into customer-facing engineering.
- Solutions engineers, consultants and implementation specialists who want to build more.
- Engineering and product leaders designing or scaling an FDE function.
- Founders deciding whether to use forward deployment as a go-to-market strategy.

### Companion books

FDEs integrate systems and often drive commercial outcomes. Two companion books in this repository go deeper on those areas:

- [*The Integration Design Engineer*](../integration-design-engineer/): APIs, events, reliability, security and operations.
- [*GTM Engineering*](../gtm-engineering/): how B2B companies sell, and the systems behind it.

---

## How to read this book

| If you are… | Read |
|---|---|
| New to customer-facing engineering | Parts I and II in order, then Part III |
| An experienced engineer moving into an FDE role | Chapters 1, 4–8, then Part III |
| Deploying AI systems for customers | Chapters 10–15 |
| Building or managing an FDE team | Chapters 3, 16, 17 and 18 |
| Preparing for FDE interviews | Chapters 1, 5, 19 and the exercises |

Folders:

- [`chapters/`](chapters/): the main text.
- [`examples/`](examples/): runnable, tested standard-library Python:
  - data profiling and record linkage;
  - an LLM evaluation harness;
  - permission-aware retrieval;
  - agent tool guardrails;
  - an impact calculator;
  - a deployment-readiness gate;
  - a field-feedback tracker.
- [`exercises/`](exercises/): exercises with solutions for every chapter.
- [`templates/`](templates/):
  - discovery guide and problem decomposition canvas;
  - success plan and statement of work;
  - weekly update and executive brief;
  - security and AI risk review;
  - handover pack and field report.
- [`diagrams/`](diagrams/): Mermaid diagrams.
- [`appendices/`](appendices/): glossary, bibliography, checklists and an interview question bank.

---

## Table of contents

### Part I: The Role

1. [What a Forward Deployed Engineer Is](chapters/01-the-role.md)
2. [From Palantir's Deltas to the AI Deployment Boom](chapters/02-history.md)
3. [The Business of Forward Deployment](chapters/03-business.md)

### Part II: Working with Customers

4. [The Engagement Lifecycle](chapters/04-engagement-lifecycle.md)
5. [Discovery and Problem Decomposition](chapters/05-discovery-and-decomposition.md)
6. [Scoping, Success Criteria and Statements of Work](chapters/06-scoping.md)
7. [Stakeholders, Politics and Trust](chapters/07-stakeholders.md)
8. [Communication: Demos, Writing and Hard Conversations](chapters/08-communication.md)

### Part III: Technical Craft

9. [The FDE Technical Toolkit](chapters/09-toolkit.md)
10. [Enterprise Data in the Wild](chapters/10-enterprise-data.md)
11. [Configure, Extend or Change the Product](chapters/11-configure-extend-change.md)
12. [Deploying LLM and Agent Systems in the Enterprise](chapters/12-ai-deployment.md)
13. [Evaluation and Measuring Business Impact](chapters/13-evaluation-and-impact.md)
14. [Security, Compliance and Restricted Environments](chapters/14-security-and-restricted-environments.md)
15. [Production Readiness, Operations and Handover](chapters/15-production-and-handover.md)

### Part IV: The Feedback Loop and the Organisation

16. [Turning Field Work into Product](chapters/16-field-to-product.md)
17. [Building and Running an FDE Organisation](chapters/17-running-an-fde-org.md)

### Part V: The Career

18. [Life as an FDE: Pace, Travel, Ethics and Sustainability](chapters/18-life-as-an-fde.md)
19. [Becoming a Forward Deployed Engineer](chapters/19-career.md)
20. [Case Studies](chapters/20-case-studies.md)

### Appendices

- A. [Glossary](appendices/A-glossary.md)
- B. [Bibliography and Sources](appendices/B-bibliography.md)
- C. [Checklists](appendices/C-checklists.md)
- D. [Interview Question Bank](appendices/D-interview-questions.md)

### Supporting material

- [Examples](examples/README.md) · [Exercises](exercises/README.md) · [Templates](templates/README.md) · [Diagrams](diagrams/README.md)

---

## Currency of information

The FDE market moved fast in 2025–2026. Hiring numbers, company programmes, salaries and product names were checked in **October 2026** and are marked *(as of October 2026)*. Much public writing about FDEs comes from recruiters, training providers and vendors; this book flags such sources and prefers primary sources (company announcements, filings, major news outlets) where available.
