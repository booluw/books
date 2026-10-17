# Chapter 20. Case Studies

> "Every engagement teaches something. The good ones teach it to the product."

## What you will learn

This chapter applies the whole book to six composite engagements. Each follows the lifecycle in Chapter 4 and highlights different lessons. The companies are **fictional** (named after Microsoft's sample companies), and each case combines patterns reported publicly and commonly described by practitioners. Numbers are illustrative but internally consistent. Each case ends with questions to discuss before reading the commentary.

| Case | Setting | Main lessons |
|---|---|---|
| 20.1 Northwind Insurance | Claims coverage assistant | Discovery, decomposition, non-AI wins, impact measurement |
| 20.2 Woodgrove Bank | Agentic operations in a regulated bank | Security review, guardrails, model risk, autonomy earned gradually |
| 20.3 Contoso Logistics | Pilot purgatory | Scoping, production decisions, sponsor change |
| 20.4 Fabrikam Health | Air-gapped hospital deployment | Restricted environments, data quality, clinicians' trust |
| 20.5 Tailspin Toys | The agency trap | Custom forks, rule of three, productisation |
| 20.6 Wide World Importers | Handover done right | Handover planning, support model, leaving well |

---

## 20.1 Northwind Insurance: the claims coverage assistant

### Situation

Northwind Insurance, a mid-sized UK home insurer, bought an AI platform after a successful bootcamp. The COO's stated goal: "use AI to speed up claims". Median claim cycle time was 9 days; the target was 5.

### What happened

**Discovery (weeks 1–2).** Two FDEs and a deployment strategist interviewed the COO, three claims managers, twelve adjusters and the policy-system team, and shadowed six adjusters for half a day each. Findings (Chapter 5):

- Triage took about 0.5 days; coverage clarification 3 days; assessment 2 days; approval queues 3.5 days.
- Adjusters emailed underwriting when policy wording or endorsements were unclear, then waited one to three days.
- Payments under £2,000 still needed a manager's approval, although managers approved more than 99% of them unchanged.

**Decomposition and scoping (week 3).** The team proposed three slices: a coverage summary with citations (AI), auto-approval below £2,000 with audit and sampling review (rules), and a queue dashboard (reporting). The success plan (Chapter 6) set criteria at three levels: cycle time for the pilot team, adoption (≥ 70% of eligible claims), and quality (≥ 90% correct on a 200-claim evaluation set, 100% with citations).

**Build and prove (weeks 4–10).** The FDEs built permission-aware retrieval over policy wordings and endorsements (Chapter 12), an evaluation set labelled by two senior adjusters with a rubric (Chapter 13), and a panel embedded in the claims system rather than a separate chatbot (Chapter 7). Auto-approval required no AI at all; it took two weeks, most of it waiting for finance and audit sign-off.

**Results (week 12).** Using difference-in-differences against a comparison team (Chapter 13 §13.8), the pilot team's median cycle time fell by 2.0 days attributable to the deployment, of which roughly half came from auto-approval. Adoption reached 72% of eligible claims. Quality was 91% on the evaluation set. Time saved on coverage questions was valued, with Northwind's finance team, at roughly £373,000 per year if rolled out to all 60 adjusters (60 × 3 hours/week × 46 weeks × £45/hour).

### Discussion questions

1. Why did the team propose a rules-based slice in an "AI" engagement, and how might the sponsor have reacted?
2. What would have happened if the team had built a standalone chatbot instead of a panel in the claims system?
3. Was a 91% quality score good enough? What else would you need to know?

### Commentary

Half of the measured improvement came from a rules change that discovery uncovered. **Good FDEs solve the problem, not the technology brief** (Chapter 5). The sponsor initially wanted "an AI story"; the strategist reframed the brief around cycle time, which was what the COO was measured on. A 91% score was acceptable because the design kept adjusters in the loop with citations to check, and because errors on coverage were caught before payment decisions. The same score in an automated payment decision would not have been acceptable.

---

## 20.2 Woodgrove Bank: agentic operations under model risk management

### Situation

Woodgrove Bank wanted an AI agent to resolve routine payment-operations exceptions: failed transfers, mismatched references, duplicate submissions. Operations staff handled about 4,000 exceptions per week.

### What happened

**Security and risk first.** The FDE started the security review in week 1 (Chapter 14). The bank's model risk management team, applying its existing model-governance policy, classified the agent as a model needing validation. Their questions: what can it do, what data does it see, how is it tested, who is accountable, how is it monitored?

**Designing for limited harm.** The FDE designed tools at business level (`get_payment(id)`, `propose_repair(id, change)`, `request_customer_contact(id)`), never `run_sql` (Chapter 12 §12.5). Every write action was a *proposal* approved by an operator; irreversible actions (returning funds) also required a second approver. The agent acted with the operator's own permissions. Budgets capped tool calls per exception, and every call went into a tamper-evident audit log ([`examples/agent-guardrails/`](../examples/agent-guardrails/) shows the pattern). Exceptions arrived with free-text fields from external banks, so the design assumed prompt injection would sometimes succeed. The agent had no way to send data outside the bank, which removed one leg of the lethal trifecta (Chapter 14 §14.4).

**Earning autonomy.** For six weeks the agent ran in shadow mode (Chapter 15 §15.3): its proposals were logged but not shown. The team compared them with what operators actually did. Then proposals were shown to operators for approval. After three months, operators accepted 96% of proposals for one category (duplicate submissions) unchanged, and sampled audit found no errors. The model risk team approved auto-execution for that category only, with daily sampling review.

### Discussion questions

1. Why start in shadow mode rather than with operator approval from day one?
2. What evidence would you present to justify auto-execution for a second category?
3. Which stakeholders were the highest-influence sceptics, and how were they converted?

### Commentary

The model risk and security teams were the highest-influence sceptics (Chapter 7 §7.3). Involving them from week 1, and designing so that a compromised model could do only limited, recoverable, logged harm, turned them into co-designers. Autonomy was earned category by category on evidence (Chapter 12 §12.5), which is slower than the demo suggested but survived audit.

---

## 20.3 Contoso Logistics: escaping pilot purgatory

### Situation

Contoso Logistics ran a ten-week pilot of a delivery-delay prediction tool with a vendor's FDE. The pilot "succeeded": the model predicted late deliveries 24 hours ahead with useful accuracy, and dispatchers liked it. Six months later, nothing had moved to production.

### What went wrong

- **No production decision was agreed** at scoping (Chapter 6 §6.10). Nobody had said who would decide, or from which budget.
- **The pilot ran in a sandbox** with weekly data extracts. Production needed real-time feeds from the transport management system, which IT had never been asked about.
- **The sponsor**, the head of operations innovation, **moved to another company** in month two of the pilot. Nobody else senior had been involved.
- **Impact was never quantified** in money. "Dispatchers like it" didn't compete with other budget requests.

### The recovery

A new FDE lead was assigned. They:

1. Mapped stakeholders again (Chapter 7) and found that the regional operations director was measured on on-time delivery and late-delivery penalties.
2. Quantified impact with Contoso's finance team: penalties on late deliveries for the pilot region, and the share that earlier intervention could plausibly avoid. The range ran from £180,000 to £420,000 per year, with a base case of £290,000.
3. Brought IT in to design production data feeds, with an estimate and a security review timeline.
4. Wrote a new success plan with the director as sponsor, a production decision date, and a phased rollout that doubled as a controlled measurement (Chapter 13).

Production went live four months later.

### Discussion questions

1. Which three actions at scoping time would have prevented purgatory?
2. How should the vendor have responded when the original sponsor left?
3. What does this case suggest about running pilots in sandboxes?

### Commentary

Pilots fail to convert for organisational reasons far more often than technical ones. Agreeing the production decision up front, piloting in production conditions, keeping relationships with several senior people, and quantifying value in money are all cheap at scoping and expensive later.

---

## 20.4 Fabrikam Health: an air-gapped hospital deployment

### Situation

Fabrikam Health, a hospital group, wanted to identify patients at risk of delayed discharge, so that social-care arrangements could start earlier. Clinical data could not leave the hospital network; the analytics environment was disconnected from the internet.

### What happened

- **Restricted environment (Chapter 14 §14.6).** The FDEs bundled container images, dependencies and an open-weight language model (used to extract discharge barriers from clinical notes) with a software bill of materials. Each transfer went through the hospital's approval and scanning process, which took about a week. The team learned to batch changes into planned releases.
- **Data (Chapter 10).** Profiling showed that 18% of admissions had placeholder discharge dates (`1900-01-01`), that ward codes had changed in a 2023 reorganisation, and that the same patients appeared under different identifiers in two systems. Record linkage with clinical review of uncertain matches came before any modelling.
- **Trust.** Clinicians distrusted "risk scores". The FDEs co-designed the output with discharge coordinators: instead of a score, a list of specific barriers extracted from notes ("awaiting care home assessment", "no package of care"), each linked to the source note, so coordinators could verify it in seconds.
- **Ethics and fairness (Chapter 18).** Evaluation by patient group showed lower extraction accuracy for notes written in a particular template used by one specialty. It was fixed before go-live, and the result was reported to the clinical safety officer.

### Discussion questions

1. Why did presenting barriers rather than scores improve adoption?
2. How would you handle a production incident when you can't access the environment remotely?
3. What would you include in the clinical safety case?

### Commentary

The constraints (air gap, data quality, clinical safety) dictated the design more than the model choice did. Explanations that users can check against sources build trust far faster than abstract scores (Chapter 8 §8.8).

---

## 20.5 Tailspin Toys: falling into, and climbing out of, the agency trap

### Situation

A vendor of an AI-powered customer-service platform had five large retail customers, including Tailspin Toys. Each had asked for a returns-handling workflow. Each FDE had built one, in customer-specific code, slightly differently.

### What happened

- **The trap (Chapter 3 §3.6).** Product upgrades broke two of the five implementations. FDEs spent about 30% of their time maintaining custom returns code. Tailspin was two releases behind.
- **The field report (Chapter 16).** One FDE ran the field reports through a feedback tracker ([`examples/feedback-tracker/`](../examples/feedback-tracker/)) and showed that returns handling had appeared at five distinct customers, comfortably past the rule of three.
- **Generalisation.** The FDEs who built the five versions worked with a product team for six weeks. Common core: order lookup, returns eligibility rules, label generation, refund initiation with approval. Variation: eligibility rules and carrier integrations, which became configuration and connectors.
- **Migration.** Each customer moved to the product feature, with contract tests proving equivalent behaviour (Chapter 11 §11.4). Custom code was deleted.

The sixth retail customer deployed returns handling in four days instead of the five to six weeks the first five had taken.

### Discussion questions

1. At which point should the vendor have noticed the pattern?
2. What would you put in configuration, and what in code, for the returns feature?
3. How would you persuade Tailspin's sponsor that migration was worth their effort?

### Commentary

The loop works only when someone deliberately closes it. The tracker made the pattern visible; the FDEs who built the instances made the generalisation good; the deleted custom code made the economics work.

---

## 20.6 Wide World Importers: handover done right

### Situation

Wide World Importers, a distributor, deployed a supplier-invoice extraction and reconciliation system with two FDEs over five months. The system would be run by Wide World's own small platform team.

### What happened

- **Named receiving team in week 1.** Two Wide World engineers joined stand-ups from the start and paired on the pipeline and evaluation suite (Chapter 15 §15.7).
- **Their tools.** Code lived in Wide World's repositories, deployed through their CI, monitored in their observability stack. Nothing needed migrating at the end.
- **Documentation as they went.** ADRs from week 2; runbooks written as each failure mode was first seen.
- **Readiness gate.** The production readiness review used a checklist with evidence ([`examples/readiness-gate/`](../examples/readiness-gate/)): one major item (a disaster-recovery restore test) became a condition with a date, which was met two weeks after launch.
- **Unaided operation.** For three weeks the Wide World team operated alone, including one supplier changing its invoice format, which they handled using the "new invoice layout" runbook and by adding cases to the evaluation set. The FDEs observed without intervening.
- **Leaving well.** An impact report validated by finance (invoice processing time down from 6 minutes to 1.5 minutes per invoice, with sampled accuracy above target), a joint retrospective, field reports on two product gaps, and access revoked.

### Discussion questions

1. Which handover practices would be hardest to replicate on a shorter engagement, and what would you do instead?
2. Why does the unaided operation period matter more than the handover document?
3. What should the FDEs do if Wide World's engineers contact them directly six months later?

### Commentary

Handover is planned from day one, not performed in the last week. The receiving team's ability to handle a real change unaided is the only test that matters.

---

## 20.7 Patterns across the cases

| Pattern | Seen in |
|---|---|
| The highest-value fix wasn't the obvious technology | Northwind (rules), Fabrikam (barriers, not scores) |
| Early engagement with high-influence sceptics speeds everything | Woodgrove (model risk), Fabrikam (clinicians) |
| Autonomy is earned with evidence | Woodgrove |
| Pilots need production decisions, owners and money from the start | Contoso |
| Constraints shape the design more than the model does | Fabrikam, Woodgrove |
| The loop to product must be closed deliberately | Tailspin |
| Handover is designed, not done | Wide World |
| Measurement makes success legible | All six |

---

## Summary

- The cases show the book's ideas working together: discovery and decomposition (Northwind), security and guarded autonomy (Woodgrove), scoping and stakeholders (Contoso), restricted environments and trust (Fabrikam), the field-to-product loop (Tailspin) and handover (Wide World).
- Across them: solve the problem, not the brief; engage sceptics early; earn autonomy; agree production decisions up front; let constraints shape design; close the loop to product; plan handover from day one; measure everything.

## Exercises

See [`exercises/20-case-studies.md`](../exercises/20-case-studies.md).

## Further reading

- Palantir, AIP bootcamp customer stories (palantir.com).
- Anthropic and OpenAI customer stories pages, for public examples of enterprise AI deployments.
- MIT NANDA, *The GenAI Divide: State of AI in Business 2025*.
- Harvard Business School case method resources, on learning from cases.
