# Exercises: Chapter 18, [Life as an FDE: Pace, Travel, Ethics and Sustainability](../chapters/18-life-as-an-fde.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional and all figures illustrative. Several questions are personal; the solutions give the points a good answer covers.

## Questions

1. **Concept.** What are the three dimensions of burnout in the World Health Organization's ICD-11 description? For each, give one warning sign an FDE might notice in themselves. Why does the chapter say a good FDE organisation should treat burnout as a capacity problem rather than a personal failing?

2. **Calculation.** You have two FDE offers. Offer A says "travel up to 50%"; offer B says "on site one week a month". Assume 46 working weeks a year (230 working days), on-site trips run Monday to Thursday (four days, three nights away), and each trip costs six hours of door-to-door travel.
   - (a) For each offer, at its maximum, how many trips, nights away and hours of travel is that a year?
   - (b) What share of working days is offer B?
   - (c) Which questions would you ask both employers before comparing the offers?

3. **Calculation.** A week's calendar audit for an FDE on a production deployment at Contoso Insurance: 47 hours worked, made up of 18 hours of meetings, 6 hours travelling, 9 hours of email and chat, 5 hours answering ad hoc support questions from Contoso users, and 9 hours building. The building time came in eleven fragments, the longest 75 minutes.
   - (a) What share of the week was building? How many uninterrupted blocks of two hours or more did the FDE have?
   - (b) Propose a weekly pattern that gives at least three two-hour deep-work blocks and brings the week down to 45 hours, and say which hours you would cut and how.

4. **Scenario.** For each situation, say what you would do, and which institution or person you would involve.
   - (a) Woodgrove Bank's project manager asks you to switch off multi-factor authentication for pilot users "just until the security review finishes next week, or we'll miss the board demo".
   - (b) Your company's account executive wants you to show Adventure Works an "automatic parts ordering" feature tomorrow. It doesn't exist; he suggests a scripted mock-up "because it's on the roadmap anyway".
   - (c) Evaluation of Fabrikam Health's discharge-barrier extraction shows 93% accuracy overall but 81% on notes from one specialty, which serves mainly older patients.
   - (d) Northwind Traders' operations director asks you to reuse the complaints classifier to score individual call-centre agents for performance reviews.
   - (e) While fixing a data pipeline at Wide World Importers you notice invoices that seem to have been paid twice to a supplier owned by a Wide World manager.

5. **Scenario.** Tailspin Toys asks your team to extend its warehouse deployment: cameras and an AI model would track each picker's movements and idle time, and produce a ranked list each week for supervisors, which would feed into bonuses and disciplinary decisions. Work through the seven questions in §18.5 (purpose, legitimacy, proportionality, fairness, transparency, accountability, your red lines). Then say what you would recommend to your lead, and what a more acceptable version of the deployment might look like.

6. **Scenario.** You are the FDE manager. One of your FDEs, eight months into a demanding Woodgrove Bank engagement, has been on site four days a week throughout. In your one-to-one she says she dreads the Monday stand-up, describes the customer's team as "idiots", and has made two careless deployment mistakes this month. What do you do this week, this month and structurally? What would you say if she apologises for "not coping"?

7. **Hands-on.** (a) Write a learning-log entry for a recent project, engagement or piece of work: the technical things you learned, the questions you couldn't answer, and what you will read or build to answer them. (b) Choose a depth area (§18.6) and write a six-month plan to grow in it using at least three of the chapter's methods. (c) Write down your own red lines, and list the institutions at your current or target employer you would use if you met one (code of conduct, acceptable-use policy, responsible-AI review, confidential reporting channel). You can use section 8 of [`../templates/engagement-retrospective.md`](../templates/engagement-retrospective.md) as a model for turning lessons into actions.

## Solutions

1. **Exhaustion** (persistent fatigue that rest doesn't fix; dreading the week on Sunday afternoon), **cynicism or detachment from the job** (calling the customer "idiots"; not caring whether the deployment succeeds), and **reduced professional effectiveness** (small mistakes increasing; tasks that used to take an hour taking a day). Burnout is chronic workplace stress that hasn't been managed, so its causes are mostly structural: too much travel, too many engagements, no slack, no breaks between engagements. Treating it as personal weakness hides the cause and loses good engineers. Treating it as a capacity problem leads to the fixes that work: rotation, reduced travel, reserve capacity and protected time (Chapter 17 §17.6 and §17.9).

2. (a) **Offer A at 50%:** 50% × 230 = 115 days on site; 115 ÷ 4 = 28.75, so about **29 trips**, 28.75 × 3 ≈ **86 nights** away and 28.75 × 6 ≈ **173 hours** of travel (more than four 40-hour weeks).
   **Offer B:** 12 trips × 4 days = 48 days; **12 trips, 36 nights, 72 hours** of travel.

   (b) 48 ÷ 230 = **20.9%** of working days.

   (c) Ask both: what the *typical* rather than maximum travel was for FDEs in the last year (get it in numbers); how far the customers are (a six-hour trip and a 40-minute train are different jobs); whether travel days count as working time; recovery days after long trips; flexibility for life events; whether travel varies by engagement phase (heavy in discovery and go-live, light during build); and whether you can see the current customer list. "Up to 50%" can mean anything from occasional visits to 86 nights a year, so pin it down before you compare pay (Chapter 19).

3. (a) Building was 9 ÷ 47 = **19%** of the week, and there were **no** uninterrupted two-hour blocks (the longest was 75 minutes). Eleven fragments averaging under 50 minutes each is very little real engineering time.

   (b) One reasonable pattern:
   - **Deep work:** Tuesday, Wednesday and Friday mornings, 09:00–11:30, calendar-blocked and notifications off: three blocks of 2.5 hours = 7.5 hours, plus shorter afternoon build sessions, keeping total building at 9–11 hours.
   - **Support (cut 5 → 1 hour):** this is the biggest structural fix. Ad hoc support from Contoso users means the support route isn't working (Chapter 15 §15.6). Route questions through Contoso's service desk, write runbooks or FAQ entries for the recurring ones, and hold one 30-minute office hour twice a week for what remains.
   - **Meetings (18 → 15 hours):** batch them into Monday and Thursday afternoons; drop or delegate recurring meetings where you are not needed; replace one status meeting with the written weekly update.
   - **Email and chat (9 → 8 hours):** check at fixed times.
   - Travel stays at 6 hours; work on the train counts only if it is real work.

   Total: 15 + 6 + 8 + 1 + about 15 hours of building and other work ≈ 45 hours. Agree the pattern with your engagement lead and tell the customer when you are available, so that protected time is respected rather than resented.

4. - (a) **Decline**, explain the risk briefly, and offer alternatives: a demo with synthetic data, or pilot users on a test tenant with MFA kept on; ask the security team whether the review can be expedited. Escalate to your lead and the customer's sponsor if pressed (Chapter 14). A missed demo is recoverable; a breach traced to a control you removed is not.
   - (b) **Refuse to misrepresent.** Offer an honest demo of what exists, and if the roadmap is relevant, describe it clearly as future work, with the product team's confirmed timing (Chapter 7 §7.5). Raise it with your manager: a sale won on a mock-up becomes an FDE's problem in month two, when the customer expects the feature.
   - (c) **Don't ship until it's understood and addressed.** Report it to the customer's sponsor and clinical safety officer and to your company. Investigate the cause (often a template or note format, as in Chapter 20 §20.4), fix it, re-evaluate by group, and record the finding and fix in the safety case. That the affected group is mainly older patients makes this a fairness issue as well as a quality one.
   - (d) This is a **purpose beyond what was approved**. Don't silently enable it. Raise it with your lead and Northwind's compliance and data-protection team: it is new processing of employee data for consequential decisions, needing its own legal basis, DPIA, and consultation, and the classifier was never evaluated for this purpose.
   - (e) **Don't investigate alone.** Record exactly what you saw, keep the data where it is, and follow your company's legal and ethics escalation process; they will decide how and whether to inform the customer. Do not confront anyone or copy data.

5. - **Purpose:** to measure and rank individual pickers. Who benefits: supervisors and the company's cost base. Who could be harmed: pickers, through surveillance, pressure, and decisions about pay and discipline.
   - **Legitimacy:** workplace monitoring of employees using cameras is heavily regulated (in the UK, data protection law and Information Commissioner's Office guidance on monitoring workers; in many countries, works-council consultation). It needs a lawful basis, a DPIA, and transparency to workers. Check your own company's acceptable-use policy too.
   - **Proportionality:** continuous individual tracking is intrusive; is there a less intrusive way to reach the business goal (picking productivity)?
   - **Fairness:** "idle time" penalises people with disabilities, older workers, those doing unrecorded tasks (helping colleagues, waiting for stock) and those in badly laid-out zones. Has anyone measured that?
   - **Transparency:** would the pickers know how they are measured and ranked?
   - **Accountability:** is a human accountable for each disciplinary decision, with a way to appeal against a model output?
   - **Red lines:** many engineers would not build covert or punitive individual surveillance; decide whether this is one of yours.

   **Recommendation:** raise it with your lead and your company's responsible-AI review before agreeing anything; do not start building. Suggest a more acceptable version: aggregate, anonymised flow analysis by zone and shift to find layout problems, stock-outs and bottlenecks (most picking delay is usually process, not people); no individual ranking; no link to pay or discipline; consultation with workers or their representatives; and a DPIA. This may well solve the real problem better, which is the Chapter 5 lesson again: solve the problem, not the brief.

6. **This week:** listen; name what you see without diagnosing ("dreading stand-ups, frustration with the team and a couple of slips are signs you're running on empty after eight months"); reduce load immediately (cover for a few days, cancel the next trip, take leave if she wants it); remind her of the employee assistance programme or other support. **This month:** plan a rotation off the engagement or a reduction to two days on site, with a proper handover to a colleague; agree protected recovery time; look at what made the mistakes possible (lack of review, fatigue) without blame. **Structurally:** this is a capacity failure (Chapter 17): eight months at four days a week breached any sensible travel limit. Introduce travel limits, rotation on intense engagements, reserve capacity and health-check columns for team load, and check whether others are in the same state.

   If she apologises: "You don't need to apologise. We kept you on a heavy engagement too long; that's on the planning, not on you. Telling me is exactly the right thing to do."

7. A good learning-log entry is specific: "Learned: how SharePoint's permission inheritance breaks when a folder's inheritance is stopped; how to measure retrieval recall at k. Couldn't answer: how to evaluate answer faithfulness without a human grader. Next: read the evaluation chapter of the model provider's documentation; build a small LLM-as-judge experiment with the [`../examples/llm-eval-harness/`](../examples/llm-eval-harness/) example and compare it with my own labels."

   A good six-month plan names one depth area (for example retrieval and evaluation) and combines methods: seek an engagement that uses it; productise one field component in that area (Chapter 16); write an internal design note or playbook section; teach a session to new FDEs; and keep the learning log monthly.

   Red lines are personal, but should be written down in advance, specific ("I will not build systems whose main purpose is covert surveillance of individuals"), and paired with the route you would use, so that you are not deciding under pressure in the customer's office.
