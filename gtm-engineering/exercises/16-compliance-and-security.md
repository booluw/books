# Exercises: Chapter 16, Compliance and Security

## Questions

1. For a campaign to operations directors in the US, UK, Germany and Canada, list the main legal questions per country.
2. Design a global suppression system across HubSpot, Outreach, a cold-email tool and Clay.
3. Complete the LIA template for one of your plays (with counsel, in a real setting).
4. What should a GTM team change after reading about the 2025 Salesloft Drift breach?
5. Is it acceptable to scrape LinkedIn profiles into your CRM with a browser extension? Explain the risks.

## Solutions

1. US: CAN-SPAM requirements (identity, honest subject, address, opt-out in 10 business days); state privacy laws. UK: PECR corporate-subscriber rule (sole traders need consent); UK GDPR LI + transparency. Germany: national rules may require prior consent even for B2B email; GDPR. Canada: CASL consent (express or a narrow implied exception); often excluded.
2. One canonical suppression store (database or CRM object) fed by unsubscribes, replies and complaints from all tools; checked in code before every enrolment and send; synced to each tool's suppression list on a schedule and on event; audit log; tests with a canary address.
3. Personal exercise.
4. Inventory and minimise connected apps and OAuth scopes; remove unused integrations; restrict connected-app access; scan for and remove secrets in CRM records; monitor integration-user API activity; prepare a token-revocation and credential-rotation runbook.
5. It conflicts with LinkedIn's User Agreement (accounts can be restricted; LinkedIn litigates against scrapers, such as ProAPIs in 2025), raises GDPR transparency and lawful-basis questions, and creates data-provenance problems. Prefer official tools and compliant data sources.
