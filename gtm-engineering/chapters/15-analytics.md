# Chapter 15. Analytics, Attribution and Experimentation

> "If you can't show which play created the pipeline, you can't defend the budget, or kill the play that isn't working."

## What you will learn

- What to measure, at which level: play, channel, segment, rep, system.
- Funnel analytics done right: cohorts, time windows and definitions.
- Attribution models and their limits; self-reported attribution.
- Experiment design for GTM: A/B tests, holdouts, sample sizes and pitfalls.
- Dashboards and reporting cadence.

---

## 15.1 Levels of measurement

| Level | Example questions | Key metrics |
|---|---|---|
| **Play** | Is "new VP Ops" outbound worth running? | Meetings held per 100 contacts, pipeline per 100, cost per meeting, win rate |
| **Channel / motion** | Is outbound or inbound more efficient this quarter? | Pipeline created, CAC by motion, cycle length |
| **Segment** | Which tiers and industries convert? | Conversion by tier, ACV, win rate |
| **System** | Is routing fast? Is enrichment accurate? | Speed-to-lead, data-quality metrics, credit spend |
| **Business** | Are we on track? | Pipeline coverage, bookings, CAC payback |

GTM engineers own the **system** metrics and should drive **play**-level measurement, because they build the plays.

## 15.2 Funnel analytics done right

1. **Agreed definitions** (Chapter 3): what counts as a meeting held, an SQL or an opportunity. Document them.
2. **Cohorts:** analyse "of contacts enrolled in March, how many became opportunities within 90 days", not "March meetings ÷ March enrolments".
3. **Time windows:** choose and state an attribution window (for example 90 days from first touch to opportunity creation).
4. **Lag:** recent cohorts haven't finished converting. Show them as incomplete.
5. **Stage history:** use stage-change history (Salesforce Opportunity Field History or OpportunityHistory; HubSpot deal stage history) to compute conversion and velocity, not current-state snapshots.
6. **Single source:** compute metrics in one place (warehouse models or one CRM report set). Competing spreadsheets cause arguments.

## 15.3 Attribution

**Attribution** assigns credit for pipeline or revenue to the touches that preceded it.

| Model | Credit to | Pros | Cons |
|---|---|---|---|
| **First touch** | The first recorded interaction | Shows what creates awareness | Ignores everything after |
| **Last touch** (often "last touch before opportunity") | The final interaction before conversion | Simple; shows what converts | Ignores earlier influence |
| **Linear** | All touches equally | Fair-ish | Treats a newsletter open like a demo |
| **U-shaped / W-shaped** | Heavier weight on first, lead-creation and opportunity-creation touches | Reflects key moments | Arbitrary weights |
| **Time decay** | More to recent touches | Recency matters | Arbitrary half-life |
| **Data-driven / algorithmic** | Statistical models | Can capture interactions | Opaque; needs volume; still correlational |
| **Sourced vs influenced** | "Sourced" = the touch that created the opportunity; "influenced" = any touch on the account before close | Practical for B2B | Double counting in "influenced" |

### Why attribution is hard in B2B

- **Buying committees:** touches are spread across many people. Account-level attribution is needed.
- **Dark funnel:** podcasts, communities, word of mouth, AI assistants and private messages leave no trackable touch.
- **Tracking limits:** cookie restrictions, ad blockers and privacy rules reduce visibility.
- **Long cycles:** months between first touch and revenue.

### Self-reported attribution

Add a required free-text field to demo forms: **"How did you hear about us?"** Classify answers (an LLM does this well) and compare with software attribution. It often reveals large dark-funnel sources (a podcast, a LinkedIn creator, a community) that software attribution misses.

### Practical approach

Use **sourced pipeline by motion and play** for planning, **influenced** views for marketing programmes, **self-reported** data to catch the dark funnel, and **experiments** (§15.4) for causal questions. Never treat any attribution model as the truth.

## 15.4 Experimentation

Attribution shows correlation. **Experiments** show causation.

### A/B tests in outbound

Example: does a signal-based opener beat a segment opener?

1. **Hypothesis:** signal-based openers increase positive reply rate.
2. **Randomise** at the **account** level (so colleagues at one account don't get both variants), stratified by tier.
3. **Primary metric:** positive replies per delivered email, or better, meetings held per contact.
4. **Sample size:** small effects need large samples. To detect a lift from 2% to 3% positive reply rate (two-sided, α = 0.05, power 80%) you need roughly **3,800 contacts per arm**. Most single plays cannot detect small differences quickly, so test **big** differences (angle, offer, audience), not commas.
5. **Fix the duration** in advance; don't stop the moment it "looks significant" (peeking inflates false positives).
6. **Hold everything else constant:** same sending infrastructure, timing and list source.

### Holdout tests

To measure whether a whole programme works (an intent subscription, signal alerts, an AI SDR), keep a random **holdout** of eligible accounts that do *not* receive the treatment, and compare pipeline after 60–120 days. This is the cleanest answer to "is this tool worth its price?"

### Pitfalls

- **Novelty effects** fade.
- **Deliverability confounds:** a variant sent from a weaker domain loses for reasons unrelated to copy.
- **Multiple comparisons:** testing 20 subject lines guarantees a "winner" by chance.
- **Optimising the wrong metric:** opens (inflated by Apple Mail Privacy Protection) or replies (including negative ones) instead of meetings and pipeline.

The [`examples/funnel-metrics/`](../examples/funnel-metrics/) module includes a sample-size calculator and a two-proportion test.

## 15.5 Dashboards and cadence

A useful GTM engineering dashboard set:

1. **Play scorecard:** per play: contacts, delivered, bounce %, positive reply %, meetings held, opportunities, pipeline, cost per meeting, trend.
2. **Inbound health:** volume, speed-to-lead p50/p95, % routed correctly, orphaned leads.
3. **Deliverability:** per domain and inbox: volume, bounce, spam rate (Postmaster), reply rate.
4. **Data quality:** completeness, duplicates, freshness (Chapter 5).
5. **Spend:** credits and tool costs by play and in total; cost per meeting.

Cadence: **weekly** operating review (plays, deliverability, incidents); **monthly** play portfolio review (scale, fix or kill); **quarterly** ICP, scoring and signal recalibration.

---

## Summary

- Measure at play, channel, segment, system and business levels. GTM engineers own system metrics and drive play metrics.
- Use agreed definitions, cohorts, stated windows and stage history; compute metrics in one place.
- Attribution models are lenses, not truth. Combine sourced and influenced views, self-reported attribution and experiments.
- Run account-level randomised tests on big differences with adequate samples and fixed durations; use holdouts to judge whole programmes and tools.
- Maintain play, inbound, deliverability, data-quality and spend dashboards with a weekly, monthly and quarterly review rhythm.

## Exercises

See [`exercises/15-analytics.md`](../exercises/15-analytics.md).

## Further reading

- Ron Kohavi, Diane Tang and Ya Xu, *Trustworthy Online Controlled Experiments* (Cambridge University Press, 2020).
- Chris Walker and Refine Labs' writing on self-reported attribution and the dark funnel.
- Evan Miller's sample-size calculator and articles on A/B testing pitfalls (evanmiller.org).
