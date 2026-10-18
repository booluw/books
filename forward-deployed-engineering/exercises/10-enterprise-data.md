# Exercises: Chapter 10, [Enterprise Data in the Wild](../chapters/10-enterprise-data.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional and all figures illustrative.

## Questions

1. **Scenario.** Choose a form of data access from §10.2 for each situation, and say what you would plan for production.
   - (a) Week 1 at Contoso Insurance: you need two years of claims to profile, the warehouse has them refreshed nightly, and production database access needs a six-week approval.
   - (b) Woodgrove Bank's fraud assistant must see card transactions within seconds of authorisation.
   - (c) Northwind's ERP vendor forbids direct database access; the ERP has a documented REST API with permissions.
   - (d) A hospital's security team won't release patient data until the DPIA is complete in eight weeks, but the FDE team wants to build the parsing pipeline now.

2. **Scenario.** Your profile of Fabrikam's 180,000-row supplier table shows:

   | Column | Null rate | Distinct | Top values / notes |
   |---|---|---|---|
   | `supplier_id` | 0% | 179,412 | — |
   | `vat_number` | 22% | 120,300 | `N/A` (9,800 rows), `0000000` (2,100) |
   | `country` | 1% | 214 | `GB`, `UK`, `United Kingdom`, `DE`… |
   | `created_date` | 0% | 6,021 | min `1900-01-01` (3,400 rows), max `2031-07-14` |
   | `status` | 0% | 4 | `A`, `I`, `C`, `X` |

   List every problem you can see, what you would ask the data owner, and how you would handle each.

3. **Hands-on.** Write a SQL profiling query, in the style of §10.3, for a `shipments` table with columns `shipment_id`, `customer_id`, `ship_date`, `delivered_date`, `weight_kg` and `destination_postcode`. It should report row count, distinct shipment IDs, null rates for both dates, date ranges, impossible values (delivered before shipped, non-positive weights) and placeholder postcodes. Then list two things you would check before running it on a billion-row table.

4. **Scenario.** Explain how you would handle each of these at Wide World Importers:
   - (a) Status code `C` meant "closed" before the 2018 system migration and "cancelled" after.
   - (b) Warehouse scan timestamps are in local time with no time zone, from sites in the UK, Poland and Singapore.
   - (c) 14% of shipments reference a customer ID that doesn't exist in the customer table.
   - (d) A business analyst suggests "just deleting the bad rows" before loading.

5. **Calculation.** Fabrikam is linking 200,000 CRM accounts to 150,000 billing accounts. (a) How many comparisons would an all-pairs approach need? (b) With blocking that spreads records evenly across 2,000 blocks, how many? (c) On a labelled sample containing 120 true matching pairs, the system automatically links 110 pairs, of which 104 are correct, and sends 14 pairs to human review, of which 10 are true matches. Compute precision and recall for the automatic links alone, and for automatic links plus correctly resolved review pairs. (d) For linking patient records at a hospital rather than CRM accounts, which way would you move the thresholds, and why?

6. **Hands-on.** In [`../examples/record-linkage/`](../examples/record-linkage/): (a) run the linkage and its tests, and note the automatic matches, review pairs, precision and recall; (b) raise the match threshold and then lower it, and record how precision, recall and the size of the review queue change; (c) add a new pair of records to the sample data that should *not* match but probably will (for example, two branches of one company at the same postcode), add it to the labels, and propose a rule or field that would separate them.

7. **Scenario.** Contoso's HR team wants an attrition-risk analysis, and the data team offers you a full extract of the HR system: names, home addresses, dates of birth, salaries, sickness records, performance ratings and ethnicity. Using §10.8, describe what you would actually request and how you would handle it.

8. **Concept.** Define *idempotent* for a pipeline step. Fabrikam's nightly load appends each day's invoice extract to a table; on Tuesday it failed half-way and the on-call engineer re-ran it. What went wrong, and how would you redesign the step?

## Solutions

1. - (a) **Warehouse** now: built for analysis, governed, available. Its nightly refresh is fine for profiling. Plan production access (warehouse or replica, depending on freshness needs) in parallel; don't let a temporary extract become the integration.
   - (b) **Change data capture** or an event stream: near real time, low load on the source. Needs infrastructure and approval, so start early.
   - (c) **API:** supported, enforces business rules and permissions. Plan for rate limits and pagination (Chapter 9).
   - (d) **Synthetic or masked data**, clearly labelled, to build parsing and pipeline code. It won't reveal real quality problems, so plan a profiling pass as soon as real data is approved, and budget time for surprises.

2. Problems and handling:
   - **`supplier_id` is not unique:** 180,000 rows but 179,412 distinct, so 588 rows repeat an ID that already appears (at most 588 IDs are affected; fewer if some appear three or more times). Ask whether these are true duplicates, history rows or merged suppliers. Never assume a "key" is unique.
   - **`vat_number` real completeness is much lower than it looks:** 22% null plus `N/A` and `0000000` placeholders (11,900 rows, about 6.6% of all rows) means about 28.6% missing in reality. Treat placeholders as missing; ask why VAT numbers aren't captured (perhaps non-VAT-registered suppliers).
   - **Inconsistent `country` codes:** `GB`, `UK` and `United Kingdom` mean the same thing; 214 distinct values exceeds the number of real countries. Normalise to ISO 3166 codes in tested code and report the mapping.
   - **`created_date` placeholder and impossible values:** `1900-01-01` on 3,400 rows is a placeholder for "unknown"; a maximum in 2031 is a future date. Treat the placeholder as missing; investigate the future dates (perhaps a typo for 2021, or a field used for something else).
   - **Undocumented status codes:** ask what `A`, `I`, `C` and `X` mean, and whether their meaning has changed over time (code drift).

   Share the profile with the data owner; their explanations are the most valuable output.

3. ```sql
   SELECT
     COUNT(*)                                                     AS row_count,
     COUNT(DISTINCT shipment_id)                                  AS distinct_shipments,
     SUM(CASE WHEN ship_date IS NULL THEN 1 ELSE 0 END) * 1.0 / COUNT(*)      AS ship_date_null_rate,
     SUM(CASE WHEN delivered_date IS NULL THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS delivered_date_null_rate,
     MIN(ship_date)                                               AS earliest_ship,
     MAX(ship_date)                                               AS latest_ship,
     MIN(delivered_date)                                          AS earliest_delivery,
     MAX(delivered_date)                                          AS latest_delivery,
     SUM(CASE WHEN delivered_date < ship_date THEN 1 ELSE 0 END)  AS delivered_before_shipped,
     SUM(CASE WHEN weight_kg <= 0 THEN 1 ELSE 0 END)              AS non_positive_weights,
     SUM(CASE WHEN UPPER(TRIM(destination_postcode)) IN ('N/A', 'UNKNOWN', 'TBC', '')
              THEN 1 ELSE 0 END)                                  AS placeholder_postcodes
   FROM shipments;
   ```

   (A null `delivered_date` may be legitimate for shipments still in transit; compare the null rate with recent ship dates before calling it a problem.)

   Before running it on a billion rows: check the **query plan** and the warehouse's **cost model** (a full scan may be expensive or slow), and consider restricting to a date range or a sample (`TABLESAMPLE` or a partition) first. Also check whether you are on a production system or a replica, so you don't affect live performance.

4. - (a) **Code drift.** Confirm the migration date with the data owner, then map by date range in tested transformation code (`C` before the cut-over → `closed`; after → `cancelled`). Flag records near the boundary and document the rule.
   - (b) **Time zones.** Establish each site's convention (and daylight-saving handling: the UK and Poland observe it, Singapore doesn't), derive the zone from the site ID, convert to UTC, and keep the original value. Flag ambiguous times around clock changes.
   - (c) **Orphans.** Report the count and examples to the data owner; find out why (deleted customers, a different customer master, a load-order problem). Decide explicitly whether to exclude or repair, and show the excluded count to users.
   - (d) **Never silently drop data.** Every exclusion should be counted and reported, so users know what the system doesn't see. Fix at source where possible; otherwise clean in tested code, not by deleting rows by hand.

5. (a) All pairs: 200,000 × 150,000 = **3.0 × 10¹⁰** (30 billion) comparisons.

   (b) Even blocks: each has 200,000 ÷ 2,000 = 100 CRM and 150,000 ÷ 2,000 = 75 billing records, so 100 × 75 = 7,500 pairs per block; × 2,000 blocks = **1.5 × 10⁷** (15 million), 2,000 times fewer. Real blocks are uneven (a London postcode district may hold many times the average), so check the largest blocks.

   (c) Automatic links only: 104 correct of 110 links, so 6 false links.
   - Precision = 104 ÷ 110 ≈ **94.5%**.
   - Recall = 104 ÷ 120 ≈ **86.7%**.

   Adding the 10 true matches from review (reviewers correctly reject the other 4):
   - Correct links = 104 + 10 = 114; total links = 110 + 10 = 120.
   - Precision = 114 ÷ 120 = **95.0%**.
   - Recall = 114 ÷ 120 = **95.0%**.

   The review band recovers recall without much loss of precision; the 6 automatic false links remain and need a higher upper threshold or a better rule to remove.

   (d) For patients, **raise the automatic-match threshold** (favour precision), and route more pairs to human review. A false merge of two patients can put one person's allergies or results in another's record, which is far worse than a missed duplicate. Thresholds should reflect the business cost of each error type.

6. (a) The sample should give 7 automatic matches (all correct) and 1 review pair, with automatic precision 1.00 and recall about 0.88; accepting the review pair takes both to 1.00. (The example's README states the expected figures; check yours against it.)

   (b) Raising the threshold typically keeps precision at or near 1.00 while lowering recall and growing the review queue; lowering it shrinks the queue and raises recall but eventually admits false matches. Plot the three numbers against the threshold: the right setting depends on the cost of each error and of reviewer time.

   (c) Two branches at one postcode with similar names will score highly on name and postcode. Separating signals include a different email domain or phone number, a branch or registered-company number, or a rule that a qualifier such as "(Scotland)" or "Branch" in one name and not the other blocks automatic matching and sends the pair to review. Add the pair to the labels so the evaluation catches regressions.

7. **Minimise:** ask what the analysis needs. Typically: a pseudonymised employee token, role, grade, department, tenure band, salary band (not exact salary), leaving date and reason. **Do not request** names, home addresses, exact dates of birth, sickness records or ethnicity unless there is a specific, approved purpose. Sickness (health data) and ethnicity are **special category data** under GDPR; using them requires a specific legal basis and, almost certainly, a DPIA. If the analysis must check for bias by ethnicity, that is a separate, governed question for HR, legal and privacy to decide.

   **Handling:** pseudonymise at extraction (the mapping kept by HR, not by you); know the classification; keep the data in the customer's environment and agreed region; restrict and log access; never use it outside the engagement; agree retention and delete at the end, confirming in writing. Also check whether the works council or employee representatives need to be consulted (Chapter 7).

8. **Idempotent:** re-running the step with the same input produces the same result, so failures can be retried safely.

   An **append-only** load is not idempotent. The half-finished run had already appended part of Tuesday's invoices; the re-run appended all of them again, so those invoices are now duplicated and totals are overstated.

   Redesign: load each day's extract into a staging table, then **replace that day's partition** (delete-then-insert within one transaction, or a `MERGE` / upsert keyed on invoice ID plus a load-date partition). Record the batch ID, source file and row counts in and out; add a data test that invoice IDs are unique and that loaded rows equal extract rows; and alert on mismatches.
