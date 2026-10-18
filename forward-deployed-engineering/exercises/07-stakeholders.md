# Exercises: Chapter 7, [Stakeholders, Politics and Trust](../chapters/07-stakeholders.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies and people are fictional.

## Questions

1. **Scenario.** Adventure Works is deploying a predictive-maintenance system at its Birmingham plant. Place each person on the influence/attitude map in §7.3 and say what you would do with each in the next two weeks.
   - The operations VP (sponsor), who championed the purchase.
   - The head of OT (operational technology) security, who has not been consulted and "doesn't like cloud".
   - The maintenance manager, cautiously positive; his bonus depends on unplanned downtime.
   - Senior maintenance technicians, who say "a model can't hear a bearing going".
   - Two apprentice technicians who are excited about the tablets.
   - The plant's data historian administrator, neutral, who controls access to sensor data.

2. **Calculation.** Use the trust equation from §7.5, scoring each element from 1 to 10. FDE A: credibility 9, reliability 4, intimacy 5, self-orientation 6. FDE B: credibility 6, reliability 8, intimacy 7, self-orientation 2. (a) Compute trust for each. (b) FDE A could improve trust most by raising which element by 2 points, or by lowering self-orientation by 2? Compute both. (c) What is the main limitation of using the equation this way?

3. **Scenario.** Four weeks after go-live at Contoso Insurance, the coverage panel is opened on only 18% of eligible claims. List four diagnostic questions or measurements you would use to find out why, and for each likely cause in §7.6 the response you would take.

4. **Scenario.** During a training session at Northwind Traders, a credit controller asks you in front of her colleagues: "Is this thing going to replace us?" You know the sponsor's stated goal is "to absorb 30% volume growth without hiring", but you don't know their long-term plans. Write what you would say, and what you would do afterwards.

5. **Scenario.** Your company's account executive asks you to tell Woodgrove Bank's CIO that the platform "already supports on-premises deployment", which is on the roadmap but not released. Explain why you should not, and write an alternative true statement that still helps the deal.

6. **Scenario.** At Woodgrove Bank, payments operations wants invoices under £5,000 to be paid automatically; compliance insists every payment must have a named human approver. Both bring it to you. Apply the five steps in §7.9 and propose a design.

7. **Scenario.** Fabrikam's sponsor, the chief operating officer, announces she is leaving in three weeks. The deployment is in week 7 of 12. Write an action plan for the next three weeks and beyond.

8. **Concept.** Fabrikam GmbH, a German subsidiary, wants the same AI assistant that logs every user's queries and response ratings. What is a works council, why might it be relevant here, and what should you do about it?

## Solutions

1. | Person | Quadrant | Action in the next two weeks |
   |---|---|---|
   | Operations VP (sponsor) | High influence, supportive: **partner** | Brief before anyone else; ask her to introduce you to the OT security head; agree how she will communicate the project's intent |
   | Head of OT security | High influence, opposed: **risk** | Meet one to one, early. Understand the objection (often legitimate: plant networks are safety-critical). Bring an architecture showing what leaves the plant network, if anything, and ask what an acceptable design looks like. Involve the sponsor if needed |
   | Maintenance manager | Moderately high influence, supportive: **partner** | Make his life easier quickly; frame results in unplanned downtime, his metric; credit him publicly |
   | Senior technicians | Moderate influence, opposed: **risk / sceptics** | Listen seriously; their knowledge of failure sounds and edge cases is exactly what the model lacks. Invite them to help label historical failures and to test alerts. Many sceptics become the best testers |
   | Apprentice technicians | Low influence, supportive: **allies** | Future champions: early access, training, recognition. But don't let them be the only voices; peers trust senior technicians more |
   | Historian administrator | Medium influence, neutral: **key gatekeeper** | Treat as high priority despite neutrality: sensor-data access is on the critical path. Follow their process, ask what they need, and keep them informed |

   Keep the map private and write it respectfully.

2. (a) A: (9 + 4 + 5) ÷ 6 = 18 ÷ 6 = **3.0**. B: (6 + 8 + 7) ÷ 2 = 21 ÷ 2 = **10.5**.

   (b) Raising any numerator element by 2: (18 + 2) ÷ 6 = **3.33**. Lowering self-orientation by 2: 18 ÷ 4 = **4.5**. Lowering self-orientation helps far more, because it divides everything else. In practice for FDE A that means: stop pitching the product and talking about their own cleverness; ask more, listen more, and visibly put the customer's problem first. Reliability (4) is also a concern: missed small promises are easy to fix and are noticed.

   (c) The equation is a **heuristic, not a measurement**. The scores are subjective, the elements are not independent, and the arithmetic suggests precision that doesn't exist. Its value is diagnostic: it tells you which behaviours to change (especially self-orientation), not a number to report.

3. Diagnostics:
   - **Usage by user and team:** is it 18% across everyone, or 90% for three users and zero for the rest? (Points to champions versus a team-level issue.)
   - **Shadow two adjusters** for an hour: do they have to switch screens, re-enter claim numbers, or wait for the panel to load? (Workflow fit.)
   - **When they open it, do they act on it** or re-check the policy anyway? Compare time on task for users and non-users. (Trust.)
   - **Ask the team manager what adjusters are measured on**, and listen to informal conversations about the tool. (Incentives; job fear.)

   Responses by cause (§7.6): poor workflow fit, embed the panel where they already work and remove steps; low trust, show citations, publish evaluation results and fix visible errors fast; job fear, be honest about intent and involve management; no time to learn, short in-context training, champions, office hours; incentives pointing the other way, work with management to align targets; and if it's actually worse, listen and fix it, or stop.

4. Say something honest that doesn't overstep: "That's a fair question, and I'd want to know too. I don't make staffing decisions, so I can't answer for Northwind. What I can tell you is what this phase is for: [sponsor] has said the goal is to handle the expected 30% growth in volume without the team being swamped, and the tool is designed to take on the manual matching you've told me you dislike, while you make the decisions on disputed accounts. I'll make sure your question gets to [sponsor] so you hear from them directly."

   Afterwards: tell the sponsor (or the team's manager) that staff are asking, and recommend that leadership communicate intent directly and soon. Do **not** say "this won't affect anyone's job": it isn't yours to promise. If you came to believe the deployment was being presented deceptively to staff, raise it within your own company (Chapter 18).

5. Saying it would be **untrue**, and the CIO will find out, probably during the security review or the first on-premises conversation. It would destroy your credibility and the trust you need for every later request (§7.5: "tell the truth about your product"; §7.8: sales pressure). It may also have contractual consequences if it is relied on.

   Alternative true statement: "Today the platform runs in your own cloud tenancy, with private networking and keys you control, which meets most of the requirements we've heard from your team. Full on-premises deployment is on our roadmap; I can arrange a briefing with our product team on the timeline and what it would mean for you." Then tell the account executive privately why you said it that way.

6. Applying §7.9:
   1. **Understand the interests:** operations needs speed and less manual work; compliance needs an audit trail showing that payments were authorised and that controls work, not necessarily a human click on each payment.
   2. **Look for a design that satisfies both:** auto-approve invoices under £5,000 that match a purchase order and goods receipt from an approved supplier with unchanged bank details; route exceptions (new suppliers, changed bank details, no PO match) to a human; keep a complete audit log; and have compliance review a random sample each week (say 5%), with the threshold and rules owned by compliance.
   3. **Put the options in writing:** status quo; full automation; the hybrid above, with trade-offs (speed, residual risk, review effort).
   4. **Escalate to the decision-maker** (the sponsor, possibly with the head of financial control) with your recommendation.
   5. **Record the decision** in the success plan and move on.

   Do not choose a side, and do not build both versions.

7. **Next three weeks:**
   - This week: ask the departing COO for a named successor or interim sponsor, an introduction, and a short written endorsement of the project's goals and results to date.
   - Prepare a one-page executive brief (results so far against the success plan, what is next, the asks) that the new sponsor can absorb in five minutes.
   - Meet the successor early and **re-sell from their perspective**: their goals may differ; ask what they are accountable for.
   - Confirm the production decision, budget and decision date in writing before the COO leaves, if possible.

   **Beyond:** broaden the base so the deployment never again depends on one person: strengthen relationships with the day-to-day owner, the IT lead and a second senior executive who benefits. Update the stakeholder map. Record the risk in the weekly update (amber, with the mitigation).

8. A **works council** is an elected body representing employees. In Germany it has legal co-determination rights over the introduction of technical systems that can monitor employee behaviour or performance. An assistant that logs every user's queries and ratings could be capable of monitoring individuals, so the works council's agreement may be required before rollout, regardless of the intended purpose.

   What to do: raise it with Fabrikam GmbH's HR and legal teams at the start, not at go-live; let the customer lead the engagement with the works council; be ready to explain exactly what is logged, who can see it and for how long; consider designs that reduce monitoring potential (aggregated usage statistics, pseudonymised logs, restricted access to individual-level data, shorter retention); and plan the timeline to allow for the consultation.
