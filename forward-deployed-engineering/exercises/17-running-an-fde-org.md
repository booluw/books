# Exercises: Chapter 17, [Building and Running an FDE Organisation](../chapters/17-running-an-fde-org.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional and all figures illustrative.

## Questions

1. **Concept.** List the four questions in §17.1 that a company should answer before starting an FDE function. For each, describe what typically goes wrong if it is left unanswered.

2. **Scenario.** Litware, a 120-person legal-AI start-up, has just signed its first three enterprise customers and asks you to set up an FDE function. The chief revenue officer wants FDEs in the sales team "so they're close to deals"; the chief technology officer wants them in engineering. Recommend a reporting line, a team structure for the first year (§17.3), and the first six steps from §17.2. Say which two things you would protect whatever the reporting line.

3. **Calculation.** You run a team of 12 FDEs. Two joined this month and are in product immersion, so they have no engagement capacity for the next quarter. You keep 15% of the remaining capacity in reserve (§17.6). Six requests are in the intake queue:

   | Request | FDEs needed (full-time equivalent) | Value at stake | Probability of success | Learning value for the product |
   |---|---|---|---|---|
   | A. Woodgrove Bank production rollout | 3 | £2,400,000 | 0.8 | High (first regulated bank) |
   | B. Contoso Insurance expansion to a second line of business | 2 | £1,200,000 | 0.7 | Medium |
   | C. Adventure Works unpaid pilot (pre-sale) | 2 | £600,000 | 0.4 | Low |
   | D. Fabrikam renewal at risk | 1.5 | £900,000 | 0.6 | Medium |
   | E. Wide World Importers new use case | 2 | £500,000 | 0.75 | High (new connector pattern) |
   | F. Northwind Traders demo requested by an account executive | 1 | £300,000 | 0.2 | Low |

   - (a) How much engagement capacity do you have?
   - (b) Compute expected value (value × probability) and expected value per FDE for each request.
   - (c) Allocate capacity, and say what happens to each request you don't staff.
   - (d) An account executive offers to "make it work" by splitting two FDEs across three engagements each. What do you say?

4. **Calculation.** Two years of data for an FDE function (fully loaded cost £200,000 per FDE a year):

   | | Year 1 | Year 2 |
   |---|---|---|
   | FDEs | 15 | 22 |
   | ARR from FDE-deployed customers | £18,000,000 | £24,000,000 |
   | Average FDE utilisation | 81% | 94% |
   | Customer satisfaction (out of 10) | 8.1 | 8.6 |
   | FDE attrition | 7% | 23% |

   - (a) Compute FDE cost as a percentage of ARR, and revenue per FDE, for both years, and the growth rates of ARR and headcount.
   - (b) The CEO reads the utilisation and satisfaction rows and calls year 2 a success. Write your reply, naming the failure modes from §17.10 you suspect and the metrics you would add.

5. **Hands-on.** Use `build_deal()` in [`../examples/impact-calculator/impact.py`](../examples/impact-calculator/impact.py) to model one customer two ways: ACV of $800,000, $1,200,000 and $1,500,000 over three years, platform cost 20% of ACV, FDE loaded cost $350,000. In plan 1, two FDEs are on the account full-time in year 1 and 1.5 FDEs stay on in years 2 and 3 (a "permanent resident"). In plan 2, FDE effort falls to 0.5 after handover. Report gross margin by year and over three years, and write two sentences to the head of FDE about what the difference implies. (Hint: `fde_plan=[(2, 1.0), (1.5, 1.0), (1.5, 1.0)]`.)

6. **Scenario.** Design a five-stage interview loop for Litware's first FDE hires (question 2), and write a scoring rubric for the decomposition round with four criteria and what a "strong" and a "weak" answer looks like for each. Say which signals from §17.4 you would deliberately *not* weight heavily.

7. **Scenario.** For each set of symptoms, name the failure mode from §17.10 and the first two remedies you would apply.
   - (a) Tailspin Toys' vendor: FDEs spend most weeks building demo environments for prospects; under 20% of pilots convert.
   - (b) An FDE has been "temporarily" at Contoso Insurance for 22 months; Contoso's IT team calls her before calling the vendor's support line.
   - (c) FDEs are paid 15% less than product engineers at the same level and cannot merge to product repositories.
   - (d) The team's most celebrated story is an FDE who worked three nights straight to rescue a go-live.
   - (e) Two engagements in the same quarter: one delivered on time with a full handover pack; the other had no tests, no runbooks and an angry sponsor.

8. **Hands-on.** Take one completed retrospective written with [`../templates/engagement-retrospective.md`](../templates/engagement-retrospective.md) (your own, or the Wide World Importers case in [Chapter 20 §20.6](../chapters/20-case-studies.md) written up as one). Turn its sections 6 and 8 into concrete changes: one playbook change with a named section owner, one reusable asset, and one field report. Then design a monthly engagement health check: the columns of the red-amber-green table, the definition of red for each, and who attends.

## Solutions

1. - **What is the function for?** Unanswered, FDEs get pulled between pre-sale demos, delivery and discovery; metrics conflict and nobody can say whether the team is succeeding. The usual outcome is pre-sales captivity.
   - **How will it be paid for?** Unanswered, FDE time is either given away (margin collapses) or sold as hourly services (the team drifts into a consultancy). The pricing model (Chapter 3 §3.4) shapes customer expectations from the first meeting.
   - **How will it feed the product?** Unanswered, you build a consultancy: each customer's custom code is maintained forever and deployment effort never falls (Chapter 16).
   - **What is the exit path for each engagement?** Unanswered, FDEs become permanent residents and capacity is eaten by old accounts.

2. **Reporting line:** engineering (or a dedicated deployment organisation reporting to the CTO), with a strong, explicit link to sales. At this size the overriding risks are a slipping technical bar and FDEs becoming pre-sales support, both of which are more likely under sales. Give the CRO a seat in the intake process (question 3) rather than the reporting line.

   **Structure for year one:** one pod per customer while there are three customers, each pairing FDEs with an engagement lead or deployment strategist and a part-time product liaison; move to industry or practice-area alignment (for example litigation versus contracts) once patterns repeat.

   **First steps (§17.2):** hire two or three strong generalists (engineers who are comfortable with customers); treat the three signed customers as lighthouses and choose the first use case at each for achievability and visibility; write things down from day one (engagement plans, field reports, retrospectives); define the handoffs with sales, product and support; measure time to first value, deployment effort and expansion from the start; scale only once the playbook works.

   **Protect:** an engineering hiring bar equal to product engineering, and a direct channel to product.

3. (a) Productive FDEs = 12 − 2 = 10. Reserve = 15% × 10 = 1.5. **Engagement capacity = 8.5 FTE.** Demand is 3 + 2 + 2 + 1.5 + 2 + 1 = 11.5, so 3 FTE of requests cannot be staffed.

   (b) Expected value and expected value per FDE:

   | Request | Expected value | Per FDE |
   |---|---|---|
   | A | £2,400,000 × 0.8 = £1,920,000 | £640,000 |
   | B | £1,200,000 × 0.7 = £840,000 | £420,000 |
   | C | £600,000 × 0.4 = £240,000 | £120,000 |
   | D | £900,000 × 0.6 = £540,000 | £360,000 |
   | E | £500,000 × 0.75 = £375,000 | £187,500 |
   | F | £300,000 × 0.2 = £60,000 | £60,000 |

   (c) Staff **A (3), B (2) and D (1.5)** = 6.5 FTE, the three highest expected values per FDE. The remaining 2 FTE go to **E** rather than C: its expected value per FDE is higher (£187,500 against £120,000) and its learning value is high (a new connector pattern that will speed up later deployments, Chapter 16). Total 8.5 FTE.
   - **C:** don't staff as an unpaid pilot. Qualify it properly (Chapter 4 §4.2); offer a paid, scoped pilot next quarter or a smaller solutions-engineering proof.
   - **F:** route to solutions engineering; a demo is not FDE work.
   - Keep the 1.5 FTE reserve for escalations, productisation and training; don't spend it on C.

   (d) Decline. §17.6's norm is no more than two engagements per engineer, because context switching destroys productivity; six one-third allocations deliver far less than two engineers each focused on one engagement, and all three engagements run late. The honest answer to more demand than capacity is prioritisation (or hiring), not dilution.

4. (a) The figures:

   | | Year 1 | Year 2 |
   |---|---|---|
   | FDE cost | 15 × £200,000 = £3,000,000 | 22 × £200,000 = £4,400,000 |
   | FDE cost as % of ARR | £3.0M ÷ £18M = **16.7%** | £4.4M ÷ £24M = **18.3%** |
   | Revenue per FDE | £18M ÷ 15 = **£1,200,000** | £24M ÷ 22 = **£1,090,909** |

   ARR grew (24 − 18) ÷ 18 = **33.3%**; FDE headcount grew (22 − 15) ÷ 15 = **46.7%**.

   (b) "Customers are happier, but the function is getting less efficient and burning people out. FDE headcount is growing faster than revenue and FDE cost as a share of ARR is rising, which is the signature of **consultancy drift**: we are adding people per customer instead of product. 94% utilisation leaves no slack for productisation or escalations, and 23% attrition suggests a **heroics culture** or burnout (Chapter 18). High satisfaction may partly reflect over-servicing." Add: FDE-hours per deployment by segment, deployment time for the Nth customer, productisation rate, custom code per customer, overdue engagement exits, and team-health measures (travel load, survey results), and set a target utilisation that keeps the 10–15% reserve. §17.8's warning applies: each single metric pushes behaviour in a bad direction on its own.

5. Results (check with the calculator):

   | Year | ACV | Plan 1 FDE cost | Plan 1 margin | Plan 2 FDE cost | Plan 2 margin |
   |---|---|---|---|---|---|
   | 1 | $800,000 | $700,000 | **−7.5%** (gross profit −$60,000) | $700,000 | **−7.5%** |
   | 2 | $1,200,000 | $525,000 | 36.25% (the calculator prints 36.2%) | $175,000 | 65.4% |
   | 3 | $1,500,000 | $525,000 | 45.0% | $175,000 | 68.3% |
   | 3 years | $3,500,000 | | **30.0%** (gross profit $1,050,000) | | **50.0%** (gross profit $1,750,000) |

   For example, plan 2, year 2: $1,200,000 − $240,000 − $175,000 = $785,000, and 785,000 ÷ 1,200,000 = 65.4%.

   To the head of FDE: "Keeping 1.5 FDEs on this account after year 1 costs $700,000 of gross profit over three years and leaves us at a services-business margin of 30%; with a proper handover we reach 50% overall and software-like margins of 65–68% from year 2. Every engagement needs a planned exit date, and we should track overdue exits as a function-level metric."

6. **Loop:** (1) practical coding with messy data (parse, clean, aggregate, with error handling); (2) decomposition case (for example, "a law firm wants to reduce the time to prepare for litigation"); (3) learning round (teach a small unfamiliar API or query language and have the candidate use it); (4) system design and integration into a realistic enterprise (document permissions, security review, evaluation); (5) customer simulation plus values (a sceptical general counsel; a scope dispute). Include a current FDE on every panel, use structured rubrics and calibrate interviewers.

   **Decomposition rubric:**

   | Criterion | Strong | Weak |
   |---|---|---|
   | Clarifies the goal | Asks who cares and how success is measured before proposing anything | Jumps to "build a RAG chatbot" |
   | Structures the problem | Breaks the outcome into measurable drivers; sizes them | Lists technologies or a generic consulting framework |
   | Grounds it in data and users | Names the users, decisions and data for each driver; sketches a data model | Stays abstract; no data or system thinking |
   | Plans and adapts | Proposes a small first slice; names risks; restructures cleanly when the interviewer adds a requirement | One big-bang plan; the structure breaks or is defended when the problem changes |

   **Don't weight heavily:** knowledge of a specific framework (learnable) and polished sales presence (not the job).

7. - (a) **Pre-sales captivity.** Remedies: qualification criteria at intake; paid pilots with production decisions agreed up front; a separate solutions engineering team for demos.
   - (b) **Permanent resident.** Remedies: set an exit date and a handover plan now; enable Contoso's team (pairing, runbooks, unaided-operation period, Chapter 15) and move the support route to the vendor's support line.
   - (c) **Second-class citizens.** Remedies: levelling and pay parity with product engineering; shared code ownership with product-team review. (Also check the hiring bar is the same.)
   - (d) **Heroics culture.** Remedies: celebrate boring reliability and early escalation instead; capacity planning with reserve, and sustainable-pace policies. Also run a blameless review of why the rescue was needed.
   - (e) **Inconsistent quality.** Remedies: a living playbook with templates and examples; design reviews, cross-engagement code review and a standard readiness gate (Chapter 15). Strengthen onboarding so new FDEs learn the standard.

8. From the Wide World Importers case, for example: **playbook change:** "Name the receiving team in week 1 and invite them to stand-ups", added to the kick-off checklist, owned by the head of delivery; **reusable asset:** the "new invoice layout" runbook and its evaluation-case procedure, generalised into the document-extraction reference architecture; **field report:** one of the two product gaps the FDEs found, written with the field-report template and checked against the tracker for other instances.

   **Health check:** one row per engagement, with columns for: success criteria progress, schedule against plan, sponsor health, access and dependencies, technical risk, team load (travel, hours), exit date and handover readiness, and commercial status. Define red for each, for example: no measurable progress for two weeks; more than two weeks behind with no recovery plan; sponsor absent or changed; a blocking access request older than three weeks; an FDE above agreed travel limits; exit date passed or no receiving team named; renewal at risk. Attendees: FDE leadership, engagement leads, a product liaison and someone from sales or customer success, monthly, with actions owned and followed up the next month.
