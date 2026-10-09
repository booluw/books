# Exercises: Chapter 12, Enterprise Applications

## Questions

1. Using the §12.1 checklist, document the integration surface of one SaaS application you use (APIs, auth, limits, change detection, bulk, upsert, customisation).
2. In a free Salesforce Developer Edition org: create an External ID field on Account, upsert an account by it twice with the REST API, and confirm only one record exists.
3. Why can a simple Salesforce API update fail with `UNABLE_TO_LOCK_ROW`? How do you design around it?
4. A NetSuite integration was built on SOAP web services in 2022. What must happen by 2028, and what is your migration plan?
5. A Workday "worker changes" extract runs daily. A termination is entered today with an effective date next month. When should downstream systems act on it?
6. Shopify: why are bulk operations better than paginating the Admin API for a 2-million-order export?

## Solutions

1. Personal answer.
2. Hands-on. Use `PATCH /services/data/vXX.X/sobjects/Account/My_Ext_Id__c/ABC-1` twice; the first returns `201`, the second `204`.
3. Parallel updates to child records lock the same parent (or the same record is updated concurrently), and triggers may update related records. Group updates by parent, reduce parallelism, sort by parent ID within batches, and retry lock errors with backoff.
4. SOAP is removed in NetSuite 2028.2; from 2027.1 only the 2025.2 endpoint is supported. Plan: inventory SOAP operations used; map to REST record API, SuiteQL or RESTlets; move to OAuth 2.0; build and test in sandbox; migrate in waves; monitor; retire SOAP credentials.
5. Depends on the downstream process: identity systems should schedule deprovisioning for the effective date (not now); payroll needs it in the right period; some systems need advance notice. The extract must carry effective dates, and consumers must handle future-dated and rescinded transactions.
6. Bulk operations run asynchronously server-side and produce JSONL files, avoiding millions of paginated calls, cost-based rate limits and long-running cursors.
