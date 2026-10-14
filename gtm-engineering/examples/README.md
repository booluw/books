# Examples

Runnable companions to the chapters. Everything uses **only the Python standard library** (Python 3.11+, tested with 3.13). There is nothing to install, and no API keys are needed: data providers, DNS and LLM outputs are simulated with in-memory fakes, which you swap for real clients.

| Folder | Chapter | What it shows |
|---|---|---|
| [`icp-scoring/`](icp-scoring/) | 4 | Explainable, versioned rules-based fit scoring and tiering, with disqualifiers |
| [`enrichment-waterfall/`](enrichment-waterfall/) | 7 | A cost-aware email waterfall: verification after each provider, caching, "retry later" vs "not found", domain checks, provenance, budget cap |
| [`dedupe-and-matching/`](dedupe-and-matching/) | 5 | Domain normalisation (public suffixes, free-email domains), company-name normalisation, fuzzy matching, lead-to-account matching with tie-breaks and review flags, hierarchy, duplicate detection |
| [`lead-routing/`](lead-routing/) | 9 | Rules of engagement in code: disqualify, customer-first, opportunity owner, account owner, weighted availability-aware round robin with a durable pointer, fallback queue, audit reasons |
| [`email-auth-checker/`](email-auth-checker/) | 11 | SPF (record count, recursive 10-lookup limit, `all` mechanism, loops) and DMARC (policy, reporting, pct) checks |
| [`safe-personalization/`](safe-personalization/) | 10, 13 | Guardrails for AI-written lines: JSON validation, evidence URLs, unsupported numbers, banned phrases, placeholders, fallback copy, deterministic QA sampling |
| [`signal-pipeline/`](signal-pipeline/) | 8 | Signal de-duplication, exponential decay scoring, thresholds, cool-downs, hand-raiser bypass, suppression |
| [`funnel-metrics/`](funnel-metrics/) | 3, 15, App. B | Reverse funnel, CAC, payback, LTV, NRR, velocity, coverage, cost per meeting, sample size and two-proportion test |

## Run every test

```bash
cd gtm-engineering/examples
python3 run_all_tests.py
```

Each folder also runs on its own: `python3 -m unittest -v`, and most have a demo: `python3 <module>.py`.

## A note on production use

These examples teach logic. Production systems also need persistent storage, secrets management, rate limiting, logging, monitoring and the compliance controls from Chapter 16.
