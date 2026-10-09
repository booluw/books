# Exercises: Chapter 19, Career

## Questions

1. Write your 12-month plan using §19.2, with dates and the portfolio project for each stage.
2. Rewrite these résumé bullets to show outcomes: "Worked on MuleSoft integrations." "Responsible for EDI." "Built APIs for partners."
3. Practise answering these interview questions out loud (5 minutes each), then compare with the outlines below:
   a. "Design a system to sync products from a PIM to Shopify, Amazon and eBay."
   b. "How would you migrate 200 integrations off an on-premises ESB?"
   c. "A partner's API is slow and sometimes returns 500. Your integration must not lose data. Design it."
   d. "How do you handle secrets in integrations?"
   e. "What happens, step by step, when you call `https://api.partner.com/orders` from your code?"
4. Implement, in 45 minutes, a cursor-paginated API client with retries and `Retry-After` handling, with tests.

## Answer outlines

2. "Built 14 MuleSoft integrations connecting Salesforce, SAP and Workday, processing 2M messages/month at 99.95% success." "Owned EDI with 60 retail partners (850/855/856/810); cut chargebacks by 70% by automating ASN validation." "Designed partner REST APIs (OpenAPI, OAuth 2.0) adopted by 35 partners in 6 months, with zero breaking changes."
3a. Clarify scale and attributes; the PIM is the source of truth; events or delta export from the PIM; per-channel adapters with mapping specs (categories, variants, images); per-channel rate limits and bulk APIs (Shopify bulk mutations, Amazon feeds); idempotent upserts by SKU; error queue per channel with business-friendly messages; reconciliation; observability per channel.
3b. Inventory from runtime data; classify (retire, rehost, refactor, replace); target platform and standards; templates and CI/CD; waves by risk; parallel runs; partner coordination; decommissioning; metrics.
3c. Accept and persist work first (queue/outbox); call the partner with timeouts, retries with jittered backoff and a circuit breaker; idempotency keys; DLQ and replay; reconciliation; alerts on lag and DLQ.
3d. Secrets manager, no secrets in code or logs, least-privilege identities, rotation with overlap, inventory with expiry alerts, secretless federation where possible, secret scanning.
3e. Client pool → DNS → egress → TCP → TLS (chain, SNI, optional mTLS) → HTTP request with headers → CDN/WAF → gateway (auth, rate limit) → app → response; timeouts and failure modes at each step (Chapter 3).
