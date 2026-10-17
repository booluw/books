# Statement of Work: <Engagement name>

*SOW number: <n> · Version: <n> · Date: <YYYY-MM-DD> · Under master agreement: <MSA / platform agreement reference and date>*

> **Not legal advice.** This template shows the structure and the questions a statement of work should answer for a forward deployed engagement. It is not a contract and does not replace review by your company's legal, commercial and finance teams, or by the customer's. Many enterprises insist on their own SOW format; map these sections onto it. Contract law, tax and procurement rules vary by country and sector.

## How to use this template

- **Purpose:** a **statement of work (SOW)** is the contractual document that describes a specific piece of paid work: what will be delivered, how it will be accepted, what it costs, and what happens if things change. It normally sits under a **master services agreement (MSA)** or platform licence, which holds the general legal terms (liability, confidentiality, governing law). The SOW holds the specifics of this engagement.
- **When:** Phase 2 (Frame and scope) of the [engagement lifecycle](../chapters/04-engagement-lifecycle.md), after the [success plan](success-plan.md) is agreed in principle. Not every engagement needs one: bundled FDE time often runs on the success plan alone ([Chapter 3 §3.4](../chapters/03-business.md)).
- **Owner:** the account executive or engagement manager owns the commercial document; the lead FDE owns the scope, deliverables, assumptions and acceptance criteria, which are the parts most likely to cause disputes.
- **Sign-off:** authorised signatories of both parties, after legal and commercial review. The customer's procurement team usually controls the process.

Background reading: [Chapter 6](../chapters/06-scoping.md).

*Write the SOW so that an engineer who joins in week 6, or a procurement manager in a dispute, can tell what was promised. Ambiguity is cheap to fix now and expensive later.*

---

## 1. Parties

| | Supplier | Customer |
|---|---|---|
| Legal entity name | <Your company Ltd> | <Customer legal entity> |
| Registered address | | |
| Company number | | |
| Commercial contact | | |
| Delivery lead | | |
| Address for notices | | |

## 2. Background

*Two or three paragraphs: the customer's business context, the problem, what discovery found, and why this work is being commissioned. Reference the discovery summary and success plan by version.*

<…>

## 3. Objectives

*The business outcomes the work aims to support. Be careful to distinguish outcomes the supplier **commits to deliver** (usually deliverables) from outcomes the work **aims to influence** (business metrics that also depend on the customer). Unless the commercial model is outcome-based, business metrics are usually objectives, not guarantees.*

1. <Objective>
2. <Objective>

Success criteria are set out in the success plan <version, date>, Appendix A.

## 4. Scope of work

*Describe the activities and the boundaries: systems, sites, user groups, data sources, environments, languages, volumes.*

| Area | In scope |
|---|---|
| Use case(s) | |
| Business units / sites / user groups | |
| Systems integrated (read / write) | |
| Data sources | |
| Environments (development, test, production) | |
| Volumes / scale assumed | |
| Phases covered | <e.g. prove value and productionise; not adoption at scale> |

## 5. Deliverables and acceptance criteria

*Each deliverable needs objective acceptance criteria, an acceptance method and a named approver. "Working chatbot" is not a deliverable; "assistant answering order-status enquiries in the production contact-centre platform, meeting the criteria below" is.*

| # | Deliverable | Description | Acceptance criteria | Acceptance method (test, demo, review) | Target date | Customer approver |
|---|---|---|---|---|---|---|
| D1 | | | | | | |
| D2 | | | | | | |
| D3 | | | | | | |

**Example (filled):**

| # | Deliverable | Description | Acceptance criteria | Method | Target date | Approver |
|---|---|---|---|---|---|---|
| D2 | Shipment exception classifier, Wide World Importers | Classifies inbound carrier exception messages into 12 agreed categories and routes them to the right queue | ≥ 92% accuracy on the agreed held-out evaluation set of 1,000 messages; p95 latency < 2 s; deployed to production environment with monitoring | Evaluation report reviewed jointly; production smoke test | 2026-12-11 | Head of Logistics Operations |

## 6. Out of scope

*List explicitly what is not included, especially things stakeholders have asked for. Each line here prevents an argument later.*

- <e.g. Integration with systems other than those listed in §4>
- <e.g. Data cleansing of source systems>
- <e.g. Training more than <n> users; translation; 24×7 support>
- <e.g. Changes to the core product roadmap (raised as field reports, not delivered under this SOW)>

## 7. Assumptions

*Assumptions are conditions the price and timeline depend on. If an assumption proves false, it is grounds for a change request (§10).*

| # | Assumption | Impact if false |
|---|---|---|
| A1 | Read access to <system> is granted within <n> working days of the start date | Timeline moves day for day |
| A2 | Data quality of <source> is sufficient for <purpose>; a profiling report in week 2 will confirm | Re-scope via change control |
| A3 | Supplier staff may work remotely except for <n> on-site days | |
| A4 | | |

## 8. Customer responsibilities

| # | Responsibility | Needed by | Customer owner |
|---|---|---|---|
| C1 | Name an executive sponsor and a day-to-day owner with <n> hours/week available | Start date | |
| C2 | Provide accounts, VPN, environments and data access per the access plan | | |
| C3 | Make subject-matter experts available for <n> hours/week | | |
| C4 | Complete security, privacy and risk reviews within <n> working days of receiving documents | | |
| C5 | Provide a baseline for success criteria, or support measuring one | | |
| C6 | Name the team that will receive the handover | | |

*Customer dependencies are the most common cause of delay. Tie them to dates so slippage is visible and attributable.*

## 9. Timeline

| Phase / milestone | Start | End | Deliverables | Dependency |
|---|---|---|---|---|
| Mobilisation and access | | | | C1, C2 |
| | | | | |
| | | | | |
| Handover and close | | | | C6 |

**Start date:** <date> · **End date:** <date> · **Key dates the customer must meet:** <…>

## 10. Change control

*Scope will change. The question is whether it changes in writing.*

1. Either party may raise a **change request** in writing, describing the change, the reason and the requester.
2. The supplier assesses impact on scope, deliverables, timeline, fees and risk within <n> working days and issues a change note.
3. The change takes effect only when the change note is signed by both parties' authorised representatives (<names / roles>).
4. Minor changes with no impact on fees or dates may be agreed by email between the delivery leads and recorded in the change log.
5. Work on a requested change does not start until approved, unless both delivery leads agree in writing to proceed at risk.

| CR # | Date raised | Description | Raised by | Impact (scope / time / fees) | Status | Approved by / date |
|---|---|---|---|---|---|---|
| | | | | | | |

## 11. Fees and commercial model

*Choose one model (or a combination) and delete the rest. The model shapes incentives and what "done" means; see [Chapter 3 §3.4](../chapters/03-business.md). Amounts exclude VAT or other sales taxes unless stated.*

### Option A: Fixed fee

| Item | Entry |
|---|---|
| Total fixed fee | <£ / $> |
| Payment milestones | <e.g. 30% on signature; 40% on acceptance of D2; 30% on acceptance of D4> |
| What the fee covers | The deliverables in §5 under the assumptions in §7 |

*Suits well-understood scope. The supplier carries the risk of overrun, so assumptions and out-of-scope lists must be precise.*

### Option B: Time and materials (T&M)

| Role | Day rate | Estimated days | Estimate |
|---|---|---|---|
| Forward deployed engineer | | | |
| Deployment strategist | | | |
| **Total estimate** | | | |

- Cap / not-to-exceed amount: <…> (further work needs a change note).
- Invoicing: monthly in arrears, with timesheets.
- Expenses: <policy, e.g. pre-approved travel at cost, per the customer's travel policy>.

*Suits uncertain scope. The customer carries overrun risk; a cap and regular burn reporting keep trust.*

### Option C: Paid pilot, credited against a subscription

| Item | Entry |
|---|---|
| Pilot fee | <£ / $> |
| Pilot duration | <n> weeks |
| Credit | <100% / x%> of the pilot fee credited against the first-year subscription if an order is signed by <date> |
| Conversion decision | Based on success criteria in the success plan, at a review on <date> |

*Filters unserious buyers and aligns both sides on a decision date. Beware the pressure to over-promise in a short window.*

### Option D: Outcome-based

| Item | Entry |
|---|---|
| Outcome metric | <e.g. enquiries resolved without an agent> |
| Definition and data source | <precise definition; whose system is the record> |
| Baseline | <value, period> |
| Fee mechanism | <e.g. £x per resolved enquiry; or base fee + bonus on reaching target> |
| Floor / cap | |
| Measurement and audit | <who measures, how often, dispute process> |
| Exclusions | <events outside the supplier's control, e.g. customer process changes> |

*Strong alignment, but measurement disputes are common. Agree the metric definition, data source and dispute process before signing.*

## 12. Intellectual property and ownership of custom code

*This is where forward deployed work most often goes wrong. FDEs write code inside the customer; who owns it, and can it become product? Agree this explicitly. Common positions are listed below; legal teams will draft the actual clause.*

| Item | Position (choose / edit) |
|---|---|
| Supplier's pre-existing IP and the platform | Remains the supplier's; customer receives a licence under the master agreement |
| Generic improvements, tools and know-how developed during the work | Owned by the supplier and may be incorporated into the product (so field work can become product) |
| Customer-specific code and configuration (e.g. integrations to the customer's systems) | <Owned by the customer / owned by the supplier and licensed to the customer> |
| Customer data, and outputs derived from it | Owned by the customer |
| Models trained or fine-tuned on customer data | <State explicitly: who owns them, whether the supplier may reuse them; usually no reuse without consent> |
| Source code escrow or repository access | <Where the custom code lives; whether the customer gets a copy at handover> |
| Open-source components | Used under their licences; list provided at handover |

## 13. Data handling

| Item | Entry |
|---|---|
| Data categories processed (including personal and special-category data) | |
| Roles under data protection law (controller / processor) | |
| Data processing agreement (DPA) reference | |
| Where data is stored and processed (regions) | |
| Third-party sub-processors (including model providers) | |
| Retention and deletion at end of engagement | |
| Security standards that apply | <customer policies; supplier certifications> |
| Security and AI risk review reference | <link to [review](security-and-ai-risk-review.md)> |

## 14. Acceptance

1. On completion of each deliverable, the supplier gives notice with evidence against the acceptance criteria.
2. The customer reviews within <n> working days and either accepts or lists, in writing, the specific criteria not met.
3. The supplier remedies listed non-conformities and resubmits; the review period restarts for the affected items only.
4. If the customer neither accepts nor rejects within the review period, or uses the deliverable in production, <the deliverable is deemed accepted / escalation applies>.
5. Final acceptance of the engagement includes acceptance of the [handover pack](handover-pack.md).

## 15. Termination

| Item | Entry |
|---|---|
| Termination for convenience | <Either party, on <n> days' written notice> |
| Termination for breach | <Per master agreement> |
| Fees on termination | <Fees for work done and accepted to date; non-cancellable expenses> |
| Handover on termination | <Supplier delivers work in progress, documentation and custom code per §12 within <n> days> |
| Data on termination | <Return / deletion per DPA, with written confirmation> |

## 16. Governance

| Forum | Frequency | Attendees |
|---|---|---|
| Steering (sponsor review) | | |
| Delivery check-in | | |
| Written status | Weekly ([template](weekly-update.md)) | |

## 17. Signatures

| | Supplier | Customer |
|---|---|---|
| Name | | |
| Title | | |
| Signature | | |
| Date | | |

### Appendices

- A. Success plan <version>
- B. Access and environment plan
- C. Rate card (if T&M)
- D. Data processing agreement (reference)
