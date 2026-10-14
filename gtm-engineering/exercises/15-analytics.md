# Exercises: Chapter 15, Analytics

## Questions

1. Compare first-touch, last-touch and W-shaped attribution for a deal touched by: webinar → outbound email reply → demo request → opportunity.
2. How many contacts per arm are needed to detect a positive-reply lift from 1.5% to 3% (α 0.05, power 80%)? Use `examples/funnel-metrics`.
3. Variant A: 40 meetings from 2,000 contacts; B: 58 from 2,000. Is B significantly better? Use the two-proportion test.
4. Design a play scorecard dashboard.
5. Why randomise at the account level?

## Solutions

1. First-touch: webinar. Last-touch (before opportunity): demo request. W-shaped: heavy credit to the first touch (webinar), the lead-creation touch (email reply or demo, depending on definition) and the opportunity-creation touch (demo), with the remainder spread.
2. `sample_size_per_arm(0.015, 0.03)` gives about 1,534 per arm.
3. `two_proportion_test(40, 2000, 58, 2000)`: z ≈ 1.84, p ≈ 0.066, not significant at 0.05. Keep running to the planned sample, or treat as inconclusive.
4. Per play: contacts, delivered, bounce %, positive reply %, meetings held, opportunities, pipeline, cost per meeting, trend, status vs kill criteria.
5. Colleagues at one account talk to each other and share inboxes and context; mixing variants within an account contaminates results.
