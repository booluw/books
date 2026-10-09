# Chapter 16. Deploying, Observing and Operating Integrations

> "An integration is not done when it is deployed. It is done when it is decommissioned."

## What you will learn

- How to deploy integrations safely: environments, configuration, CI/CD and infrastructure as code.
- Observability for integrations: logs, metrics, traces, correlation IDs and OpenTelemetry.
- What to monitor, including business-level signals, and how to alert without fatigue.
- SLIs, SLOs and error budgets for integrations.
- Runbooks, incident response, replay and post-incident reviews.
- Day-2 operations: credential and certificate rotation, vendor changes, capacity, cost and decommissioning.

---

## 16.1 Environments and promotion

A typical setup has **development**, **test / QA**, **staging / pre-production** and **production** environments. For integrations, each environment must be **wired to the corresponding environments of every connected system**: your staging integration talks to the Salesforce full-copy sandbox, the NetSuite sandbox and the 3PL's test SFTP server.

Rules:

- **One artefact, many configurations.** Build once; promote the same artefact (container image, iPaaS package, flow version) through environments, changing only configuration.
- **Configuration is external:** endpoints, credentials (by reference to a secrets manager), feature flags, value maps, schedules and limits.
- **Never point non-production at production systems** (and especially never the reverse). Use allow-lists and distinct credentials per environment so it is impossible by construction.
- **Keep an environment matrix** documenting which system instance each environment uses, with owners and refresh schedules. Sandbox refreshes can silently break credentials and configuration.

---

## 16.2 CI/CD for integrations

- **Version control everything:** code, iPaaS flow definitions (exported), mappings, value maps, OpenAPI and AsyncAPI documents, infrastructure, dashboards and alert rules ("monitoring as code"), runbooks.
- **Pipeline stages:** lint (including Spectral for API specifications), unit tests, component tests, contract tests, build artefact, deploy to test, sandbox and E2E tests, approval, deploy to production, smoke test.
- **Infrastructure as code (IaC):** Terraform / OpenTofu, Pulumi, AWS CloudFormation / CDK, Azure Bicep, Crossplane. Queues, topics, subscriptions, DLQs, gateway routes, IAM roles, secrets references and alarms should all be code, reviewed in pull requests.
- **iPaaS CI/CD:** most platforms provide APIs, CLIs or Maven plugins for deployment (MuleSoft Maven plugin and Anypoint CLI; Boomi's Platform API and packaged deployments; SAP Cloud Integration's API and Transport Management Service; Workato's recipe lifecycle management and environments; Logic Apps Standard as code with Azure DevOps or GitHub Actions). Use them, and avoid "click-ops" deployments.
- **Database and schema migrations** for outbox and inbox tables run as part of the pipeline.
- **Deployment strategies:** rolling, blue-green and canary. For message consumers, ensure the new version can process messages produced for the old version (and vice versa during rollout).
- **Rollback:** fast and rehearsed. Remember that rolling back code does not roll back data already sent to partners.

---

## 16.3 Observability: the three signals

**Observability** is the ability to understand a system's internal state from its outputs. For integrations, which cross many systems, it is what turns a three-hour investigation into a three-minute one.

### Logs

- **Structured** (JSON) logs with consistent fields: `timestamp`, `level`, `service`, `flow`, `tenant`, `trace_id`, `span_id`, `correlation_id`, `message_id`, `entity_type`, `entity_id`, `external_system`, `operation`, `status`, `duration_ms`, `attempt`, `error_code`.
- **Log events, not payloads** by default (Chapter 10). Payloads go to a protected message store when needed.
- **Log at boundaries:** every inbound and outbound call or message, with outcome and duration.
- **Centralise** in a log platform (Elastic, OpenSearch, Splunk, Datadog, Grafana Loki, cloud-native logging) with retention matched to support and audit needs.

### Metrics

Numeric time series, cheap to store and fast to alert on. Key integration metrics:

| Metric | Why |
|---|---|
| Messages / requests in and out per flow (rate) | Throughput; sudden drops signal upstream problems |
| Success / failure counts by error class | Health |
| End-to-end latency (event time → completion), as percentiles | Freshness SLOs |
| Outbound call latency and status codes per dependency | Dependency health |
| Queue depth and **age of oldest message** | Backlog; age matters more than depth |
| **Consumer lag** (Kafka offset lag, or time lag) | Falling behind |
| DLQ depth and inflow rate | Unprocessable messages |
| Retry counts | Hidden instability |
| Rate-limit headroom (e.g. Salesforce daily API usage %) | Avoid exhaustion |
| Circuit-breaker state | Dependency outages |
| Token refresh failures; certificate days-to-expiry | Credential health |
| Reconciliation differences | Silent data loss |

### Traces

**Distributed tracing** follows one transaction across services and systems as a tree of **spans**. For integrations it answers "where did this order get stuck?"

- **W3C Trace Context** (`traceparent`, `tracestate` headers) is the standard propagation format over HTTP. Propagate it through **message headers** too (Kafka headers, AMQP application properties, SQS message attributes, CloudEvents' distributed-tracing extension) so traces continue across asynchronous hops.
- **OpenTelemetry (OTel)**, a CNCF project, is the vendor-neutral standard for generating and exporting traces, metrics and logs. It has SDKs for all major languages, auto-instrumentation for common HTTP and messaging libraries, the **OTel Collector** for processing and routing telemetry, and **semantic conventions** (including messaging conventions for spans such as `publish`, `receive` and `process`). Most observability back ends (Jaeger, Grafana Tempo, Honeycomb, Datadog, New Relic, Dynatrace, Elastic, Splunk, cloud APMs) accept OTLP.
- Many iPaaS platforms now export OTel or offer their own tracing. Check, and connect it to your central observability stack where possible.
- Third-party SaaS systems will not join your traces. Log the vendor's request ID alongside your trace ID at every boundary.

### Correlation IDs and business keys

Traces are technical. Support staff search by **business keys**: "what happened to order ORD-55821?" Index logs and the message store by business keys (order ID, customer ID, invoice number, tenant), and provide a **transaction search** tool or dashboard that shows the journey of a business entity across flows. This single capability reduces support load dramatically.

---

## 16.4 What to monitor: technical and business signals

Technical health is necessary but not sufficient. An integration can be "green" (no errors) while silently processing nothing because an upstream filter changed. Monitor **business signals** too:

- **Volume expectations:** "We normally receive 800–1,200 orders between 09:00 and 10:00 on weekdays." Alert on anomalously *low* volume, not just errors. Many of the worst integration incidents are silent.
- **Freshness:** "The latest record in the warehouse feed is more than 2 hours old."
- **Completeness:** daily file arrived? Record count matches control totals?
- **Reconciliation results** (Chapter 8).
- **Business error queue size** and age (records waiting for humans to fix).

**Synthetic monitoring** (periodic test transactions or health probes through the whole flow) catches breakages before customers do.

**Monitor your partners too:** subscribe to their status pages (via RSS, webhooks or Statuspage integrations), probe their health endpoints, and track certificate expiry on their endpoints.

---

## 16.5 Alerting without fatigue

Bad alerting is either silent or noisy. Principles:

- **Alert on symptoms that need human action,** not on every error. A single retried `503` is not an alert. A DLQ with growing messages is.
- **Route by ownership and type:** technical failures go to integration on-call; business-data errors go to the business owner's queue (email, ticket or dashboard), not the pager.
- **Use severity levels:** *page* (urgent, customer impact now: orders not flowing), *ticket* (needs attention within business hours: one record in the error queue), *log / dashboard only* (informational).
- **Include context in alerts:** what is wrong, since when, impact, link to dashboard, link to runbook, recent deploys.
- **Use multi-window, burn-rate alerts** for SLOs (§16.6) rather than thresholds that flap.
- **Review alerts monthly:** delete or tune any alert that fired without requiring action.

---

## 16.6 SLIs, SLOs and error budgets for integrations

From Google's SRE practice:

- **SLI (Service Level Indicator):** a measured property, such as "proportion of orders reaching the ERP within 15 minutes".
- **SLO (Service Level Objective):** a target for the SLI, such as "99.5% over 28 days".
- **Error budget:** the allowed shortfall (0.5% of orders late), spent by incidents and risky changes. When it is exhausted, prioritise reliability work over features.
- **SLA (Service Level Agreement):** a contractual promise, usually looser than the SLO, with consequences.

Good integration SLIs are **end-to-end and user-centric**:

| SLI | Measurement |
|---|---|
| **Freshness / latency** | % of events delivered to target within *T* of source event time |
| **Correctness / completeness** | % of source records present and matching in target at reconciliation |
| **Availability (for integration APIs)** | % of valid requests answered successfully |
| **Durability** | Messages lost (target: zero, verified by reconciliation) |

Agree SLOs with business owners during design (Chapter 14's NFRs), publish them, and report on them.

---

## 16.7 Runbooks

A **runbook** tells an on-call engineer what to do for each alert or common failure. Every production integration needs one. A template is in [`templates/runbook.md`](../templates/runbook.md). Contents:

- **Overview:** what the integration does; context diagram; owners; business impact if it stops.
- **Dashboards and log queries:** links.
- **Dependencies:** each external system with support contacts, status page, escalation path and maintenance windows.
- **Alerts:** for each, its meaning, likely causes, diagnostic steps and remediation.
- **Common procedures:**
  - pause and resume consumers;
  - inspect, fix and **replay DLQ messages**;
  - **replay a time window** from the message store;
  - re-run reconciliation and repair;
  - rotate credentials and certificates;
  - handle a partner outage (open circuit, notify business, catch up);
  - rerun a failed batch file safely.
- **Known issues** and their workarounds.
- **Escalation:** when and to whom.

Test runbooks with **fire drills**: break something in staging and have someone unfamiliar follow the runbook.

---

## 16.8 Incident response

When an integration incident happens:

1. **Detect and declare:** an alert, a user report or a reconciliation gap. Declare an incident with a severity and an owner (incident commander).
2. **Assess impact:** which business processes, how many records, since when, which customers or tenants?
3. **Mitigate first, fix later:** stop the bleeding by pausing a consumer to prevent bad data spreading, opening the circuit, rolling back a deploy or switching to a manual process. Preserve messages; **do not delete queues** in a panic.
4. **Communicate:** to business owners and, if needed, partners and customers, at a regular cadence.
5. **Resolve:** fix the root cause or apply a workaround.
6. **Recover data:** replay from DLQs or the message store; run reconciliation; repair divergent records; confirm with business owners that data is correct. This step is often longer than the fix itself.
7. **Post-incident review:** blameless, written, with contributing factors and action items (detection, prevention and recovery improvements). Track actions to completion.

**Integration-specific recovery questions:**

- Which records were affected? (You need the message store and business-key search for this.)
- Were any *wrong* updates sent to partners that must be corrected, not merely missing ones re-sent?
- Is replay safe? (Idempotency.) Will the replay surge overload the target? (Throttle.)
- Do partners need to be told to reprocess or ignore something?

---

## 16.9 Day-2 operations

Most of an integration's lifetime cost is after go-live.

### Credentials and certificates

- Maintain a **credential inventory** with expiry dates, owners and rotation procedures (Chapter 10).
- **Alert well before expiry:** 30, 14 and 7 days for certificates (including partners' certificates you trust and your mTLS client certificates), OAuth client secrets (Microsoft Entra ID client secrets have maximum lifetimes; Salesforce and others have their own policies) and SFTP keys.
- **Automate rotation** wherever possible, and practise manual rotation where it is not.
- Watch for **integration users being deactivated** by HR or identity processes (the employee who created the integration leaves, and their account, which the integration used, is disabled). Use dedicated service identities.

### Vendor changes

- Track **API version deprecations** and **release calendars** (Chapter 12) in the integration catalogue.
- Test against **preview sandboxes** before vendor releases.
- Re-verify after vendor releases with smoke tests.

### Capacity and cost

- Watch growth trends in volume, API-allocation usage, broker storage and iPaaS consumption (many iPaaS products bill per task, message, flow or vCore).
- **Cost observability:** attribute costs per flow and per tenant. Chatty polling and unbounded retries are common cost leaks.

### Data retention

- Purge message stores, DLQs, logs and execution histories according to retention policy (privacy and cost).

### Continuous improvement

- Review incidents, alert noise, error-queue trends and support tickets quarterly; fix the top recurring causes.
- Keep design documents and runbooks current.

### Decommissioning

Integrations outlive their purpose. When retiring one:

1. Confirm no consumers remain (check logs and traffic for weeks).
2. Disable, then wait; then remove.
3. **Revoke credentials,** delete secrets, remove firewall rules and allow-listed IPs, remove partner certificates, remove webhook registrations at the provider, and delete topics, queues and subscriptions.
4. Archive documentation and update the catalogue.

Forgotten integrations with live credentials are a security risk (OWASP API9: Improper Inventory Management).

---

## 16.10 Operating integrations on an iPaaS

- Use the platform's **monitoring and alerting**, but forward logs, metrics and traces to your central observability stack for correlation with everything else.
- Configure **execution-history retention and payload masking** deliberately.
- Learn the platform's **replay and reprocess** capabilities and their limits.
- Track **platform limits and consumption** (tasks, connections, worker capacity, concurrency).
- Subscribe to the vendor's **status page and release notes**; iPaaS vendors also deprecate connectors and runtimes.
- Ensure **runtime upgrades** (Mule runtime versions, Boomi Atom updates, SAP Cloud Integration adapter updates) are tested and scheduled.

---

## Summary

- Promote one artefact through environments wired to matching partner environments; keep configuration and infrastructure as code.
- Instrument logs, metrics and traces with OpenTelemetry; propagate W3C Trace Context through messages; index by business keys.
- Monitor business signals (volume, freshness, completeness, reconciliation), not only errors. Silent failures are the dangerous ones.
- Alert on actionable symptoms, routed by ownership; define end-to-end SLOs with business owners.
- Write and rehearse runbooks; in incidents, mitigate, preserve messages, recover data safely, and review blamelessly.
- Day-2 work (credentials, certificates, vendor changes, capacity, cost, retention, decommissioning) is where most of the lifetime effort goes.

## Exercises

See [`exercises/16-operations.md`](../exercises/16-operations.md).

## Further reading

- Betsy Beyer et al., *Site Reliability Engineering* and *The Site Reliability Workbook* (O'Reilly, 2016 and 2018; free at sre.google).
- Charity Majors, Liz Fong-Jones and George Miranda, *Observability Engineering*, 2nd edition (O'Reilly, 2026).
- OpenTelemetry documentation and messaging semantic conventions (opentelemetry.io).
- W3C Trace Context Recommendation (w3.org/TR/trace-context).
- Alex Hidalgo, *Implementing Service Level Objectives* (O'Reilly, 2020).
