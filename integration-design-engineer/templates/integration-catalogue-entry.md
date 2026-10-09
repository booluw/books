# Catalogue entry: <Integration / API / event name>

```yaml
id: INT-0042
name: Salesforce Closed-Won → NetSuite Sales Order
kind: integration            # integration | api | event | file-feed
lifecycle: production        # design | review | production | deprecated | retired
criticality: tier-1
owner:
  team: integrations-platform
  person: jane.doe
business_owner: finance-operations
purpose: Create customers and sales orders in ERP when deals close.
systems:
  source: [salesforce-prod]
  target: [netsuite-prod]
style: event-driven          # api | event-driven | batch-file | cdc | ipaas-flow
platform: <ipaas or runtime>
interfaces:
  - type: platform-event
    ref: Opportunity_Closed_Won__e
  - type: rest
    ref: netsuite REST record API (salesOrder, customer)
    api_versions_in_use: ["v1"]
deprecations:
  - what: NetSuite SOAP endpoint 2023.2
    removal: 2028.2
    migration_ticket: INT-311
data_classification: [pii, financial]
regions: [us]
credentials:                 # references only, never secrets
  - ref: vault://integrations/sf-jwt-cert
    expires: 2027-03-01
slo: 95% of orders in ERP within 15 minutes (28-day window)
docs:
  design: link
  runbook: link
  dashboard: link
consumers: []                # for APIs/events: registered consumers to notify of changes
```
