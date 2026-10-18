# Exercises: Chapter 20, [Case Studies](../chapters/20-case-studies.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation**, **hands-on** and **case analysis**. All companies are fictional and all figures illustrative. Questions 1–6 build on the six cases in the chapter; question 7 is a new case.

## Questions

1. **Calculation and judgement: Northwind Insurance (§20.1).**
   - (a) Check that the four stages found in discovery account for the 9-day median cycle time.
   - (b) The pilot cut the median by 2.0 days, about half from auto-approval. Roughly where does that leave the pilot team against the 5-day target, and which stages would you look at next? Why is "roughly" the right word?
   - (c) How many of the 200 evaluation claims were wrong at 91%? Give two conditions under which 91% would *not* be acceptable.
   - (d) Verify the £373,000 rollout figure, and say which input you would most want to measure in the pilot.

2. **Calculation and judgement: Woodgrove Bank (§20.2).** Woodgrove handles 4,000 payment exceptions a week. Assume duplicate submissions are 20% of them and mismatched references 30%.
   - (a) For duplicates, how many proposals a week did operators accept unchanged at 96%, and how many did they change or reject?
   - (b) The team wants auto-execution for mismatched references. Over eight weeks of operator approval, operators accepted 93% of these proposals unchanged, and a sampled audit of 600 accepted proposals found no errors. Use the statistical "rule of three" (with zero errors in *n* independent samples, the 95% upper confidence bound on the error rate is about 3 ÷ *n*) to bound the error rate among accepted proposals. What does that imply per week if every mismatched reference were auto-executed?
   - (c) Why is the 93% acceptance rate a bigger problem for auto-execution than the audit result suggests? What would you propose to the model risk team instead?

3. **Scenario: Contoso Logistics (§20.3).** (a) Name the three actions at scoping time that would most likely have prevented pilot purgatory, and the document each belongs in. (b) Draft the email the vendor's FDE lead should have sent within a week of the original sponsor leaving. (c) The value range was £180,000 to £420,000, base £290,000. Write the one sentence you would put in front of the new sponsor, following the impact calculator's advice on presenting ranges.

4. **Scenario: Fabrikam Health (§20.4).** (a) The hospital group has about 24,000 admissions a year. How many would have placeholder discharge dates at 18%, and what would happen to an average length-of-stay calculation if they were not cleaned? (b) A Sev 2 incident occurs: the extraction service stops producing barriers for one ward. You cannot reach the environment remotely and software transfers take a week. What must already be in place for the hospital's team to handle it? (c) List five things the clinical safety case should contain.

5. **Scenario: Tailspin Toys (§20.5).** (a) At which customer should the vendor have noticed the returns pattern, and at which should it have generalised? (b) Sort these into product code or configuration: order lookup; eligibility window (30, 60 or 90 days); label generation; carrier integration; refund approval threshold; refund initiation with approval; excluded product categories. (c) The sixth customer deployed in four days instead of 5–6 weeks. Express the saving in FDE-hours per deployment (assume 40-hour weeks and 8-hour days). (d) Write three sentences to persuade Tailspin's sponsor that migrating is worth their effort.

6. **Calculation and judgement: Wide World Importers (§20.6).** (a) Wide World processes 9,000 supplier invoices a month. Processing time fell from 6 minutes to 1.5 minutes per invoice. How many hours a year is that, and roughly how many full-time clerks (46 weeks × 37.5 hours)? At a loaded cost of £32 an hour, what is it worth? (b) If the deployment cost £120,000 one-off and costs £30,000 a year to run, what is the payback period? (c) Answer the case's discussion question 3: what should the FDEs do if Wide World's engineers contact them directly six months later?

7. **New case analysis: Adventure Works' field-service copilot.** Read the case, then answer the questions.

   > **Situation.** Adventure Works makes bicycles and gym equipment and employs 140 field-service engineers who repair equipment at gyms and dealers, about 12 jobs each a week. A vendor's FDE, Sam, is in week 9 of a 10-week pilot of a copilot that answers engineers' repair questions from service manuals and service history.
   >
   > **What you find when you take over from Sam:**
   > - 25 engineers are in the pilot; 18 use it weekly. In a survey they say it saves "about 30 minutes a job".
   > - The evaluation set has 150 questions; the copilot gets 84% right. Of the 12 electrical-safety questions, it failed 3; one answer told an engineer how to bypass a safety interlock to test a treadmill motor.
   > - 35% of the manuals are scanned PDFs with no text layer; answers about older models are poor.
   > - The pilot runs in the vendor's sandbox, fed by a service-history export that Sam runs by hand every night. Adventure Works IT has not seen the architecture. The success plan has criteria but no production decision date, budget or decision-maker.
   > - The sponsor, the VP of service operations, wants "phase 2: the copilot orders parts automatically from SAP" live by Christmas. In week 6 the account executive demonstrated automatic parts ordering with a scripted mock-up and told the VP it was "on the roadmap for Q1". The product team says it is not.
   > - FDEs at Fabrikam and Litware have each built a custom SAP parts-lookup connector.
   > - Sam has been on site four days a week for nine weeks and answers engineers' WhatsApp questions in the evenings. Several engineers call him "the copilot helpdesk".
   >
   > **Questions.**
   > - (a) List the problems, linking each to the chapter of the book that addresses it, and rank the three most urgent.
   > - (b) Use [`../examples/impact-calculator/`](../examples/impact-calculator/) to estimate annual value at face value from the survey, and a conservative case (only the 72% adoption seen in the pilot; half the claimed time saving). Add a low case of 100 engineers saving 2 hours a week. Which would you present, and how?
   > - (c) Write a go-live checklist for the copilot in the format of [`../examples/readiness-gate/checklist.json`](../examples/readiness-gate/checklist.json) and run it through `gate.py`. What is the verdict, and why?
   > - (d) How do you handle the parts-ordering request and the mock-up demo?
   > - (e) What field reports should be filed, and what does the feedback tracker's rule of three say about the SAP connector?
   > - (f) Write the plan for the last week of the pilot and the following eight weeks.

8. **Hands-on.** (a) Map the Adventure Works case onto the "patterns across the cases" table in §20.7: which patterns does it show, and which is it at risk of failing? (b) Write a one-page case study of an engagement or project you have worked on (or would like to), in the chapter's format: situation, what happened, discussion questions and commentary. Anonymise it.

## Solutions

1. (a) Triage 0.5 + coverage clarification 3 + assessment 2 + approval queues 3.5 = **9 days**.

   (b) About **7 days** (9 − 2.0), still about **2 days** short of the 5-day target. Approval contributed about 1.0 day of the saving and coverage about 1.0 day, leaving roughly approval queues 2.5 days (claims above £2,000), coverage 2 days and assessment 2 days. Next candidates: the approval queue for claims above £2,000 (could the threshold rise, or approval be delegated for low-risk categories?) and assessment. "Roughly", because medians of stages don't add up exactly to the median of the whole, and the 2.0-day effect is an estimate from difference-in-differences with its own uncertainty.

   (c) 91% of 200 = 182 correct, so **18 wrong**. It would not be acceptable if (1) the output drove an automated decision (the commentary's point: no adjuster checks it before payment), or (2) the errors were concentrated in a high-stakes category (for example, exclusions that lead to wrongly declined claims), or if citations were missing so adjusters couldn't check. You'd also want to know the error types, whether adjusters actually check the citations, and how it compares with the human baseline.

   (d) 60 × 3 × 46 × £45 = 180 × 46 × £45 = 8,280 × £45 = **£372,600 ≈ £373,000**. Measure **hours saved per adjuster per week** first: it is the least certain input and moves the answer most (the impact calculator's sensitivity table shows £186,300 to £496,800 for 1.5 to 4 hours).

2. (a) Duplicates: 20% × 4,000 = 800 a week. 96% × 800 = **768 accepted unchanged**; **32 changed or rejected**.

   (b) Upper bound ≈ 3 ÷ 600 = **0.5%** (the exact figure, 1 − 0.05^(1/600), is 0.498%). Mismatched references: 30% × 4,000 = 1,200 a week, so at the bound up to 0.5% × 1,200 = **6 erroneous auto-executions a week** could go unnoticed by the audit. Whether that is acceptable depends on whether the errors are recoverable and how quickly daily sampling would catch them.

   (c) The audit only covers proposals operators *accepted*. Operators changed or rejected 7% of proposals, about 0.07 × 1,200 = **84 a week**. Under auto-execution nobody would be there to change them, so the realistic disagreement rate is closer to 7% than 0.5%. Propose instead: auto-execute only a sub-category where shadow-mode and approval data show near-100% agreement (for example, a reference mismatch differing only by formatting), keep operator approval for the rest, require reversibility, continue daily sampling with a stop rule ("revert to approval if sampled errors exceed X"), and present the evidence the way §20.2 did for duplicates: category by category.

3. (a) (1) **Agree the production decision**: who decides, when, against which criteria, from which budget, in the success plan (Chapter 6 §6.10). (2) **Pilot in production conditions**, or at least involve IT in designing the production data feeds from the start; in the scope and architecture section of the statement of work or success plan. (3) **Quantify value in money with finance**, and keep relationships with **more than one senior stakeholder**; in the success plan's criteria and the stakeholder map (Chapter 7).

   (b) Example:

   > Subject: Delay-prediction pilot: continuing after Maria's move
   >
   > Dear James (regional operations director),
   >
   > Maria Lopez, who sponsored the delay-prediction pilot, left Contoso last week. The pilot is predicting late deliveries 24 hours ahead for the North region, and dispatchers are using it daily. Before it ends on 14 March, Contoso needs to decide whether to take it to production. Since late-delivery penalties fall under your region, could we have 30 minutes this week to show you the results, agree who should make that decision, and agree what evidence they'll need? I'll bring an estimate of the penalty savings, which we'll check with your finance team.

   (c) "On the pilot region's penalty data, we expect earlier intervention to avoid at least £180,000 a year, most likely around £290,000, and up to £420,000; the phased rollout will tell us which." Lead with the low case: a conservative number the customer can check is more credible than an impressive one.

4. (a) 18% × 24,000 = **4,320 admissions a year**. A discharge date of 1 January 1900 gives a length of stay of about −45,000 days (roughly 125 years in reverse) for each one, which would wreck any average (and anything trained on it). Treat placeholders as missing, not as dates (Chapter 10).

   (b) A runbook for "no barriers for one ward" (check whether the ward code changed, a template changed, or the note feed stopped); dashboards and logs the hospital team can read on site; a hospital engineer trained and authorised to operate and roll back; the previous release kept deployable inside the environment; a pre-approved emergency transfer route agreed with the hospital's approval process; and a call bridge so the FDE can guide on-site staff. Meanwhile, coordinators fall back to the existing manual process, which is why the output was designed as a helper, not a replacement.

   (c) Intended use and users, and what it must not be used for; hazard log (missed barrier, wrong barrier, wrong patient through linkage error) with risk ratings and controls; evaluation results overall and by patient group and note template, including the specialty finding and its fix; the human in the loop (coordinators verify each barrier against the linked source note); monitoring and incident process; data-quality controls (placeholder dates, linkage review); change control for model and prompt updates; and sign-off by the clinical safety officer.

5. (a) **Notice at the second** customer; **generalise at the third** (the rule of three, Chapter 16 §16.4). By the fifth, with two implementations broken by upgrades, it was overdue.

   (b) **Product code:** order lookup; label generation; refund initiation with approval; the eligibility-rules engine itself. **Configuration:** eligibility window; refund approval threshold; excluded product categories; choice of carrier. **Connectors:** carrier integrations (a pluggable interface in the product, with one connector per carrier).

   (c) Before: 5–6 weeks × 40 hours = **200–240 FDE-hours**. After: 4 days × 8 hours = **32 FDE-hours**. Saving: **168–208 FDE-hours** per deployment (about 85%).

   (d) "Your returns workflow is two releases behind because it is custom code, and every upgrade risks breaking it. Moving to the product version brings you back onto the supported upgrade path, and contract tests will show it behaves exactly as your current workflow does before we switch. Future improvements to returns will reach you automatically instead of waiting for an FDE."

6. (a) Saved per invoice: 6 − 1.5 = 4.5 minutes. 9,000 × 12 = 108,000 invoices a year × 4.5 = 486,000 minutes = **8,100 hours a year**. 8,100 ÷ (46 × 37.5 = 1,725) ≈ **4.7 full-time clerks**. Value: 8,100 × £32 = **£259,200 a year** (capacity, not necessarily cash; say whether the time is redeployed or hiring avoided).

   (b) Net annual benefit = £259,200 − £30,000 = £229,200, or £19,100 a month. Payback = £120,000 ÷ £19,100 = **6.3 months**. (Check: `payback_months(120_000, 259_200, 30_000)` in the impact calculator.)

   (c) Respond politely and redirect to the agreed support route (Wide World's own team first, then the vendor's support line or customer success manager), copying in the account owner. If the question reveals a gap in the handover pack, fix the documentation through the vendor's normal channels. If it is a new need, treat it as a lead for the account team, not a personal favour. Don't log into their systems: your access was revoked for good reason.

7. (a) Problems, with chapters (most urgent first):
   1. **Unsafe answers** (bypassing a safety interlock): a safety and ethics issue (Chapters 13 and 18). Stop any wider use until fixed.
   2. **Misrepresented capability** (the mock-up and "Q1 roadmap"): honesty with the customer (Chapters 7 and 18).
   3. **No production decision, budget, decision-maker or IT involvement**, and a sandbox with a manual feed: pilot purgatory in the making (Chapter 6 §6.10, Case 20.3).
   - Also: evaluation below threshold, 84% (Chapter 13); scanned manuals, a data problem (Chapter 10); Sam as de facto support and the support model (Chapter 15); Sam's travel and evenings, sustainability (Chapter 18); value based only on self-report (Chapter 13); three custom SAP connectors, the field-to-product loop (Chapter 16); a security review not started (Chapter 14).

   (b) With `ValueInputs`:
   - **Face value:** `people=140, hours_saved_per_week=6` (12 jobs × 0.5 hours), `weeks_per_year=46, loaded_hourly_cost=42` → 140 × 6 × 46 × £42 = **£1,622,880**.
   - **Conservative:** `people=100.8` (72% × 140), `hours_saved_per_week=3` (12 × 0.25) → **£584,236.80 ≈ £584,000**.
   - **Low:** `people=100, hours_saved_per_week=2` → 100 × 2 × 46 × £42 = **£386,400**.

   Present the range with the low case first (£386,000 to £584,000, with £1.6M as an unvalidated upper bound from self-report) and say the pilot's remaining job is to measure time per job from service records rather than surveys. The illustrative payback on the conservative case, with £250,000 to deploy and £60,000 a year to run, is about 5.7 months, so even the cautious figure makes a strong case.

   (c) A reasonable checklist has blockers for the security review, evaluation pass rate (≥ 0.9), every electrical-safety case passing, and a named support owner who is not the FDE; majors with owners and dates for an automated service-history feed and for OCR of scanned manuals; and a minor for training. With `eval_pass_rate` 0.84 and `high_risk_eval_pass_rate` 0.75 (9 of 12), the gate returns **NO-GO** with four blockers:

   ```
   x SEC-1 Security review signed off: status is 'not_started'; no evidence link
   x EVAL-1 Evaluation pass rate at or above 90%: eval_pass_rate = 0.84 fails >= 0.9
   x EVAL-2 Every electrical-safety eval case passes: high_risk_eval_pass_rate = 0.75 fails >= 1.0
   x OPS-2 Support owner named (not the FDE): status is 'not_done'; no evidence link
   ```

   The two data items appear as dated conditions. The verdict is the useful part: it turns "the VP wants it by Christmas" into a specific list of what stands between the pilot and production.

   (d) **Correct the record first**, with your own lead and the account executive, then the VP: "In week 6 you saw a mock-up of automatic parts ordering. That feature isn't on the product roadmap for Q1, and I don't want you planning around it." Then **reframe the need**: what problem does automatic ordering solve? (Probably engineers waiting for parts, or second visits.) A safer first step is **parts lookup and a drafted order that a person approves** (Chapter 12 §12.5: autonomy is earned, as at Woodgrove), built on the SAP connector pattern in (e). Agree it as a later phase in the production success plan, after the safety and evaluation issues are fixed.

   (e) File field reports for: (1) **SAP parts lookup**: with Fabrikam and Litware, Adventure Works is the **third distinct customer**, so the tracker would recommend **PRODUCTISE**; build it once in the product rather than a third custom version; (2) **scanned manuals**: OCR and text layers for older documents are probably a common gap; (3) **safety-critical answers**: a product guardrail or evaluation template for "never advise bypassing safety devices" in equipment-maintenance deployments. Also feed back the sales issue through your manager, not as a field report.

   (f) **Last week of the pilot:**
   - Restrict the copilot's answers on electrical safety (refuse and point to the manual) and add the failed cases to the evaluation set; tell the pilot engineers what changed and why.
   - Meet the VP: correct the parts-ordering message; present the value range; agree a production decision date, the decision-maker and the budget; bring Adventure Works IT and security in.
   - Set up a support route for the pilot engineers (a named contact at Adventure Works and the vendor's support channel) and stop the evening WhatsApp support; agree a sustainable schedule for Sam or a handover from him.

   **Weeks 1–8 after:**
   - Weeks 1–2: production success plan signed (criteria, decision date, owners); security review and DPIA started; receiving team named.
   - Weeks 2–5: OCR and re-indexing of scanned manuals; automated service-history feed designed with IT; evaluation raised to ≥ 90% with all safety cases passing; measurement of time per job from service records against a comparison group.
   - Weeks 5–7: readiness gate re-run until GO or GO WITH CONDITIONS; runbooks and handover pack; support model agreed.
   - Week 8: production decision meeting with evidence; parts lookup scoped as phase 2 on the product connector.

8. (a) Patterns shown or at risk: **pilots need production decisions, owners and money from the start** (at risk: Contoso's pattern exactly); **the loop to product must be closed deliberately** (the SAP connector); **autonomy is earned with evidence** (parts ordering); **early engagement with high-influence sceptics** (IT and security, not yet involved); **handover is designed, not done** (failing: Sam is the support); **measurement makes success legible** (at risk: self-reported value). The "obvious technology" pattern may also apply: OCR, a data fix, may improve answers more than any model change.

   (b) Personal. A good case study is specific (numbers, dates, named roles), honest about what went wrong, ends with questions a reader can argue about, and contains nothing that would identify a customer or reveal confidential data.
