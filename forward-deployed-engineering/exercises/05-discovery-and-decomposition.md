# Exercises: Chapter 5, [Discovery and Problem Decomposition](../chapters/05-discovery-and-decomposition.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional and all figures illustrative.

## Questions

1. **Concept.** Rewrite each interview question so that it asks about the past and produces facts rather than polite agreement. Explain what was wrong with each original.
   - (a) "Would you use a tool that flagged risky invoices?"
   - (b) "How long does reconciliation usually take?"
   - (c) "Do you think the current process works well?"
   - (d) "If we built an AI assistant, what features would you want?"

2. **Scenario.** You shadow two accounts-payable clerks at Fabrikam for a morning. List five specific things you would look for that interviews would probably miss, with an example of what each might look like in accounts payable.

3. **Scenario.** Wide World Importers' operations director says: "We want AI to reduce late shipments." Decompose this goal using the eight-step method in §5.7. Assume: on-time delivery is 82% against a 95% target; late shipments break down as 35% customs-documentation errors, 25% carrier capacity shortfalls, 20% late supplier handover, and 20% warehouse picking delays. Produce a decomposition tree (as text or Mermaid) with at least five candidate sub-solutions, and say which are not AI.

4. **Calculation.** (a) Verify the chapter's example: 60 adjusters × 3 hours a week × 46 weeks × £45 an hour. (b) Fabrikam's accounts-payable team: 25 clerks would each save 4 hours a week, over 46 working weeks, at a loaded cost of £38 an hour. Separately, the system would prevent about 60 payment errors a year at an average cost of £900 each. Compute the annual value. (c) Fabrikam's finance director says only half of the time saving is cashable, because clerks will be redeployed to supplier-query work rather than overtime falling. Recompute a conservative figure and explain how you would present both numbers.

5. **Scenario.** Score these four candidate first use cases at Woodgrove Bank and choose the lighthouse. Explain your choice and what you would do about the others.

   | Candidate | Value (£/yr) | Data feasibility | Technical feasibility | Organisational feasibility | Weeks to first result | Risk |
   |---|---|---|---|---|---|---|
   | A. Automated credit decisions for small-business loans | 1,200,000 | Medium | Medium | Low (credit committee opposed) | 20 | High |
   | B. Summaries of commercial loan files for relationship managers | 350,000 | High | High | High (champion in place) | 5 | Low |
   | C. Complaints classification and routing | 220,000 | High | High | Medium | 4 | Low |
   | D. Fraud-pattern detection across all payments | 900,000 | Low (eight systems, no access yet) | Medium | Medium | 26 | Medium |

6. **Concept.** Identify the pitfall from §5.7 in each draft decomposition and suggest a fix.
   - (a) Northwind's goal "improve customer retention" decomposed as: data ingestion, feature store, churn model, dashboard.
   - (b) "Reduce stock-outs" decomposed into 34 sub-problems covering every product line, warehouse and supplier, all to be delivered together.
   - (c) "We need a chatbot for our HR policies" decomposed as: chatbot UI, policy ingestion, LLM selection.
   - (d) A model predicting which deliveries will be late, displayed on a report emailed weekly to a regional manager who has no authority to reroute shipments.

7. **Hands-on.** Using [`../templates/discovery-guide.md`](../templates/discovery-guide.md), prepare a discovery plan for the Wide World Importers engagement in question 3: who you will talk to at each level in §5.3, five questions for each group, and what you will shadow. Then fill in [`../templates/problem-decomposition-canvas.md`](../templates/problem-decomposition-canvas.md) for your decomposition. Finally, check your value estimate from question 4 with [`../examples/impact-calculator/`](../examples/impact-calculator/), adding low and high scenarios.

## Solutions

1. - (a) "Tell me about the last invoice that turned out to be a problem. How did you find out? What happened next?" The original is hypothetical and invites a polite yes; it also pitches a solution.
   - (b) "Can you show me the last reconciliation you did? How long did it take from start to finish, and where did you get stuck?" "Usually" invites an idealised average; the last real case gives a timed fact and an artefact.
   - (c) "When did the process last go wrong? What did you do?" The original is a leading yes/no opinion question; people rarely criticise their own process to a stranger.
   - (d) "What did you spend most of yesterday doing? Which parts would you happily never do again?" The original asks users to design a product, which they are poor at; it also anchors on "AI assistant" before the problem is known.

2. - **Workarounds:** a personal spreadsheet of suppliers whose invoices "always have the wrong VAT", or sticky notes with purchase-order numbers.
   - **Exceptions:** the 20% of invoices (no matching purchase order, partial deliveries, foreign currency) that take 80% of the time.
   - **Hidden dependencies:** waiting for a budget holder to approve by email, phoning a warehouse to confirm a delivery.
   - **Real timing:** a "two-minute" match that actually takes eight because the ERP screen times out and must be reopened.
   - **Trust:** which fields the clerks double-check (bank details, always) and which they rely on blindly (supplier name).

   Interviews miss these because people describe the process as designed, forget habitual workarounds, and underestimate the time spent on exceptions.

3. Following §5.7:
   1. **Goal:** reduce late shipments.
   2. **Measurable outcome:** on-time delivery rate, 82% now, target 95%.
   3. **Drivers:** late shipments are 18% of all shipments; documentation errors cause 35% of them (6.3 points), carrier capacity 25% (4.5 points), supplier handover 20% (3.6 points), warehouse picking 20% (3.6 points).
   4. **Decisions and information** per driver: documentation needs product classification codes, origin data and the customs rules for each lane; carrier capacity needs bookings, forecasts and carrier commitments; and so on.
   5. **Users and workflow change:** customs clerks check flagged documents before submission; planners book capacity earlier.
   6. **Capabilities:** document extraction, rules engine, booking data integration, forecasting, dashboards.
   7. **Value and feasibility** for each (question 5 shows the method).
   8. **Sequence:** documentation is the largest driver and the data is local, so it is a natural first slice.

   ```mermaid
   flowchart TB
     G["Goal: on-time delivery<br/>82% → 95%"] --> D1["Customs documentation errors<br/>(35% of late)"]
     G --> D2["Carrier capacity shortfalls<br/>(25%)"]
     G --> D3["Late supplier handover<br/>(20%)"]
     G --> D4["Warehouse picking delays<br/>(20%)"]
     D1 --> S1["Pre-submission document check<br/>(LLM extraction + rules)"]
     D1 --> S2["Validated product-code master<br/>(data cleanup, no AI)"]
     D2 --> S3["Earlier capacity booking from<br/>demand forecast"]
     D3 --> S4["Supplier handover alerts and<br/>scorecard (rules, no AI)"]
     D4 --> S5["Pick-wave scheduling report<br/>(no AI)"]
   ```

   **Not AI:** S2 (master-data cleanup), S4 (alerts and scorecard), S5 (scheduling report), and arguably S3 if the forecast is statistical rather than model-based. The best first slice may well be S2 plus the rules part of S1. As the chapter puts it: solve the problem, not the technology brief.

4. (a) 60 × 3 = 180 hours a week; × 46 = 8,280 hours a year; × £45 = **£372,600**, which the chapter rounds to £373,000.

   (b) Time: 25 × 4 = 100 hours a week; × 46 = 4,600 hours a year; × £38 = **£174,800**. Errors: 60 × £900 = **£54,000**. Total ≈ **£228,800 a year**.

   (c) Cashable time saving: 50% × £174,800 = £87,400. Conservative total: £87,400 + £54,000 = **£141,400 a year**.

   Present both, labelled: "£141k a year in cash savings (finance-validated), plus capacity worth a further £87k a year that the team will redeploy to supplier queries." This follows Chapter 13 §13.8: hours freed are not cash saved unless overtime falls, hiring is avoided or the time is redeployed to valuable work, and you should say which. The finance director's adjustment makes the number more credible, not less.

5. **Choose B (loan-file summaries)** as the lighthouse: high value, high feasibility on all three dimensions, a champion in place, five weeks to a first result, low risk. It builds credibility and reusable foundations (document parsing, retrieval, evaluation sets) for harder problems.

   - **C** is a strong second and could follow quickly, or run in parallel if capacity allows; it is lower value and has medium organisational feasibility.
   - **A** has the highest headline value but is the classic trap: high risk (credit decisions are high-risk under the EU AI Act and subject to model risk management), low organisational feasibility and a 20-week horizon. Put it on the *later* list; revisit once B has built trust and if the credit committee's objections can be addressed (perhaps as decision support, not automation).
   - **D** is blocked by data access across eight systems. Start the access requests now so it becomes feasible later.

6. - (a) **Decomposing by technology** instead of by business driver. Fix: break retention into drivers (onboarding failures, service complaints, price-driven churn, contract-renewal lapses) and ask what decision would change for each.
   - (b) **Boiling the ocean.** Nothing ships for months. Fix: pick the product line or warehouse with the most stock-outs and highest value, and deliver that slice first.
   - (c) **Anchoring on the customer's proposed solution.** Fix: ask what the chatbot is for (perhaps HR answers the same 20 questions 300 times a month, and a better search page or FAQ would solve it).
   - (d) **Ignoring the human workflow:** a prediction nobody can act on is worthless. Fix: deliver the prediction to the planner who can reroute shipments, in the tool they use, early enough to act.

7. Check your discovery plan includes all six groups in §5.3, with front-line staff (warehouse pickers, customs clerks, planners) scheduled **early**. Good questions are about past events and artefacts ("Show me the last customs rejection: what was wrong?"). Shadowing should cover at least one customs-submission session and one shift on the warehouse floor.

   On the canvas, each sub-problem should have a measurable driver, the users affected, data and integration needs, a value estimate and feasibility scores, and the chosen first slice should be justified.

   The calculator should reproduce £228,800 (base, all time counted) and £141,400 (cashable). Reasonable low and high scenarios vary the most uncertain inputs: hours saved per clerk (say 2.5 low, 5 high) and errors avoided (40 low, 80 high). For example, low: 25 × 2.5 × 46 × £38 × 50% + 40 × £900 = £54,625 + £36,000 = £90,625; high: 25 × 5 × 46 × £38 + 80 × £900 = £218,500 + £72,000 = £290,500. Present the range with the base case, and state which assumptions drive it.
