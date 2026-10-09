# Exercises: Chapter 20, Case Studies

## Questions

1. For case study 1, write the error-classification table (§8.1 style) for the 945 shipment-confirmation flow.
2. For case study 2, design the "mapping review" step that caught hidden business logic. Who participates, and what are the outputs?
3. For case study 3, design the per-tenant rate-limit budget. How is it configured, enforced and shown to customers?
4. For case study 4, list the FHIR resources you would populate from an 835 remittance and an 837 claim.
5. For case study 5, add a tool that lets the agent update a customer's shipping address on an unshipped order. What safeguards do you add?
6. Write your own case study (one page) about an integration you have worked on, using the structure of this chapter: context, requirements, options, design, what went wrong, lessons.

## Answer outlines

1. Unknown order → fix-then-retry (order may not be created yet: delayed retry, then business queue). Duplicate shipment ID → ignore (idempotent). NetSuite concurrency limit → retry with backoff. Item not on order → business queue to operations. Shopify fulfilment API `429` → retry with `Retry-After`. Malformed EDI → reject to the EDI provider, alert.
2. Participants: integration engineer, business owner of the process, original developer if available, tester. Outputs: documented rules in the mapping spec, golden-file test cases from production samples, sign-off.
3. Default share of the customer's daily allocation (e.g. 20%); configurable in the integration settings; enforced by a distributed token bucket per tenant; adaptive using limit headers; usage shown on the sync health page with alerts when nearing the budget.
4. `ExplanationOfBenefit` (adjudicated claim and payment), `Claim` (where used), `Coverage`, `Patient`, `Practitioner`/`Organization` (providers), with codes mapped to standard code systems.
5. Ownership check; only for unshipped orders; address validation; idempotency on order and new address; human or customer confirmation step (MCP Apps or elicitation); audit log; a notification to the customer's email on file; rate limits.
6. Personal answer.
