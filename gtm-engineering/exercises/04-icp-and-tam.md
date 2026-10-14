# Exercises: Chapter 4, ICP and TAM

## Questions

1. Using won/lost data, how would you test whether "uses a legacy TMS" belongs in the ICP?
2. Propose two custom AI-researched attributes for a company selling cybersecurity training to hospitals, and how you'd validate them.
3. Your TAM is 120,000 accounts and you have 6 AEs who can each actively work 150 accounts. What does that imply?
4. Run `examples/icp-scoring` on the sample CSV. Change the employee core band to 300–3,000. Which accounts change tier?
5. What's wrong with an ICP score that includes "has our integration installed"?

## Solutions

1. Compare win rate, ACV, cycle and retention for accounts with and without the attribute (with sample sizes), ideally controlling for size and industry; validate with sellers.
2. Examples: "Has the hospital had a reported data breach or ransomware incident in the last 3 years?" (from public breach lists, news); "Does the hospital publish a security-awareness or compliance officer role?" (careers page). Validate on 100 hand-labelled hospitals; require evidence URLs; measure accuracy and UNKNOWN rate.
3. Only ~900 accounts can be actively worked; tiering and signals must decide which 900, and the rest need automated, low-touch or marketing plays.
4. Change the core band to `300 <= employees <= 3000` and the adjacent band to `100–299 or 3,001–5,000`. In the sample, Acme (640) stays core (Tier 1, 100 points) and Northpeak (150) stays adjacent (Tier 2, 55 points); TinyHaul's count is unknown and RivalRoute is excluded, so **no tiers change**. The real lesson: the sample has no accounts near the new boundaries (e.g. 250 or 2,500 employees). Add boundary cases to your test data before changing thresholds, and check how many TAM accounts move tier.
5. Leakage: the attribute exists because the account already became a customer, so it inflates the model's apparent accuracy and is useless for prospects.
