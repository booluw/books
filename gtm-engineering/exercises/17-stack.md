# Exercises: Chapter 17, Stack

## Questions

1. Propose a stack for a 25-person seed-stage company selling to HR leaders, with a $3,000/month tool budget.
2. Write evaluation criteria for choosing between two intent providers.
3. Compute cost per meeting: 3,000 contacts at $0.15 data, $0.02 AI, $300 infrastructure, $400 seats, 10 hours QA at $50; 24 meetings held.
4. What should you build rather than buy, and why?
5. List three vendor risks and a mitigation for each.

## Solutions

1. Example: HubSpot Starter or Attio; Clay (starter plan); Apollo or Instantly with secondary domains; a verifier; Google Workspace inboxes; Calendly or HubSpot meetings; n8n or Zapier; a DMARC monitor. Skip intent platforms until they're proven.
2. Data source (independent or the same co-op?), coverage of your ICP, measured lift via a holdout pilot, integration, refresh frequency, price, terms.
3. 450 + 60 + 300 + 400 + 500 = $1,710; ÷ 24 ≈ $71.25 per meeting.
4. Logic that differentiates you (ICP model, custom signals, scoring, routing rules), kept in version control and portable across tools.
5. Acquisition or sunset (keep logic portable, export data); breach (minimise scopes, monitor, rotate); price changes (track usage, avoid lock-in, have alternatives).
