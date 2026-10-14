# Chapter 6. The Technical Toolkit

> "The best GTM engineers can move between a Clay table, a SQL query and a Python script without changing gears."

## What you will learn

- The technical skills GTM engineers use, and how much of each you need.
- Spreadsheet-style workflow tools (Clay and similar) as a programming environment.
- APIs, webhooks, JSON and authentication, applied to GTM tools.
- SQL for GTM analytics; Python or JavaScript for glue and services.
- No-code and low-code automation (Zapier, Make, n8n) and when to graduate from them.
- LLM fundamentals for GTM work: prompting, structured output, cost and evaluation.
- Engineering habits: version control, testing, documentation, idempotency.

---

## 6.1 How technical do you need to be?

Job postings vary. Bloomberry's 2026 analysis found roughly 38% of GTM engineering postings explicitly require SQL or Python. Another analysis of a smaller sample found over half asking for SQL, Python or JavaScript, and nearly all mentioning AI skills. The highest-paid roles expect you to write code, not only click through no-code tools.

A practical ladder:

| Level | Can do | Typical tools |
|---|---|---|
| 1. No-code | Build tables, formulas, enrichment columns, simple automations | Clay, spreadsheets, Zapier/Make, CRM workflows |
| 2. Low-code | Call APIs with HTTP steps, parse JSON, write small formulas/scripts, write prompts with structured output | Clay HTTP API columns, n8n, Make, JS/Python snippets |
| 3. Code | Write scripts and small services, SQL models, webhooks, scheduled jobs, tests | Python/TypeScript, SQL/dbt, cloud functions, Git |
| 4. Engineering | Design data pipelines and internal tools, warehouse-native GTM, reliable integrations, agents | Warehouses, orchestration, CI/CD, observability |

You can start at Level 1, but aim for Level 3. Code makes you faster, cheaper (fewer tool credits) and more reliable.

## 6.2 Workflow tables (Clay and similar)

**Clay** popularised the *programmable table*. Each row is an entity (company or person). Each column is either data or an **action**: an enrichment from a provider, an HTTP API call, a formula, a web-scraping step, an AI prompt (Claygent), or a push to a CRM or sequencer. Columns can depend on other columns and run conditionally. Similar tools include Persana, Databar, Bitscale, Cargo, Freckle and others, and enrichment/automation features inside Apollo, HubSpot and ZoomInfo.

Treat a table like code:

- **Inputs, transformations and outputs** should be clear. Name columns descriptively.
- **Run conditions** ("only run if email is empty", "only if fit score ≥ 55") control cost and correctness.
- **Waterfalls** try providers in order until one returns a valid result (Chapter 7).
- **Credits are money.** Every enrichment, AI call and lookup costs something. Test on 10–50 rows before running on 50,000.
- **Document** the table's purpose, inputs, owner and schedule. Tables multiply quickly, and undocumented ones become liabilities.

*(As of October 2026)* Clay's product has expanded beyond tables: reusable **Functions** (beta, September 2026), **Audiences** (a GTM data layer for dynamic lists), **Sequencer** (sending with deliverability management), agent features in **Claygent**, and **Clay Workflows** (a visual workflow builder announced at its October 2026 Sculpt event, in beta). Capabilities change fast, so check current documentation.

## 6.3 APIs and webhooks for GTM

Every GTM tool exposes an API. You will constantly:

- **Read** (search companies, fetch contacts, list sequence activity).
- **Write** (create or update CRM records, add a prospect to a sequence).
- **Receive webhooks** (form submitted, email replied, meeting booked, product sign-up).

Essentials (covered in depth in *The Integration Design Engineer*, Chapters 3, 6 and 7):

- **HTTP methods and status codes:** `GET`, `POST`, `PATCH`; `200`, `201`, `400`, `401`, `403`, `404`, `409`, `422`, `429` and `5xx`, and what each means for retries.
- **JSON:** nested objects and arrays; null vs missing fields.
- **Authentication:** API keys (store them in a secrets manager or the tool's credential store, never in a shared table or doc), OAuth 2.0 (for CRM connections), webhook signatures (HMAC).
- **Pagination** and **rate limits:** CRMs and enrichment APIs throttle you. Respect `Retry-After`; batch requests; use bulk APIs for large volumes.
- **Idempotency:** use **upserts** by external ID or email so that retries and re-runs do not create duplicates. This is the single most important habit when writing to a CRM.
- **Webhooks:** verify signatures, acknowledge fast, process asynchronously, and de-duplicate on event ID.

Example: upsert a HubSpot contact by email (simplified):

```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/upsert" \
  -H "Authorization: Bearer $HUBSPOT_TOKEN" -H "Content-Type: application/json" \
  -d '{"inputs":[{"idProperty":"email","id":"jane@acme-logistics.com",
       "properties":{"firstname":"Jane","jobtitle":"VP Operations","icp_tier":"1"}}]}'
```

Example: Salesforce upsert by external ID field:

```http
PATCH /services/data/v62.0/sobjects/Account/Domain__c/acme-logistics.com
Content-Type: application/json

{"Name": "Acme Logistics", "ICP_Tier__c": "1"}
```

(`Domain__c` must be marked as an External ID field. Check your org's current API version.)

## 6.4 SQL for GTM

SQL answers the questions that drive GTM decisions. Typical queries:

```sql
-- Win rate and ACV by ICP tier for opportunities created in the last 12 months
SELECT a.icp_tier,
       COUNT(*)                                             AS opps,
       AVG(CASE WHEN o.is_won THEN 1.0 ELSE 0 END)          AS win_rate,
       AVG(CASE WHEN o.is_won THEN o.amount END)            AS avg_won_acv
FROM opportunities o
JOIN accounts a ON a.id = o.account_id
WHERE o.created_date >= CURRENT_DATE - INTERVAL '12 months'
  AND o.is_closed
GROUP BY a.icp_tier
ORDER BY a.icp_tier;
```

```sql
-- Pipeline created per outbound play this quarter
SELECT p.play_name,
       COUNT(DISTINCT m.meeting_id)          AS meetings,
       COUNT(DISTINCT o.id)                  AS opportunities,
       SUM(o.amount)                         AS pipeline
FROM play_enrollments p
LEFT JOIN meetings m      ON m.contact_id = p.contact_id AND m.booked_at >= p.enrolled_at
LEFT JOIN opportunities o ON o.account_id = p.account_id AND o.created_date >= p.enrolled_at
WHERE p.enrolled_at >= DATE_TRUNC('quarter', CURRENT_DATE)
GROUP BY p.play_name
ORDER BY pipeline DESC NULLS LAST;
```

(The second query has attribution assumptions baked in. Chapter 15 discusses how to make them explicit.)

Learn: `JOIN`s, `GROUP BY`, window functions (`ROW_NUMBER()` for de-duplication, `LAG` for stage transitions), CTEs (`WITH`), date functions, and `CASE`. dbt is the standard tool for version-controlled SQL models in the warehouse.

## 6.5 Python or JavaScript

Use code for:

- Logic too complex for formulas (matching, scoring, parsing).
- Calling APIs that tools don't support natively.
- Scheduled jobs (re-enrichment, data-quality checks, reconciliation).
- Webhook receivers and small internal services.
- Data analysis (pandas, notebooks).

Where to run it: cloud functions (AWS Lambda, Google Cloud Functions/Run, Vercel and Cloudflare Workers), workflow tools with code steps (n8n, Pipedream, Windmill), notebooks for analysis, or a small container service. Use **environment variables or a secrets manager** for credentials.

The examples in this book use standard-library Python so they run anywhere.

## 6.6 No-code and low-code automation

| Tool | Strengths | Watch out for |
|---|---|---|
| **Zapier** | Huge app catalogue, easy | Cost at volume; limited error handling; opaque logic |
| **Make** | Visual scenarios, data manipulation | Complex scenarios become hard to maintain |
| **n8n** | Self-hostable, code nodes, popular for AI agent workflows | You operate it (if self-hosted) |
| **Pipedream, Windmill** | Code-first automation | More engineering required |
| **CRM-native workflows** (HubSpot Workflows, Salesforce Flow) | Run inside the CRM; no sync lag | Platform limits; Flow complexity |
| **iPaaS** (Workato, Tray.ai, Boomi) | Enterprise governance | Cost; usually owned by IT |

**Graduate from no-code** when a workflow is business-critical, high-volume, complex, or needs testing and version control. A good pattern is to prototype in no-code, then harden in code or a governed platform.

## 6.7 LLMs for GTM: fundamentals

Large language models power research, classification, personalisation and agents. Essentials:

- **Prompts are specifications.** State the task, the input fields, the output format, constraints ("if unknown, output `UNKNOWN`; never guess"), and examples.
- **Structured output:** request JSON matching a schema (most model APIs support schema-constrained output). Parse and validate it, and reject malformed output.
- **Grounding:** give the model the source text (a scraped website, a job post) rather than asking it to recall facts. Models can **hallucinate** plausible but false details, which is fatal in a personalised email ("Congrats on your Series C!" to a company that never raised one).
- **Classification tasks** (industry, persona, "do they sell to enterprise?") are where LLMs are most reliable. **Generation tasks** (writing emails) need the most QA.
- **Cost and latency:** cost scales with tokens × rows. Use smaller, cheaper models for simple classification and larger ones for nuanced writing. Cache results, and only run on rows that pass cheaper filters first.
- **Evaluation:** build a labelled sample (50–200 rows), measure accuracy or quality, and re-run the evaluation when you change prompts or models (Chapter 13).
- **Data protection:** know what data you send to which model provider and under which terms (Chapter 16).

## 6.8 Engineering habits that set you apart

1. **Version control** (Git) for code, SQL, prompts and exported workflow definitions.
2. **Test on samples** before full runs; keep golden test cases for matching, scoring and parsing (see the examples).
3. **Idempotent writes:** upsert by key; never "create" blindly.
4. **Dry-run modes:** compute what *would* change before writing to the CRM.
5. **Logging and alerts** for scheduled jobs and webhooks (Chapter 14).
6. **Documentation:** a one-page brief per play or system (template: [`templates/play-brief.md`](../templates/play-brief.md)).
7. **Change management:** tell sales before you change routing or scoring.
8. **Cost tracking:** credits and API spend per play.

---

## Summary

- Aim for working proficiency in workflow tables, APIs and webhooks, SQL, and Python or JavaScript, plus LLM fundamentals.
- Treat tables and automations like code: clear inputs and outputs, run conditions, testing on samples, documentation and cost awareness.
- Use upserts and idempotent writes to the CRM. Respect rate limits and secure credentials.
- Prototype in no-code; harden critical workflows in code or governed platforms.
- Use LLMs where they are strong (grounded classification, structured extraction) and evaluate them like any other model.

## Exercises

See [`exercises/06-technical-toolkit.md`](../exercises/06-technical-toolkit.md).

## Further reading

- *The Integration Design Engineer*, Chapters 3 (HTTP), 6 (APIs), 7 (webhooks), 8 (reliability).
- Clay University (clay.com/university) and Clay's changelog.
- Salesforce REST API and HubSpot CRM API documentation.
- Mode's SQL tutorial; dbt Labs' "dbt Fundamentals" course.
