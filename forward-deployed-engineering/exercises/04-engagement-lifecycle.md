# Exercises: Chapter 4, [The Engagement Lifecycle](../chapters/04-engagement-lifecycle.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional.

## Questions

1. **Concept.** Name the eight phases of the engagement lifecycle (0–7) in order. For each, give its purpose in a few words and one exit criterion or output.

2. **Scenario.** Phase 0 at Contoso Retail. The head of innovation says: "We want to do AI. We have budget for a pilot this quarter, but we're still deciding the use case. IT will give you data access once the project is approved, which usually takes a quarter. Our COO hasn't been briefed yet." Using the qualification questions in §4.2, decide go, no-go or "not yet", and say what would change your answer.

3. **Scenario.** Choose an engagement shape from §4.10 for each situation, with a reason.
   - (a) Fabrikam's executive team wants to see what AI could do across five departments, on their own data, before choosing where to invest.
   - (b) Woodgrove Bank has chosen one use case (summarising commercial loan files) and wants evidence against agreed criteria within two months.
   - (c) Wide World Importers has signed a three-year strategic partnership covering customs, routing and demand planning.
   - (d) A consultancy partner will deploy the product at Northwind Traders; the vendor wants quality assurance without assigning a full-time engineer.

4. **Calculation.** Tailspin Toys is deploying a returns-triage system. Dependencies (lead times are from the day a request is submitted):
   - VPN accounts: 2 weeks.
   - Read access to the returns database replica: 4 weeks. It can only be *used* once VPN works.
   - Security architecture review: 6 weeks from submission of the security pack.
   - Build: 3 weeks of work, which needs replica access.
   - Change advisory board (CAB): 1 week, after both build and security approval are complete. Go-live follows CAB.

   **Plan A:** request VPN on day one; request replica access only when VPN arrives; submit the security pack at the end of week 3, once the architecture has settled.
   **Plan B:** request VPN and replica access on day one; submit a draft security pack at the end of week 1.

   (a) When does each plan go live? (b) What is the critical path in each? (c) In Plan B, what happens if the security review takes 8 weeks instead of 6? (d) How much of Plan A's elapsed time is build effort?

5. **Scenario.** Week 4 of a ten-week pilot at Woodgrove Bank. You notice: still no production data access (you have a sample extract); the sponsor has cancelled two check-ins; at every demo the operations manager adds "one more report"; and only one of eight pilot users came to Thursday's demo. Diagnose each sign using §4.12, give your response, and say which you would raise first and how.

6. **Scenario.** At the end of a pilot at Adventure Works the plant manager says: "It's great. Everyone loves it. Let's keep the pilot running while we think about next year's budget." Explain the risk, and list four things you should have done earlier to prevent this, and two things you can still do now.

7. **Hands-on.** Draft a one-page engagement plan for the Tailspin Toys returns-triage engagement in question 4, using [`../templates/success-plan.md`](../templates/success-plan.md). Include objective, success criteria with baselines (invent plausible numbers and mark them as assumptions), in/out/later scope, weekly milestones, people, the dependency list (use Plan B), risks and cadence. Then write the week-2 update using [`../templates/weekly-update.md`](../templates/weekly-update.md), assuming the replica request has been queried by the data platform team.

8. **Concept.** Phase 6's exit criterion is that "the receiving team has operated the system unaided for an agreed period (for example two weeks), including handling at least one incident or change." Why is "including at least one incident or change" there? What would you do if no incident occurs during the period?

## Solutions

1. | Phase | Purpose | Exit criterion or output |
   |---|---|---|
   | 0 Qualify | Is this customer and problem worth forward deployment? | Go/no-go decision and an engagement hypothesis |
   | 1 Discover | Understand how the operation really works | Team can explain the operation in the customer's words; sponsor agrees with the picture |
   | 2 Frame and scope | Choose the first problem and define success | Signed success plan with measurable criteria, baseline, named owners, access requests submitted |
   | 3 Prove value | Working system on real data with real users, fast | Criteria met (or accepted reason), go decision and production scope |
   | 4 Productionise | Reliable, secure, supportable | Production readiness review passed; IT and security sign-off |
   | 5 Adopt | People use it; outcome measured | Adoption targets met; impact report delivered |
   | 6 Hand over | Sustainable without the FDE | Receiving team operated it unaided for an agreed period, including an incident or change |
   | 7 Expand and feed back | Capture value for customer and company | Expansion proposal; field reports and product contributions; reusable assets |

2. **Not yet** (effectively no-go for now). Against §4.2:
   - *Executive sponsor with budget and authority?* No: the head of innovation has pilot budget, but the COO, who would own an operational outcome, has not been briefed.
   - *Specific, valuable problem?* No: "we want to do AI" is the textbook warning sign.
   - *Data access within weeks?* No: a quarter, and only after approval.
   - *People's time committed?* Unknown.

   Deploying now would burn scarce FDE capacity on a search for a problem, with no access and no operational owner. **What would change the answer:** a short, inexpensive alternative such as a one- or two-day discovery workshop (or bootcamp if data can be made available) to identify a specific problem; the COO's sponsorship; and a commitment to start data-access requests in parallel. Write back with these conditions rather than a flat no: it protects the relationship.

3. - (a) **Bootcamp.** One to five days of building on real data across several departments generates a use-case backlog and proves value quickly. It must then convert to a pilot.
   - (b) **Proof of value / pilot**, 2–8 weeks, one use case, success criteria agreed up front.
   - (c) **Embedded programme:** many use cases over years, a pod of FDEs with a strategist and a product liaison.
   - (d) **Partner-led deployment** with 0.5–1 vendor FDE coaching and reviewing.

4. (a) and (b):

   **Plan A**
   - VPN arrives end of week 2; replica requested then, arrives end of week 6.
   - Build weeks 7–9, ends end of week 9.
   - Security pack submitted end of week 3; approval end of week 9.
   - Both complete end of week 9; CAB week 10; **go-live end of week 10**.
   - Critical path: **both** chains finish at week 9. Data chain (VPN → replica → build) and security chain (pack → review) are tied, so a slip in either delays go-live.

   **Plan B**
   - VPN end of week 2; replica requested day one, arrives end of week 4 (usable, since VPN already works).
   - Build weeks 5–7, ends end of week 7.
   - Security pack end of week 1; approval end of week 7.
   - CAB week 8; **go-live end of week 8**, two weeks earlier.
   - Critical path: again both chains finish together at week 7.

   (c) Security approval moves to end of week 9; CAB week 10; go-live **end of week 10**. Security is now the sole critical path: the build would sit finished for two weeks. This is why the chapter calls access and approvals "the hidden critical path" and why you should ask the security team for their real lead time in Phase 2.

   (d) Build effort is 3 weeks of a 10-week elapsed schedule: **30%**. The other 70% is waiting. Making the waiting visible, and starting it early, is the most effective schedule improvement available, and it costs no engineering.

5. | Sign | Likely cause | Response |
   |---|---|---|
   | No production data access at week 4 | Security process, low priority, wrong contacts | Escalate through the sponsor; propose a restricted extract as an interim; reset the timeline in writing |
   | Sponsor cancelled two check-ins | Priorities shifted; lost interest | Ask directly; re-anchor on their goals; consider pausing |
   | "One more report" at every demo | No agreed scope, eager stakeholder | Write it down; "yes, and that goes on the later list" (Chapter 6) |
   | One of eight users at the demo | No champion; wrong users; too busy | Go to the users at their desks; find a champion; shrink the ask |

   **Raise the sponsor first**, because the sponsor is also your route to fixing data access, and an absent sponsor at week 4 means the pilot may lose its production decision at week 10. Ask for a short call (not an email thread): "I want to make sure this is still a priority for you. Two things need your help to hit week 10: production data access and pilot users' time." Follow up in writing with the reset timeline. If the sponsor says priorities have shifted, discuss pausing rather than drifting.

6. **Risk: pilot purgatory.** The pilot "succeeds", but there is no budget, owner or decision to go to production. Usage decays, the sponsor's attention moves on, and the reference value is lost.

   Should have done earlier (Chapter 6 §6.10 and §4.12): agreed the production decision and who makes it up front ("if we meet these criteria, the next step is X"); identified the production owner and budget line during scoping; involved IT, security and the run team in the pilot; set a decision date; and sized the production case during the pilot from measured results.

   Can still do now: quantify the impact in business terms with the customer's finance team and put it in an executive brief the plant manager can take to the budget holder; and propose a dated decision meeting with a scoped production proposal (including procurement), so the default outcome is a decision rather than drift.

7. A good plan fits on one page. Key features to check in your answer:
   - **Objective** in business language: "Reduce the time to route a returned item to restock, refurbish or recycle."
   - **Success criteria** at three levels with baselines marked as assumptions, for example: median triage time from 11 minutes (assumed baseline, to be measured in weeks 1–2) to under 4 minutes; ≥ 80% of pilot staff using it on ≥ 70% of eligible returns by week 6; ≥ 92% correct routing on a 150-item evaluation set.
   - **Scope** with a *later* list (other warehouses, write-back to the warehouse management system).
   - **Milestones by week** consistent with Plan B: data access by week 4, thin end-to-end slice on real data by week 5, pilot use from week 6, CAB week 8.
   - **People** named by role: sponsor, day-to-day owner, SMEs, IT and security contacts.
   - **Dependency table** with owners, lead times and status.
   - **Cadence:** weekly working session, written weekly update, fortnightly sponsor check-in.

   The week-2 update should be **amber**, not green: the replica query threatens the week-4 data date, which is on the critical path. It should name the cause, the impact ("if not resolved by Wednesday, the end-to-end slice moves from week 5 to week 6") and the ask ("sponsor to confirm the business justification to the data platform lead by Wednesday").

8. Operating a system on a quiet day proves little; the real test of a handover is whether the receiving team can **diagnose and act** when something goes wrong or needs changing, using the runbooks rather than calling the FDE. Requiring an incident or change exercises the runbook, the access, the escalation path and the team's confidence.

   If no incident occurs, **create one deliberately**: run a game day or tabletop exercise (simulate an expired credential, a failed nightly load or a model-version upgrade) and have the receiving team handle it while you observe without intervening. Alternatively, have them make and release a real, low-risk configuration change through the normal change process. Record the result in the handover pack.
