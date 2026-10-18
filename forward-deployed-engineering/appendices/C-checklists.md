# Appendix C. Checklists

Practical checklists for each stage of a forward deployed engagement. Copy them into tickets, engagement plans or review agendas, and adapt them to your product, your industry and the customer's own standards. Each list links to the chapter that explains *why* each item matters, and to the matching template where one exists.

A checklist does not replace judgement. As Atul Gawande argues in *The Checklist Manifesto*, its job is to make sure the obvious, easily forgotten steps happen, so attention is free for the hard ones.

| # | Checklist | When | Chapter |
|---|---|---|---|
| C.1 | [Engagement qualification (Phase 0)](#c1-engagement-qualification-phase-0) | Before committing FDE time | [4](../chapters/04-engagement-lifecycle.md), [3](../chapters/03-business.md) |
| C.2 | [First week on site](#c2-first-week-on-site) | Days 1–5 | [9](../chapters/09-toolkit.md) |
| C.3 | [Discovery](#c3-discovery) | Phase 1 | [5](../chapters/05-discovery-and-decomposition.md) |
| C.4 | [Success plan review](#c4-success-plan-review) | Phase 2, before sign-off | [6](../chapters/06-scoping.md) |
| C.5 | [SOW review](#c5-statement-of-work-sow-review) | Before the contract is signed | [6](../chapters/06-scoping.md) |
| C.6 | [Access and dependency tracking](#c6-access-and-dependency-tracking) | From Phase 2, weekly | [4](../chapters/04-engagement-lifecycle.md), [6](../chapters/06-scoping.md) |
| C.7 | [Demo preparation](#c7-demo-preparation) | Before every demo | [8](../chapters/08-communication.md) |
| C.8 | [Weekly update](#c8-weekly-update) | Every Friday | [8](../chapters/08-communication.md) |
| C.9 | [Security review pack](#c9-security-review-pack) | Start in scoping | [14](../chapters/14-security-and-restricted-environments.md) |
| C.10 | [AI deployment guardrails (RAG and agents)](#c10-ai-deployment-guardrails-rag-and-agents) | Design and build | [12](../chapters/12-ai-deployment.md) |
| C.11 | [Evaluation readiness](#c11-evaluation-readiness) | Before any quality claim | [13](../chapters/13-evaluation-and-impact.md) |
| C.12 | [Production readiness](#c12-production-readiness) | Before go-live | [15](../chapters/15-production-and-handover.md) |
| C.13 | [Handover acceptance](#c13-handover-acceptance) | Before leaving | [15](../chapters/15-production-and-handover.md) |
| C.14 | [Engagement close and offboarding](#c14-engagement-close-and-offboarding) | Last week | [4](../chapters/04-engagement-lifecycle.md), [14](../chapters/14-security-and-restricted-environments.md), [15](../chapters/15-production-and-handover.md) |
| C.15 | [Field report quality](#c15-field-report-quality) | Before filing | [8](../chapters/08-communication.md), [16](../chapters/16-field-to-product.md) |

---

## C.1 Engagement qualification (Phase 0)

Decide whether this customer and this problem justify forward deployment. See [Chapter 4 §4.2](../chapters/04-engagement-lifecycle.md) and the factors in [Chapter 3 §3.5](../chapters/03-business.md).

**Sponsor and problem**

- [ ] A named executive sponsor with budget and authority
- [ ] A specific, painful, valuable problem (not "we want to do AI")
- [ ] A rough value estimate (time, money or risk) the sponsor recognises ([Chapter 5 §5.8](../chapters/05-discovery-and-decomposition.md))
- [ ] The sponsor can say what would make them cancel the project

**Feasibility**

- [ ] The data and systems needed can be reached within weeks, not quarters
- [ ] The customer will commit people's time: subject-matter experts, IT, security
- [ ] The problem fits the product; it would not mean building a custom application ([Chapter 11](../chapters/11-configure-extend-change.md))
- [ ] Known constraints listed: security, regulation, works councils or unions, restricted environments, budget cycles

**Commercial and strategic fit**

- [ ] Commercial model known: bundled, paid pilot, bootcamp, SOW, outcome-based, partner-delivered or build-operate-transfer ([Chapter 3 §3.4](../chapters/03-business.md))
- [ ] Commercial upside understood: ACV, expansion potential, renewal date, reference value
- [ ] Learning value for the product: new segment, new pattern, or a repeat of a known one
- [ ] FDE capacity available without splitting anyone across more than two engagements ([Chapter 17 §17.6](../chapters/17-running-an-fde-org.md))
- [ ] Planned end and exit path (customer, partner or support team) identified

**Output**

- [ ] Go or no-go decision recorded, with the engagement hypothesis in one paragraph

## C.2 First week on site

Become productive in an unfamiliar environment fast. See [Chapter 9 §9.8](../chapters/09-toolkit.md).

**Days 1–2: access and orientation**

- [ ] Accounts, laptop or virtual desktop, VPN, email, chat, ticketing and code repositories working
- [ ] Customer device and data policies read, including policy on AI coding assistants ([Chapter 9 §9.6](../chapters/09-toolkit.md))
- [ ] Existing architecture documentation read; gaps noted
- [ ] People found: platform owner, DBA, security contact, the engineer who knows the history
- [ ] Change process learned: how code reaches production, who approves, release windows, CAB dates

**Days 2–4: data and systems**

- [ ] Environments identified (development, test, staging, production) and which you may use
- [ ] Read-only queries run against in-scope systems; first data profile produced ([Chapter 10 §10.3](../chapters/10-enterprise-data.md), [`examples/data-profiler/`](../examples/data-profiler/))
- [ ] One real case traced end to end through the systems
- [ ] Profile reviewed with the data owner

**Days 3–5: ship something small**

- [ ] A script, report or tool that helps someone with a real problem, delivered
- [ ] Repository set up with version control, secrets in a secret manager, a README and a test ([Chapter 9 §9.9](../chapters/09-toolkit.md))
- [ ] First weekly update sent ([C.8](#c8-weekly-update))
- [ ] Notes started; they will become handover documentation

## C.3 Discovery

Understand how the operation really works before building. See [Chapter 5](../chapters/05-discovery-and-decomposition.md) and [`templates/discovery-guide.md`](../templates/discovery-guide.md).

**Preparation**

- [ ] Public material read: annual reports, investor presentations, filings, job postings
- [ ] Deal history read: what sales promised, what the customer asked for, what the proof of concept showed
- [ ] Domain vocabulary learned
- [ ] Hypotheses drafted (and held loosely)
- [ ] Interview plan covers every level: sponsor, managers, front line, IT and data, security and legal, sceptics

**Conducting**

- [ ] Front-line staff interviewed early
- [ ] Questions about past events, not hypotheticals; artefacts requested; answers quantified
- [ ] At least one half-day of shadowing per key role, with permission and within the customer's rules ([§5.5](../chapters/05-discovery-and-decomposition.md))
- [ ] Notes written up the same day, with quotes
- [ ] No pitching

**Outputs**

- [ ] Discovery summary in the customer's language
- [ ] Current-state maps: workflow (swimlanes, timings, error points), systems, data inventory
- [ ] Decomposition by business driver, not by technology ([`templates/problem-decomposition-canvas.md`](../templates/problem-decomposition-canvas.md))
- [ ] Value and feasibility (data, technical, organisational), time to value and risk estimated per sub-problem
- [ ] Non-AI options considered for every driver
- [ ] Recommended lighthouse use case, with a backlog of others
- [ ] Risks and constraints listed; proposed success criteria drafted
- [ ] 30-minute readout held; the sponsor agrees with the picture

## C.4 Success plan review

Check the working agreement before the sponsor signs. See [Chapter 6 §6.7](../chapters/06-scoping.md) and [`templates/success-plan.md`](../templates/success-plan.md).

- [ ] Objective is one paragraph in business language
- [ ] Success criteria at three levels: business outcome, adoption, system quality
- [ ] Each criterion is specific, measurable, achievable, relevant, time-bound, **owned** and **baselined**
- [ ] Each criterion has a baseline (or a plan and dates to measure one), target, method, customer owner and date
- [ ] Leading indicators agreed for the pilot window; how the lagging metric will be measured later is agreed
- [ ] Comparison or control group planned where feasible ([Chapter 13 §13.8](../chapters/13-evaluation-and-impact.md))
- [ ] No weak criteria ("deploy an assistant", "users are satisfied", "95% accuracy" without data and judge, "production-ready" without a checklist)
- [ ] Scope written as **in**, **out** and **later**, covering users, process, data, integration, non-functional requirements, deliverables and support
- [ ] Phases and milestones with exit criteria
- [ ] RACI agreed
- [ ] Dependencies and access table attached ([C.6](#c6-access-and-dependency-tracking))
- [ ] Effort and elapsed time both stated; contingency named
- [ ] Risks with mitigations and owners
- [ ] Governance: weekly working session, weekly written update, sponsor review cadence, escalation path
- [ ] **Production decision agreed up front:** who decides, by when, from which budget ([§6.10](../chapters/06-scoping.md))
- [ ] Production owners (IT, security, the team that will run it) named and involved
- [ ] Consistent with the SOW, if there is one
- [ ] Signed, with names and dates

## C.5 Statement of work (SOW) review

Review every SOW you will deliver; SOWs written without delivery input routinely commit to the impossible. See [Chapter 6 §6.8](../chapters/06-scoping.md) and [`templates/statement-of-work.md`](../templates/statement-of-work.md). This is not legal advice; involve your legal team.

- [ ] Objectives match the success plan and describe outcomes, not only activities
- [ ] Each deliverable is specific and has acceptance criteria
- [ ] Out-of-scope list covers likely misunderstandings
- [ ] Assumptions stated: data-access dates, customer staff availability, environments, decision turnaround
- [ ] Customer responsibilities name roles and time commitments, including access provision
- [ ] Timeline uses realistic elapsed time, including security review, CAB and procurement
- [ ] Acceptance process: who accepts, how, and deemed acceptance after N days of silence
- [ ] Change control: how changes are requested, estimated, approved and priced
- [ ] Commercials understood: fixed fee or time and materials, milestones, credit against subscription
- [ ] Fixed fee only where scope is tight and change control is strong
- [ ] **IP clause protects the feedback loop:** the customer owns its data and customer-specific configuration; the vendor keeps its platform and generic tools, templates and improvements, and may reuse them ([Chapter 16](../chapters/16-field-to-product.md))
- [ ] Data handling: what customer data the vendor may access, where, for how long, and deletion at the end
- [ ] Ownership and support of custom code after the engagement is stated ([Chapter 11 §11.5](../chapters/11-configure-extend-change.md))

## C.6 Access and dependency tracking

Access is the hidden critical path. Request it in Phase 2 and track it like a deliverable. See [Chapter 4 §4.11](../chapters/04-engagement-lifecycle.md) and [Chapter 6 §6.6](../chapters/06-scoping.md).

For **each** dependency, record:

- [ ] What is needed (account, VPN, data extract, replica access, environment, approval, SME time)
- [ ] Customer owner (a named person or team)
- [ ] Needed-by date, tied to a milestone
- [ ] Typical lead time, as given by the owning team
- [ ] Status (not started, requested, scheduled, draft, granted) and date of last chase
- [ ] Minimum data requested: specific tables, fields and date ranges ([Chapter 10 §10.2](../chapters/10-enterprise-data.md))
- [ ] Where the data may go (environment, region, network) and when copies will be deleted

Every week:

- [ ] Overdue items escalated through the sponsor, in writing
- [ ] Plan B ready for each critical item: restricted extract, sandbox, or clearly labelled synthetic data
- [ ] Timeline reset in writing when a dependency slips
- [ ] No "temporary" extract has quietly become the production integration
- [ ] Typical items covered: VPN and accounts; data access (replica or warehouse); security architecture review; DPIA; AI or model risk review; SME availability; production environment; CAB slot

## C.7 Demo preparation

Demos build belief when they show real progress on the customer's own problem. See [Chapter 8 §8.7](../chapters/08-communication.md).

- [ ] Audience and the decision you want from them identified
- [ ] Opening states the outcome in numbers ("median time on coverage questions fell from 25 to 7 minutes on 412 claims")
- [ ] Customer's real (or approved, realistic) data used
- [ ] Walkthrough follows a real task from the user's point of view, not a feature tour
- [ ] A front-line user is ready to drive, if possible
- [ ] At least one honest failure case prepared, showing how the user sees it
- [ ] No hard-coded happy path; any case the audience asks for will run
- [ ] For AI: demo cases tested repeatedly at the live temperature and configuration; citations shown; difficult and "not found" cases ready
- [ ] Variability and how quality is measured explained in one sentence
- [ ] Rehearsed the day before, on the same environment
- [ ] Backup recording ready (unedited; never hide latency or errors)
- [ ] Slides kept to a minimum before the software
- [ ] Ends with asks and next steps; follow-up written within 24 hours

## C.8 Weekly update

The FDE's heartbeat. See [Chapter 8 §8.3](../chapters/08-communication.md) and [`templates/weekly-update.md`](../templates/weekly-update.md).

- [ ] Subject line: customer, project, week number, RAG status
- [ ] Three-line summary, answer first
- [ ] Progress against each success criterion: current value, baseline, target
- [ ] Done this week; planned next week
- [ ] Decisions needed, each with owner and date
- [ ] Risks and blockers, each with owner and next step
- [ ] Status colour explained if not green: cause, impact, what is needed
- [ ] Status moved to amber as soon as a risk appeared (never green straight to red)
- [ ] Uses the customer's words, quantifies, and is honest about uncertainty
- [ ] Sent to the customer owner, sponsor and internal team; field notes passed to the product team
- [ ] Bad news delivered in person or by call first, then confirmed here ([§8.9](../chapters/08-communication.md))

## C.9 Security review pack

Bring a complete, precise pack early, so the review confirms rather than discovers. See [Chapter 14 §14.2](../chapters/14-security-and-restricted-environments.md) and [`templates/security-and-ai-risk-review.md`](../templates/security-and-ai-risk-review.md).

**Process**

- [ ] Security contact asked, during scoping, what they need and how long each step takes
- [ ] Review types identified: vendor risk assessment, architecture review, data protection review (DPIA), AI or model risk review, penetration test, change approval
- [ ] Company's standard security pack and answered questionnaires (SIG, CAIQ) reused

**Contents**

- [ ] Architecture diagram and data-flow diagram
- [ ] Data inventory with classifications and legal basis
- [ ] Hosting: regions, tenancy, data residency, sub-processors
- [ ] Access model: SSO (SAML or OpenID Connect), SCIM provisioning, RBAC mapped to customer groups, least-privilege service accounts, privileged access process ([§14.5](../chapters/14-security-and-restricted-environments.md))
- [ ] Encryption at rest and in transit, stated precisely (algorithm, key ownership, TLS version)
- [ ] Logging and audit: what is logged, where, retention
- [ ] Certifications and attestations: SOC 2, ISO/IEC 27001, ISO/IEC 42001, FedRAMP or national schemes as relevant
- [ ] Model provider data terms: retention, training use, region
- [ ] AI-specific controls mapped to the risks in [§14.4](../chapters/14-security-and-restricted-environments.md): prompt injection, sensitive data disclosure, excessive agency, data leaving the boundary, insecure output handling, supply chain, high-stakes errors, auditability
- [ ] Lethal-trifecta analysis for every agent: at least one leg removed, or human approval on the external channel
- [ ] Evaluation evidence and human oversight design
- [ ] Applicable regulation identified with the customer's counsel (GDPR, EU AI Act risk class, HIPAA, DORA, SR 11-7, sector rules)
- [ ] Incident response agreed: contacts both ways, notification timelines, kill switch, evidence preservation ([§14.8](../chapters/14-security-and-restricted-environments.md))

**Answers**

- [ ] Every answer precise and true; gaps stated with a plan, never over-claimed
- [ ] For restricted environments: bundled release, SBOM, transfer process, self-hostable models, cleared staff ([§14.6](../chapters/14-security-and-restricted-environments.md))

## C.10 AI deployment guardrails (RAG and agents)

See [Chapter 12](../chapters/12-ai-deployment.md), [`examples/permission-aware-retrieval/`](../examples/permission-aware-retrieval/) and [`examples/agent-guardrails/`](../examples/agent-guardrails/).

**Pattern choice**

- [ ] Least autonomous pattern that delivers the value chosen (assistant, extraction, workflow step before free-roaming agent)
- [ ] Non-AI alternatives considered for each step
- [ ] Plan for earning more autonomy on evidence (shadow mode, then approval, then sampled auto-execution) ([Chapter 20 §20.2](../chapters/20-case-studies.md))

**Retrieval (RAG)**

- [ ] Parsing tested on the customer's real documents (tables, scans, slides)
- [ ] Chunks follow document structure and carry title and headings
- [ ] Retrieval method chosen (keyword, vector, hybrid, reranker) and evaluated separately (recall at k)
- [ ] Metadata captured: type, date, owner, version, jurisdiction, ACL
- [ ] ACLs captured at ingestion and kept in sync; user groups resolved from the identity provider at query time
- [ ] **Security trimming before ranking and generation**; deny by default when an ACL is missing
- [ ] Citations checked: every cited source was retrieved and is readable by the user
- [ ] The model can say "not found"
- [ ] Re-indexing on change and prompt removal of deleted documents
- [ ] Documents used for each answer logged for audit

**Agents and tools**

- [ ] Tools are business-level (`get_policy_coverage(id)`), never `run_sql`
- [ ] Clear tool descriptions; strict input validation in code; bounded, paginated output with no secrets
- [ ] Read and write tools separated; each tool classified read, write or irreversible
- [ ] Tool allow-lists per role
- [ ] Human approval for irreversible or high-value actions, with what the reviewer needs to judge quickly
- [ ] Budgets on tool calls, tokens, spend and time per run
- [ ] Agent acts with the user's own permissions, not a super-user service account
- [ ] Tamper-evident audit log of every call, argument, result and approval
- [ ] Untrusted content isolated from instructions; tool outputs screened for injection
- [ ] Lethal trifecta broken ([Chapter 14 §14.4](../chapters/14-security-and-restricted-environments.md))
- [ ] Output filtered for sensitive data; model output never executed or rendered without treatment as untrusted input
- [ ] Design reviewed against the question: if the model were fully compromised, is the harm limited, recoverable and logged?

**MCP and models**

- [ ] MCP servers authenticate callers, act with user permissions, validate inputs, rate-limit and log ([§12.6](../chapters/12-ai-deployment.md))
- [ ] Third-party MCP servers, packages and models reviewed; versions pinned
- [ ] Model chosen on the customer's eval set, cost, latency, deployment options and data terms; version pinned
- [ ] Cost estimated (requests × tokens × price) and controlled with caching, routing, batching and loop caps
- [ ] Region-pinned endpoints where residency applies

## C.11 Evaluation readiness

Do not claim a quality figure until these are true. See [Chapter 13](../chapters/13-evaluation-and-impact.md) and [`examples/llm-eval-harness/`](../examples/llm-eval-harness/).

**Eval set**

- [ ] Built from the customer's real cases (50–200 well-chosen cases to start)
- [ ] Stratified and tagged by slice (case type, document type, language, difficulty, segment)
- [ ] Includes "should refuse" cases: out-of-scope questions, data the user may not see
- [ ] Includes adversarial and injection cases with security input
- [ ] Includes high-risk cases, tagged so they can be gated separately
- [ ] Sensitive data handled per the customer's rules
- [ ] Versioned in source control; cases never edited to make a run pass
- [ ] Hold-out portion kept back from prompt iteration

**Labels and graders**

- [ ] Rubric written with SMEs (correct, partially correct, wrong, with examples)
- [ ] Two experts labelled a sample independently; agreement measured
- [ ] Simplest reliable grader used per property (exact, rule-based, reference, model, human)
- [ ] Any LLM judge validated against human labels before it gates releases; judged one property at a time with pass/fail or small scales
- [ ] Retrieval and tool choices evaluated as components, not only end results

**Process**

- [ ] Eval suite runs on every change: prompt, model, retrieval, code, data refresh
- [ ] Release thresholds agreed: overall pass rate, high-risk slice pass rate, maximum slice regression
- [ ] Failures read, not just scored
- [ ] Every production failure added to the set after it is fixed
- [ ] Run metadata recorded: model version, prompt version, temperature, date
- [ ] Production monitoring planned: usage, latency, errors, cost, feedback, override rate, refusal rate, sampled grading, input drift, safety signals ([§13.6](../chapters/13-evaluation-and-impact.md))

**Impact**

- [ ] Measurement design chosen: before-and-after, phased rollout, difference-in-differences or randomised trial
- [ ] Adoption measured by reach, depth, retention and reliance against eligible tasks
- [ ] Financial conversion agreed with the customer's finance team; ranges and assumptions stated; costs subtracted ([`examples/impact-calculator/`](../examples/impact-calculator/))

## C.12 Production readiness

Run the review as a checklist with **evidence**, not a meeting of opinions. See [Chapter 15 §15.2](../chapters/15-production-and-handover.md) and [`examples/readiness-gate/`](../examples/readiness-gate/).

**Rules** (as implemented in `gate.py`):

- Each item has an **owner**, a **severity** and **evidence** (a link to the signed review, change ticket, test report, dashboard or runbook). "Done" with no evidence is not done.
- An item is **satisfied** when its status is done, it has at least one evidence link, and any numeric check passes. A missing metric fails the check.
- **GO:** every blocker and major item satisfied.
- **GO WITH CONDITIONS:** every blocker satisfied, and each unmet major item has an owner and a due date on or after the assessment date.
- **NO-GO:** any blocker unmet; any unmet major without an owner or due date, or already overdue; or an invalid checklist.
- **Minor** items are tracked but never change the verdict.
- Agree severities with the customer **before** the review, not during it.

**Core items** (the sample [`checklist.json`](../examples/readiness-gate/checklist.json); IDs match)

| ID | Item | Severity |
|---|---|---|
| SEC-1 | Security review signed off by customer security team | Blocker |
| SEC-2 | SSO and role-based access control in place; leavers removed automatically | Blocker |
| DATA-1 | Data protection impact assessment (DPIA) approved | Blocker |
| EVAL-1 | Evaluation pass rate at or above the agreed threshold (sample: ≥ 90%) on the agreed eval set | Blocker |
| EVAL-2 | Every high-risk eval case passes (pass rate = 100%) | Blocker |
| OPS-1 | Monitoring dashboards and alerts routed to on-call | Blocker |
| OPS-2 | On-call and support owner named for after go-live | Blocker |
| OPS-3 | Rollback plan written and rehearsed | Blocker |
| OPS-4 | Runbook covering common failures and escalation | Major |
| OPS-5 | Load test at expected peak: p95 latency within target | Major |
| DR-1 | Backups restored and disaster recovery tested | Major |
| HAND-1 | Handover pack accepted by the customer's support team | Major |
| TRAIN-1 | User training materials published | Minor |

As checkboxes:

- [ ] SEC-1 Security review signed off (blocker)
- [ ] SEC-2 SSO and RBAC; automatic leaver removal (blocker)
- [ ] DATA-1 DPIA approved (blocker)
- [ ] EVAL-1 Eval pass rate ≥ agreed threshold (blocker)
- [ ] EVAL-2 All high-risk eval cases pass (blocker)
- [ ] OPS-1 Dashboards and alerts routed to on-call (blocker)
- [ ] OPS-2 On-call and support owner named (blocker)
- [ ] OPS-3 Rollback plan written and rehearsed (blocker)
- [ ] OPS-4 Runbook for common failures and escalation (major)
- [ ] OPS-5 Load test at peak; p95 latency within target (major)
- [ ] DR-1 Backups restored; DR tested (major)
- [ ] HAND-1 Handover pack accepted (major)
- [ ] TRAIN-1 Training materials published (minor)

**Further items** to add as your organisation requires (assign severity with the customer):

- [ ] Secrets in a secret manager; none in code or configuration repositories
- [ ] Retries, timeouts and graceful degradation when each dependency fails
- [ ] SLIs and SLOs agreed, including a quality SLO for AI; error budget understood
- [ ] Data pipelines monitored for failures and freshness; "data as of" shown to users
- [ ] Regression eval suite running in CI
- [ ] Release strategy chosen (pilot group, phased, canary, feature flags, shadow mode, blue-green) with written rollback criteria
- [ ] AI configuration (prompts, model versions, retrieval settings) versioned; rollback is a configuration change
- [ ] Logs structured with correlation IDs; traces for agent runs; model and prompt versions, sources, tool calls and token counts captured (within retention rules)
- [ ] Thirty-second health dashboard: up, fast, correct, fresh, cost
- [ ] Alerts on user-felt symptoms, each linked to a runbook, routed to the support owner (not the FDE)
- [ ] Incident process and severity levels agreed; tabletop exercise held with customer security
- [ ] Support model and tiers written down, with contacts, hours and response targets
- [ ] Compliance records complete: AI or model risk review, records of processing, audit logging
- [ ] Sector items: model risk validation (banking), clinical safety case (health), accessibility
- [ ] Users and support staff trained; launch communications sent
- [ ] Customer IT and security sign-off recorded

## C.13 Handover acceptance

Handover is planned from day one and proven by practice. See [Chapter 15 §15.7](../chapters/15-production-and-handover.md), [Chapter 20 §20.6](../chapters/20-case-studies.md) and [`templates/handover-pack.md`](../templates/handover-pack.md).

**From the first week**

- [ ] Receiving team named and involved in design decisions
- [ ] Their engineers paired on real work, making changes while you review
- [ ] Their repositories, CI, monitoring and ticketing used, so nothing needs migrating
- [ ] Documentation written as you go: README, ADRs, runbooks

**Handover pack complete**

- [ ] System overview: purpose, users, value, success criteria and current results
- [ ] Architecture: diagrams, components, data flows, integrations, environments
- [ ] Access: who has what; how to grant and revoke
- [ ] Runbooks for routine tasks (deploy, roll back, rotate secrets, re-index, add users) and known failure modes
- [ ] Monitoring: dashboards, alerts and what each means
- [ ] Quality: eval sets, how to run them, thresholds, how to add cases
- [ ] Change: how to update a prompt, add a data source or adjust a threshold safely
- [ ] Known issues and limitations, with workarounds
- [ ] ADR log
- [ ] Support model, tiers and contacts
- [ ] Ownership of code, configuration and pipelines (a team, not a person)
- [ ] Training record

**Knowledge transfer**

- [ ] Sessions held: architecture and decisions; operating; changing; troubleshooting each runbook
- [ ] Sessions recorded (with consent) and linked from the pack

**Proof**

- [ ] Receiving team operated the system **unaided** for the agreed period (for example two weeks)
- [ ] During it: at least one deploy, one routine change and one real or simulated incident
- [ ] FDE observed without touching; gaps found became documentation or training fixes
- [ ] Alerts route to the support owner, not the FDE
- [ ] Handover accepted **in writing** by the receiving team

## C.14 Engagement close and offboarding

End deliberately, even when the relationship continues. See [Chapter 4 §4.13](../chapters/04-engagement-lifecycle.md), [Chapter 14 §14.7](../chapters/14-security-and-restricted-environments.md) and [Chapter 15 §15.8](../chapters/15-production-and-handover.md).

**Outcomes**

- [ ] Impact report delivered against each success criterion, validated by the customer's finance or operations team ([Chapter 13 §13.9](../chapters/13-evaluation-and-impact.md))
- [ ] Executive brief the sponsor can forward
- [ ] Next step explicit: expansion proposal, steady state, or clean exit
- [ ] Case study or reference requested, if the customer agrees

**Learning**

- [ ] Retrospective held with the customer and internally ([`templates/engagement-retrospective.md`](../templates/engagement-retrospective.md))
- [ ] Field reports filed for every product gap, bug and pattern ([C.15](#c15-field-report-quality))
- [ ] Reusable components proposed to the product or template library (no customer data or names)
- [ ] Playbook updated; actual duration recorded for reference-class estimates ([Chapter 6 §6.6](../chapters/06-scoping.md))
- [ ] Custom-component inventory updated: component, version, owner, supported product versions ([Chapter 11 §11.5](../chapters/11-configure-extend-change.md))

**Offboarding**

- [ ] All your access revoked: accounts, VPN, repositories, privileged access, tokens
- [ ] Customer devices and badges returned
- [ ] Local copies of customer data and code deleted as agreed; deletion confirmed in writing
- [ ] Nothing customer-specific carried into your personal toolkit ([Chapter 9 §9.10](../chapters/09-toolkit.md))
- [ ] Customer told how to reach your company (not you personally) for future needs
- [ ] People thanked by name, especially customer staff who made it work
- [ ] Capacity model updated; real break planned before the next engagement ([Chapter 18 §18.4](../chapters/18-life-as-an-fde.md))

## C.15 Field report quality

Field reports that are specific, evidenced and quantified get acted on. See [Chapter 8 §8.6](../chapters/08-communication.md), [Chapter 16 §16.3](../chapters/16-field-to-product.md), [`templates/field-report.md`](../templates/field-report.md) and [`examples/feedback-tracker/`](../examples/feedback-tracker/).

- [ ] Describes the **problem**, the user and the context, not only the requested feature
- [ ] Type stated: bug, gap, pattern, reusable code, playbook, evaluation asset, market insight or documentation gap
- [ ] **Evidence:** quotes, screenshots, data
- [ ] **Workaround** described: what you built, how long it took, how it is maintained
- [ ] **Impact quantified:** users affected, frequency, revenue (ARR) at risk or unlocked, deployment time added
- [ ] Severity stated
- [ ] **Other customers** with the same need linked; distinct-customer count stated (rule of three)
- [ ] A **generalisation** proposed: what is core, what should be configuration
- [ ] Tagged consistently by product area and industry, in the one agreed system
- [ ] Searched for existing reports on the same need first; linked rather than duplicated
- [ ] No customer data, confidential details or proprietary logic included
- [ ] Owner on the product side identified; follow-up date set
- [ ] When it ships: customers migrated, workaround deleted, filer and customers told
