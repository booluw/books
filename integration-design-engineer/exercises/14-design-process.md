# Exercises: Chapter 14, Design Process

## Questions

1. Write the one-paragraph frame (§14.2) for an integration you know or invent.
2. Write ten discovery questions you would ask a warehouse manager before integrating your ERP with their WMS.
3. Turn these vague statements into measurable NFRs: "It should be fast." "It must be reliable." "It must handle Black Friday."
4. Write an ADR for choosing between polling and webhooks for a HubSpot → data warehouse integration.
5. Using `templates/integration-design-document.md`, write a design for: new hires in Workday → accounts in Okta → laptop order in ServiceNow. Include at least one failure-path sequence diagram.
6. Estimate the integration in question 5 using the complexity drivers in §14.11. Which unknowns would you spike first?
7. Run a mock design review of a colleague's design using the questions in §14.10.

## Solutions (outline)

1. Must name the business event, outcome, timeliness, value and current state.
2. Examples: Which events matter (pick, pack, ship, short-pick, return)? How do you handle partial shipments? What are your cut-off times? What identifiers do you use for orders, lines and SKUs? What happens on Black Friday? How do you correct a shipment sent in error? How do you report inventory adjustments? What are your maintenance windows? Who do we call when it breaks? Which file or API formats can you send and receive?
3. "95% of requests complete within 500 ms and 99% within 2 s, measured weekly." "No message loss, verified by daily reconciliation; 99.9% of events processed within 15 minutes over 28 days." "Sustain 3,000 orders/hour for 4 hours with p95 end-to-end latency under 10 minutes, and drain a 6-hour backlog within 2 hours."
4. Should state context (volumes, latency need, API limits), decision (for example webhooks plus daily reconciliation), consequences and alternatives.
5. Look for: Workday as source of truth; effective-dated hires (future start dates); idempotent user creation keyed on employee ID; SCIM or Okta APIs; ServiceNow catalog request; failure path when Okta is down or the username conflicts; deprovisioning considered; PII handling.
6. Spike first: Workday access (ISU, security groups) and the extract mechanism; Okta API rate limits and username rules; ServiceNow request API and approvals.
7. Practice exercise.
