# Runbook: <GTM system name>

*Owner: · Backup: · Business owner: · Dashboard: · Last fire drill:*

## 1. What it does and why it matters
(Two sentences, plus a data-flow diagram link. What breaks for sales if it stops?)

## 2. Dependencies
| System | Role | Status page | Support contact | Credential |
|---|---|---|---|---|

## 3. Alerts and responses

### Inbound leads not routed (zero volume in business hours)
- Check: form submissions arriving? webhook errors? routing tool status? CRM API limit?
- Mitigate: switch to the fallback queue; notify SDR manager
- Recover: re-route leads created during the outage; check SLAs

### Bounce rate > 2% / spam rate > 0.1%
- Pause affected domain or inboxes; check list source and verification; check DNS (SPF/DKIM/DMARC); see Chapter 11 §11.7

### Enrichment spend spike
- Stop scheduled runs; check run conditions and cache; identify the table

### Sync failures (reverse ETL / CRM)
- Check API limits, field validation errors, permission changes

## 4. Procedures
- Pause and resume sequences for a play
- Add an address or domain to global suppression (all tools)
- Re-run a failed enrichment batch safely (idempotent upserts)
- Rotate an integration credential
- Offboard a rep (routing, ownership, tools)

## 5. Change log
