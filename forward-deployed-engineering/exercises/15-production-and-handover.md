# Exercises: Chapter 15, [Production Readiness, Operations and Handover](../chapters/15-production-and-handover.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional and all figures illustrative.

## Questions

1. **Concept.** Define a service level indicator (SLI), a service level objective (SLO), a service level agreement (SLA) and an error budget, using one running example of your own. Then explain (a) why the SLA is usually looser than the internal SLO, (b) why a back-office summarisation tool should not be given the availability target of a payments system, and (c) why an AI system needs a quality SLO as well as an availability one.

2. **Calculation.** Fabrikam's invoice-extraction API has an availability SLO of **99.5% of requests succeed, measured over a 30-day month**. It serves about 1,200,000 requests a month (roughly 40,000 a day).
   - (a) What is the error budget, in failed requests and, assuming even traffic, in minutes of complete outage?
   - (b) In the first ten days of the month there were three sources of failures: a 45-minute outage (about 1,500 failed requests), an elevated error rate of 3% for ten hours across 20,000 requests, and about 400 routine background failures. What share of the budget has been used, and what is the **burn rate** (budget used ÷ share of the period elapsed)?
   - (c) The product team proposes tightening the SLO to 99.9%. What would the budget be, and where would this month stand?
   - (d) The accounts-payable team also has a quality SLO: "in a weekly sample of 150 extractions, at least 90% are fully correct". This week 17 sampled extractions had errors. Is the quality SLO met?
   - (e) What should the team do now in each case?

3. **Calculation.** Tailspin Toys' customer-service assistant normally peaks at 21,600 model requests an hour; each request takes 5 seconds end to end. For the Black Friday weekend, marketing expects three times normal peak. Each application instance handles 20 concurrent requests. The model provider's limit on the account is 2,000,000 input tokens per minute; each request uses about 2,500 input tokens and 400 output tokens.
   - (a) Using **Little's law** (average concurrency = arrival rate × time in the system), how many requests are in flight at normal peak, and at Black Friday peak?
   - (b) With 50% headroom on top of the Black Friday peak, how many instances do you need? Add one spare instance for resilience.
   - (c) What input-token rate per minute does Black Friday peak need, with and without headroom? Is the provider limit a problem, and what would you do about it?

4. **Scenario.** Woodgrove Bank wants to replace the model behind its live complaints-classification service with a newer, cheaper model version. Offline evaluation shows the new version scores 1.5 points higher on the eval set. The service routes about 3,000 complaints a day; misrouting a regulatory complaint can breach a statutory deadline. Choose a release strategy from §15.3 (you may combine them), write the rollback criteria in the form the chapter recommends, and say what must be true about the prompt and model configuration for rollback to be fast.

5. **Scenario.** Three weeks after go-live, a Contoso Insurance claims manager reports that the coverage assistant has started citing a policy wording that was withdrawn in September. Every request has returned HTTP 200 and no alert has fired.
   - (a) Is this an incident? Assign a severity and justify it.
   - (b) Walk through the five incident steps for this case, including what you would do to mitigate before you understand the cause.
   - (c) Outline the blameless post-incident review, and propose two actions that would have detected the problem earlier.

6. **Scenario.** Northwind Traders' AI-assisted purchase-order matching went live two months ago. Northwind has a four-person IT team and a busy service desk. The FDE, who has moved to another account, still receives two or three Teams messages a week from Northwind users ("the match screen is slow again", "can you add Priya?", "why did it reject this invoice?").
   - (a) What does this tell you about the handover?
   - (b) Choose a support model from §15.6 and write a tier table (who handles what, hours, response targets, escalation route).
   - (c) What should the FDE reply to the next message?

7. **Hands-on.** Copy [`../examples/readiness-gate/checklist.json`](../examples/readiness-gate/checklist.json) to a scratch folder and run `python3 gate.py <your copy>` from [`../examples/readiness-gate/`](../examples/readiness-gate/) after each change below (restore the original between parts). Predict the verdict before you run it, then explain the result.
   - (a) Set `eval_pass_rate` to 0.88.
   - (b) Set the `due` date of DR-1 to `2026-10-20`.
   - (c) Delete the `due` field from HAND-1.
   - (d) Mark DR-1 and HAND-1 as `"done"`, each with an evidence link.
   - (e) Add a major item `QUAL-1` for the quality SLO in question 2(d), status `"done"`, with evidence, an owner, a due date of `2026-11-16` and a check `{"metric": "weekly_quality_sample", "op": ">=", "value": 0.9}`, but do not add the metric.
   - (f) Set `p95_latency_ms` to 3400.
   - Finally, say which outcome surprised you, and what each tells you about how to write a checklist.

8. **Hands-on.** Using [`../templates/handover-pack.md`](../templates/handover-pack.md), draft sections 1 (system overview), 5 (runbooks), 8 (support model and escalation) and 13 (acceptance criteria) for the Fabrikam invoice-extraction system in question 2. Include one complete runbook, in the chapter's format, for the failure mode "a supplier changes its invoice layout and extraction accuracy drops". Then write a two-week unaided-operation plan that proves the handover worked.

## Solutions

1. Running example: an internal search assistant.
   - **SLI:** a measured quantity, such as "the share of search requests that return a result within 2 seconds".
   - **SLO:** a target for the SLI over a period: "99% of requests return within 2 seconds, each calendar month".
   - **SLA:** a contractual commitment, with remedies if missed: "95% of requests within 2 seconds each month, or a 10% service credit".
   - **Error budget:** 100% minus the SLO, here 1% of the month's requests may be slow or fail. While budget remains, the team can ship changes; when it is spent, reliability work takes priority.

   (a) The SLA is a promise with financial consequences, so the vendor leaves a safety margin: the internal SLO is the early warning that fires well before the contract is breached.
   (b) Each extra "nine" costs money (redundancy, on-call, slower releases). A summarisation tool that is unavailable for an hour delays some reading; a payments system that is unavailable for an hour stops revenue and may breach regulation. Matching the target to the cost of failure is the point of the conversation.
   (c) An AI system can be fully available and still wrong: every request returns HTTP 200 while the answers degrade (a model update, stale documents, a retrieval bug). Availability SLOs cannot see this; a quality SLO based on sampled grading, such as "≥ 90% of weekly sampled summaries correct", can.

2. (a) Budget = 0.5% × 1,200,000 = **6,000 failed requests a month**. In time: 0.5% × 30 × 24 × 60 = 0.005 × 43,200 = **216 minutes (3 hours 36 minutes)** of complete outage.

   (b) Failures so far = 1,500 + (3% × 20,000 = 600) + 400 = **2,500**. Share of budget used = 2,500 ÷ 6,000 = **41.7%**. Share of the period elapsed = 10 ÷ 30 = 33.3%. Burn rate = 41.7 ÷ 33.3 = **1.25**: the budget is being spent 25% faster than an even pace, so it would run out around day 24 (30 ÷ 1.25) if the pattern continued. 3,500 failures remain for 20 days, about 175 a day, against a routine background of about 40 a day, so there is room, but one more outage like the first would take usage to 4,000 (66.7%).

   (c) At 99.9%, the budget is 0.1% × 1,200,000 = **1,200 failed requests** (43.2 minutes of outage). This month's 2,500 failures would be **208%** of it: the SLO would already be breached on day 10. Before tightening, ask whether Fabrikam's finance users actually notice the difference between 99.5% and 99.9% for a batch extraction service; if not, the stricter target buys cost, not value.

   (d) 90% of 150 = 135, so at most **15** incorrect extractions are allowed. 17 errors means 133 ÷ 150 = **88.7%**: the quality SLO is **missed**, even though availability is within budget.

   (e) Availability: no emergency, but the burn rate is above 1; hold risky releases until the 45-minute outage's review actions are done, and watch the burn rate daily. Quality: treat it as a quality incident (§15.5). Read the 17 failures, look for a common cause (often one supplier's new layout; see question 8), add the failing cases to the evaluation set, fix and re-run before the next weekly sample.

3. (a) Normal peak: 21,600 ÷ 3,600 = **6 requests a second**; concurrency = 6 × 5 = **30 requests in flight**. Black Friday: 3 × 6 = 18 a second; 18 × 5 = **90 in flight**.

   (b) With 50% headroom: 90 × 1.5 = 135 concurrent requests; 135 ÷ 20 = 6.75, so **7 instances**, plus one spare = **8 instances**.

   (c) 18 requests a second = 1,080 a minute; × 2,500 = **2,700,000 input tokens a minute** at peak, and **4,050,000** with 50% headroom. Both exceed the 2,000,000 limit, so on the busiest hour the assistant would be throttled (errors or long queues) exactly when customers need it. Actions, in order: ask the provider for a temporary limit increase now (these take time); cut tokens per request (trim retrieved context, cache the fixed system prompt if the provider supports prompt caching, shorten conversation history); and design graceful degradation (queue, then hand off to human agents with a clear message) if the limit is hit anyway. Output tokens (1,080 × 400 = 432,000 a minute) should be checked against any separate output limit. Load-test the real configuration before the weekend; capacity plans that have not been tested are guesses.

4. A good answer combines **shadow mode** and a **canary**, with a **feature flag** for the model version:
   - **Shadow (one to two weeks):** the new model classifies every live complaint alongside the old one; only the old model's routing is used. Compare disagreements, with special attention to regulatory complaints. A 1.5-point average gain can hide a drop on the rare, costly category.
   - **Canary:** route 5% of traffic using the new model, then 25%, 50% and 100%, comparing misrouting rates (from the complaints team's reassignment data) at each step.
   - **Rollback criteria, written in advance:** "Roll back to the previous model version if (a) any regulatory complaint is misrouted by the new model during the canary, (b) the reassignment rate on canary traffic exceeds the control by more than 1 percentage point over a full day, or (c) the complaints operations lead requests it."
   - **Fast rollback requires:** prompt, model version and any thresholds held as **versioned configuration**, not code; the previous version still deployable; the flag switchable without a redeploy; and the decision owner named. Rollback should then be a configuration change taking minutes.

5. (a) **Yes.** §15.5 says quality incidents count even when every request succeeds. Severity depends on impact: adjusters can still work and the citations let them check, but a withdrawn wording could lead to a wrong coverage decision and a customer complaint. **Sev 2** (significant degradation of a business function, workaround available) is reasonable; Sev 1 if claims were already paid on the wrong wording.

   (b) 1. **Detect:** user report (note that monitoring missed it). 2. **Triage and declare:** confirm with two or three examples; name an incident lead; set severity. 3. **Communicate:** tell the claims managers now ("the assistant may cite withdrawn wording WD-2019; check the wording date before relying on a summary"), with the next update time. 4. **Mitigate first:** remove the withdrawn document from the index or filter it out at retrieval, or, if that is not quick, switch the coverage panel off with its feature flag; identify claims summarised since the withdrawal date so that adjusters can recheck them. 5. **Resolve and review:** find the cause (for example, the document sync adds new wordings but never deletes withdrawn ones) and fix it.

   (c) Review outline: summary; impact (period, number of claims affected, any wrong decisions); timeline; contributing causes, written about the system rather than people ("the sync job had no deletion path"; "the evaluation set had no withdrawn-document cases"); what went well (a user noticed quickly; citations made it checkable); actions with owners and dates. Two detection actions: **a freshness and consistency check** comparing the index's document list with the policy system's list of current wordings, alerting on any mismatch; and **evaluation cases for withdrawn documents**, run in CI and in the weekly production sample.

6. (a) The handover failed or was incomplete. Users don't know the support route, or the route doesn't work, and the FDE has become an unofficial support tier, which §15.6 says is the sign of a failed handover.

   (b) **Hybrid** fits: Northwind's service desk takes first line; the vendor takes platform and complex issues; Northwind's IT team owns access and integrations.

   | Tier | Handles | Who | Hours | Response target | Escalates to |
   |---|---|---|---|---|---|
   | 1 | User questions, access requests ("add Priya"), known issues | Northwind service desk | 08:00–18:00 weekdays | 4 business hours | Tier 2 via ticket queue "PO-matching" |
   | 2 | Configuration, data issues, diagnosing failures ("why did it reject this invoice?", slowness) | Northwind IT (named owner) with vendor support | 08:00–18:00 weekdays | 1 business day | Tier 3 via vendor support portal |
   | 3 | Product defects, complex engineering | Vendor engineering | Per support contract | Per contract (e.g. Sev 1 within 1 hour) | Vendor support manager |

   Publish it in the handover pack, the service desk's knowledge base and the application's help link.

   (c) Reply helpfully once, and redirect: "Thanks, Priya. Access requests now go through the Northwind service desk (link), who can add users the same day. I've copied them in on this one. For anything else, the support route is here (link)." Then tell the Northwind system owner and your own lead, so the gap is fixed properly: add the route to user communications, train the service desk on the three recurring questions, and add a runbook for "match screen slow".

7. Results (assessed 26 October 2026):

   | Change | Verdict | Why |
   |---|---|---|
   | (a) `eval_pass_rate` 0.88 | **NO-GO** | EVAL-1 is a blocker: "eval_pass_rate = 0.88 fails >= 0.9". Status "done" and evidence are not enough when the numeric check fails. |
   | (b) DR-1 due 2026-10-20 | **NO-GO** | "condition already overdue (due 2026-10-20)": a condition whose date has already passed is a broken promise, not a condition. |
   | (c) HAND-1 without `due` | **NO-GO** | "major item not met and has no due date": an undated promise is not a condition. |
   | (d) DR-1 and HAND-1 done with evidence | **GO** | 12 of 13 items satisfied; TRAIN-1 is still listed under "Minor items open", but minors never change the verdict. |
   | (e) QUAL-1 without the metric | **GO WITH CONDITIONS** | QUAL-1 joins the conditions: "metric 'weekly_quality_sample' not reported". A missing metric fails the check even though the item says "done" with evidence. |
   | (f) `p95_latency_ms` 3400 | **NO-GO** | OPS-5 (load test, a major) now fails "<= 3000", and because OPS-5 has no `due` date it cannot become a condition, so it blocks. |

   The usual surprise is (f): a *major* item blocked go-live. That is because only majors with an owner and a date can be deferred. Lessons for writing checklists: give every major item a fallback due date in case it fails late; decide severity before the review (would you really launch with p95 latency 13% over target? if not, it should be a blocker); report every metric a check depends on, automatically if possible; and remember the gate checks that evidence exists, not that it is good.

8. A strong draft includes:
   - **Overview:** purpose (extract fields from supplier invoices and match them to purchase orders), users (accounts-payable clerks), value and current results, SLOs from question 2.
   - **Support model:** the tier table from question 6, adapted to Fabrikam, with named contacts and hours.
   - **Acceptance criteria:** unaided operation for two weeks; at least one deploy, one routine change and one real or simulated incident handled by Fabrikam staff; all runbooks used at least once; written sign-off.
   - **Runbook** in the chapter's format:

   ```
   Runbook: Extraction accuracy drops for one supplier (new invoice layout)

   Symptom: Quality sample or clerk reports show repeated field errors for one supplier;
            "low-confidence extraction" alert rate for that supplier above 20%.
   Impact: Invoices from that supplier go to manual review. Payments may be delayed.
           Other suppliers unaffected.
   Check:
     1. Open the quality dashboard → filter by supplier. Did errors start on a specific date?
     2. Compare a recent invoice PDF with one from before that date. Has the layout changed
        (new template, moved fields, new logo, different language)?
     3. If yes: add 10 recent invoices from this supplier, with correct values, to the
        evaluation set (eval/suppliers/<supplier-id>/). See "Adding eval cases" in section 9.
     4. Update the supplier's extraction profile (config/suppliers/<supplier-id>.yaml), or
        the prompt examples, on a branch. Run `make eval` and confirm the supplier's cases
        pass and the overall pass rate stays ≥ 90%.
     5. Deploy through the normal pipeline. Re-run failed invoices from the review queue.
   Workaround meanwhile: set the supplier to "manual review" in config (no deploy needed).
   Escalate: if accuracy for the supplier is still below 90% after step 4, raise a Tier 3
            ticket with five example invoices attached.
   ```

   - **Unaided-operation plan (two weeks):** week 1, Fabrikam engineers deploy a routine change (for example adding a document type) and handle all alerts while the FDE observes only; week 2, a simulated incident (the FDE swaps in a supplier invoice with a changed layout in the test environment, or replays a past failure) worked through using the runbook. Record every question the receiving team had to ask: each one becomes a documentation or training fix before acceptance is signed.
