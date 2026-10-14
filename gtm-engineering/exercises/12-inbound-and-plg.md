# Exercises: Chapter 12, Inbound and PLG

## Questions

1. Design a two-field demo form with real-time enrichment, including failure handling.
2. Define a PQA for a collaboration tool and explain how to derive thresholds.
3. What should stay event-driven and what can run in the warehouse?
4. Write a dbt-style SQL model that maps product users to company domains, excluding free-email domains.
5. What can go wrong with reverse ETL writing to the CRM, and how do you prevent it?

## Solutions

1. Fields: work email + "What prompted you?" Enrich in under 2 s; reveal missing fields only if needed; on timeout show the full form or accept and enrich asynchronously; spam protection; route and offer booking.
2. Example: ICP tier 1–2 AND ≥ 5 active users in 14 days AND (integration connected OR admin/SSO page viewed). Derive thresholds by comparing converted vs non-converted accounts historically.
3. Event-driven: inbound routing, demo booking, real-time alerts. Warehouse: scores, segments, PQAs, attribution, data quality.
4. Example:
```sql
SELECT u.user_id, lower(split_part(u.email, '@', 2)) AS email_domain
FROM {{ ref('stg_users') }} u
WHERE lower(split_part(u.email, '@', 2)) NOT IN (SELECT domain FROM {{ ref('free_email_domains') }})
```
(Then join to accounts on the normalised domain.)
5. API-limit exhaustion, overwriting human-edited fields, loops with CRM automation, partial failures. Prevent with dedicated sync-owned fields, diff-only syncs, upserts, rate limiting, failure monitoring and Flow guards for integration-user changes.
