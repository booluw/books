# Appendix D. Interview Question Bank

Questions for preparing for (or running) forward deployed engineer interviews, grouped by round, with brief notes on what a strong answer looks like. [Chapter 19 §19.3](../chapters/19-career.md) describes the loop from the candidate's side; [Chapter 17 §17.4](../chapters/17-running-an-fde-org.md) describes it from the hiring side.

**Formats vary.** No two companies run the same loop, and loops change. The rounds below are the common elements *(as of October 2026)*. Descriptions of Palantir's **decomposition** and **learning** rounds come from third-party guides and candidate reports (for example Exponent's interview guide; see [Appendix B](B-bibliography.md)), not from Palantir itself. Treat them as indicative. Ask your recruiter which rounds you will face, how long each is, and which language and tools you may use.

**Using this bank.** Practise out loud, with a timer and, ideally, a partner who interrupts. For interviewers: pick a few questions per round, use a written rubric, and calibrate across the panel.

| Round | Tests | Book chapters |
|---|---|---|
| [D.1 Recruiter and motivation](#d1-recruiter-and-motivation) | Fit, motivation, logistics | [1](../chapters/01-the-role.md), [18](../chapters/18-life-as-an-fde.md), [19](../chapters/19-career.md) |
| [D.2 Coding with practical data tasks](#d2-coding-with-practical-data-tasks) | Clean, working code on messy inputs | [9](../chapters/09-toolkit.md), [10](../chapters/10-enterprise-data.md) |
| [D.3 Decomposition](#d3-decomposition) | Turning ambiguity into buildable, measurable structure | [5](../chapters/05-discovery-and-decomposition.md), [6](../chapters/06-scoping.md) |
| [D.4 Learning](#d4-learning) | Picking up something unfamiliar fast | [9](../chapters/09-toolkit.md) |
| [D.5 System design and integration](#d5-system-design-and-integration) | Deploying into a realistic enterprise | [10](../chapters/10-enterprise-data.md)–[15](../chapters/15-production-and-handover.md) |
| [D.6 AI deployment](#d6-ai-deployment) | RAG, agents, evaluation, AI risk | [12](../chapters/12-ai-deployment.md), [13](../chapters/13-evaluation-and-impact.md), [14](../chapters/14-security-and-restricted-environments.md) |
| [D.7 Customer simulation (role-plays)](#d7-customer-simulation-role-plays) | Judgement and communication under pressure | [6](../chapters/06-scoping.md), [7](../chapters/07-stakeholders.md), [8](../chapters/08-communication.md) |
| [D.8 Behavioural (STAR)](#d8-behavioural-star) | Ownership, judgement, ethics, resilience | [7](../chapters/07-stakeholders.md), [16](../chapters/16-field-to-product.md), [18](../chapters/18-life-as-an-fde.md) |
| [D.9 Questions to ask the employer](#d9-questions-to-ask-the-employer) | Whether the role is real and sustainable | [1](../chapters/01-the-role.md), [3](../chapters/03-business.md), [17](../chapters/17-running-an-fde-org.md) |

---

## D.1 Recruiter and motivation

1. Why do you want to be a forward deployed engineer rather than a product engineer?
2. Why this company, and why now?
3. Tell me about a time you built something for a user you could talk to directly.
4. How do you feel about ambiguity: being handed a problem with no specification?
5. What level of travel can you sustain? (Give a number.)
6. How do you explain the difference between an FDE, a solutions engineer and a consultant?
7. Which of your past roles was most like this one, and what was different?
8. What do you want to be doing in three years?
9. Are you comfortable working in regulated, security-cleared or on-site environments? Do you hold, or could you obtain, a clearance (if relevant)?
10. What are your compensation expectations? *(Prepare a range based on total compensation; see [Chapter 19 §19.2](../chapters/19-career.md).)*

**What good looks like.** Answers connect your history to the core of the role: building for real users, working through ambiguity, liking variety and customer contact, and caring whether the product learns ([Chapter 19 §19.3](../chapters/19-career.md)). You can state the two tests that separate a real FDE role from a relabelled one: it ships production systems for the customer, and there is a deliberate loop back to the product ([Chapter 1 §1.5](../chapters/01-the-role.md)). Travel and pace answers are concrete and honest. Weak answers dwell on the title, the hype or the pay.

---

## D.2 Coding with practical data tasks

FDE coding rounds are usually practical rather than puzzle-heavy. Candidate reports for Palantir's FDSE loop suggest easy-to-medium difficulty, weighted towards clarity and working code. This book's [`examples/`](../examples/README.md) are good practice material.

1. Given a CSV of insurance claims, report per column: null rate, distinct count, top five values and inferred type. Treat `N/A`, `unknown` and empty strings as missing. *(Compare [`examples/data-profiler/`](../examples/data-profiler/).)*
2. Two files list customers from a CRM and a billing system with no shared ID. Write code to propose matches. How do you avoid comparing every pair? How do you know it works? *(Compare [`examples/record-linkage/`](../examples/record-linkage/).)*
3. Parse a log file of API requests and return the p50 and p95 latency per endpoint, ignoring malformed lines (and counting them).
4. Given JSON order events that may arrive out of order and more than once, compute each order's final status. Make it idempotent.
5. A date column mixes `DD/MM/YYYY` and `MM/DD/YYYY`. Write a function to normalise it, and decide what to do with ambiguous values.
6. Implement a client for a paginated REST API with rate limiting: follow cursors, retry with exponential backoff on 429 and 5xx, and stop on 4xx.
7. Write a small HTTP service with one endpoint that validates input and returns a structured error for bad requests.
8. Given field reports tagged with free text, group reports that describe the same need and count distinct customers per group. *(Compare [`examples/feedback-tracker/`](../examples/feedback-tracker/).)*
9. Write SQL: for each policy, the most recent claim and the number of claims in the last 12 months. Then rewrite it with a window function.
10. Given a list of evaluation results with tags, compute the pass rate per tag and flag any tag that dropped more than five points between two runs. *(Compare [`examples/llm-eval-harness/`](../examples/llm-eval-harness/).)*
11. Write a function that builds a context string from retrieved documents, labelling each with its ID and stopping at a character budget.
12. Here is a 200-line function from a customer's codebase. Explain what it does, then add a test that would catch the bug we tell you about.

**What good looks like.**

- Asks a few clarifying questions about inputs, scale and edge cases before typing.
- Gets a simple correct version working first, then improves it.
- Handles messy data **explicitly**: counts and reports bad rows instead of silently dropping them ([Chapter 10 §10.4](../chapters/10-enterprise-data.md)).
- Names things clearly, writes small functions, and adds a test or two.
- Thinks aloud and explains trade-offs (memory versus streaming; precision versus recall for matching).
- Mentions what production would need (logging, idempotency, retries) without gold-plating the exercise.

---

## D.3 Decomposition

The signature FDE round, especially at Palantir. Third-party guides describe it as roughly an hour, sometimes with live modelling or code; interviewers may add a requirement partway through. The method is [Chapter 5 §5.7](../chapters/05-discovery-and-decomposition.md); the canvas is [`templates/problem-decomposition-canvas.md`](../templates/problem-decomposition-canvas.md).

### Prompts

1. A hospital wants to reduce emergency department wait times. How would you help?
2. An insurer wants to "use AI to speed up claims".
3. A city wants to reduce the time potholes stay unrepaired.
4. A logistics company wants fewer late deliveries.
5. A bank's operations team handles 4,000 payment exceptions a week and wants to halve the effort.
6. An airline wants to reduce aircraft time out of service for maintenance.
7. A retailer has five regional warehouses and keeps running out of stock in some while overstocked in others.
8. A food bank network wants to reduce food waste.
9. A national charity wants to match volunteers to opportunities better.
10. A manufacturer wants to predict and reduce supplier delays.
11. A government agency wants to detect fraudulent benefit claims without wrongly denying genuine ones.
12. A law firm wants to cut the time associates spend on first-pass contract review.

### Typical mid-interview twists

- "The data you assumed doesn't exist. What now?"
- "The sponsor has just left. Who do you talk to?"
- "Now add a second hospital with a different system."
- "Legal says no patient data may leave the building."
- "You have two weeks, not three months. What ships?"

### What a strong answer looks like

A strong answer follows a recognisable structure and adapts when challenged ([Chapter 19 §19.3](../chapters/19-career.md)):

1. **Clarifies the goal and who cares about it** before proposing anything.
2. **Defines a measurable outcome** and how to baseline it.
3. **Breaks the outcome into drivers** (where does the time, cost or error come from?), by business driver rather than by technology.
4. **Identifies users, decisions and data** for each driver.
5. **Sketches a data model**: key objects, properties and relationships.
6. **Proposes a first slice** that delivers value soon and extends naturally, ranked on value, feasibility and risk ([Chapter 5 §5.8](../chapters/05-discovery-and-decomposition.md)).
7. **Names risks**: data access, privacy, adoption, safety, fairness.
8. **Adapts** when the problem changes: the structure bends rather than breaks.

Common failures: treating it as a consulting case (frameworks, no data or system thinking); jumping straight to implementation; anchoring on "build a model"; ignoring the human workflow; boiling the ocean.

### Worked guidance for three prompts

**Prompt 1: emergency department wait times.**

- *Clarify:* wait from arrival to what (triage, first clinician, decision, admission or discharge)? Which patients? Who is the sponsor (operations director, clinical lead)? Any national targets in play (for example a four-hour standard)?
- *Outcome:* median and 95th-percentile time from arrival to departure, baselined from the patient administration system's timestamps.
- *Drivers:* arrival to triage; triage to first assessment; waiting for diagnostics (bloods, imaging); waiting for specialist review; waiting for an inpatient bed (often the largest, and driven by discharges elsewhere in the hospital).
- *Data model:* `Patient`, `Attendance`, `TriageEvent`, `Order` (test), `Result`, `Bed`, `Ward`, `Discharge`, `StaffShift`, linked by attendance and time.
- *First slice:* often **not** in the department at all. A live view of expected discharges and bed availability for the bed-management team, or a flag on patients whose diagnostics are complete but who have not been reviewed. Both are quick, need no prediction, and attack the biggest driver.
- *Risks:* clinical safety governance, patient data staying in the hospital network ([Chapter 14 §14.6](../chapters/14-security-and-restricted-environments.md)), clinicians' trust in scores (show reasons, not scores, as in [Chapter 20 §20.4](../chapters/20-case-studies.md)), and record linkage across systems.
- *Twist ("no data may leave the building"):* move to an on-premises or air-gapped design, self-hosted models, bundled releases. The decomposition stays the same; the architecture changes.

**Prompt 2: "use AI to speed up claims".**

- *Reframe:* the goal is cycle time, not AI. Ask what the COO is measured on.
- *Drivers:* triage, coverage clarification, assessment, approval queues ([Chapter 5 §5.7](../chapters/05-discovery-and-decomposition.md)).
- *Slices:* a coverage summary with citations (AI, retrieval over policy wordings); **auto-approval below a threshold with audit and sampling review (rules, no AI)**; a queue dashboard.
- *Strong signal:* the candidate notices that the non-AI slice may deliver half the value faster, as in the Northwind case ([Chapter 20 §20.1](../chapters/20-case-studies.md)), and proposes success criteria at three levels: business outcome, adoption and system quality ([Chapter 6 §6.3](../chapters/06-scoping.md)).

**Prompt 11: benefit fraud without wrongly denying genuine claims.**

- *Clarify the costs of each error:* a missed fraud versus a wrongly delayed or denied claim. These are not symmetric, and the second harms vulnerable people.
- *Outcome:* fraud losses detected, **and** false-positive rate and time-to-payment for genuine claims, measured together.
- *Design:* risk signals route claims to **human** investigators with reasons and evidence; nothing is denied automatically. Evaluate by segment for fairness; provide appeal routes ([Chapter 18 §18.5](../chapters/18-life-as-an-fde.md)).
- *Strong signal:* the candidate raises legitimacy, proportionality, accountability and applicable regulation (for example high-risk classification under the EU AI Act) without being prompted, and still produces a buildable plan.

---

## D.4 Learning

Palantir and some other companies test how fast you learn something unfamiliar: candidate reports describe being taught a new concept, API or simple query language during the interview, then asked to use it ([Chapter 19 §19.3](../chapters/19-career.md)). Example formats:

1. Here is the documentation for a small query language we invented. Write queries to answer these five questions.
2. Here is an unfamiliar API (with a short reference). Use it to build a small feature.
3. We'll explain a domain concept (for example reinsurance treaties, aircraft maintenance intervals or clinical coding). Now model it as objects and relationships.
4. Here is a codebase in a language you don't use. Find where a value is calculated and change it.
5. We'll teach you a statistical idea (for example difference-in-differences). Apply it to this small dataset.
6. Read this two-page specification and tell us what's ambiguous in it.

**What good looks like.** Asks clarifying questions and restates the concept in their own words; starts with simple uses and builds up; thinks aloud so the interviewer can see the mental model forming; treats the interviewer as a resource, the way they would treat a customer expert; notices and tests their own misunderstandings rather than bluffing. Speed matters less than a visible, self-correcting learning process.

---

## D.5 System design and integration

Use Part III of the book as your checklist: data ([Chapter 10](../chapters/10-enterprise-data.md)), extension choices ([11](../chapters/11-configure-extend-change.md)), AI architecture ([12](../chapters/12-ai-deployment.md)), evaluation ([13](../chapters/13-evaluation-and-impact.md)), security ([14](../chapters/14-security-and-restricted-environments.md)) and operations ([15](../chapters/15-production-and-handover.md)).

1. Design a system that lets a bank's analysts ask questions over their internal documents, respecting permissions.
2. Integrate our platform with a customer's ERP to keep supplier data in sync. The ERP has a SOAP API, nightly exports and no webhooks.
3. A customer wants one view of each of its customers across CRM, billing and support systems. Design it, including how you'd keep it current.
4. Deploy our product into a customer's own cloud tenancy with no public internet access. What changes?
5. Design the deployment of an AI system into an air-gapped government network. How do you ship updates and diagnose problems?
6. The customer needs an approval step our product doesn't support. Walk me through your options. *(Expect the build ladder: question the need, configure, extend, build alongside, change the product, decline; [Chapter 11 §11.2](../chapters/11-configure-extend-change.md).)*
7. A pilot ran on weekly CSV extracts. Design the production data path.
8. How would you design the monitoring and support model for a system you're about to hand over?
9. Design a pipeline that ingests 2 million scanned invoices a year, extracts fields and reconciles them against purchase orders.
10. The customer's policy database is at 80% CPU at peak and the DBA won't allow analytical queries. How do you get the data you need?

**What good looks like.** Starts with users, the business outcome and constraints (volume, latency, freshness, residency, security) before boxes and arrows. Prefers supported interfaces and the lowest rung of the build ladder. Plans access, identity (SSO, SCIM, acting as the user), data quality and lineage. Mentions evaluation, observability, rollback and handover unprompted. Records key trade-offs as decisions (an ADR mindset). Knows that in enterprises a firewall rule or TLS-rewriting proxy is a likely cause of "the integration doesn't work" ([Chapter 9 §9.5](../chapters/09-toolkit.md)).

---

## D.6 AI deployment

1. When would you use RAG, fine-tuning, a workflow with one model step, or an autonomous agent? How do you choose?
2. How do you stop a RAG system leaking documents a user isn't allowed to read? Why is filtering after generation too late? *(Security trimming; [Chapter 12 §12.4](../chapters/12-ai-deployment.md).)*
3. A user says the assistant gave a wrong answer. How do you find out whether retrieval or generation failed?
4. Design the tools for an agent that resolves payment exceptions. What would you refuse to give it?
5. Explain prompt injection to a bank's CISO, and the controls you'd put in place.
6. What is the lethal trifecta, and how would you break it for an email-triage agent?
7. How would you build an evaluation set for a contract-review assistant? Who labels it, and how do you know the labels are reliable?
8. When is an LLM judge acceptable as a release gate?
9. Your eval pass rate is 91%. Is that good enough to launch?
10. A new model version is released. How do you decide whether to upgrade?
11. Estimate the monthly model cost for 20,000 questions a month with 8,000 input and 500 output tokens each. What would make it ten times higher?
12. How would you measure whether the system actually reduced handling time, not just whether people liked it?
13. Where would you put humans in the loop, and how would you reduce review over time?
14. The customer wants to use a third-party MCP server they found online. What do you check?

**What good looks like.**

- Chooses the **least autonomous pattern** that delivers the value and earns autonomy with evidence (shadow mode, approvals, sampled auto-execution) ([Chapter 12 §12.3](../chapters/12-ai-deployment.md), [Chapter 20 §20.2](../chapters/20-case-studies.md)).
- Designs so that **a fully compromised model can do only limited, recoverable, logged harm**: business-level tools, validation, allow-lists, approvals, budgets, user permissions, audit logs.
- Talks about evaluation **first**: real cases, slices, refusal cases, rubrics, expert agreement, validated judges, component evaluation (recall at k), regression gating ([Chapter 13](../chapters/13-evaluation-and-impact.md)).
- Answers "is 91% good enough?" with "it depends": on the cost of errors, whether a human checks with citations, and how it fails by slice (the Northwind commentary in [Chapter 20 §20.1](../chapters/20-case-studies.md)).
- Distinguishes evaluation from impact measurement, and knows a control group or difference-in-differences beats before-and-after.
- Pins model versions, re-runs evals before upgrading, and dates any product or price claims.

---

## D.7 Customer simulation (role-plays)

The interviewer plays a customer. These test judgement, honesty and composure as much as content. Prepare by re-reading [Chapters 6–8](../chapters/06-scoping.md).

1. **The sceptical expert.** "I've been an underwriter for 25 years. Your system got this case wrong, and I don't trust any of it."
2. **Scope creep.** The operations manager, delighted with week 4's demo, asks for three new features "by the go-live date".
3. **The failing demo.** Halfway through a demo to the sponsor's boss, the system returns an error.
4. **Bad news.** You must tell the sponsor the week-8 milestone will slip because API access is two weeks late.
5. **The unsafe shortcut.** "Just write the results straight to the ledger. Security approval will take weeks; nobody will notice."
6. **The jobs question.** A front-line user asks: "Is this thing going to replace me?"
7. **Sales pressure.** Your account executive asks you to tell the customer the product does something it doesn't yet do.
8. **Conflicting stakeholders.** Operations wants automatic approvals; compliance wants every payment reviewed.
9. **The new sponsor.** The sponsor who championed the project has left; you have 20 minutes with her replacement.
10. **The fork request.** A strategic customer wants a change to the product's core data model "just for us".
11. **Post-handover call.** Six months after handover, a customer engineer messages you directly about an outage.

**What good looks like.**

- **Listens first** and acknowledges the need or feeling behind the request; asks to see the case ("Let's look at what the system saw") rather than arguing ([Chapter 8 §8.9](../chapters/08-communication.md)).
- **Tells the truth** about the product, the schedule and their own authority ("I don't make staffing decisions"; leaves job messages to the customer's leadership, [Chapter 7 §7.7](../chapters/07-stakeholders.md)).
- **Bad news structure:** state it plainly, brief cause without blame, impact, options with a recommendation, the ask ([Chapter 8 §8.9](../chapters/08-communication.md)).
- **Says no with an alternative** and points to the agreed process: the later list and change control for scope ([Chapter 6 §6.9](../chapters/06-scoping.md)); a reviewed export instead of an unapproved ledger write.
- **Makes decisions possible** in conflicts rather than taking sides: understand interests, design for both (threshold plus audit plus sampling), write options down, escalate to the decider ([Chapter 7 §7.9](../chapters/07-stakeholders.md)).
- **Protects the product** without stonewalling: configure, extend or field-report rather than fork ([Chapter 11](../chapters/11-configure-extend-change.md)).
- **Re-sells to a new sponsor** from their goals, with results so far ([Chapter 7 §7.10](../chapters/07-stakeholders.md)).
- **After handover:** helps them reach the agreed support path, rather than becoming a personal support tier ([Chapter 15 §15.6](../chapters/15-production-and-handover.md)).
- Stays calm, concise and kind when the interviewer pushes.

---

## D.8 Behavioural (STAR)

Answer with specific stories structured as **situation, task, action, result**, with numbers, and a reflection on what you learned. Prepare six to eight stories that can flex across questions ([Chapter 19 §19.3](../chapters/19-career.md)).

1. Tell me about a time you delivered with incomplete information.
2. Tell me about a time you won over a sceptic.
3. Tell me about a time you had to deliver bad news.
4. Tell me about a time you said no to a customer, colleague or manager.
5. Tell me about a technical decision you'd make differently now.
6. Tell me about a time you turned something one-off into something reusable.
7. Tell me about a time you got productive quickly in an unfamiliar codebase or domain.
8. Tell me about a project that failed. What was your part in it?
9. Tell me about a time you discovered that the problem you were asked to solve wasn't the real problem.
10. Tell me about a time you were asked to cut a corner on security, privacy or quality.
11. Tell me about a time you disagreed with someone more senior, and what happened.
12. Tell me about a time you managed several competing priorities under pressure.
13. Tell me about a time something you built went wrong in production.
14. Tell me about a time you made other people successful.
15. Tell me about a time you had an ethical concern about your work.
16. How do you sustain yourself through intense periods? What are your warning signs?

**What good looks like.** Specific, recent, first-person stories ("I", not only "we") with measurable results; honest about mistakes and what changed afterwards; shows ownership without heroics. Strong candidates show the behaviours in [Chapter 7 §7.5](../chapters/07-stakeholders.md) (shipping early, keeping small promises, bringing bad news early with a plan, giving credit away) and the ethical reasoning of [Chapter 18 §18.5](../chapters/18-life-as-an-fde.md): purpose, legitimacy, proportionality, fairness, transparency, accountability, and knowing when to escalate. Weak answers are hypothetical ("I would…"), vague, or blame others.

---

## D.9 Questions to ask the employer

Use these to test whether the role is a genuine FDE role and whether it is sustainable ([Chapter 1 §1.5–1.6](../chapters/01-the-role.md), [Chapter 17](../chapters/17-running-an-fde-org.md), [Chapter 18](../chapters/18-life-as-an-fde.md)).

**The role**

1. What did the last FDE who joined ship to production in their first six months?
2. What share of time is pre-sale (demos, pilots) versus post-sale delivery?
3. How long is a typical engagement, and how many engagements does one FDE work on at once?
4. How much travel, in numbers? How much on site versus remote?
5. Are FDEs held to the same hiring bar as product engineers?

**The feedback loop**

6. How do field reports reach the product team? Can you give an example of field work that became a product feature?
7. Can FDEs contribute to the product codebase?
8. Is there a product liaison, field council or productisation budget?

**The business**

9. How is FDE work paid for: bundled, paid pilots, SOWs, or partners?
10. Is the function measured on utilisation or billable hours? *(If yes, it may be professional services; [Chapter 3](../chapters/03-business.md).)*
11. How do engagements end? Who takes over the systems FDEs build?

**Growth and sustainability**

12. Where does the FDE team report, and what is the career ladder? Are levels and pay at parity with product engineering?
13. Where have FDEs here gone next?
14. What protects people from burnout: travel limits, rotations, breaks between engagements?
15. How are ethical concerns about a customer or use case raised and handled?

**What good looks like (in their answers).** Concrete examples of production systems and productised field work; a direct channel to product; planned engagement exits; travel stated in numbers; levelling parity; sustainable-pace policies; and an honest account of the hard parts. Vague answers about the loop to product, or heavy emphasis on utilisation, suggest a relabelled solutions or services role.
