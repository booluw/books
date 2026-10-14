# Exercises: Chapter 14, CRM Engineering

## Questions

1. An enrichment sync and a Salesforce Flow keep updating each other. Explain the loop and fix it.
2. Write a spec for a nightly "owner hygiene" job.
3. Name five fields you would add to Account for GTM engineering, with owner and source.
4. What belongs in an automation inventory entry?
5. A bulk update set 30,000 accounts' Industry to blank. How should your jobs have prevented this, and how do you recover?

## Solutions

1. The sync writes Industry → Flow re-scores and writes a field the sync reads → the sync writes again. Fix: field ownership, "only if changed" checks, and a Flow entry condition that skips integration-user updates.
2. Find records owned by inactive users or outside territory rules; dry-run report; reassign by routing rules (cap N per run); notify managers; log changes.
3. `gtm_fit_score` / `gtm_fit_tier` (scoring job), `enr_employee_count` + `_source` + `_updated_at` (enrichment), `gtm_last_signal_type` / `_date` (signal pipeline), `pqa_score` (warehouse sync), `do_not_contact` + reason (compliance process).
4. Name, owner, purpose, trigger or schedule, systems read and written, credentials, cost, runbook link, last review.
5. Prevent: per-run change caps, dry-run diffs, refusal to write blanks over values, sandbox testing. Recover: restore from backup or field history, or re-run enrichment for affected records.
