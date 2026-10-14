# Exercises: Chapter 2, History

## Questions

1. Match each modern practice to its historical precursor: (a) signal-based outbound; (b) PQLs; (c) Clay waterfalls; (d) AI SDRs; (e) RevOps.
2. Why did Google's and Yahoo's 2024 bulk-sender rules change outbound strategy?
3. What did the 2025 Salesloft Drift breach reveal about GTM stacks?
4. Name two consolidation events in the GTM tooling market in 2023–2025 and one implication for a stack owner.

## Solutions

1. (a) Trigger-based selling and intent data (Bombora, 2010s); (b) MQL lead scoring; (c) multiple data vendors plus manual research and list brokers; (d) outsourced SDR and telemarketing teams and sales engagement automation; (e) separate sales, marketing and CS ops functions.
2. Authentication, one-click unsubscribe and spam-rate thresholds (below 0.3%) made high-volume, low-relevance sending far riskier, pushing teams to relevance, infrastructure discipline and list hygiene.
3. Integrations hold powerful OAuth tokens to the CRM. A compromised third-party integration exposed data at hundreds of organisations, and attackers harvested secrets stored in CRM records.
4. HubSpot acquired Clearbit (December 2023, now Breeze Intelligence, HubSpot-only); Clari and Salesloft merged (closed December 2025). Implication: vendor changes can remove capabilities (Clearbit outside HubSpot) or force migrations, so keep logic portable and data exportable.
