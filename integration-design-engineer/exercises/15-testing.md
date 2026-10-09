# Exercises: Chapter 15, Testing

## Questions

1. Write a test plan (table as in §15.13) for the webhook receiver example.
2. Add three new golden-file cases to `examples/data-mapping`: an emoji in the address, a GBP order with a discount line (negative amount), and an order placed at 01:30 on the day the clocks go back in Los Angeles.
3. Using `unittest.mock` or a fake, write a component test that proves an order sync retries a `503` twice and then succeeds without creating duplicates.
4. Explain the difference between consumer-driven contract testing and specification-based contract testing. Which would you use with Salesforce's API? With an internal team's API?
5. Design a backlog-drain test for an integration whose downstream allows 20 requests/second.
6. How would you verify in production that a new integration version produces the same output as the old one before switching over?

## Solutions (outline)

1. Unit: signature verification cases. Component: HTTP tests with duplicates and oversize. Resilience: worker crash. Performance: burst of 1,000 webhooks/second. Production: synthetic signed webhook every 5 minutes.
2. Hands-on. Note that the mapping currently rejects negative quantities but negative *amounts* need a design decision (discount lines). DST: 2026-11-01 01:30 occurs twice in Los Angeles, so the source instant's offset (−07:00 or −08:00) decides the UTC time, while the business date is the same.
3. Use a fake client returning 503, 503, 201 and assert one created record and three calls; use the same idempotency key on each attempt.
4. Consumer-driven: the consumer publishes expectations and the provider verifies them in its CI (needs both teams' cooperation): internal teams. Specification-based: validate against the provider's published spec, plus diffs and canary checks: third-party SaaS such as Salesforce.
5. Queue N = 6 hours × peak rate of messages; release; verify the consumer never exceeds 20 rps (rate limiter), time to drain, no `429` storms, no DLQ growth, and reconciliation passes after.
6. Shadow mode: run the new version on the same inputs, write outputs to a sink, and compare field by field with the old version's outputs; investigate differences; then canary by tenant or percentage.
