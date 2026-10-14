# Exercises: Chapter 8, Signals

## Questions

1. Classify as first-, second- or third-party: G2 category research, pricing-page visit, funding round, Slack community question, product seat added, Bombora topic surge, champion job change (from your CRM contacts).
2. Compute a decayed score today for: new exec hire 30 days ago (weight 30, half-life 60), pricing visit 3 days ago (weight 25, half-life 7), funding 45 days ago (weight 20, half-life 90).
3. Why might buying topic intent from two vendors not give two independent signals?
4. Design a holdout test to decide whether to renew a $60k/year intent subscription.
5. Rewrite this opener to avoid "surveillance": "I saw you were on our pricing page 3 times this week."

## Solutions

1. Second-party; first-party; third-party; second-party (community); first-party; third-party; first-party data (job-change tracking may use a third-party provider).
2. 30 × 0.5^(30/60) ≈ 21.2; 25 × 0.5^(3/7) ≈ 18.6; 20 × 0.5^(45/90) ≈ 14.1; total ≈ 53.9.
3. Many vendors resell the same Bombora co-op data, so both reflect the same underlying observations.
4. Randomly hold out, say, 30% of intent-flagged accounts (no special action) for 90 days; compare meeting, opportunity and pipeline rates against actioned accounts and a non-flagged baseline; renew only if the lift justifies the cost.
5. Use the visit only for timing, and lead with relevance: "Teams evaluating route-planning tools usually compare X and Y. Happy to share how similar 3PLs decided."
