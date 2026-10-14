# Exercises: Chapter 7, Enrichment

## Questions

1. Provider A: 55% coverage, 92% accuracy, $0.04. Provider B: 70% coverage, 85% accuracy, $0.10. Compute cost per correct email for each. Which goes first?
2. Why must a 429 from a provider not be recorded as "not found"?
3. Design a refresh policy for a 50,000-contact database with tiers 1–3.
4. Extend `examples/enrichment-waterfall` with a phone-number step that only runs for Tier 1 contacts with a valid email. Write tests.
5. What is a catch-all domain, and what are three ways to handle one?

## Solutions

1. A: 0.04 ÷ (0.55 × 0.92) ≈ $0.079. B: 0.10 ÷ (0.70 × 0.85) ≈ $0.168. A first (cheaper per correct result); B catches A's misses.
2. A rate limit or outage says nothing about whether the email exists. Recording "not found" (and caching it) permanently hides findable data. Retry later instead.
3. Example: Tier 1 re-verify emails monthly and re-enrich quarterly; Tier 2 every 6 months; Tier 3 only when entering a play. Event-based refresh on bounce or job change; always re-verify before sequence enrolment if older than 30–60 days.
4. Hands-on: add a run condition (`tier == 1 and status == found`), a separate budget line, and tests for skip, success and budget behaviour.
5. A domain whose mail server accepts any address, so mailbox existence can't be verified. Options: exclude; send at low volume with monitoring; use catch-all verification services carefully; reach the person through another channel.
