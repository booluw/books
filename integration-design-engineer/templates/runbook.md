# Runbook: <Integration name>

| | |
|---|---|
| Owner team / on-call rotation | |
| Business owner | |
| Criticality tier | |
| Design document | *link* |
| Dashboards | *links* |
| Log queries | *saved searches by trace id and business key* |
| Last fire drill | YYYY-MM-DD |

## 1. What it does

*Two sentences and the context diagram. What breaks for the business if it stops?*

## 2. Dependencies

| System | Purpose | Status page | Support contact & hours | Escalation | Maintenance windows |
|---|---|---|---|---|---|

## 3. Alerts

### <Alert name>

- **Meaning:**
- **Impact:**
- **Likely causes:**
- **Diagnose:** *steps, queries, commands*
- **Mitigate:** *pause consumer / open circuit / switch to manual process*
- **Resolve:**
- **Recover data:** *replay / reconcile*
- **Escalate if:**

## 4. Procedures

### 4.1 Pause and resume processing
### 4.2 Inspect and replay dead-lettered messages
*Triage categories: bug / bad data / missing reference data / partner outage. Never delete a DLQ to "clear" an alert.*
### 4.3 Replay a time window from the message store
### 4.4 Run reconciliation and repair
### 4.5 Rotate credentials and certificates
*Inventory: credential → used for → expiry → rotation steps → who to notify.*
### 4.6 Partner outage playbook
### 4.7 Rerun a failed batch file safely
### 4.8 Throttle a catch-up surge after an outage

## 5. Known issues and workarounds

## 6. Change log
