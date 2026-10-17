# Production readiness gate (Chapters 4 and 15)

## The problem

The pilot worked, the users like it, and the customer's sponsor wants it live on Monday. Is it ready? Without an agreed checklist, that question is answered by whoever is most impatient. With one, it is answered by evidence.

A **production readiness review** (the exit criterion of the build phase in Chapter 4) checks that a system can be run safely by the people who will own it: secured, monitored, recoverable, evaluated and handed over. A **go/no-go gate** is the decision at the end of that review. FDEs usually prepare the evidence, and the customer's IT, security and business owners make the call. Encoding the rules makes the call consistent, fast and hard to argue with.

## Terms

- **Severity:** how much an unmet item matters.
  - **Blocker:** must be met before go-live. Missing → **NO-GO**.
  - **Major:** may be met shortly after go-live, as a **condition** with a named owner and a due date. Missing owner or date, or a date already passed → NO-GO.
  - **Minor:** tracked, never changes the verdict.
- **Evidence:** a link to the proof (signed review, change ticket, test report). "Done" with no evidence is not done.
- **Numeric check:** a measured value compared with a threshold, such as an evaluation pass rate ≥ 0.9, or p95 latency (the time within which 95% of requests complete) ≤ the agreed target.
- **DPIA (data protection impact assessment):** the UK GDPR assessment required before processing personal data in ways likely to be high-risk.
- **DR (disaster recovery):** restoring service after a major failure. Backups that have never been restored are not tested backups.

## How `gate.py` decides

An item is **satisfied** when its `status` is `"done"`, it has at least one `evidence` link, and its `check` (if any) passes. Thresholds can be literal (`"value": 0.9`) or another metric (`"metric_target": "p95_latency_target_ms"`). A missing metric fails the check.

| Outcome | When |
|---|---|
| **GO** | Every blocker and major item satisfied |
| **GO WITH CONDITIONS** | Every blocker satisfied; each unmet major item has an owner and a due date on or after the assessment date |
| **NO-GO** | Any blocker unmet, any unmet major item without owner or due date (or already overdue), or an invalid checklist (duplicate IDs, unknown severity or operator) |

## The sample

`checklist.json` is the go-live checklist for a fictional Contoso Insurance claims coverage assistant, with 13 items: security review sign-off, SSO and access control, DPIA, evaluation pass rate ≥ 90%, all high-risk eval cases passing, monitoring and alerts, on-call and support owner, rollback plan, runbook, load test (p95 2,400 ms against a 3,000 ms target), backups and DR tested, handover accepted, and training materials.

Result: **GO WITH CONDITIONS**. DR testing is due 30 November 2026 and handover acceptance 15 December 2026; the training materials are a minor open item.

## Run it

```bash
python3 gate.py checklist.json     # exit code 0 for GO / GO WITH CONDITIONS, 1 for NO-GO
python3 -m unittest -v
```

The exit code lets a deployment pipeline refuse to promote a release on NO-GO.

## Extending it

- **Pull metrics automatically.** Fill `metrics` from the latest eval run (see `llm-eval-harness/`) and load test, rather than typing numbers.
- **Check the evidence.** Verify links resolve and documents are signed and recent; flag evidence older than, say, 90 days.
- **Sign-off.** Add an `approvals` list (customer IT, security, business owner) that must be complete for GO.
- **Track conditions.** Create tickets for conditions and re-run the gate weekly after go-live until they close.
- **Use your organisation's list.** Appendix C has a fuller checklist; regulated sectors add their own items (model risk, clinical safety, accessibility).

## Limitations

- The gate checks that evidence exists, not that it is good. A person still has to read the security review.
- Severity is a judgement. Agree it with the customer *before* the review, not during it.
- A GO is a point-in-time decision. Monitoring and incident response (Chapter 15) keep it true afterwards.
