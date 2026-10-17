# Weekly Update: <Customer>: <Engagement name>: Week <n> (<date range>)

*From: <FDE lead> · To: <sponsor, day-to-day owner, stakeholders> · Success plan: <link, version>*

## How to use this template

- **Purpose:** a short written status sent every week, so that everyone knows where the engagement stands against the success plan, what needs deciding, and what is blocked. Writing it forces clarity, and it creates a record that protects both sides when memories differ.
- **When:** every Friday from Phase 3 (Prove value) to Phase 6 (Hand over) of the [engagement lifecycle](../chapters/04-engagement-lifecycle.md); during discovery, a lighter version works too.
- **Owner:** the lead FDE writes it. Aim for 15–30 minutes of writing; if it takes longer, the engagement is too complicated or the template too long.
- **Sign-off:** none formally. The customer's day-to-day owner should see a draft before it goes to the sponsor if it contains bad news they have not heard; nobody should be surprised in writing.

Background reading: [Chapter 4 §4.11](../chapters/04-engagement-lifecycle.md) and [Chapter 8](../chapters/08-communication.md).

*Lead with the answer. Busy readers stop after the first three lines, so those lines must carry the status, the headline and any decision needed. Keep the whole update to one screen where possible.*

---

## Summary

**Status:** Green / Amber / Red *(choose one)*

| Area | RAG | One-line reason |
|---|---|---|
| Overall | | |
| Progress against milestones | | |
| Success criteria | | |
| Access and dependencies | | |
| Stakeholder engagement | | |

*RAG means red / amber / green. Define it once and use it consistently: **Green** = on track; **Amber** = at risk, recoverable within the team's control or with a small decision; **Red** = will miss a milestone or criterion without sponsor action. Do not stay "green" until the week before a miss.*

**Headline:** <one sentence: the most important thing that happened this week>

**Decision needed:** <the single most important decision or ask, with a date; or "none this week">

---

## Progress against success criteria

| # | Criterion | Baseline | Target | This week | Last week | Trend | Comment |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | ↑ / → / ↓ | |
| 2 | | | | | | | |
| 3 | | | | | | | |

*Use the success plan's criteria verbatim. If you cannot measure a criterion yet, say when you will.*

## Milestones

| Milestone | Planned date | Forecast date | Status |
|---|---|---|---|
| | | | Done / on track / at risk / late |

## Demoed this week

*Working software shown to users, not slides. Note who attended and what they said.*

- **What:** <feature / slice>
- **To whom:** <users, number>
- **Feedback:** <quotes; what changes as a result>
- **Recording / screenshots:** <link>

## Next week

1. <Planned outcome, not activity: "pilot users process claims with the coverage panel", not "work on panel">
2. <…>
3. <…>

## Decisions needed

| # | Decision | Options | Our recommendation | Who decides | Needed by | Impact if late |
|---|---|---|---|---|---|---|
| 1 | | | | | | |

## Risks and blockers

| # | Risk / blocker | Type (risk / blocker) | Impact | Owner | Action and date | Age (days) | Escalated to |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |

*Every blocker needs a named owner on the customer side where the customer holds the key. Show age so long-running blockers are visible.*

## Access tracker

*Access is usually the critical path. Keep this table until every item is granted.*

| Item | Needed for | Requested | Customer owner | Status | Days waiting | Next step |
|---|---|---|---|---|---|---|
| | | | | Requested / granted / blocked | | |

## Metrics

| Metric | This week | Last week | Notes |
|---|---|---|---|
| Active users (pilot) | | | |
| Cases / transactions processed | | | |
| Evaluation score (if AI) | | | |
| Errors / incidents | | | |
| Cost (compute, model usage) | | | |
| FDE effort this week (days) | | | |

## Field notes for the product team (internal; remove before sending to the customer)

- <Product gaps, workarounds, feature requests; raise a [field report](field-report.md) for anything significant>

---

## Example (filled, summary section only)

**Status:** Amber

| Area | RAG | One-line reason |
|---|---|---|
| Overall | Amber | Build on track; production data access 9 days late |
| Progress against milestones | Green | Classifier slice demoed to 8 users on Thursday |
| Success criteria | Green | Accuracy 91.4% on held-out set (target 92%) |
| Access and dependencies | Red | Read access to carrier message archive still pending security approval |
| Stakeholder engagement | Green | Operations team attending every demo |

**Headline:** Contoso Logistics' operations team classified 640 real carrier exceptions with the new tool this week; reviewers agreed with 91.4% of its categories.

**Decision needed:** Approve the restricted 90-day extract of the carrier archive by Wednesday 18 November, so we can keep the week-6 production date. Owner: Head of IT Security.
