# Exercises: Chapter 9, Scoring and Routing

## Questions

1. What do the HBR (2011) and InsideSales lead-response studies each claim? Why does it matter which is which?
2. Write the rules of engagement for a company with SMB, mid-market and enterprise teams in NA and EMEA, plus an AM team.
3. Add "fairness by value" to `examples/lead-routing`: balance Tier 1 leads evenly across reps in a pool. Write tests.
4. List five routing failure modes and a monitor for each.
5. A lead fills the demo form at 9:58 pm local time on Friday. What should happen?

## Solutions

1. HBR: firms contacting web leads within an hour were nearly 7× as likely to qualify them as those waiting longer, and over 60× as likely as those waiting 24+ hours; only 37% of audited companies responded within an hour. InsideSales: odds of contact are about 100× higher within 5 minutes than at 30 minutes. Citing correctly protects credibility; both point to speed.
2. Example: customers → AM; open opportunity → opportunity owner; named enterprise accounts → named owner; otherwise region × segment pools (employee bands) with weighted round robin; unknown size → mid-market pool; ownership expiry 90 days; disputes to regional sales directors.
3. Hands-on: keep per-rep counts per tier; choose the eligible rep with the fewest Tier 1 leads today, breaking ties by the round-robin pointer.
4. Inactive owner (daily owner-status check); orphans (unassigned > 5 min alert); duplicate routing systems (assignment-change audit); rule gaps (fallback-queue volume alert); speed SLA breaches (p95 latency dashboard).
5. Route and assign immediately; offer booking for the next business day on the thank-you page; send an instant acknowledgement; the SLA timer runs in business hours; if follow-the-sun coverage exists, route to the on-duty region.
