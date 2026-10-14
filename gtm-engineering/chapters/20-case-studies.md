# Chapter 20. Case Studies

> These case studies are **composites** built from common industry patterns, not accounts of specific companies. Company names are fictional (several are borrowed from Microsoft's well-known sample companies). Numbers are illustrative.

1. [Seed-stage: founder-led outbound to first pipeline](#case-study-1-seed-stage-founder-led-outbound)
2. [Series B: fixing inbound speed-to-lead and routing](#case-study-2-series-b-inbound-speed-to-lead)
3. [PLG company: product-qualified accounts and sales-assist](#case-study-3-plg-product-qualified-accounts)
4. [Deliverability crisis and recovery](#case-study-4-deliverability-crisis-and-recovery)
5. [Evaluating an AI SDR with a holdout](#case-study-5-evaluating-an-ai-sdr)

---

## Case study 1: Seed-stage founder-led outbound

**Context.** *Tailspin Freight Analytics* (12 people) sells route-optimisation software to mid-sized 3PLs. The two founders sell. They hired a fractional GTM engineer to build repeatable outbound before hiring SDRs.

**Discovery.** 9 closed-won and 14 closed-lost deals. All wins were 3PLs with 150–1,500 employees whose operations leader had joined within the previous year, and most used one of three legacy transport management systems (TMS).

**Build.**

- TAM: 6,200 North American 3PLs from a data provider plus an industry directory, deduplicated by domain to 4,900. A Clay AI research column answered "Do they run their own fleet? YES/NO/UNKNOWN + evidence URL" (evaluated at 91% accuracy on 100 hand-labelled rows). Fit tiers: 640 Tier 1, 1,450 Tier 2.
- Signals: new VP/Director of Operations in the last 120 days; job posts mentioning the legacy TMS names.
- Waterfall: two email providers plus verification; catch-all domains excluded for the first month.
- Infrastructure: 4 secondary domains × 2 inboxes, warmed for 3 weeks; 35 sends per inbox per day.
- Messaging: founder-written templates with one AI-generated relevance line grounded in the job post or company site; 10% human QA; Tier 1 fully reviewed by a founder.

**Results (first 12 weeks).** 2,300 contacts; bounce rate 1.1%; positive reply rate 2.6%; 41 meetings held; 14 opportunities; $610k pipeline; about $70 per meeting in tool and data costs.

**Lessons.** The ICP insight (new ops leaders plus legacy TMS) mattered more than any tool. A custom AI attribute differentiated targeting. Small volume and high relevance kept the domains healthy.

## Case study 2: Series B inbound speed-to-lead

**Context.** *Fabrikam Security* (180 people) receives about 900 demo requests a month. Median first response time was 3 hours 40 minutes, and 18% of demo requests were never contacted.

**Diagnosis.**

- Leads landed in a shared queue; SDRs cherry-picked.
- 23% of requests came from existing customers' employees and went to new-business SDRs.
- Assignment rules skipped leads with missing employee counts, which caused orphans.
- Some leads went to deactivated reps.

**Build.**

- Two-field form (work email + "What prompted you to reach out?") with real-time enrichment and a fallback to the full form on timeout.
- Matching by domain and corporate hierarchy; customer-first and open-opportunity rules.
- Territory plus weighted round robin with out-of-office awareness and a durable pointer; fallback queue with manager alerts.
- Instant booking for qualified buyers on the thank-you page.
- SLA dashboard (p50/p95 speed-to-lead; orphan and inactive-owner alerts).
- Self-reported attribution field classified by an LLM.

**Results (one quarter).** Median time to booked meeting fell to 2 minutes for qualified requests; uncontacted requests fell from 18% to under 2%; demo-to-opportunity conversion rose from 31% to 39%. Self-reported attribution showed a podcast sponsorship driving 11% of demo requests, almost invisible to software attribution.

**Lessons.** Fixing inbound beat any new outbound play. Write rules of engagement first, then code them.

## Case study 3: PLG product-qualified accounts

**Context.** *Northwind Docs*, a collaborative documentation tool with 40,000 free workspaces, wanted to sell enterprise plans.

**Build.**

- Warehouse (BigQuery) with product events, billing and CRM data; dbt models mapping users to companies by domain (excluding free-email domains) and enrichment.
- PQA model: fit tier + active users (14-day) + workspaces per domain + SSO or admin-settings page views + integrations connected. Thresholds came from 18 months of conversion history.
- Reverse ETL (Hightouch) writing PQA score, reasons and workspace list to Salesforce account fields; a task for the owner when an account crosses the threshold.
- Plays: sales-assist outreach from the AE referencing *what the team is doing* (never surveillance-style detail); consolidation offers for companies with 3+ workspaces.

**Results.** 6% of high-fit companies qualified as PQAs each month. PQAs converted to enterprise opportunities at 5× the rate of other high-fit companies, and consolidation deals averaged 2.4× the ACV of single-team upgrades.

**Lessons.** User-to-account mapping is the hardest and most valuable step. Keep scores explainable so AEs trust them.

## Case study 4: Deliverability crisis and recovery

**Context.** *Contoso HR Cloud* scaled cold email from 400 to 3,000 sends a day in a month by buying a large list and adding inboxes.

**What happened.** Bounce rate hit 7%. Google Postmaster Tools showed domain reputation "Bad" on three of five secondary domains and a 0.5% spam rate. Reply rates fell to near zero. A misconfigured tool had also been sending some cold sequences from the **primary** domain, and invoices from finance began landing in spam.

**Recovery.**

1. Stopped all cold sending immediately.
2. Moved the primary domain off cold sending; audited every tool's sending domain; confirmed SPF, DKIM and DMARC for the primary domain; tightened DMARC monitoring.
3. Re-verified the list; removed catch-alls and role addresses; suppressed non-engagers.
4. Retired the two worst domains; rested the others for 3 weeks; restarted with warmup and only Tier 1–2, signal-qualified contacts at 25 per inbox per day.
5. Added alerts: bounce > 2%, spam rate > 0.1%, sending-domain allow-list enforced in code.

**Results.** Primary-domain transactional mail recovered within weeks. Cold reply rates returned to 2%+ at a quarter of the previous volume, with more meetings than before the crisis.

**Lessons.** Volume without relevance is self-destructive. Protect the primary domain with technical controls, not policy alone.

## Case study 5: Evaluating an AI SDR

**Context.** *Wide World Importers Software* considered an AI SDR at roughly the cost of one human SDR.

**Pilot design.** 1,200 Tier 2 accounts randomised (stratified by industry and size) into: (A) AI SDR, (B) the existing human SDR process, and (C) a holdout with no outbound, for 8 weeks. Approval required for the first 2 weeks, then 20% sampling. Global suppression enforced by the company's own code before every send.

**Findings.**

- Meetings held per 100 accounts: A 2.1, B 3.4, C 0.6 (inbound only).
- Quality audit: 4% of AI messages contained factual errors (wrong funding stage, wrong product names); 1% had tone problems.
- Spam complaints were higher for A, so the AI SDR's sending was moved to separate domains.
- Cost per meeting: A slightly lower than B, but the pipeline per meeting was 35% lower.

**Decision.** Hybrid: AI research and first drafts for SDRs; humans send and own conversations. SDR capacity rose about 40% without the error rate.

**Lessons.** Measure against a holdout and the existing process, on pipeline, not activity. Keep compliance controls in your own code.

---

## Cross-cutting lessons

1. **ICP insight and relevance** beat tools and volume.
2. **Inbound and routing fixes** are often the highest-ROI work.
3. **Data mapping** (users to accounts, leads to accounts) unlocks PLG and routing.
4. **Deliverability and compliance** must be enforced technically.
5. **AI works best supervised,** and should be evaluated against holdouts.

## Exercises

See [`exercises/20-case-studies.md`](../exercises/20-case-studies.md).
