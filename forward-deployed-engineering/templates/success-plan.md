# Success Plan: <Customer>: <Use case>

*Version: <n> · Date: <YYYY-MM-DD> · Status: draft / agreed / re-baselined · Engagement shape: bootcamp / pilot / production deployment / embedded programme*

## How to use this template

- **Purpose:** a short (two- to four-page) agreement, in plain language, on what the engagement will achieve, how success will be measured, what is in and out of scope, who does what and when. It is the spine of the engagement: weekly updates report against it, and the retrospective compares results with it.
- **When:** written in Phase 2 (Frame and scope) of the [engagement lifecycle](../chapters/04-engagement-lifecycle.md); re-signed whenever success criteria or scope change materially.
- **Owner:** the lead FDE drafts it; the customer's day-to-day owner co-writes it.
- **Sign-off:** the customer's executive sponsor and your engagement lead. Where a contract is needed, the [statement of work](statement-of-work.md) references this plan rather than duplicating it.
- **Exit criteria it serves:** measurable success criteria, a baseline (or a plan to measure one), named customer owners and access requests submitted.

Background reading: [Chapter 4 §4.11](../chapters/04-engagement-lifecycle.md) and [Chapter 6](../chapters/06-scoping.md).

*Keep it short. If the sponsor will not read it, it is not an agreement. The act of agreeing it matters as much as the document: it forces conversations about measurement, ownership and scope while they are cheap.*

---

## 1. Objective

*One or two sentences in the customer's language: the business outcome, for whom, by when.*

<e.g. "Cut the time Tailspin Toys' customer service team spends on order-status enquiries, so the team can absorb peak-season volume without temporary staff.">

**Why now:** <the business trigger: peak season, regulation, cost target, board commitment>

**Link to discovery and decomposition:** <link to canvas>

## 2. Success criteria

*Each criterion needs a baseline, a target, a measurement method that both sides accept, and a named owner. Include at least one business outcome, one quality measure and one adoption measure. Distinguish criteria that decide go / no-go from those that are merely tracked.*

| # | Criterion | Type (outcome / quality / adoption / operational) | Baseline (value, source, date) | Target | Measurement method | Measured when | Owner (customer) | Go / no-go? |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | Yes / no |
| 2 | | | | | | | | |
| 3 | | | | | | | | |
| 4 | | | | | | | | |

**Example (filled):**

| # | Criterion | Type | Baseline | Target | Measurement method | When | Owner | Go / no-go? |
|---|---|---|---|---|---|---|---|---|
| 1 | Share of order-status enquiries resolved without an agent | Outcome | 0% (all handled by agents), contact-centre report, Aug–Sep 2026 | ≥ 40% | Contact-centre platform tags, weekly | Weeks 6–8 | Head of Customer Service, Tailspin Toys | Yes |
| 2 | Answer accuracy on evaluation set (300 real enquiries) | Quality | n/a (new) | ≥ 97% correct, 0 critical errors | Blind review by two senior agents | Weeks 4 and 8 | QA Lead | Yes |
| 3 | Customer satisfaction (CSAT) on automated contacts | Outcome | 4.1 / 5 (agent-handled) | ≥ 4.0 / 5 | Post-contact survey | Weekly | CX Manager | No (tracked) |

*If no baseline exists, write "to be measured by <date> using <method>" and make measuring it a week-1 milestone.*

## 3. Scope

| In scope | Out of scope | Later (candidate for next phase) |
|---|---|---|
| | | |
| | | |
| | | |

*"Out" and "later" are as important as "in". When a new request arrives, capture it, assess its impact, then decide with the sponsor: swap it for something in scope, add it with more time or money, or put it on the later list. Record the decision in the change log (§9) and, if there is one, a change order under the [SOW](statement-of-work.md).*

## 4. Milestones

| Week / date | Milestone | Evidence it is done | Owner |
|---|---|---|---|
| 1 | Kick-off; access requests submitted; baseline confirmed | | |
| 2 | First end-to-end slice on real data shown to users | | |
| <n> | Evaluation set built and first results reviewed | | |
| <n> | Pilot users live | | |
| <n> | Success-criteria review and go / no-go decision for production | | |

## 5. Roles and responsibilities (RACI)

*R = responsible (does the work), A = accountable (one per row; decides), C = consulted, I = informed.*

| Activity | Customer sponsor | Customer day-to-day owner | Customer SMEs | Customer IT / data | Customer security | FDE lead | FDE team | Account executive |
|---|---|---|---|---|---|---|---|---|
| Agree success criteria | A | R | C | I | I | R | I | C |
| Provide data and system access | I | A | I | R | C | C | I | I |
| Build and evaluate solution | I | C | C | C | I | A | R | I |
| Security and risk approval | I | C | I | C | A/R | R | C | I |
| User testing and feedback | I | A | R | I | I | R | R | I |
| Go / no-go decision | A | R | C | C | C | R | I | C |

**Named people:**

| Role | Name | Organisation | Contact | Time commitment |
|---|---|---|---|---|
| Executive sponsor | | | | <e.g. 30 min fortnightly> |
| Day-to-day owner | | | | <e.g. 4 h/week> |
| Subject-matter experts | | | | |
| IT / data contact | | | | |
| Security contact | | | | |
| FDE lead | | | | |
| FDE team | | | | |
| Account executive | | | | |

## 6. Dependencies and access

*Access (accounts, VPN, data permissions, environments, approvals) is usually the critical path. Track each item like a deliverable and agree a plan B.*

| # | Dependency / access item | Needed for | Needed by | Requested on | Customer owner | Status | Plan B if late |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | Not requested / requested / granted / blocked | |
| 2 | | | | | | | |
| 3 | | | | | | | |

## 7. Risks

| # | Risk | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation | Owner | Trigger to escalate |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |

*Common risks: no data access after two weeks; sponsor disengages; users don't come to demos; scope grows; success criteria shift; pilot succeeds but no production budget or owner ([Chapter 4 §4.12](../chapters/04-engagement-lifecycle.md)).*

## 8. Cadence and communication

| Forum | Frequency | Attendees | Purpose | Owner |
|---|---|---|---|---|
| Working session | Weekly (e.g. Monday) | Day-to-day owner, FDE team | Plan the week; unblock dependencies | FDE lead |
| Demo to users | Weekly (e.g. Thursday) | Pilot users, SMEs | Show working software; collect feedback | FDE team |
| Written update | Weekly (Friday) | Sponsor, owner, stakeholders | Status against this plan ([template](weekly-update.md)) | FDE lead |
| Sponsor check-in | Fortnightly | Sponsor, FDE lead, account executive | Decisions, escalations, direction | FDE lead |
| Go / no-go review | At end of phase | Sponsor and decision-makers | Decide on production | Sponsor |

**Escalation path:** <FDE lead> → <customer day-to-day owner> → <customer sponsor> (and in parallel <your engagement manager>). Escalate any blocker older than <n> working days.

## 9. Sign-off

*By signing, both parties agree the objective, success criteria and scope above. Changes are made by issuing a new version with a change log.*

| Name | Role | Organisation | Signature / approval | Date |
|---|---|---|---|---|
| | Executive sponsor | <Customer> | | |
| | Day-to-day owner | <Customer> | | |
| | Engagement lead | <Your company> | | |

### Change log

| Version | Date | Change | Agreed by |
|---|---|---|---|
| 1.0 | | Initial agreement | |
