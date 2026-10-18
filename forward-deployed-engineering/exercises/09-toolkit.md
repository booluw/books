# Exercises: Chapter 9, [The FDE Technical Toolkit](../chapters/09-toolkit.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional.

## Questions

1. **Concept.** What does "T-shaped" mean for an FDE, and why does §9.1 say that the most important technical skill is not any particular technology? Which two languages should an FDE *write* fluently, and which should they be able to *read*?

2. **Scenario.** You start on Monday at Wide World Importers. The in-scope systems are SAP (orders and deliveries), a Snowflake warehouse fed nightly from SAP, a customs broker's SFTP drop and a ServiceNow instance for incidents. Write a day-by-day first-week plan following §9.8, including one small thing you could ship by Friday.

3. **Scenario.** A colleague hands over a prototype for Contoso's claims team: a Jupyter notebook run by hand each morning, with an API key pasted in a cell, results written to a CSV on a shared drive, no tests, and prompts edited directly in the notebook. Using the table in §9.9, list what must be fixed before the customer's platform team will look at it, in priority order, and what can safely be deferred.

4. **Calculation.** You need to pull 2,400,000 customer records from Northwind's CRM API. Pages hold at most 500 records, and the API allows 100 requests a minute. (a) How many requests, and what is the minimum time for a full load? (b) If 2% of requests receive a "429 Too Many Requests" response and your client waits 30 seconds before each retry, roughly how long does the full load take with a sequential client? (c) About 1.5% of records change each day. How long does a daily incremental load take? (d) What does this imply for the design?

5. **Scenario.** Your new connector from Woodgrove Bank's network to the vendor's model API fails with "certificate verify failed: self-signed certificate in certificate chain". It works from your laptop at home. What is the most likely cause, how would you confirm it, and what is the correct fix (and the incorrect one)?

6. **Scenario.** On a previous engagement at Fabrikam you wrote an excellent script that reconciles SAP vendor records with a procurement system, including Fabrikam's custom field mappings and a sample of their vendor data for tests. Your new customer, Adventure Works, has the same problem. What may you carry over, what may you not, and what should you do with the generic part?

7. **Hands-on.** (a) Run the book's example tests with `python3 forward-deployed-engineering/examples/run_all_tests.py` from the repository root and confirm they pass. (b) Run the profiler in [`../examples/data-profiler/`](../examples/data-profiler/) on its sample file and list the five most serious problems it reports. (c) Take any notebook-style script you have written and restructure it as §9.9 describes: logic in a module with functions and tests, a thin notebook or command-line entry point that calls it, configuration and secrets outside the code, and a README saying how to run it and who owns it.

## Solutions

1. **T-shaped** means broad working knowledge across many technologies (the horizontal bar), plus genuine depth in one or two (the vertical stroke). FDEs need breadth because they inherit whatever stack the customer runs, from mainframe extracts to Kubernetes, plus their own product.

   The most important skill is **getting productive quickly in an unfamiliar environment**: reading unknown code, finding the data, understanding constraints and shipping something within days. Any particular technology will be wrong at the next customer; the meta-skill transfers.

   **Write fluently:** Python and SQL. **Read confidently:** TypeScript/JavaScript, Java, C#, Go and shell.

2. Model plan:
   - **Monday:** accounts, laptop or virtual desktop, VPN, email, chat, ServiceNow and repository access. Read the existing architecture documentation (and note what's missing). Meet the SAP basis or integration lead, the Snowflake data owner and the security contact. Learn the change process and release windows.
   - **Tuesday:** read-only queries against Snowflake for orders and deliveries; profile the key tables (Chapter 10). Confirm how fresh the nightly load is and which SAP tables feed it.
   - **Wednesday:** trace one real late shipment end to end: SAP order, delivery, the broker's SFTP file, any ServiceNow incident. Identify which environments (development, test, production) you may use.
   - **Thursday:** profile the broker's SFTP files (formats, dates, encodings); find the engineer who knows where the bodies are buried.
   - **Friday:** ship something small: for example, a daily report of shipments whose customs documents are missing a product classification code, sent to the customs team lead. It proves your access works end to end and helps someone with a real problem.

3. Fix first (cheap now, expensive later):
   1. **Secret out of the code:** the API key goes into the customer's secret manager, and the exposed key is rotated now, because it may already be in notebook history or backups.
   2. **Version control** for code and **prompts** (as files, reviewed).
   3. **Move logic from the notebook into a module** with functions, called by a scheduled job rather than run by hand.
   4. **A small automated test suite**, including an **evaluation set** for the AI output (Chapter 13).
   5. **Basic logging with request IDs.**
   6. **Respect the customer's access controls:** a CSV of claims on a shared drive may breach data handling rules; write to an approved, access-controlled store.
   7. **Infrastructure as code** for whatever is deployed, and a **README** (how to run it, how it works, who owns it).

   Safe to defer: elaborate abstractions, horizontal scaling, a polished UI, full test coverage, multi-region failover, comprehensive documentation, performance optimisation.

4. (a) 2,400,000 ÷ 500 = **4,800 requests**. At 100 a minute: **48 minutes** minimum.

   (b) 2% of 4,800 = 96 throttled requests. Each costs a 30-second wait: 96 × 0.5 = **48 minutes** of waiting, plus 96 extra requests (about 1 minute). Total ≈ 48 + 48 + 1 ≈ **97 minutes**, roughly double. (Retries are themselves sometimes throttled; exponential backoff with jitter is the standard approach.)

   (c) 1.5% of 2,400,000 = 36,000 changed records ÷ 500 = **72 requests**, under a minute at 100 a minute.

   (d) Design for an **initial full load once** (scheduled outside business hours, resumable from the last page so a failure doesn't restart from zero) and **incremental loads** thereafter using a modified-since filter or change data capture. Respect the rate limit deliberately (client-side throttling at, say, 90 a minute) rather than relying on 429s, and make the load idempotent so retries are safe (Chapter 10 §10.6).

5. **Most likely cause:** Woodgrove's network has a **TLS-inspecting proxy** that terminates TLS and re-signs traffic with the bank's own internal certificate authority. Your connector doesn't trust that CA. It works at home because there is no proxy there. §9.5 notes that a surprising share of "the integration doesn't work" turns out to be a proxy or firewall.

   **Confirm:** inspect the certificate chain the connector receives from inside the network (for example with `openssl s_client -connect host:443 -showcerts` through the proxy) and compare the issuer with the provider's real certificate; ask the network team whether TLS inspection is in place and whether the model API's domain can be excluded.

   **Correct fix:** add the bank's internal root CA to the connector's trust store (from the network team, through the proper process), or have the domain added to the proxy's inspection bypass list if policy allows. Also confirm whether inspection of model traffic is acceptable under the data-handling agreement. **Incorrect fix:** disabling certificate verification. It removes the protection against interception, and a security reviewer will (rightly) reject it.

6. **May carry over:** the generic technique and generic code you wrote, if your contract allows (matching logic, normalisation, the reconciliation report structure), and your own knowledge of SAP's vendor tables.

   **May not carry over:** Fabrikam's custom field mappings, configuration, any of Fabrikam's data (including the test sample), and anything else that is Fabrikam's asset or confidential. This is both a contractual and an ethical line (§9.10). Check the Fabrikam SOW's IP clause too (Chapter 6 §6.8): if Fabrikam owns all work product, even the generic code may not be yours to reuse.

   **The generic part:** contribute it to your company's toolkit or, better, the product (a standard SAP vendor-reconciliation connector or template), with synthetic test data. A snippet every FDE copies is a feature waiting to be built (Chapter 16).

7. (a) The runner should report each example's tests passing; a failure means a broken example or a Python version issue (the examples use only the standard library).

   (b) On the sample claims extract, expect findings such as: a **duplicate claim ID** (and a lower-case variant of an ID); a **ragged row** caused by an unquoted `£1,200.00`, which shifts columns; **placeholders** (`N/A`, `unknown`, `TBC`, `0000-00-00`) counted as missing; **mixed date formats**, including a UK-format date among ISO dates and the value `yesterday`; a **sentinel amount** (`99999999`) and a **negative amount**; a **policy number with the wrong shape** (one digit short); inconsistent status capitalisation; and trailing whitespace. The most serious are those that silently corrupt joins and totals: duplicates, the shifted row, the sentinel amount and the unparseable dates.

   (c) Check your refactor: could a colleague run it from the README without asking you anything? Do the tests run without network access or secrets? Is there no customer data in the repository?
