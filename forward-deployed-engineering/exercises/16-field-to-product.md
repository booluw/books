# Exercises: Chapter 16, [Turning Field Work into Product](../chapters/16-field-to-product.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional and all figures illustrative.

## Questions

1. **Concept.** Paul Graham's advice is "do things that don't scale". The chapter adds a second half. State it, and explain in three or four sentences why the field-to-product loop is what makes forward deployment a software business rather than a services business. Refer to the economics in [Chapter 3](../chapters/03-business.md).

2. **Concept.** Classify each item using the table in §16.2 (bug, gap, pattern, reusable code, playbook, evaluation asset, market insight or documentation gap) and name where it should go.
   - (a) An FDE at Litware wrote a connector to a widely used legal practice-management system.
   - (b) Three insurance customers' security teams each asked where model inputs are stored and for how long.
   - (c) The PDF parser drops tables that span two pages.
   - (d) Every logistics customer has needed the same shipment-to-invoice join.
   - (e) Two public-sector prospects said they cannot buy unless the model runs in a UK region.
   - (f) An FDE wrote a rubric and 60 test cases for grading contract-clause extraction.
   - (g) No way to give a group of users read-only access to an agent's audit trail.

3. **Scenario.** Rewrite this field report so that a product manager is likely to act on it. Invent plausible details and mark them as assumptions.

   > "URGENT: Woodgrove Bank needs a PDF export button on the answers page ASAP or they won't sign. Can we add it to the next sprint? Thanks, Sam"

4. **Scenario.** The product council has capacity for two items next quarter. Using the rule of three and the factors in §16.4, decide what to do with each candidate (productise now, use an intermediate form, keep as a field solution, or decline), and justify each in one or two sentences.

   | Need | Distinct customers | ARR affected | Deployment time per customer with workaround | Notes |
   |---|---|---|---|---|
   | A. Audit log of AI answers | 4 | £2.6M | 2 weeks | Regulators ask for it; workarounds vary in quality |
   | B. Welsh-language answers | 1 | £0.6M | 3 days | One insurer; quality unverified |
   | C. Bespoke dashboard colour themes | 5 | £1.1M | 2 hours | Cosmetic |
   | D. Basel-style model-risk documentation pack | 1 | £3.0M | 4 weeks | First bank customer; three more banks in the pipeline |
   | E. Connector for a niche warehouse system | 3 | £0.4M | 1 week | Vendor of that system is retiring it in 2028 |

5. **Calculation.** Case 20.5 describes a returns-handling feature built separately for five retail customers. Use these assumptions: the five FDEs each spend 30% of their time maintaining their custom version; there are 46 working weeks a year; an engineer-week costs £3,500 (fully loaded). Generalising takes the five FDEs and four product engineers six weeks each, plus one engineer-week per customer to migrate. Once productised, the feature needs a quarter of one product engineer to maintain. Eight more retail customers are expected next year; each would have taken 5.5 weeks of FDE time with custom code, and will take 4 days (0.8 weeks) with the product feature.
   - (a) What is the one-off cost of generalising?
   - (b) What is the net annual benefit?
   - (c) What are the payback period in months and the first-year return on investment (ROI)?
   - (d) Which assumption would you most want to check, and why?

6. **Scenario.** Three FDEs built SharePoint permission handling for Wide World Importers, Northwind Traders and Litware. Their versions differ: Wide World syncs access-control lists nightly; Northwind checks permissions live at query time; Litware syncs nightly but also excludes sites tagged "HR". The product manager proposes shipping Northwind's version as "the feature" next month.
   - (a) Which generalisation mistake does the proposal risk, and what is the opposite mistake?
   - (b) Separate core from variation for this feature.
   - (c) List the six steps of §16.5 as a concrete plan for this feature.

7. **Hands-on.** Run `python3 tracker.py` in [`../examples/feedback-tracker/`](../examples/feedback-tracker/) and confirm the five needs in the README. Then create a CSV file `new_reports.csv` with the same columns as `more_reports.csv` containing these three reports, and run `python3 tracker.py field_reports.json more_reports.csv new_reports.csv`:

   | id | customer | problem | workaround | severity | arr_affected | tags |
   |---|---|---|---|---|---|---|
   | FR-015 | Litware | SharePoint search returns documents from folders the user has no permission to open | Excluded the legal team's sites from indexing | critical | 280000 | sharepoint;permissions |
   | FR-016 | Contoso Insurance | Welsh translation of answers for the Cardiff office | Second prompt translates each answer | medium | 600000 | language |
   | FR-017 | Tailspin Toys | Folder access rules are not respected when we index the intranet | Indexed only public pages | high | 90000 | *(empty)* |

   - (a) What happens to the SharePoint need, the Welsh-language need and FR-017? Explain each from the way the tracker works.
   - (b) Fix FR-017 in two different ways, and say which you prefer for the long term.
   - (c) Using [`../templates/field-report.md`](../templates/field-report.md), write the field report the product team should receive for the SharePoint need now.

8. **Scenario.** The head of FDE at a vendor reports a "healthy loop": field reports filed rose from 40 to 120 a quarter over the year. Data for the vendor's insurance segment:

   | Deployment (in order) | 1 | 2 | 3 | 4 | 5 | 6 |
   |---|---|---|---|---|---|---|
   | FDE-weeks to production | 18 | 17 | 18 | 16 | 17 | 18 |
   | Custom components left in customer code | 9 | 11 | 10 | 12 | 11 | 12 |
   | Used a template or accelerator? | No | No | No | Yes | No | No |

   Is the loop working? What would you look at next, and which mechanisms from §16.6 would you introduce first?

## Solutions

1. The second half is: **systematically convert what you learned into things that do scale.** Chapter 3's model only works if FDE effort per customer falls over time while revenue expands, so that gross margin rises from services-like levels towards software levels. That fall happens when what an FDE builds for one customer becomes product, templates or connectors that the next customer gets with little FDE effort. Without the loop, every customer needs the same bespoke work, FDE headcount grows in step with revenue, and the company is a consultancy with a software licence attached.

2. - (a) **Reusable code** → product connector library (after review and generalisation).
   - (b) **Documentation gap** → a standard security pack and the product docs.
   - (c) **Bug** → product engineering backlog.
   - (d) **Pattern** → an industry template or data model for logistics.
   - (e) **Market insight** → product strategy and partnerships (hosting regions, cloud partners).
   - (f) **Evaluation asset** → product evaluation tooling and the shared templates library (with customer data removed).
   - (g) **Gap** → product roadmap.

3. A good rewrite follows §16.3: problem, user, context, workaround, numbers and links, not a feature request.

   > **Title:** Compliance users need a fixed, shareable record of an AI answer and its sources
   >
   > **Customer:** Woodgrove Bank (financial services, ARR £1.2M; renewal and branch rollout of about £400k expansion depend on it, *assumption*).
   >
   > **User and context:** Complaints-handling team leaders (about 40 people) must attach the evidence behind a decision to the complaint file, which the regulator can inspect. Today they cannot capture an answer with its cited sources in a form that doesn't change.
   >
   > **Workaround:** Users take screenshots and paste them into Word; citations are lost. The FDE has prototyped a "save as PDF" script that renders the answer, sources and timestamp (about 3 days' work, unsupported).
   >
   > **Frequency and impact:** About 250 complaints a week need this (*assumption*). Compliance has said the screenshot process will fail its next audit.
   >
   > **Other instances:** Closely related to the audit-log need that Woodgrove itself raised in July (FR-003) and that three other customers share (FR-006, FR-009, FR-013): a fixed record of an answer is probably a view on the same data, so this strengthens an existing rule-of-three item rather than starting a new one.
   >
   > **Ask:** A product decision on how users export a tamper-evident record of an answer, by 15 November, because the renewal decision is due in December.

   Note what changed: "PDF button" became the underlying need (a fixed, evidential record), which the product team may meet better another way; "won't sign" became specific revenue and dates; linking it to the four-customer audit-log cluster makes it far more persuasive than a one-customer request.

4. - **A: productise now.** Four customers, the most ARR, regulatory pressure, and workarounds of varying quality (a risk in itself, since a weak audit trail is worse than none if relied on).
   - **D: productise now, despite one customer.** §16.4 notes that the first bank needing a compliance feature often means every bank will; here three more banks are in the pipeline, it is the largest ARR and it saves four weeks per deployment. Build it with the FDE who has done the first one.
   - **C: decline** (or a small configuration option if trivially cheap). It passes the rule of three, but it saves two hours per deployment and has no strategic value: the rule triggers consideration, not a decision.
   - **E: intermediate form.** Three customers, but small revenue and an unstable, end-of-life target system. Publish the connector as a recipe or marketplace component so FDEs stop rewriting it, without committing the core product to it.
   - **B: field solution, but fix the risk now.** One customer and unverified quality; build an evaluation of Welsh answers before anyone relies on it, and watch for a second customer.

5. (a) Engineer-weeks: (5 FDEs + 4 product engineers) × 6 weeks = 54; plus 5 customers × 1 week of migration = 5; total **59 engineer-weeks × £3,500 = £206,500**.

   (b) - Maintenance avoided: 5 FDEs × 30% × 46 weeks = 69 engineer-weeks = £241,500.
   - Maintenance added: 0.25 × 46 = 11.5 engineer-weeks = £40,250.
   - Net maintenance saving: £241,500 − £40,250 = £201,250.
   - Faster deployments: 8 customers × (5.5 − 0.8) weeks = 8 × 4.7 = 37.6 engineer-weeks = £131,600.
   - **Net annual benefit: £201,250 + £131,600 = £332,850.**

   (c) Payback = £206,500 ÷ (£332,850 ÷ 12) = £206,500 ÷ £27,737.50 = **7.4 months**. First-year ROI = (£332,850 − £206,500) ÷ £206,500 = **61%**. You can check both with `payback_months(206_500, 332_850)` and `roi(332_850, 206_500)` from [`../examples/impact-calculator/impact.py`](../examples/impact-calculator/impact.py).

   (d) The **eight new customers**: the deployment saving depends entirely on the pipeline, and sales forecasts are optimistic. With no new customers the benefit is still £201,250 a year and payback about 12.3 months (£206,500 ÷ £16,770.83), so the case survives, which is worth saying. The 30% maintenance figure also deserves a check against timesheets. Unmeasured benefits (fewer upgrade breakages, Tailspin back on the current release, FDEs freed for new work) strengthen it further.

6. (a) Shipping Northwind's version as is risks **under-generalising**: Northwind's assumptions (live checks, which may be too slow for large tenants, and no site exclusions) get baked in, and the other two customers can't migrate. The opposite mistake is **over-generalising**: an abstract permissions framework for every content system and every conceivable rule, which nobody can configure.

   (b) - **Core** (same everywhere): reading SharePoint access-control lists, mapping SharePoint groups to the product's users, filtering retrieval results by the user's permissions, and logging the decision.
   - **Variation** (configuration): sync mode (nightly sync, live check, or nightly with a live check on the final results); sync schedule; sites or tags excluded from indexing; behaviour when the permission service is unavailable (fail closed).

   (c) 1. **Collect** the three implementations and why they differ (Northwind needs immediate revocation; Wide World has 2 million documents; Litware's HR rule came from its works council). 2. **Separate** core and variation as above. 3. **Design with the three FDEs.** 4. **Build** to product standards: permission tests, including the "user removed from group an hour ago" case, documentation and a security review. 5. **Migrate** the three customers with contract tests that prove equivalent results, then delete the custom code. 6. **Measure** whether the next SharePoint deployment is faster and needs no custom code.

7. Running the bundled samples gives 14 reports and 5 needs, as in the README. With the new file: **17 field reports → 6 needs**.

   (a) - **SharePoint permissions becomes PRODUCTISE** (rank 3): Litware is the third distinct customer (with Wide World Importers and Northwind Traders), and ARR affected rises from £550,000 to £830,000 (£400,000 + £150,000 + £280,000). It now ranks above export (£590,000) because both are in the PRODUCTISE tier and SharePoint has more ARR.
   - **Welsh stays FIELD SOLUTION:** FR-016 joins FR-010, but both are from Contoso Insurance. The tracker de-duplicates by customer, so it is still one customer and £600,000 (ARR counted once, not £1.2M).
   - **FR-017 forms its own cluster** with a blank label, one customer, £90,000. It has no tags, and none of its words ("folder", "access", "rules", "intranet") is in the synonym table, so its concept set is empty and its Jaccard similarity with every other report is 0. This is the limitation the README warns about: needs described in unfamiliar words are missed.

   (b) **Fix 1:** add tags `sharepoint;permissions` to FR-017. The tracker then reports 5 needs, with SharePoint permissions at **4 customers and £920,000**. **Fix 2:** add `"access": "permissions"` to `SYNONYMS` in a copy of `tracker.py`. FR-017's concepts become {permissions}, whose Jaccard similarity with {sharepoint, permissions} is 1 ÷ 2 = 0.5, which meets the 0.5 threshold, so it joins the cluster with the same result (the label may read "permissions, sharepoint"). Prefer both: tagging is the immediate fix, and growing the synonym table is the durable one, since it is the shared vocabulary between field and product. Check that a new synonym doesn't chain unrelated reports together (for example, "access" in an SSO report).

   (c) The report should state the problem (search results leak documents users cannot open, a security failure, not an inconvenience), the users and the four customers, the workarounds (indexing only public sites, switching the connector off for HR and legal sites, which removes much of the product's value), severity (critical), ARR affected (£920,000 if FR-017 is included), the rule-of-three line ("fourth customer to need this"), the variations from question 6, and a request for a decision by a date.

8. **No.** More field reports is an activity measure; §16.7 says that if deployment time and custom code per customer are not falling across successive customers in a segment, the loop is not working, whatever the number of reports. Here FDE-weeks are flat (16–18), custom components are *rising* (9 to 12), and templates were used once in six deployments.

   Look next at: **time from field report to decision** (are reports being read and decided on?), the **productisation rate** (how many field-built components became product or reusable assets), why deployment 4's template wasn't reused (poor quality? not known about? not maintained?), and which custom components recur across the six customers (the tracker, or a simple custom-code inventory, will show them).

   Mechanisms to introduce first: a **field council** that decides publicly what happens to the top needs; a **product liaison** for the insurance segment; and a **productisation budget** so the generalisation work isn't always displaced by customer urgency. Then close the loop visibly when something ships, and track the Nth-deployment metrics every quarter.
