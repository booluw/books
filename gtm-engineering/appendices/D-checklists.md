# Appendix D. Checklists

## D.1 New play launch
- [ ] Play brief complete (hypothesis, audience, trigger, angle, offer, metrics, kill criteria)
- [ ] TAM filters and tiers applied; exclusions (customers, open opps, recently contacted, competitors) verified with test records
- [ ] Global suppression checked in code; a canary suppressed address is blocked
- [ ] Country rules applied; LIA referenced; opt-out present
- [ ] Enrichment waterfall run on a sample; accuracy spot-checked; emails verified; catch-all policy applied
- [ ] AI outputs validated; 20–50 samples reviewed by a human; Tier 1 fully reviewed; seller read-through
- [ ] Sending domains authenticated (SPF ≤ 10 lookups, DKIM, DMARC); warmed; caps set
- [ ] Sequence stop conditions and reply routing configured
- [ ] Dashboard and play tags ready; cost estimate recorded
- [ ] Pilot volume set; review date scheduled

## D.2 Inbound routing go-live
- [ ] Rules of engagement approved by sales leadership
- [ ] Matching tested: domain, extra domains, hierarchy, free email, duplicates
- [ ] Customer-first and open-opportunity rules tested
- [ ] Inactive-user, out-of-office and cap handling tested
- [ ] Fallback queue and alerts working
- [ ] Booking flow tested for qualified and unqualified paths; enrichment-timeout fallback tested
- [ ] SLA dashboard live; on-call or owner named

## D.3 Deliverability health (weekly)
- [ ] Postmaster spam rate < 0.1% on every domain
- [ ] Bounce rate < 2%
- [ ] No blocklist listings
- [ ] DMARC reports reviewed (no unknown senders)
- [ ] SPF lookup count checked after any tool change
- [ ] Per-inbox volumes within caps; warmup running where needed
- [ ] Primary domain not used for cold outreach (enforced in code)

## D.4 Data quality (monthly)
- [ ] Completeness, validity, duplicates, freshness reported
- [ ] Owner hygiene (no records owned by inactive users)
- [ ] Re-enrichment schedule run by tier
- [ ] Job changes processed (champion plays and re-threading)

## D.5 Tool evaluation
- [ ] Problem and target metric defined
- [ ] Bake-off on own ICP sample
- [ ] Integration: upsert support, API-limit impact, field control
- [ ] Controls: caps, approvals, suppression, audit logs
- [ ] Security: SOC 2, DPA, scopes requested, data residency
- [ ] Total cost modelled; pilot with holdout; exit plan

## D.6 Security review (quarterly)
- [ ] Connected apps and OAuth grants inventoried; unused ones removed
- [ ] Integration users least-privilege; MFA and SSO on human accounts
- [ ] No secrets stored in CRM records (scan)
- [ ] API keys in a secrets manager; rotation dates tracked
- [ ] Offboarded users removed from all GTM tools
- [ ] Incident runbook for token compromise tested

## D.7 AI step in production
- [ ] Evaluation set (50–200 labelled rows) and metrics
- [ ] Structured output validated by code; fallbacks defined
- [ ] Cost per 1,000 rows known; caps set
- [ ] Prompt and model versions logged
- [ ] Research agents have no send or write tools; approvals for actions
- [ ] Data sent to model provider covered by terms and DPA
