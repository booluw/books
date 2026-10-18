# Exercises: Chapter 3, [The Business of Forward Deployment](../chapters/03-business.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional and all figures illustrative.

## Questions

1. **Concept.** Define gross margin. Why does counting FDE salaries as cost of revenue pull an FDE-heavy company's gross margin towards services levels, and what three conditions must hold for the model in §3.2 to work?

2. **Calculation.** Wide World Importers signs a three-year deal for an AI logistics platform. Platform delivery cost is 20% of ACV each year. An FDE costs $320,000 a year fully loaded.

   | Year | ACV | FDE effort |
   |---|---|---|
   | 1 | $400,000 | 1.5 FDEs at 60% of their time |
   | 2 | $900,000 | 0.5 FDE |
   | 3 | $1,400,000 | 0.25 FDE |

   (a) Compute the gross margin for each year and for the three years combined. (b) Recompute years 2 and 3, and the three-year figure, if FDE effort never falls (it stays at 1.5 × 60% every year). (c) What does the comparison tell you?

3. **Calculation.** Fabrikam's FDE function has 12 FDEs, each costing $350,000 fully loaded, supporting $21M of ARR from FDE-deployed customers. A year later it has 15 FDEs supporting $30M. (a) Compute ARR per FDE and FDE cost as a percentage of ARR for both years. (b) How many FDEs would Fabrikam have needed in year 2 if headcount grew linearly with revenue? (c) Is the trend healthy?

4. **Scenario.** Classify each observation at Contoso AI as a sign of a healthy or unhealthy FDE model, and explain briefly.
   - (a) The fifth hospital deployment took 6 weeks; the first took 7 months.
   - (b) Each of Contoso's 14 customers has its own branch of the core repository.
   - (c) Two FDEs have been assigned full time to the same bank for three years to "keep things running".
   - (d) Last quarter, four connectors built in the field were merged into the product.
   - (e) The product roadmap was set at an offsite without reading any field reports.

5. **Scenario.** Choose a commercial model from §3.4 for each situation and justify it.
   - (a) Woodgrove Bank's chief operating officer wants to see the platform work on real data before committing to a three-year licence, and her procurement team distrusts free trials.
   - (b) A government agency wants the vendor to build a system, run it for a year, then have its own team operate it.
   - (c) Northwind Traders will only pay for "tickets resolved without a human".
   - (d) The vendor has 400 mid-market customers with $30,000 ACV each and wants all of them deployed within a year.

6. **Scenario.** Week 3 at Adventure Works. The plant director asks you to add a custom "shift supervisor sign-off" step directly into the product's core workflow engine, "just for us, just this once". Walk through how the agency trap would start here, and what you would do instead, using §3.6.

7. **Hands-on.** Use [`../examples/impact-calculator/`](../examples/impact-calculator/) to reproduce the three-year table in §3.2 (ACV $600k, $1.5M, $2.5M; platform cost 20%; FDE cost $350k then $175k). Then model a pessimistic scenario in which the customer expands only to $900k in year 2 and stays flat in year 3. Write two sentences for your FDE lead on what each scenario implies about how much FDE effort this customer justifies.

8. **Concept.** Summarise the "trading margin for moat" and "if you need FDEs, your product doesn't work" positions in two sentences each. Then state the synthesis question from §3.3 and explain why it is more useful than either position.

## Solutions

1. **Gross margin** = (revenue − cost of delivering the product) ÷ revenue. Software companies commonly run at 70–80% or more; services businesses at around 30–40%. FDE salaries are large, recurring and scale with customers, so counting them as cost of revenue pushes the ratio down, often to services levels in early years.

   The model in §3.2 works only if (a) customers **expand** substantially; (b) **FDE effort per customer falls** over time; and (c) what FDEs build becomes **reusable product** for the next customer. If any one fails, the business becomes a low-margin consultancy.

2. (a) Base case:

   | Year | ACV | Platform (20%) | FDE cost | Gross profit | Gross margin |
   |---|---|---|---|---|---|
   | 1 | $400,000 | $80,000 | 1.5 × 0.6 × $320,000 = $288,000 | $32,000 | **8.0%** |
   | 2 | $900,000 | $180,000 | 0.5 × $320,000 = $160,000 | $560,000 | **62.2%** |
   | 3 | $1,400,000 | $280,000 | 0.25 × $320,000 = $80,000 | $1,040,000 | **74.3%** |
   | Total | $2,700,000 | | | $1,632,000 | **60.4%** |

   (b) FDE effort never falls ($288,000 every year):

   | Year | Gross profit | Gross margin |
   |---|---|---|
   | 1 | $32,000 | 8.0% |
   | 2 | $900,000 − $180,000 − $288,000 = $432,000 | **48.0%** |
   | 3 | $1,400,000 − $280,000 − $288,000 = $832,000 | **59.4%** |
   | Total | $1,296,000 on $2,700,000 | **48.0%** |

   (c) Year 1 is nearly break-even at the gross-profit line in both cases: that is the price of landing. The difference between a software-like and a services-like customer is whether FDE effort falls. Holding expansion constant, failing to reduce FDE involvement costs $336,000 of gross profit over three years and 12.4 percentage points of margin. The FDE's job therefore includes making themselves less necessary: hand over, train the customer team and productise.

3. (a)

   | | Year 1 | Year 2 |
   |---|---|---|
   | FDE cost | 12 × $350,000 = $4.2M | 15 × $350,000 = $5.25M |
   | ARR per FDE | $21M ÷ 12 = **$1.75M** | $30M ÷ 15 = **$2.0M** |
   | FDE cost as % of ARR | $4.2M ÷ $21M = **20.0%** | $5.25M ÷ $30M = **17.5%** |

   (b) Linear growth: 12 × ($30M ÷ $21M) ≈ **17.1 FDEs**, so roughly 17.

   (c) **Healthy, modestly.** Revenue grew 43% while headcount grew 25%, so ARR per FDE rose and FDE cost as a share of ARR fell. Check two things before celebrating: whether the new revenue came from expansion at existing customers (cheap to serve) or from new logos still in heavy deployment (which could reverse the trend next year), and whether deployment time for new customers is also falling (§3.2's last metric).

4. - (a) **Healthy.** Deployment time for the Nth customer in a segment is falling, which means patterns are becoming product.
   - (b) **Unhealthy.** A bespoke codebase per customer is the defining symptom of the agency trap; upgrades and fixes multiply by 14.
   - (c) **Unhealthy.** Permanent maintenance assignments mean the system was never handed over or productised.
   - (d) **Healthy.** Field work is becoming product; this is the productisation rate in action.
   - (e) **Unhealthy.** A roadmap that ignores field reports breaks the feedback loop that justifies the cost of FDEs.

5. - (a) **Paid pilot (proof of value)**, ideally with the fee credited against the licence if she signs. It gives her real-data proof, gives procurement a commitment they trust more than a free trial, and filters out unserious buyers. Agree success criteria and the production decision in advance (Chapter 6 §6.10).
   - (b) **Build-operate-transfer.** The end state (customer team operating) is explicit. The risk is that the customer team is not capable on transfer day, so build training and a supervised operation period into the plan (Chapter 4 §4.8).
   - (c) **Outcome-based.** It aligns incentives, but the vendor carries the risk and the measurement must be defined precisely: what counts as "resolved", over what period, and what about reopened tickets? Expect disputes unless the definition is agreed and measurable from system data.
   - (d) **Partner-delivered (and largely self-serve).** At $30,000 ACV, FDE time cannot be justified per customer (§3.5: small ACV favours self-serve and partners). Vendor FDEs should build templates and certify partners rather than deploy directly.

6. **How the trap starts:** you build the sign-off step inside a customer-specific copy of the workflow engine because it is quick (step 2 of §3.6). The next manufacturer wants a sign-off with two levels; another one-off follows. Each one-off needs re-testing at every product release; upgrades break them; Adventure Works falls behind the main product; your time goes on maintenance (steps 3–5).

   **What to do instead:**
   1. **Question the need** (Chapter 11, rung 0): what problem does the sign-off solve? Perhaps an audit requirement that an existing approval rule and audit log already satisfy.
   2. **Configuration first:** most workflow engines support approval steps or rules; use them.
   3. **Extension points, not forks:** if configuration cannot do it, implement it through a supported extension (a webhook or plugin), never by modifying the core.
   4. **Rule of three:** write a field report; if two more manufacturers need supervisor sign-off, it becomes a product feature.
   5. **No orphan code:** whatever you build has a named owner and support plan.

   Say this to the plant director as a benefit: "Doing it this way means your sign-off survives every product upgrade."

7. Expected reproduction (base case): gross profit $130k, $1,025k and $1,825k; margins 22%, 68% and 73%; three-year margin ≈ 65% ($2.98M on $4.6M).

   Pessimistic scenario (ACV $600k, $900k, $900k; platform 20%; FDE $350k then $175k):

   | Year | ACV | Platform | FDE | Gross profit | Margin |
   |---|---|---|---|---|---|
   | 1 | $600k | $120k | $350k | $130k | 21.7% |
   | 2 | $900k | $180k | $175k | $545k | 60.6% |
   | 3 | $900k | $180k | $175k | $545k | 60.6% |
   | Total | $2.4M | | | $1.22M | 50.8% |

   (The calculator may present results differently; the arithmetic above is what it should agree with.)

   Model note: "In the base case, heavy year-1 FDE investment pays back through expansion, and a three-year margin of about 65% is close to software levels. In the pessimistic case, margin settles near 51–61%, so we should cut FDE involvement faster (handover and partner support by year 2) unless there is a credible next use case to justify continued investment."

8. - **Trading margin for moat:** services-heavy early revenue is a deliberate investment, because embedding with customers produces data, workflows and trust that become defensible over time; Palantir is the canonical example. In new categories somebody must do the deployment, and if the vendor does it, the vendor learns.
   - **"If you need FDEs, your product doesn't work":** persistent forward deployment hides product weakness and produces consultancy-like margins and valuations; Decagon's product-led bet is the counter-example cited. It can also make customers dependent on vendor engineers and limit growth to hiring speed.
   - **Synthesis question:** "Do our services make the product more repeatable, reusable and defensible over time?" It is more useful because it is **testable**: you can measure whether FDE effort per customer falls, whether deployment time falls, and whether field work becomes product. Both slogans are true of some companies; the question tells you which kind you are.
