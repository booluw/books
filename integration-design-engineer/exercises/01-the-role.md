# Exercises: Chapter 1, The Role

## Questions

1. In your own words, explain why integration is considered a separate specialism from backend engineering. Give three reasons.
2. Classify each job-posting excerpt as *enterprise*, *product* or *services* integration, and as *build*, *design* or *customer-facing*:
   a. "Build and maintain our native integrations with Salesforce, HubSpot and Microsoft Dynamics used by 4,000 customers."
   b. "Define integration standards and patterns across our SAP, Workday and ServiceNow landscape; chair the integration design authority."
   c. "Deliver MuleSoft integration projects for clients in financial services; MuleSoft Developer certification required."
   d. "Lead technical discovery and demos with prospects, scoping how our platform connects to their ERP."
3. A posting is titled "Integration Design Engineer" and mentions "CATIA, harness routing and GD&T". Is it the role this book describes? Why or why not?
4. For the retailer in §1.1, list the systems of record you would *expect* for: customer email address, product price, stock on hand, shipment tracking number, and invoice. Explain one case where the answer is debatable.
5. Rate yourself (junior / mid / senior) in each row of the skills map (§1.7). Pick the two weakest rows and write one concrete action for each.

## Solutions

1. Possible reasons: you control neither side of most interfaces; partial failure is the normal state; the hard part is semantics, not syntax; errors have direct financial or customer impact; integrations live for years and pass between owners; the work needs stakeholder and vendor management as well as code.
2. a: product / build. b: enterprise / design. c: services / build. d: product (pre-sales) / customer-facing.
3. No. CATIA (CAD), harness routing and GD&T (geometric dimensioning and tolerancing) mark a *physical* integration role in aerospace, automotive or electronics.
4. Typical answers: email to CRM or e-commerce platform (debatable: marketing tools and the storefront both edit it, so define field ownership); price to ERP or PIM (debatable when the storefront runs promotions); stock on hand to ERP/WMS (3PL is the physical truth, ERP the financial one); tracking number to the 3PL/carrier; invoice to ERP. The debate is the point: write ownership down per field.
5. Personal answer. A good action is specific, for example: "Implement the outbox example and explain it to a colleague by Friday."
