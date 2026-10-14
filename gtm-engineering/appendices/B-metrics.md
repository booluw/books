# Appendix B. Metrics and Formulas Reference

Implementations are in [`examples/funnel-metrics/funnel.py`](../examples/funnel-metrics/funnel.py).

## Funnel

| Metric | Formula | Notes |
|---|---|---|
| Stage conversion | entered stage n+1 ÷ entered stage n | By cohort, with a stated window |
| Win rate | won ÷ (won + lost) | By count or value; closed deals only |
| Reply rate | replies ÷ delivered | |
| Positive reply rate | interested replies ÷ delivered | Better than raw reply rate |
| Meeting held rate | held ÷ booked | No-shows matter |
| Speed to lead | first meaningful response time − submission time | Report p50 and p95; business hours |

## Pipeline

| Metric | Formula |
|---|---|
| Pipeline created | Σ amount of opportunities created in period |
| Pipeline coverage | open pipeline for period ÷ target for period (rule of thumb 3–4×) |
| Pipeline velocity ($/day) | (# opportunities × average deal size × win rate) ÷ average cycle days |
| Sales cycle | close date − opportunity created date (won deals) |

## Unit economics

| Metric | Formula |
|---|---|
| CAC | sales and marketing cost in period ÷ new customers in period |
| CAC payback (months) | CAC ÷ (new MRR per customer × gross margin) |
| LTV | (ARPA per month × gross margin) ÷ monthly churn rate |
| LTV : CAC | LTV ÷ CAC (classic benchmark ≈ 3:1) |
| NRR | (starting ARR + expansion − contraction − churn) ÷ starting ARR |
| GRR | (starting ARR − contraction − churn) ÷ starting ARR |
| SaaS magic number | net new ARR in quarter ÷ S&M spend in previous quarter |
| Cost per meeting | total play cost (data + AI + infrastructure + seats + people) ÷ meetings held |

## Data quality

| Metric | Formula |
|---|---|
| Completeness | records with field populated ÷ records |
| Validity | records passing validation ÷ populated records |
| Duplicate rate | records in duplicate clusters ÷ records |
| Freshness | records enriched within N months ÷ records |
| Enrichment hit rate | results returned ÷ lookups |
| Cost per correct result | cost per lookup ÷ (coverage × accuracy) |

## Signals

| Metric | Formula |
|---|---|
| Decayed signal score | weight × 0.5^(age_days ÷ half_life_days) |
| Signal lift | conversion rate with signal ÷ baseline conversion rate (same tier) |

## Deliverability

| Metric | Threshold (guidance, Chapter 11) |
|---|---|
| Spam complaint rate (Postmaster) | < 0.1% target; never ≥ 0.3% |
| Bounce rate | < 2% |
| Cold sends per inbox per day | ~30–50 (rule of thumb) |

## Experiments

| Item | Formula |
|---|---|
| Sample size per arm (two proportions) | n = [z₁₋α/₂ √(2p̄(1−p̄)) + z₁₋β √(p₁(1−p₁)+p₂(1−p₂))]² ÷ (p₂−p₁)² |
| Two-proportion z | (p_B − p_A) ÷ √(p̂(1−p̂)(1/n_A + 1/n_B)), with pooled p̂ |
| Lift | (rate_B − rate_A) ÷ rate_A |
