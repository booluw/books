# Exercises: Chapter 6, [Scoping, Success Criteria and Statements of Work](../chapters/06-scoping.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional and all figures illustrative.

## Questions

1. **Concept.** Rewrite each weak success criterion so it is specific, measurable, owned, baselined and time-bound. State what was wrong with the original.
   - (a) "Deploy an AI knowledge assistant for the service desk."
   - (b) "Improve forecast accuracy."
   - (c) "The extraction model is 95% accurate."
   - (d) "Users like the new tool."

2. **Scenario.** Woodgrove Bank wants to speed up know-your-customer (KYC) document review for new business accounts. Analysts currently take a median of 3.5 days from application to KYC decision; 14 analysts work in the Manchester team. Write one success criterion at each of the three levels in §6.3 (business outcome, adoption, system quality), and name a plausible customer owner for each. Then identify which are leading and which are lagging indicators.

3. **Scenario.** At Northwind Traders nobody records how long purchase-order exceptions take: the team works from a shared inbox, and the manager's estimate is "about half an hour each". Propose two ways of establishing a baseline before the pilot, and explain which you would choose and why a control group might be better still.

4. **Scenario.** Contoso Insurance wants an AI assistant for its commercial underwriters. In the scoping meeting you hear: the London team (20 underwriters) is the pilot; the Edinburgh team "might join"; the assistant should answer questions from policy wordings; marine policies are "complicated"; someone asks whether it could write quotes back into the rating engine; the documents are in English but some broker submissions are in French. Write the in, out and later lists.

5. **Scenario.** Review this SOW extract for a ten-week fixed-fee pilot and list at least six problems you would raise as the delivering FDE, with a fix for each.

   > *Objectives:* Deliver an AI solution for Fabrikam's procurement team.
   > *Deliverables:* A production-ready AI assistant integrated with Fabrikam's ERP.
   > *Timeline:* Ten weeks from signature.
   > *Customer responsibilities:* Fabrikam will provide reasonable assistance.
   > *Acceptance:* Fabrikam's procurement director will confirm acceptance.
   > *Intellectual property:* All work product created under this SOW is owned by Fabrikam.

6. **Calculation.** A vendor prices a ten-week pilot for Wide World Importers at a $100,000 fixed fee, credited against the subscription if the customer signs. The plan uses two FDEs full time. An FDE costs $350,000 a year fully loaded, and there are 250 working days a year. (a) What is the FDE cost of the pilot as planned? (b) What is it if the pilot needs the two weeks' named contingency, and what if it overruns three weeks beyond plan? (c) Under time and materials at a rate of $2,000 per FDE-day, what would the customer pay in the planned and three-week-overrun cases? (d) Who carries the overrun risk in each model, and why might the vendor accept a loss on the fixed fee?

7. **Scenario.** Week 6 of the Contoso pilot. The head of underwriting, impressed by a demo, asks: "Can you add marine policies and connect it to the rating engine before the board meeting in three weeks?" Write your reply using the change process and phrases in §6.9.

8. **Hands-on.** Write a success plan for the Woodgrove Bank KYC pilot in question 2 using [`../templates/success-plan.md`](../templates/success-plan.md), including the dependency table and a RACI. Then fill in the key sections of [`../templates/statement-of-work.md`](../templates/statement-of-work.md) (objectives, deliverables with acceptance criteria, assumptions, customer responsibilities, change control, IP) so that it is consistent with the success plan. Finally, add three bullet points describing how the pilot will avoid pilot purgatory.

## Solutions

1. - (a) An **output, not an outcome**. Better: "Median time to resolve password and access tickets falls from 40 minutes to under 15 for the Level-1 service desk (22 agents) by week 10, measured from ServiceNow timestamps; owner: service-desk manager."
   - (b) **No baseline, number, scope or owner.** Better: "Weekly SKU-level forecast error (MAPE) for the top 500 SKUs falls from 31% (Q2 baseline) to 24% or below over weeks 6–12, computed by the demand-planning team's existing report; owner: head of demand planning."
   - (c) **Accuracy of what, on which data, judged by whom?** Better: "≥ 95% of extracted invoice totals and supplier VAT numbers match the ledger on a 500-invoice test set sampled from Q3, labelled by two AP clerks; owner: AP manager; measured at week 6."
   - (d) **Unmeasured and unowned.** Better: "Average rating ≥ 4 out of 5 from at least 20 pilot users in the week-6 survey, and ≥ 75% of pilot users still using the tool weekly in week 8; owner: operations team lead."

2. | Level | Criterion | Owner |
   |---|---|---|
   | **Business outcome** | Median time from application to KYC decision for the Manchester team falls from 3.5 days (baseline from case-system timestamps, last quarter) to 2.0 days within 10 weeks of go-live | Head of KYC operations |
   | **Adoption** | ≥ 12 of the 14 analysts use the document-review panel on ≥ 75% of eligible applications by week 6 | Manchester team manager |
   | **System quality** | ≥ 95% of extracted identity and ownership fields correct on a 300-application evaluation set labelled by two senior analysts; 100% of flagged discrepancies link to the source page; zero cases where a sanctions or PEP hit is suppressed | Financial-crime compliance lead |

   **Lagging:** the business outcome (decision time). **Leading:** adoption and system quality; they move first and explain why the lagging metric did or did not move. In a ten-week pilot, agree in advance that meeting the leading criteria plus a measured trend in decision time counts as success, with the full lagging measurement after a further period.

3. Options, from §6.4:
   - **Time-and-motion sampling:** have the team log start and end times for every exception for two weeks (a simple form or a column in the shared inbox), or observe a sample. Objective and fast.
   - **Reconstruct from system data:** use email timestamps in the shared inbox (received, first reply, closed) as a proxy, possibly with a sample checked against the logs. Free, historical, but noisier.

   **Choose sampling for two weeks**, cross-checked with the inbox timestamps: it is the most defensible, and the manager's "about half an hour" is an estimate, the weakest form of baseline. A two-week measurement at the start of a ten-week engagement is a good investment.

   **A control group might be better** because a before-and-after comparison is vulnerable to anything else that changes during the pilot (seasonal order volumes, a new supplier, staff changes). If half the team (or one region) keeps the old process over the same period, the comparison controls for those changes (Chapter 13 §13.8).

4. | In scope | Out of scope | Later |
   |---|---|---|
   | London commercial underwriting team, 20 users | Edinburgh team | Edinburgh rollout (phase 2 candidate) |
   | Question answering from policy wordings, with citations | Marine policies | Marine policies, once wording structure is analysed |
   | Read-only access to policy documents | Any write-back to the rating engine; producing quotes | Rating-engine integration, once audit and approval design is agreed |
   | English-language documents | French-language broker submissions | French-language support |

   "Might join" and "complicated" are classic sources of silent scope growth: pinning them to *out* now, and *later* for the future, prevents them arriving as expectations in week 6.

5. | Problem | Fix |
   |---|---|
   | **Objective is an activity, not an outcome**, and doesn't match any success plan | State outcomes consistent with the success plan ("reduce purchase-order exception handling time from X to Y for the pilot team") |
   | **"Production-ready" in a ten-week pilot**, undefined | Define the deliverable: a pilot system on agreed data, plus a production plan; "production-ready" only if defined as passing named checklists and reviews |
   | **"Integrated with Fabrikam's ERP"** is unbounded | Specify read-only access to named ERP objects through a named interface |
   | **Timeline ignores approvals and access** | Add assumptions: data access by week 2, security review complete by week 6, otherwise the timeline moves day for day |
   | **"Reasonable assistance"** is unenforceable | Name customer roles and hours (procurement SME 4 h/week; ERP administrator; security contact) and decision turnaround (5 working days) |
   | **Acceptance has no criteria and no deadline** | Acceptance against the success criteria, by a named role, with deemed acceptance after 10 working days of silence |
   | **No change control** in a fixed-fee contract | Add a change-request process: written request, impact estimate, sponsor approval, change order |
   | **IP clause gives Fabrikam everything**, blocking the field-to-product loop | Fabrikam owns its data and Fabrikam-specific configuration; the vendor owns its platform and generic tools, templates and improvements, and may reuse them (legal to advise) |
   | **No out-of-scope list or data-handling terms** | Add both |

6. Cost per FDE-day = $350,000 ÷ 250 = **$1,400**.

   (a) Planned: 2 FDEs × 10 weeks × 5 days = 100 FDE-days × $1,400 = **$140,000**. The fixed fee is $100,000, so the pilot already costs the vendor **$40,000** more than it earns.

   (b) With two weeks' contingency used: 2 × 12 × 5 = 120 days × $1,400 = **$168,000** (shortfall $68,000). With a three-week overrun beyond plan: 2 × 13 × 5 = 130 days × $1,400 = **$182,000** (shortfall $82,000).

   (c) T&M at $2,000 a day: planned 100 × $2,000 = **$200,000**; three-week overrun 130 × $2,000 = **$260,000**.

   (d) **Fixed fee: the vendor carries the overrun risk** (the customer pays $100,000 whatever happens). **T&M: the customer carries it** (they pay $60,000 more for the overrun). The vendor accepts a loss on a fixed-fee pilot because the pilot is a sales investment: the fee filters out unserious buyers and is credited against a subscription that may be worth far more. The loss is acceptable only with tight scope, strong change control and a pre-agreed production decision; otherwise it is simply an unprofitable consultancy project.

7. Model reply: "I'm really glad the demo landed, and both are good candidates. To protect the board-meeting result, here's what I suggest. Marine wordings are structured differently and would need their own evaluation set, so adding them in three weeks would put the current criteria at risk; I'd like to put marine on the later list for the phase review. Writing to the rating engine changes the security scope and the success criteria, so that needs a conversation with [sponsor] and the security team before we commit. For the board, I can prepare a slide showing the pilot results so far plus a scoped proposal for marine and the rating engine as phase 2. Shall I put that on the agenda for Thursday's check-in?"

   This captures the request, assesses the impact, offers a decision to the sponsor and records it, as §6.9 requires, without saying a flat no.

8. Check your success plan for: all three criterion levels, each with baseline, target, measurement method, owner and date; in/out/later scope; dated milestones with exit criteria; a RACI table; a dependency table with owners and lead times; risks; cadence; and sign-off names.

   Check your SOW for consistency with the plan (no deliverable in the SOW that the plan doesn't support, and vice versa); deliverables with acceptance criteria; dated assumptions about access and staff time; named customer responsibilities; a change-control clause; deemed acceptance; and an IP clause that preserves the vendor's right to reuse generic work.

   Anti-purgatory bullets, for example: "If the three criteria are met by week 10, the next step is a production order for the Manchester and Leeds teams, decided by the COO from the 2027 operations budget"; "The production run team (KYC platform and security) attend fortnightly reviews from week 2"; "Decision meeting fixed for week 11."
