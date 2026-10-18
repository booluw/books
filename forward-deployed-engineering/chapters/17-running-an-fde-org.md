# Chapter 17. Building and Running an FDE Organisation

> "An FDE team is a bet that your best engineers' time in the field is worth more than their time at the desk. Manage it like one."

## What you will learn

- When a company should build an FDE function, and how to start one.
- Team structures: pods, pairing engineers with strategists, industry alignment, and where FDEs report.
- How to hire, onboard and develop FDEs.
- Capacity planning and engagement allocation.
- Playbooks, knowledge management and quality control across engagements.
- How to measure the function, and how to avoid the common organisational failure modes.

This chapter is written for engineering leaders, founders and FDE managers. Individual FDEs will find it useful for understanding the forces that shape their work.

---

## 17.1 Should you build one?

Chapter 3 §3.5 gave the factors that favour forward deployment: large deals, complex integration, a new category, customers with limited engineering capacity, an early product, restricted environments and strategic accounts. If most of those apply, an FDE function is likely to pay off. If few do, a strong solutions engineering team, good documentation and partners may serve better.

Questions to answer before starting:

1. **What is the function for?** Winning deals (pre-sale), delivering deployments (post-sale), discovering product needs, or all three? The answer shapes hiring, metrics and reporting lines.
2. **How will it be paid for?** Bundled into licences, charged as services, or funded as a go-to-market investment (Chapter 3 §3.4)?
3. **How will it feed the product?** If there's no answer, you're building a consultancy (Chapter 16).
4. **What's the exit path for each engagement?** Handover to customer, partner or support (Chapter 15).

## 17.2 Starting small

Most FDE functions start with a few engineers on the most important customers, often founders or early engineers. Practical sequence:

1. **Start with two or three strong generalists** who are excellent engineers and comfortable with customers. Early FDE hires set the culture.
2. **Pick lighthouse customers** where success is achievable and visible.
3. **Write things down from day one:** engagement plans, field reports, retrospectives. These become the playbook.
4. **Define the handoffs** with sales (when FDEs engage), product (how field reports are handled) and support (how handover works).
5. **Measure from the start:** time to first value, deployment effort, expansion (§17.8).
6. **Scale only once the playbook works.** Hiring ahead of a repeatable motion multiplies chaos.

## 17.3 Team structures

### Pods

A **pod** is a small, cross-functional team assigned to one large customer or a few related ones. A typical pod:

| Role | Responsibility |
|---|---|
| **FDEs (1–4)** | Build, integrate, deploy |
| **Deployment strategist** (Palantir's "Echo") or engagement lead | Problem framing, stakeholder management, adoption, commercial context |
| **Product liaison** (part-time) | Field-to-product loop |
| **Account executive / customer success manager** | Commercial relationship, renewals |
| **Specialists on call** | Security, data platform, ML, design |

AWS described its 2026 FDE unit as pods of five or six engineers on roughly 45-day engagements (Chapter 2). Palantir pairs Deltas with Echoes. The common thread: engineering paired with someone who owns the business problem and the relationship.

### Alignment options

| Structure | How it works | Strengths | Weaknesses |
|---|---|---|---|
| **By customer** | Each FDE or pod owns specific accounts | Deep relationships and context | Uneven load; knowledge silos |
| **By industry** | Pods per vertical (finance, health, public sector) | Domain expertise; pattern recognition across customers | Harder to staff spikes |
| **By capability** | Teams for data, AI, integrations | Technical depth | Customers deal with several teams |
| **Pool** | Engineers assigned from a pool per engagement | Flexible | Weaker continuity; context lost |

Many organisations combine industry alignment (for pattern recognition and the feedback loop) with a flexible pool for peaks.

### Where FDEs report

| Reporting into | Pros | Risks |
|---|---|---|
| **Engineering** | Technical bar; product access; career parity with product engineers | Customer needs may be deprioritised |
| **Sales / go-to-market** | Close to revenue; responsive to deals | Pressure to be pre-sales support; technical bar slips |
| **Customer success / services** | Delivery focus | Drift towards billable services; distance from product |
| **A dedicated deployment organisation** | Clear mission; own leadership | Needs strong links to both product and sales |

Whatever the line, protect two things: **an engineering hiring bar** and **a direct channel to product**. Palantir's model held FDEs to the same technical bar as product engineers; that decision did more than any reporting line to keep the role an engineering one.

## 17.4 Hiring

### The profile

FDEs combine skills rarely found together (Chapter 1):

- **Strong engineering:** ships working software independently, across stacks.
- **Problem decomposition:** turns ambiguous problems into structured, buildable pieces.
- **Learning speed:** picks up new domains, systems and tools quickly.
- **Customer judgement:** communicates clearly, builds trust, handles pressure.
- **Ownership:** drives outcomes without close supervision.

Weaker signals include specific framework knowledge (learnable) and polished sales presence (not the job).

### Interview loop design

Typical loops combine (Chapter 19 describes them from the candidate's side):

| Stage | Tests |
|---|---|
| Coding | Practical engineering: clean, working code, often with data manipulation |
| Decomposition / case | Breaking a vague real-world problem into a model and plan |
| Learning | Picking up an unfamiliar concept, API or query language within the interview |
| System design / integration | Designing a deployment into a realistic enterprise environment |
| Customer simulation | Role-play: a sceptical stakeholder, a scope dispute, a failed demo |
| Values / behavioural | Ownership, judgement, ethics, resilience |
| Take-home or work sample (optional) | Building something end to end |

Calibrate interviewers, use structured rubrics, and include current FDEs on every loop.

### Sources

Strong FDE candidates often come from: start-up generalist engineers, consultants who code, solutions engineers who build, data engineers, former founders, technical people from the target industries (clinicians who code, ex-military engineers for defence work), and product engineers seeking variety.

## 17.5 Onboarding

New FDEs need product depth, playbook fluency and field experience. A common pattern:

1. **Product immersion (2–4 weeks):** build a realistic deployment on a sandbox customer; pass internal certification.
2. **Shadowing:** join a live engagement as a second FDE.
3. **Paired lead:** lead workstreams with a senior FDE reviewing.
4. **Independent lead** of a smaller engagement.

Anthropic's Claude Frontier Academy (Chapter 2), announced in October 2026, follows a similar shape for partner engineers: an intensive phase ending in a graded simulated deployment, then a 12-week residency leading a real use case.

## 17.6 Capacity and allocation

FDE time is the scarcest resource in a deployment-led company. Manage it explicitly:

- **Capacity model:** list FDEs, their current allocations (percentages per engagement), skills, clearances and locations. Update weekly.
- **Engagement intake:** a single process for requesting FDE time, with qualification criteria (Chapter 4 §4.2), so the loudest account executive doesn't win.
- **Prioritisation:** rank by expected value (deal size, expansion, strategic value), probability of success, and learning value for the product.
- **Allocation norms:** avoid splitting engineers across more than two engagements; context switching destroys productivity.
- **Exit discipline:** every engagement has a planned end and handover date. Track overdue exits.
- **Reserve capacity:** keep some slack (for example 10–15%) for escalations, productisation and training.

## 17.7 Playbooks and knowledge management

As the function grows, consistency matters. A **playbook** is the documented way the organisation runs engagements: phases, templates, checklists, examples and lessons. Contents typically mirror this book's Part II and III, specialised to your product and industries.

Keep it alive:

- **Retrospectives feed the playbook** (template: [`templates/engagement-retrospective.md`](../templates/engagement-retrospective.md)).
- **Assign owners** to playbook sections.
- **Reference architectures** for common deployment types, with code.
- **A searchable library** of past engagements: anonymised problem statements, solutions, results and lessons, with access controls respecting customer confidentiality.
- **Communities of practice:** regular internal sessions where FDEs share patterns and problems.

### Quality control

Engagements vary in quality with the individual FDE. Mechanisms to raise the floor:

- **Design reviews** by senior FDEs for significant architecture decisions.
- **Code review** across engagements, not just within them.
- **Readiness reviews** using a standard gate (Chapter 15).
- **Engagement health checks:** a periodic red-amber-green review of all engagements by FDE leadership, catching problems early (Chapter 4 §4.12).

## 17.8 Measuring the function

| Category | Metrics |
|---|---|
| **Customer outcomes** | Success criteria met; impact delivered (validated); customer satisfaction |
| **Speed** | Time to first value; time to production; engagement duration vs plan |
| **Commercial** | Pilot conversion rate; net revenue retention of FDE-deployed customers; revenue per FDE |
| **Efficiency** | FDE cost as % of revenue per customer over time; FDE-hours per deployment by segment |
| **Product loop** | Field reports filed and acted on; productisation rate; deployment time for the Nth customer (Chapter 16) |
| **Team health** | Utilisation; travel load; attrition; engagement survey; promotion rates vs product engineers |

Beware single metrics. Utilisation alone pushes towards billable busywork; revenue per FDE alone pushes towards only serving the biggest accounts; customer satisfaction alone pushes towards over-servicing.

## 17.9 Career paths and recognition

FDEs leave when they feel like second-class engineers or burn out (Chapter 18). Design for retention:

- **A defined levelling framework** parallel to product engineering, with expectations at each level (see Chapter 19 for a typical ladder).
- **Recognition for productisation**, not only customer heroics.
- **Movement paths:** into product engineering, product management, FDE leadership, solutions architecture, or customer-facing executive roles. Treat movement as success, not attrition; former FDEs on product teams strengthen the loop.
- **Sustainable pace** policies: travel limits, rotation off intense engagements, protected time between engagements.

## 17.10 Failure modes

| Failure | Symptoms | Remedy |
|---|---|---|
| **Consultancy drift** | Bespoke code per customer; FDE headcount grows with revenue | Productisation budget; rule of three; custom-code inventory (Chapters 11, 16) |
| **Pre-sales captivity** | FDEs spend all their time on demos and pilots that don't convert | Qualification; paid pilots; separate solutions engineering |
| **Permanent residents** | FDEs never leave accounts | Handover discipline; exit dates; customer-team enablement |
| **Second-class citizens** | Lower bar, lower pay, no product access | Shared hiring bar; levelling parity; shared code ownership |
| **Heroics culture** | Success depends on all-nighters | Pace policies; capacity planning; recognising boring reliability |
| **Product disconnect** | Field reports ignored | Product liaisons; field council; leadership commitment |
| **Inconsistent quality** | Some engagements excellent, others chaotic | Playbook; reviews; onboarding |

---

## Summary

- Build an FDE function when the business factors favour it, and decide upfront what it's for, how it's paid for, how it feeds the product and how engagements end.
- Start small with strong generalists and lighthouse customers; write the playbook as you go; scale once it works.
- Use pods that pair engineers with strategists; align by industry where possible; protect the engineering bar and the channel to product, wherever FDEs report.
- Hire for engineering, decomposition, learning speed, customer judgement and ownership; onboard through immersion, shadowing and paired leading.
- Manage capacity explicitly with intake, prioritisation, allocation norms, exit discipline and reserve.
- Keep playbooks alive through retrospectives; raise the quality floor with reviews and health checks.
- Measure outcomes, speed, commercial results, efficiency, the product loop and team health together, and design careers that keep FDEs.

## Exercises

See [`exercises/17-running-an-fde-org.md`](../exercises/17-running-an-fde-org.md).

## Further reading

- Palantir engineering blog, on Deltas, Echoes and team structure.
- Coverage of AWS's forward deployed engineering unit (June 2026) and Anthropic's Claude Frontier Academy (October 2026).
- Will Larson, *An Elegant Puzzle: Systems of Engineering Management* (2019).
- Camille Fournier, *The Manager's Path* (2017).
- Andy Grove, *High Output Management* (1983).
