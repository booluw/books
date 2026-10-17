# Field Report: <Short problem title>

*ID: FR-<nnn> · Date: <YYYY-MM-DD> · Author: <FDE name> · Customer: <name> · Product area: <area> · Status: new / triaged / accepted / scheduled / shipped / declined*

## How to use this template

- **Purpose:** carry what you learned in the field back to the product team in a form they can act on. A field report describes a **problem** customers have, with evidence and quantified impact, not just a requested feature. It is the main instrument of the feedback loop from field to product.
- **When:** any time you hit a product gap, build a workaround, or see the same need again; especially during Phase 3 (Prove value) and Phase 7 (Expand and feed back) of the [engagement lifecycle](../chapters/04-engagement-lifecycle.md). Write it within a week, while the evidence is fresh.
- **Owner:** the FDE who saw the problem writes it; the product manager for the area owns triage and the decision.
- **Sign-off:** none from the customer (this is an internal document). The product manager records a decision and reason; FDE leadership reviews open reports regularly.
- **Rule of three:** when the same need appears at three customers, it should become a product feature rather than another custom build. Track every report against this rule (§9). The book's [feedback tracker example](../examples/feedback-tracker/) shows one way to do it.

Background reading: [Chapter 16](../chapters/16-field-to-product.md) and [Chapter 8 §8.6](../chapters/08-communication.md).

*Specific, evidenced and quantified reports get acted on; vague ones ("customer X wants better search") do not. Remove anything the customer has not agreed may be shared internally, and never paste customer personal data into the report.*

---

## 1. Summary

*Two or three sentences: who has the problem, what it costs them, and what you propose.*

<…>

## 2. Customer

| Item | Entry |
|---|---|
| Customer | |
| Segment / industry / region | |
| Annual recurring revenue (ARR) | |
| Renewal date | |
| Expansion opportunity linked to this problem | |
| Engagement and phase | |
| Customer contacts who can be interviewed by product | |

## 3. Context

*What were the users trying to do, in which workflow, with which systems? Keep it to what the product team needs to understand the problem.*

<…>

## 4. Problem

*Describe the problem in user terms. Separate the problem from any solution the customer asked for.*

- **Problem:** <…>
- **Customer's requested solution (if any):** <…>
- **Why the current product does not solve it:** <missing capability / limit / bug / usability / documentation>

## 5. Current workaround

| Item | Entry |
|---|---|
| What we or the customer did instead | |
| Where it lives (custom code, configuration, manual process) | |
| Effort to build | <FDE days> |
| Ongoing cost / fragility | |
| Who owns the workaround now | |

*A workaround is evidence of real need, and also a liability. Make sure it has an owner (no orphan code).*

## 6. Frequency and severity

| Item | Entry |
|---|---|
| How often users hit it | <per day / week; number of users> |
| Severity | Blocker (deal or go-live at risk) / major (significant workaround) / minor (inconvenience) |
| Impact on the customer | <time, money, risk, adoption> |
| Impact on us | <deal at risk, delayed go-live, FDE time, support load> |

## 7. Revenue affected

| Item | Value | Source / confidence |
|---|---|---|
| ARR at this customer affected | | |
| Pipeline (open opportunities) affected | | |
| Expansion blocked or enabled | | |

*Ask the account executive to confirm figures. State whether the revenue is at risk (churn, lost deal) or upside (expansion).*

## 8. Evidence

| Type | Description | Link |
|---|---|---|
| User quotes | | |
| Screenshots / recordings (customer-approved) | | |
| Data (volumes, error rates, timings) | | |
| Workaround code / configuration | | |
| Support tickets | | |

## 9. Rule-of-three tracking

*Search existing field reports and support tickets before filing. If a matching report exists, add your customer to it instead of creating a new one.*

| # | Customer | ARR | Same need? (exact / similar) | Workaround in place | Reported by | Date | Link |
|---|---|---|---|---|---|---|---|
| 1 | <this customer> | | Exact | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |

**Count:** <n> of 3 · **Linked reports:** <FR-IDs>

## 10. Proposed generalisation

*How could the product solve this for all customers, not just this one? Think in terms of configuration, extension points and general capabilities rather than this customer's specifics ([Chapter 11](../chapters/11-configure-extend-change.md)).*

| Item | Entry |
|---|---|
| Proposed capability | |
| Configure, extend or change the product? | |
| What would be customer-specific vs general | |
| Could the field workaround be the starting point? | |
| Rough effort (product engineering) | |
| Risks / trade-offs | |
| Alternatives considered | |

## 11. Product decision

*Completed by the product manager.*

| Item | Entry |
|---|---|
| Decision | Accept / schedule / need more evidence / decline |
| Reason | |
| Target release / quarter | |
| Product owner | |
| Date | |
| Communicated back to FDE and account team | ☐ |

---

## Example (filled excerpt)

**FR-042: Retrieval ignores document-level permissions from the customer's document management system**

*Customer: Contoso (financial services) · Author: <FDE> · Status: triaged*

| Section | Entry |
|---|---|
| Summary | Contoso's compliance team cannot go live with the research assistant because retrieval does not respect per-document permissions held in their document management system. We built a nightly permission sync as a workaround; two other customers need the same thing. |
| Workaround | Custom sync job (6 FDE days) mapping document access-control lists to index metadata; filters at query time. Owned by Contoso's platform team after handover. |
| Severity | Blocker for go-live; production approval was conditional on it |
| ARR affected | Contoso £420k; expansion to two further divisions (~£600k) depends on it |
| Rule of three | 1. Contoso (exact) · 2. Woodgrove Bank (exact, FR-037) · 3. Fabrikam (similar: SharePoint permissions) → **3 of 3** |
| Proposed generalisation | A permission-aware retrieval connector framework: source connectors supply access-control lists; the index enforces them at query time. Contoso's sync job is a starting point. |
