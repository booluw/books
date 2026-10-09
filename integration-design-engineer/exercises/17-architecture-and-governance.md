# Exercises: Chapter 17, Architecture and Governance

## Questions

1. Draw a context map for an e-commerce company with bounded contexts Catalogue, Ordering, Payments, Fulfilment and Customer Support, including relationships with Shopify, Stripe and a 3PL. Mark which relationships need an anti-corruption layer.
2. Critique: "Every integration must go through Experience, Process and System APIs."
3. Write five Spectral rules that encode an API style guide (for example, snake_case properties, cursor pagination, problem+json errors).
4. Design the fields of an integration catalogue for your organisation. What are the five most important?
5. Your organisation has a central integration team with a 9-month backlog. Propose an operating-model change.
6. Write three architecture fitness functions you could automate this month.

## Solutions (outline)

1. Shopify, Stripe and the 3PL are upstream third parties; Ordering is a conformist or uses an ACL toward Shopify; Payments uses an ACL toward Stripe; Fulfilment uses an ACL toward the 3PL (EDI translation); Support consumes events from Ordering and Fulfilment (published language).
2. Rigid layering adds latency, cost and failure points without value for simple flows; use layers where reuse and decoupling are real.
3. Example Spectral rules: properties must match `^[a-z][a-z0-9_]*$`; list operations must define `limit` and `cursor` parameters; 4xx/5xx responses must use `application/problem+json`; every operation must have `operationId` and `description`; `servers` must use https.
4. Owner, criticality, connected systems, interfaces and versions (with deprecation dates), and runbook/dashboard links.
5. C4E or platform model: the central team builds the platform, templates, standards and coaching; domain teams build their own integrations; the central team keeps complex or specialised areas (EDI, SAP).
6. OpenAPI lint in CI for all API repositories; a nightly job flagging credentials expiring within 14 days; a check that every production integration in the runtime has a catalogue entry with an owner.
