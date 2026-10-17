# Exercises: Chapter 19, [Becoming a Forward Deployed Engineer](../chapters/19-career.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation**, **hands-on** and **interview practice**. All companies are fictional and all figures illustrative. Pay figures in the chapter are as of October 2026; the offers below are invented for practice.

## Questions

1. **Scenario.** For each candidate, name the strengths to emphasise and the gaps to close (§19.1), and suggest one portfolio project (§19.4) that would close the most important gap.
   - (a) Amira, a data engineer for five years at Wide World Importers, who built its supplier-data pipelines but has rarely spoken to users.
   - (b) Ben, a solutions engineer at a software vendor, excellent in front of customers, who has built demos but never owned anything in production.
   - (c) Chen, a hospital pharmacist who taught himself Python and built a medication-reconciliation script his ward now depends on.

2. **Calculation.** Compare two offers (illustrative figures, in US dollars):

   | | Offer A: AI start-up (private) | Offer B: enterprise software vendor (public) |
   |---|---|---|
   | Base salary | $210,000 | $185,000 |
   | Target bonus | 10% of base | 15% of base |
   | Equity | $400,000 of options over 4 years, one-year cliff | $160,000 of restricted stock units over 4 years |
   | Travel | "Up to 50%" | "One week a month" |

   - (a) Compute annual total compensation for each at face value.
   - (b) Recompute, valuing the private company's equity at 50% of face value because of its risk and illiquidity.
   - (c) Using the estimate in question 2 of the [Chapter 18 exercises](18-life-as-an-fde.md) that offer A's travel could mean about 86 nights away a year against 36 for offer B, what is the risk-adjusted difference per extra night away?
   - (d) List three things besides these numbers you would check before deciding.

3. **Interview practice: decomposition.** Set a timer for 45 minutes and answer out loud or on paper, then compare with the model answer.

   > "Wide World Importers imports chilled and frozen food from 40 suppliers in 12 countries, and writes off about 4% of it to spoilage each year. The chief operating officer asks: how would you help?"

   At the 25-minute mark, apply this twist without looking at the answer first: *"New regulation requires a complete temperature record for every pallet, retained for two years, from next July. And the COO now says the budget is half what she first suggested."*

4. **Interview practice: learning round.** Read this description of **SiftQL**, an invented query language, for no more than five minutes, then answer the questions without looking back at the rules more than you need to. Say aloud how you are interpreting each rule, as you would in the interview.

   > A SiftQL query is a list of steps joined by `|`, applied left to right. Each step takes a table and returns a table.
   >
   > - `from <table>` starts the query.
   > - `where <field> <op> <value>` keeps rows that match. Operators: `==`, `!=`, `>`, `<`. Text values are in double quotes.
   > - `group <field>` must be followed by `count` or `sum <field>`; the result has one row per group, with columns `<field>` and `count` or `sum`.
   > - `count` on its own returns one row with one column, `count`.
   > - `sort <field>` sorts ascending; add `desc` for descending.
   > - `take <n>` keeps the first n rows.

   Table `shipments`:

   | id | carrier | origin | status | days_late | value_gbp |
   |---|---|---|---|---|---|
   | S1 | Litware Freight | Rotterdam | late | 3 | 12000 |
   | S2 | Fabrikam Air | Shanghai | on_time | 0 | 40000 |
   | S3 | Litware Freight | Shanghai | late | 1 | 8500 |
   | S4 | Northwind Shipping | Rotterdam | on_time | 0 | 15000 |
   | S5 | Fabrikam Air | Shanghai | late | 5 | 22000 |
   | S6 | Northwind Shipping | Antwerp | late | 2 | 9000 |
   | S7 | Litware Freight | Antwerp | on_time | 0 | 30000 |
   | S8 | Northwind Shipping | Shanghai | late | 4 | 18000 |

   - (a) Write a query for the number of late shipments, and give its result.
   - (b) Write a query for late shipments per carrier, and give its result.
   - (c) Write a query for the total value of late shipments by origin, largest first, and give its result.
   - (d) Write a query for the single most delayed shipment, and give its result.
   - (e) The interviewer asks: "Which carrier is worst?" Answer using SiftQL, saying what you would ask first and what the language can't do.
   - (f) What is wrong with `from shipments | count | where status == "late"`?

5. **Scenario.** Rewrite this answer to "Tell me about a time you won over a sceptic" using situation, task, action, result (STAR), with numbers. Invent plausible details.

   > "At my last job there was a difficult stakeholder who didn't like our project. I communicated well and kept them in the loop, and eventually they came round and were happy."

   Then write a 60-second answer to "Why FDE?" for yourself.

6. **Interview practice: system design.** Outline, in ten bullet points or fewer, your answer to: "Design a system that lets Woodgrove Bank's analysts ask questions over the bank's internal documents, respecting permissions." Include the follow-ups you would expect on security, evaluation, scale and handover, using the chapters of Part III as a checklist.

7. **Hands-on.** Build a small portfolio piece and run it through the book's tools:
   - (a) Write an impact case for a process you know with [`../examples/impact-calculator/`](../examples/impact-calculator/), with low, base and high scenarios.
   - (b) Write a go-live checklist for your project in the format of [`../examples/readiness-gate/checklist.json`](../examples/readiness-gate/checklist.json) and run `python3 gate.py <your checklist>` from [`../examples/readiness-gate/`](../examples/readiness-gate/). Fix what it reports.
   - (c) Write a field report, using [`../templates/field-report.md`](../templates/field-report.md), about a gap in a tool you use every day.
   - (d) Draft your own first-90-days plan (§19.6) for a named target employer, with one concrete deliverable in each 30-day period.

## Solutions

1. - (a) **Amira.** Emphasise: data wrangling, SQL, pipelines, a supply-chain domain. Close: customer-facing work and application engineering. Project: interview three people who use a public dataset (for example, local food-inspection data), build a small web tool for one of them with a profiled, cleaned pipeline behind it, and write it up as a case study with the users' feedback.
   - (b) **Ben.** Emphasise: customer skills, discovery, product knowledge, demos. Close: production engineering and owning delivery end to end. Project: an AI system with an evaluation suite, tests, monitoring and a runbook, run through the readiness gate (question 7), so the evidence is production discipline rather than another demo.
   - (c) **Chen.** Emphasise: domain credibility and a real tool real users depend on (describe its users and outcome, without patient data). Close: software engineering rigour. Project: rebuild a de-identified version of the reconciliation tool with tests, version control, error handling and documentation, and write up the design decisions. Health-data and clinical-software employers will value both halves.

2. (a) A: $210,000 + $21,000 + $100,000 = **$331,000**. B: $185,000 + $27,750 + $40,000 = **$252,750**. Difference: **$78,250** in A's favour.

   (b) A: $210,000 + $21,000 + $50,000 = **$281,000**. B is unchanged at $252,750 (public stock, already liquid). Difference: **$28,250**.

   (c) Extra nights: 86 − 36 = 50. $28,250 ÷ 50 = **$565 per extra night away**, before tax. Whether that is worth it is personal, but the calculation turns "A pays $78k more" into a more honest comparison.

   (d) Check: what "up to 50%" means in practice (Chapter 18 exercises, question 2); the equity terms (strike price, latest valuation, the cliff: leave at month 11 and A's equity is worth nothing; exercise window after leaving); whether bonuses are usually paid at target; whether the role passes the Chapter 1 §1.6 tests for a genuine FDE role (does field work reach the product?); team, manager and engagement length; and the career ladder. As the chapter says, compare total compensation, travel expectations and equity terms together, and check current market data for the specific company and level.

3. **Model answer** (one good answer, not the only one; following §19.3 and Chapter 5 §5.7):

   **1. Clarify (first 5 minutes).** "Is 4% by value or by volume? Which products spoil most? Where is spoilage discovered: at the port, at our warehouses, or when customers reject deliveries? Who owns the outcome: the COO, the head of quality, logistics? What has been tried?" Assume the interviewer answers: by value; annual chilled and frozen imports are worth about £150M, so spoilage is about £6M a year; most is found at warehouse receipt or by customers.

   **2. Outcome and baseline.** Spoilage write-off as a percentage of import value, by product, supplier, lane and site, measured monthly; baseline from the last 12 months of write-off records. Secondary: customer rejections and claims.

   **3. Drivers** (where does spoilage come from?):
   - Temperature excursions in transit (reefer container failures, power loss at port).
   - Dwell time at ports and customs (documentation holds; containers waiting unplugged).
   - Warehouse cold-room problems (door left open, equipment failure).
   - Stock rotation: first-expiry-first-out not followed, so older stock expires.
   - Over-ordering against demand, so stock expires before sale.
   - Supplier quality at origin (product already near the limit when shipped).

   I'd ask for write-off data broken down by these causes. If it doesn't exist, building that breakdown is the first deliverable.

   **4. Users, decisions and data per driver.** Logistics planners decide routing and escalate excursions (data: reefer sensor feeds, carrier milestones); customs brokers clear documentation (data: customs entries, hold reasons); warehouse managers manage cold rooms and rotation (data: warehouse management system, cold-room sensors, expiry dates); buyers decide order quantities (data: sales, forecasts, shelf life).

   **5. Data model** (key objects and relationships):

   ```mermaid
   flowchart LR
     Supplier --> PO["Purchase order"]
     PO --> Shipment
     Shipment --> Container
     Container --> Pallet
     Pallet --> Product
     Container --> Reading["Temperature reading"]
     Pallet --> Reading
     Shipment --> Milestone["Milestone<br/>(port, customs, warehouse)"]
     Reading --> Excursion["Excursion<br/>(out of range, duration)"]
     Pallet --> WriteOff["Write-off<br/>(value, cause)"]
   ```

   The useful join is write-offs back to pallets, shipments, excursions and milestones, so that each write-off can be attributed to a cause.

   **6. First slice.** If the data shows, say, 40% of spoilage follows excursions during port dwell: an **excursion alert** for planners, using the reefer feeds most carriers already provide, with a playbook for each alert (contact the terminal, reprioritise customs clearance), plus a **write-off attribution dashboard** so the effect is measurable. Most of this is integration and rules, not AI. Later slices: expiry-aware stock rotation in the warehouse system; order quantities that account for shelf life; supplier scorecards. AI candidates later: predicting excursion risk per lane, or extracting hold reasons from customs documents.

   **7. Risks.** Data access to carrier feeds (contracts, formats); sensor coverage (not every container has one); adoption (alerts that arrive at 3 a.m. to nobody); attribution (spoilage has several causes at once); food-safety obligations if the system says a product is safe.

   **8. Adapting to the twist.** The regulation changes the order of work, and it is good news for the data model: a per-pallet temperature record *is* the `Pallet → Temperature reading` relationship, now compulsory. With half the budget:
   - Make the **compliance record** the first slice: ingest every reading, link it to pallets, retain for two years with an audit trail. It has a deadline and a legal driver, so it will be funded.
   - Build the **excursion alert** on the same data at small extra cost; it is the cheapest route to the spoilage saving.
   - Defer forecasting and supplier scorecards.
   - New risk: pallets without sensors. Ask which suppliers and carriers can provide pallet-level data, and what the fallback is (container-level readings assigned to pallets, if the regulation allows).

   Say explicitly that the structure survives the change; that is what the interviewer is testing.

   **Common weaknesses:** proposing "an AI model to predict spoilage" in the first two minutes; a consulting framework with no data model; ignoring who acts on an alert; defending the original plan after the twist.

4. (a) `from shipments | where status == "late" | count` → **5** (S1, S3, S5, S6, S8).

   (b) `from shipments | where status == "late" | group carrier | count` →

   | carrier | count |
   |---|---|
   | Litware Freight | 2 |
   | Fabrikam Air | 1 |
   | Northwind Shipping | 2 |

   (c) `from shipments | where status == "late" | group origin | sum value_gbp | sort sum desc` →

   | origin | sum |
   |---|---|
   | Shanghai | 48500 |
   | Rotterdam | 12000 |
   | Antwerp | 9000 |

   (Shanghai = 8,500 + 22,000 + 18,000.)

   (d) `from shipments | sort days_late desc | take 1` → **S5** (Fabrikam Air, Shanghai, 5 days late).

   (e) First ask what "worst" means: most late shipments, highest share late, most days late, or most value at risk? Each gives a different answer:
   - Count of late shipments (query b): Litware Freight and Northwind Shipping tie on 2.
   - Share late: SiftQL has no division, so run `from shipments | group carrier | count` (Litware 3, Fabrikam Air 2, Northwind 3) and divide by hand: Litware 2 ÷ 3 = 67%, Fabrikam Air 1 ÷ 2 = 50%, Northwind 2 ÷ 3 = 67%.
   - Total days late: `from shipments | group carrier | sum days_late | sort sum desc` → Northwind 6, Fabrikam Air 5, Litware 4.

   Then add the judgement the interviewer is looking for: with two or three shipments per carrier, none of these differences means anything; you would want months of data before ranking carriers. Saying that is as important as getting the queries right.

   (f) Steps run left to right, and `count` returns a one-row table whose only column is `count`, so there is no `status` field left to filter. The `where` must come before `count`. The point of the question is noticing that each step changes the shape of the table, which is how most pipeline languages behave.

   **How to behave in a real learning round:** restate the rules in your own words ("so `group` must always be followed by an aggregation"); start with the simplest query and build up; check results by hand against the table; ask when something is ambiguous (is `sort` stable? what does `count` return with no rows?); and treat the interviewer as the domain expert.

5. Example STAR answer:

   > **Situation:** At Contoso Insurance, we were deploying a claims-summary tool, and the head of claims IT, who had seen two failed vendor projects, refused to give us access to the policy database replica, which blocked the pilot.
   >
   > **Task:** I needed read access within three weeks, without going over his head, or the pilot would miss its decision date.
   >
   > **Action:** I asked for 30 minutes to understand his concerns rather than to pitch. They were specific: load on the replica, and personal data leaving his network. I redesigned the integration to read from a nightly extract inside his tenancy, with only the 14 fields we needed, and offered him approval rights on every schema change. I wrote it up as a one-page design and asked him to review it before anyone else saw it.
   >
   > **Result:** He approved access in nine days, became the system's technical owner, and later presented the design to his own leadership. The pilot made its decision date, and the field-reduction approach became our standard integration pattern for insurance customers.

   A good "Why FDE?" connects your history to building for real users, ambiguity, variety and customer contact, with one concrete example, and says what you want to learn. It doesn't lead with the title or the pay.

6. Outline:
   - **Clarify:** which documents and systems (SharePoint, file shares, a document management system), how many users, what questions, what regulatory constraints.
   - **Ingestion (Chapter 10):** connectors, parsing (tables, scanned PDFs), chunking, metadata including source permissions, freshness and deletions.
   - **Permissions (Chapter 14):** sync access-control lists and filter at retrieval for the signed-in user (single sign-on); fail closed; test "user removed an hour ago".
   - **Architecture (Chapters 11 and 12):** retrieval-augmented generation with citations; hosting inside the bank's cloud tenancy or region; model choice; no data leaving approved boundaries.
   - **Guardrails:** prompt-injection defences for document content; no external tools; audit log of every question and answer.
   - **Evaluation (Chapter 13):** a labelled question set built with analysts; retrieval and answer metrics; permission-leak tests; regression in CI.
   - **Security and risk:** security review, DPIA, model risk management classification, started in week 1.
   - **Scale:** document volume, index size, concurrency at peak (Little's law; see Chapter 15's exercises), token limits, cost per question.
   - **Operations and handover (Chapter 15):** SLOs including a quality SLO, monitoring, runbooks, support model, the bank's own team named and paired from the start.
   - **First slice:** one team, one document collection, measured against a baseline.

7. Personal. Check: the impact case states where each assumption came from and leads with the low case; the checklist has blockers, majors with owners and due dates, numeric checks backed by reported metrics, and evidence links that actually point at something; the field report describes the problem and workaround rather than a feature; and each 30-day period of the 90-day plan has one deliverable someone else could check (a sandbox deployment; a shipped user-facing change and a first field report; a playbook contribution or reusable component).
