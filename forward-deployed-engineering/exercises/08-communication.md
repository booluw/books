# Exercises: Chapter 8, [Communication: Demos, Writing and Hard Conversations](../chapters/08-communication.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies and people are fictional.

## Questions

1. **Scenario.** Rewrite this weekly update so it is answer-first, quantified and has an honest status colour.

   > Subject: Update
   >
   > Hi all, busy week! We had several meetings with the data team and made good progress on the pipeline. We also refactored the retrieval module, which is much cleaner now, and started looking at the evaluation set. There were some issues with the endorsements API but we're working through them. Users seem to like the tool. Status: green. Next week we'll keep going.

   Assume these facts: week 5 of 10 at Contoso Insurance; coverage summaries live for 15 pilot adjusters; opened on 72% of eligible claims (target 70% by week 6); 91% correct on the 200-claim evaluation set (target 90%); endorsements API access is two weeks late, threatening the week-8 milestone; the platform director could unblock it.

2. **Concept.** A project reports green for weeks 1–6 and red in week 7, when the data platform migration it depended on (announced in week 3) slips. What two rules from §8.3 were broken, and what should the week-3 to week-6 updates have said?

3. **Calculation.** Translate each metric into a sentence a non-technical operations manager can act on, as in §8.8.
   - (a) "91% correct on our 412-case test set."
   - (b) "The fraud flags have precision 0.95 and recall 0.80."
   - (c) "Median handling time fell from 25 to 7 minutes on 412 cases; p90 fell from 60 to 22 minutes."

4. **Hands-on.** Write an architecture decision record (ADR) in the format of §8.5 for this decision at Wide World Importers: the customs-document checker will receive shipment data from a nightly SFTP extract from the freight system rather than its API, because the API is rate-limited to 60 requests a minute and the freight system's owner has refused to raise the limit before the next quarter. Include status, context, decision and consequences.

5. **Scenario.** Woodgrove Bank's go-live date will slip by three weeks because the penetration test found two high-severity issues in the vendor's identity integration. Write the bad-news conversation using the five steps in §8.9, as you would say it to the sponsor on a call.

6. **Scenario.** Tailspin Toys' finance director asks you to have the AI agent post journal entries directly to the general ledger "so the month-end pack is ready on day one". Write a refusal that follows §8.9.

7. **Scenario.** Critique this demo plan for a Northwind Traders sponsor meeting and rewrite it: 30 minutes of slides on the platform's architecture; a live demo of six features, including two nobody asked for, on three prepared synthetic invoices; a video of the latency-free "ideal flow" in case the live system is slow; no time for questions; the FDE drives throughout.

8. **Hands-on.** Using [`../templates/executive-brief.md`](../templates/executive-brief.md), write a one-page executive brief for the Contoso Insurance sponsor at the end of the pilot, using the facts from question 1 plus: week-10 median cycle time for the pilot team was 6.4 days (baseline 9.0); a comparison team moved from 9.2 to 8.6 days over the same period; the next phase is rollout to the Bristol office. Then write the matching field report for your product team using [`../templates/field-report.md`](../templates/field-report.md), about the endorsements API problem, noting that two other insurance customers have hit it.

## Solutions

1. Model rewrite:

   > **Subject:** Contoso coverage assistant: weekly update, week 5 of 10, status AMBER
   >
   > **Summary.** Coverage summaries are live for all 15 pilot adjusters and are being used on 72% of eligible claims, ahead of target. Quality is on target at 91%. Status is **amber** because endorsements API access is two weeks late, which puts the week-8 milestone (complete summaries including endorsements) at risk.
   >
   > **Progress against success criteria**
   > - Adoption: 72% of eligible claims (target 70% by week 6): on track.
   > - Quality: 91% correct on the 200-claim evaluation set (target 90%): on track.
   > - Cycle time: measured from week 6.
   >
   > **Done this week:** pipeline to the claims system completed; retrieval refactored (no user-visible change).
   > **Next week:** add endorsements once access lands; extend evaluation set to endorsement cases.
   >
   > **Decision needed:** [Sponsor] to ask the platform director to approve endorsements API access by Wednesday. If not granted by then, we recommend launching with summaries flagged "endorsements not included".
   >
   > **Risks:** endorsements access (owner: platform team; next step: sponsor escalation).

   What changed: the subject names the customer, week and status; the conclusion comes first; vague claims ("users seem to like it") became measured criteria; internal work (refactoring) shrank to a line; the API problem became a named risk with an impact, an owner and an ask; and the status is amber because a milestone is at risk.

2. Broken rules: **"Don't stay green until you're red"** and **"Explain the colour."** The dependency was a known risk from week 3. Weeks 3–6 should have been **amber**, naming the cause (dependence on the migration), the impact (which milestone would slip, by how much, if the migration slipped) and what was needed (a contingency, such as reading from the old platform, or a decision on the critical path). Going straight from green to red tells the sponsor you either didn't know or didn't say; amber is how you ask for help in time.

3. - (a) "About 9 in every 100 summaries had an error: roughly one in eleven. Across the 412 test cases, that was about 37. That's why adjusters still check the cited clause before relying on a summary."
   - (b) "When the system flags a payment, it's right 95 times out of 100, so your team won't waste much time on false alarms. But it catches only 80 of every 100 real frauds; 20 get through, so the existing controls still need to run alongside it."
   - (c) "Half the cases now take 7 minutes or less, down from 25. Even the slowest one in ten now takes 22 minutes or less, down from an hour, so the long, painful cases have improved as well."

   Note for (c): p90 is the 90th percentile, the time within which 90% of cases are finished.

4. Model ADR:

   ```
   # ADR 004: Receive shipment data by nightly SFTP extract, not the freight API

   Status: Accepted (2026-10-12)
   Context: The customs-document checker needs about 40,000 shipment records a day.
            The freight system API is limited to 60 requests per minute; at one
            shipment per request that is about 11 hours of calls a day, and the
            system owner will not raise the limit before Q1 2027. A nightly SFTP
            extract already exists for the finance team.
   Decision: Read shipment data from the nightly SFTP extract (02:00), loaded
             idempotently into the checker's staging tables.
   Consequences: Shipments created after 02:00 are checked next morning, so
                 same-day urgent shipments are not covered; the UI shows "data as
                 of" with the extract time. We depend on the finance extract's
                 format: a contract test runs on each load and alerts on schema
                 changes. Revisit when the API limit is raised (owner: integration
                 lead; review date 2027-01-15).
   ```

   (40,000 requests ÷ 60 a minute ≈ 667 minutes ≈ 11 hours.) The value of the ADR is that six months later nobody "fixes" the extract by hammering the API.

5. Model call:
   1. **State it plainly:** "We won't go live on the 3rd. The new date I'm proposing is the 24th."
   2. **Cause, without blame:** "The penetration test found two high-severity issues in our identity integration. They're our issues, and we're fixing them."
   3. **Impact:** "Go-live moves three weeks. The pilot users carry on with the current process meanwhile, and the impact measurement moves to the end of January."
   4. **Options with a recommendation:** "We could go live on the 3rd with the integration disabled and manual sign-in, but your security team won't accept that, and I agree with them. I recommend we fix, retest with the same testers, and go live on the 24th."
   5. **What you need:** "Can you help us secure a retest slot with the pen-test team for the week of the 14th?"

   Then follow up in writing the same day, and update the weekly status to red with the recovery plan.

6. Model refusal: "I understand: you need the month-end pack ready on day one, and manual journal entry is what's holding it up. Posting directly to the ledger isn't covered by the security approval, and an incorrect entry from an automated agent would be hard to detect and reverse. What I can do is have the agent prepare the journal entries as a reviewed export: your team checks them and imports them in one step, which should get the pack ready by day one or two. If you'd like direct posting in future, let's raise it through change control so the security and audit design can be done properly."

   The structure: acknowledge the need, give the reason briefly, offer an alternative, point to the process.

7. Problems: 30 minutes of slides before the software (the audience loses interest; it looks as if there is nothing to show); features nobody asked for (signals you weren't listening); prepared synthetic data (proves little, and breaks when someone asks for a real case); an idealised video hiding latency (destroys credibility if discovered); no time for questions; and the FDE drives instead of a user.

   Rewrite (30 minutes):
   - 2 minutes: the outcome first ("Last week, the pilot team processed 230 real invoices with the assistant; exception handling time fell from 31 to 12 minutes").
   - 12 minutes: a pilot user from the accounts team walks through the workflow on two real invoices from last week, including one exception.
   - 4 minutes: a case it gets wrong, and how the user sees and corrects it.
   - 2 minutes: how quality is measured (evaluation set and results).
   - 10 minutes: questions, then asks and next steps.
   - Rehearse the day before on the same environment, and keep an honest recording as a backup only if the live system fails.

8. **Executive brief**: check that the headline is a one-sentence result, for example: "The coverage assistant cut median claim cycle time by about 2 days for the pilot team, and we recommend rolling it out to Bristol." Quote the **difference-in-differences** result, not the raw before-and-after: (6.4 − 9.0) − (8.6 − 9.2) = −2.6 − (−0.6) = **−2.0 days** (Chapter 13). Include adoption (72%+) and quality (91%) as supporting evidence, the Bristol next step with expected value, specific asks with dates, and the top two or three risks. It must fit on one page and be forwardable unchanged.

   **Field report**: describe the **problem** (coverage summaries are incomplete without endorsements, and the endorsements API is not exposed in the standard connector, so each customer waits weeks for bespoke access), not just "add endorsements support"; show **evidence** (the two-week delay, the workaround, the share of coverage questions that involve endorsements); **quantify impact** (users affected, delayed milestones, revenue at stake); name the **other two customers** (rule of three met); and propose a **generalisation** (an endorsements object in the product's standard insurance connector).
