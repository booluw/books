# Chapter 15. Production Readiness, Operations and Handover

> "Your last job on an engagement is to make yourself unnecessary."

## What you will learn

- What "production-ready" means in an enterprise, and how to prove it.
- How to run a production readiness review and a go/no-go decision.
- Release strategies that limit risk: pilots, canaries, feature flags and rollback.
- What to monitor, how to alert, and how to run incidents.
- How to define support models and service levels.
- How to hand over a system so that the customer (or a support team) can run it without you.

---

## 15.1 From working to production

A proof of value shows the system *can* work. Production means it works **reliably, securely and supportably**, every day, for everyone in scope, when the FDE isn't watching. The gap is large, and it is where many engagements stall (pilot purgatory, Chapter 6 §6.10).

Production readiness typically covers:

| Area | Questions |
|---|---|
| **Security** | Approved by the customer's security review? Access controls in place? Secrets managed? (Chapter 14) |
| **Reliability** | What happens when a dependency fails? Retries, timeouts, graceful degradation? |
| **Performance and scale** | Does it meet latency targets at expected peak load, plus headroom? |
| **Observability** | Can someone tell, quickly, whether it's healthy and why not? |
| **Data** | Pipelines monitored? Freshness agreed? Backups and restores tested? |
| **Quality (AI)** | Evaluation thresholds met? Regression suite in CI? Production monitoring? (Chapter 13) |
| **Operations** | Runbooks? On-call or support owner? Escalation paths? |
| **Recovery** | Rollback plan? Disaster recovery tested against agreed recovery objectives? |
| **Compliance** | DPIA, AI risk review, records of processing, audit logging? |
| **People** | Users trained? Support staff trained? Communications sent? |

## 15.2 The production readiness review

A **production readiness review (PRR)** is a structured check, before launch, that a system meets agreed standards. Google's site reliability engineering (SRE) practice popularised the term; most enterprises have their own version, often tied to change approval.

Run it as a checklist with evidence, not a meeting of opinions:

- Each item has an **owner**, a **severity** (blocker, major, minor) and **evidence** (a link to the test result, the signed approval, the dashboard, the runbook).
- **Blockers** without evidence mean **no-go**.
- **Majors** may proceed as **go with conditions**, each with an owner and due date.
- **Minors** go on the backlog.

[`examples/readiness-gate/`](../examples/readiness-gate/) implements this logic: it reads a checklist and evidence from JSON and returns GO, GO WITH CONDITIONS or NO-GO with reasons, including numeric checks such as minimum evaluation pass rate and maximum p95 latency. The full checklist is in Appendix C.

Running the example's sample checklist for a claims assistant produces:

```
Contoso Insurance claims coverage assistant: GO WITH CONDITIONS
10 of 13 items satisfied
Conditions (must be closed by the due date):
  - DR-1 Backups restored and disaster recovery tested
      owner: Contoso platform team; due 2026-11-30
  - HAND-1 Handover pack accepted by the customer's support team
      owner: Contoso claims IT; due 2026-12-15
Minor items open:
  . TRAIN-1 Adjuster training materials published
```

Every condition has a named owner and a date. A major item without both would turn the result into NO-GO, because a condition nobody owns will not be closed.

### Service level objectives

Agree measurable reliability targets before launch:

- A **service level indicator (SLI)** is a measured quantity, such as the share of requests that succeed or complete within 2 seconds.
- A **service level objective (SLO)** is a target for an SLI over a period, such as "99.5% of requests succeed each month".
- A **service level agreement (SLA)** is a contractual commitment, usually looser than the internal SLO, with remedies if missed.

The gap between 100% and the SLO is the **error budget**: the amount of unreliability you can tolerate. Choosing SLOs forces a useful conversation: a back-office summarisation tool doesn't need the availability of a payments system, and pretending it does wastes money.

For AI systems, add **quality SLOs** alongside availability: for example "sampled weekly grading shows ≥ 90% of coverage summaries correct".

## 15.3 Releasing safely

Never switch everyone over at once if you can avoid it.

| Strategy | How it works | When to use |
|---|---|---|
| **Pilot group** | A named team uses it first | Almost always, for new workflows |
| **Phased rollout** | Team by team or site by site | Large organisations; doubles as impact measurement (Chapter 13) |
| **Canary release** | A small percentage of traffic gets the new version; compare health before expanding | Changes to existing services |
| **Feature flags** | New behaviour switched on per user or group without redeploying | Fine-grained control; instant off switch |
| **Shadow mode** | New system runs alongside the old, outputs logged but not used | AI decisions where you want production evidence before acting |
| **Blue-green** | Two environments; switch traffic between them | Quick rollback for infrastructure changes |

### Rollback

Every release needs a tested way back:

- Keep the previous version deployable.
- Make database changes backward-compatible (add before you remove), so code can roll back without data rollback.
- For AI configuration (prompts, model versions, retrieval settings), version it and make rollback a configuration change.
- Write down the rollback decision criteria in advance: "If error rate exceeds 2% for 10 minutes, or the claims team lead requests it, roll back."

## 15.4 Observability

**Observability** is the ability to understand a system's internal state from its outputs. The three classic signals:

- **Logs:** timestamped records of events. Use structured logs (JSON), include a request or correlation ID, and never log secrets or unnecessary personal data.
- **Metrics:** numeric measurements over time: request rate, error rate, latency percentiles, queue depth, cost, data freshness.
- **Traces:** the path of a single request through multiple services, with timing for each step. Particularly useful for agents, where one user request becomes many model and tool calls. **OpenTelemetry** is the common open standard for traces, metrics and logs.

For AI systems, also capture the model version, prompt version, retrieved sources, tool calls, token counts and evaluation flags for each request (subject to retention rules).

### Dashboards and alerts

- One **health dashboard** that a support engineer can read in thirty seconds: is it up, is it fast, is it correct, is the data fresh, what does it cost?
- **Alert on symptoms users feel** (errors, latency, stale data, quality drops), not on every internal metric. Every alert should be actionable and link to a runbook.
- Route alerts to the **support owner**, not to the FDE's personal phone, before handover.

## 15.5 Incidents

An **incident** is an unplanned event that disrupts or degrades the service. Agree the process before launch:

1. **Detect:** alert or user report.
2. **Triage and declare:** assess severity (for example Sev 1: users can't work; Sev 3: minor degradation) and assign an incident lead.
3. **Communicate:** acknowledge to users and stakeholders; update on a schedule (Chapter 8 §8.9).
4. **Mitigate:** restore service first (roll back, disable the feature flag, fail over), then investigate.
5. **Resolve and review:** write a **blameless post-incident review**: timeline, impact, contributing causes, what went well, actions with owners.

For AI systems, include quality incidents: "the model started citing withdrawn policy wordings" is an incident even if every request returns HTTP 200.

## 15.6 Support models

Who supports the system after go-live? Common models:

| Model | How it works | Fits |
|---|---|---|
| **Customer-operated** | Customer's IT or platform team runs it; vendor supports the product | Customer has a capable team; code lives in customer environment |
| **Vendor-operated** | Vendor runs it as a managed service | SaaS deployments; customer lacks capacity |
| **Partner-operated** | A systems integrator or managed-service partner runs it | Large enterprises with existing partners |
| **Hybrid** | Customer handles first line (user questions); vendor handles platform and complex issues | Most common in practice |

Define **support tiers**:

- **Tier 1:** user questions, access requests, known issues (customer service desk).
- **Tier 2:** configuration, data issues, diagnosing failures (customer platform team or vendor support).
- **Tier 3:** product defects, complex engineering (vendor engineering).

Write the escalation path down, with contacts, hours and response-time targets. The FDE is **not** a support tier. An FDE who remains the de facto support channel after handover is a sign the handover failed.

## 15.7 Handover

**Handover** transfers ownership of the system (operation, change and support) from the FDE to the people who will run it long-term. Done badly, it produces a system nobody understands, which degrades until it's switched off. Done well, it is the FDE's most durable contribution.

### Plan it from the start

Handover is not a final-week activity. From the first week:

- **Name the receiving team** and involve them in design decisions.
- **Pair** with their engineers on real work; let them make changes while you review.
- **Write documentation as you go** (README, ADRs, runbooks), not at the end.
- **Use their tools and standards** (repositories, CI, monitoring, ticketing), so there's nothing to migrate.

### The handover pack

Template: [`templates/handover-pack.md`](../templates/handover-pack.md). Contents:

1. **System overview:** purpose, users, business value, success criteria and current results.
2. **Architecture:** diagrams, components, data flows, integrations, environments.
3. **Access:** who has what, how to grant and revoke it.
4. **Operations:** runbooks for routine tasks (deploy, roll back, rotate secrets, re-index documents, add users) and for known failure modes.
5. **Monitoring:** dashboards, alerts and what each means.
6. **Quality:** evaluation sets, how to run them, thresholds, and how to add cases.
7. **Change:** how to make common changes (update a prompt, add a document source, adjust a threshold) safely.
8. **Known issues and limitations**, with workarounds.
9. **Decisions:** the ADR log.
10. **Support model and contacts.**
11. **Ownership:** who owns the code, configuration and data pipelines.
12. **Training record:** who was trained on what.

### Runbooks

A **runbook** is a step-by-step procedure for an operational task, written so that someone unfamiliar with the system can follow it under pressure:

```
Runbook: Coverage panel shows "data as of" more than 48 hours old

Symptom: Freshness alert fires; users report old policy data.
Impact: Summaries may miss recent endorsements. Users can still work.
Check:
  1. Open pipeline dashboard → "policy_replica_sync". Last success time?
  2. If failed: read the error in the job log.
     - "connection refused" → the replica is down; contact DBA on-call (ext. 4410).
     - "schema mismatch" → the policy system was upgraded; see ADR 012, then step 3.
  3. Re-run the job: `make sync-policies ENV=prod` (safe to re-run; idempotent).
Escalate: if not resolved in 4 hours, page Tier 3 (vendor) via the support portal.
```

### Proving the handover worked

The best acceptance test is practice. The receiving team operates the system **unaided** for an agreed period (for example two weeks), including at least one deploy, one routine change and one incident or simulated incident, while the FDE observes but doesn't touch. Gaps that appear become documentation or training fixes. Only then is the handover accepted.

### Knowledge transfer sessions

Schedule focused sessions rather than one long walkthrough:

1. Architecture and design decisions.
2. Operating: deploy, monitor, roll back.
3. Changing: prompts, configuration, data sources, evaluation.
4. Troubleshooting: walk through each runbook on a real or simulated failure.

Record them (with consent) and link the recordings from the handover pack.

## 15.8 Leaving well

At the end of an engagement:

- Confirm the handover is accepted, in writing.
- Remove your access (Chapter 14 §14.7), and delete local copies of data.
- Deliver the impact report (Chapter 13 §13.9) and hold the retrospective (template: [`templates/engagement-retrospective.md`](../templates/engagement-retrospective.md)).
- Write field reports for anything the product should learn (Chapter 16).
- Tell people how to reach your company for future needs, so they don't reach you personally out of habit.

---

## Summary

- Production means reliable, secure and supportable without the FDE. Readiness spans security, reliability, performance, observability, data, AI quality, operations, recovery, compliance and people.
- Run an evidence-based production readiness review with blockers, majors and minors; agree SLIs, SLOs and error budgets, including quality SLOs for AI.
- Release gradually (pilot, phased, canary, flags, shadow mode) with a tested rollback and written rollback criteria.
- Instrument logs, metrics and traces (plus AI-specific fields); build a thirty-second health dashboard; alert on symptoms with runbooks.
- Agree incident processes and a tiered support model. The FDE is not a support tier.
- Plan handover from day one: name and pair with the receiving team, document as you go, deliver a complete handover pack, and prove it with a period of unaided operation.

## Exercises

See [`exercises/15-production-and-handover.md`](../exercises/15-production-and-handover.md).

## Further reading

- Betsy Beyer et al., *Site Reliability Engineering* (Google, 2016) and *The Site Reliability Workbook* (2018), especially chapters on SLOs, launches and postmortems.
- Michael Nygard, *Release It!* (2nd edition, 2018).
- OpenTelemetry documentation (opentelemetry.io).
- Atul Gawande, *The Checklist Manifesto* (2009).
