# Exercises: Chapter 6, Technical Toolkit

## Questions

1. Write a SQL query: meetings held per play in the last 30 days with the meeting-to-opportunity rate within 60 days.
2. Your Clay table writes contacts to HubSpot with "create contact". Re-runs create duplicates. Fix it.
3. A webhook from your form tool sometimes arrives twice. How do you make processing safe?
4. Write a prompt specification (task, inputs, output schema, constraints) that classifies a job title into seniority (IC/Manager/Director/VP/C-level/Unknown) and department.
5. When should a Zapier workflow be rebuilt in code?

## Solutions

1. Example:
```sql
WITH m AS (
  SELECT meeting_id, play_name, account_id, held_at
  FROM meetings WHERE status = 'held' AND held_at >= CURRENT_DATE - INTERVAL '30 days')
SELECT m.play_name, COUNT(*) AS meetings,
       AVG(CASE WHEN EXISTS (SELECT 1 FROM opportunities o WHERE o.account_id = m.account_id
             AND o.created_date BETWEEN m.held_at AND m.held_at + INTERVAL '60 days') THEN 1.0 ELSE 0 END) AS mtg_to_opp
FROM m GROUP BY m.play_name;
```
(Recent meetings haven't had 60 days yet, so mark the cohort incomplete.)
2. Use upsert by email (HubSpot batch upsert with `idProperty: email`) or search-then-update; never blind create.
3. Verify signature, de-duplicate on event ID (store processed IDs), acknowledge fast, process asynchronously, and write with upserts.
4. Task: classify title. Inputs: `job_title`, optional `company_size`. Output JSON `{"seniority": enum, "department": enum, "confidence": "high|medium|low"}`. Constraints: use only the title; `Unknown` if ambiguous; include 8–10 examples, including tricky ones ("Head of", "Lead", "Founder").
5. When it is business-critical, high-volume, complex, needs testing, version control or better error handling, or costs more than code would.
