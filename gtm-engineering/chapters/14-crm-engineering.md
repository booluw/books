# Chapter 14. CRM Engineering and Data Hygiene

> "Garbage in, gospel out." (on CRM dashboards)

## What you will learn

- How to work safely in Salesforce and HubSpot: sandboxes, automation, API limits and change management.
- In-CRM automation (Salesforce Flow, HubSpot Workflows) vs external automation.
- Field design and governance.
- Data hygiene as continuous jobs: normalisation, deduplication, decay detection and owner hygiene.
- Monitoring and operating your GTM automations.

---

## 14.1 The CRM is production

Sales leaders run their forecast, compensation and board reporting from the CRM. Treat it like a production database:

- **Use sandboxes** (Salesforce sandboxes; HubSpot developer test accounts and standard sandboxes on higher tiers) for building and testing automations and integrations.
- **Change management:** document changes, tell affected teams before they happen, deploy at low-traffic times, and have a rollback plan.
- **Least-privilege integration users:** each tool connects with its own integration user and minimal permissions. Never use an admin's personal login (Chapter 16).
- **Respect API limits:** Salesforce enforces daily API request allocations per org; HubSpot enforces per-app and per-account rate limits. A runaway sync can starve every other integration. Use bulk APIs for large jobs.
- **Backups:** Salesforce and HubSpot provide some export and backup features; many companies add third-party backup (Own, now part of Salesforce; Odaseva; Gearset and others). Know how you would restore after a bad bulk update.

## 14.2 In-CRM vs external automation

| | In-CRM (Salesforce Flow, Apex; HubSpot Workflows, custom code actions) | External (Clay, iPaaS, scripts, warehouse + reverse ETL) |
|---|---|---|
| Latency | Immediate, on record change | Seconds to hours |
| Access to other data | Limited to CRM (plus callouts) | Any source |
| Governance | Visible to admins; versioned in Salesforce metadata | Must be documented and governed separately |
| Limits | Governor limits; workflow limits | API limits; tool credits |
| Best for | Field defaults, validation, simple assignments, record-triggered updates | Enrichment, scoring with external data, cross-system orchestration |

Rule: **keep simple, record-local logic in the CRM; keep cross-system logic outside**, and make sure the two never fight over the same fields.

### Automation collisions

A classic failure: an enrichment sync updates `Industry`, which triggers a Flow that re-scores the account, which triggers a sync back to the enrichment tool, which updates `Industry` again. **Loops** burn API calls and corrupt data. Prevent them with clear field ownership (Chapter 5), "only update if changed" logic, and integration-user checks in Flows ("don't run when the integration user made the change").

## 14.3 Field design

- **Name fields clearly,** with prefixes for system-owned fields (`gtm_fit_score`, `gtm_fit_tier`, `enr_employee_count`, `enr_employee_count_source`, `enr_employee_count_updated_at`).
- **Use picklists** (controlled values) instead of free text for anything you filter or report on.
- **Store provenance** (source, date) for enriched fields.
- **Separate "computed" from "human-entered"** fields, and lock computed ones from manual edits.
- **Document every field:** purpose, owner, source, allowed values, which automations write it. Salesforce field descriptions and HubSpot property descriptions are good places for this.
- **Delete unused fields.** Old CRMs accumulate hundreds of abandoned fields that confuse users and integrations. Audit field usage before deleting.

## 14.4 Data hygiene as continuous jobs

Hygiene is not a one-off clean-up project; it is a set of **scheduled jobs**:

| Job | Frequency | What it does |
|---|---|---|
| **Normalisation** | On write + nightly | Standardise domains, countries (ISO codes), states, phone numbers (E.164), job titles (seniority and department), company names |
| **Duplicate detection** | Nightly / weekly | Find likely duplicate accounts and contacts; auto-merge only high-confidence matches; queue others for review |
| **Bounce and decay handling** | Daily | Mark bounced emails; trigger re-verification; flag contacts who changed jobs |
| **Re-enrichment** | Monthly by tier | Refresh stale fields (Chapter 7) |
| **Owner hygiene** | Daily | Reassign records owned by deactivated users; enforce ownership rules |
| **Lifecycle consistency** | Daily | Fix impossible states (a customer account with lifecycle "lead"; closed-won opportunity at an account marked prospect) |
| **Association repair** | Weekly | Contacts without accounts; accounts without domains |
| **Data-quality report** | Weekly | Completeness, validity, duplicates, freshness metrics (Chapter 5 §5.8) |

Each job should be **idempotent**, run in **dry-run mode** first, **log** what it changed, and **cap** how many records it changes per run, so a bug cannot rewrite the whole CRM.

## 14.5 Operating GTM automations

GTM engineers end up running dozens of automations: tables, workflows, syncs, webhooks, scripts. Operate them like software (see *The Integration Design Engineer*, [Chapter 16](../../integration-design-engineer/chapters/16-operations.md)):

- **Inventory:** a list of every automation, with owner, purpose, schedule, systems touched, credentials used and cost. Template: [`templates/stack-inventory.md`](../templates/stack-inventory.md).
- **Monitoring:** success and failure counts, rows processed, credits used, and latency for routing.
- **Alerts:** failures, zero-volume anomalies ("no inbound leads routed in 2 hours on a weekday" usually means something broke), spend spikes and bounce spikes.
- **Runbooks:** what to do when routing breaks, a sync fails, or a domain gets blocklisted. Template: [`templates/gtm-runbook.md`](../templates/gtm-runbook.md).
- **Change log:** what changed, when and why, so you can correlate with metric shifts.
- **Decommission:** turn off and remove automations nobody owns; revoke their credentials.

---

## Summary

- Treat the CRM as production: sandboxes, change management, least-privilege integration users, API-limit awareness and backups.
- Keep record-local logic in the CRM and cross-system logic outside; prevent automation loops with field ownership and change checks.
- Design fields with clear names, picklists, provenance, documentation and locks on computed values; remove unused fields.
- Run hygiene as idempotent, capped, logged scheduled jobs; measure data quality weekly.
- Operate automations with an inventory, monitoring, alerts, runbooks and a change log.

## Exercises

See [`exercises/14-crm-engineering.md`](../exercises/14-crm-engineering.md).

## Further reading

- Salesforce Trailhead: Flow, Data Management and Integration modules.
- HubSpot Academy: Operations Hub and data quality courses.
- *The Integration Design Engineer*, Chapters 8 (reliability) and 16 (operations).
