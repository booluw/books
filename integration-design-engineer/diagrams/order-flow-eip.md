# Worked example: order flow in EIP terms

Intake, publish-subscribe fan-out, idempotent receivers, splitter, router, aggregator and dead-letter channel.

Used in [Chapter 5](../chapters/05-integration-styles-and-patterns.md).

```mermaid
flowchart LR
  WH["Storefront webhook"] --> GW["API Gateway"] --> IN["Intake: verify, store, publish"]
  IN --> T{{orders.placed topic}}
  T --> ERP["ERP flow: idempotent receiver → translate → retry/circuit breaker"] --> ERPAPI[(ERP API)]
  ERP -.after retries.-> DLQ[[DLQ]]
  T --> FUL["Fulfilment: enrich → split → route"] --> W1["WH1 REST"]
  FUL --> W2["WH2 SFTP"]
  FUL --> W3["WH3 EDI 940"]
  W1 & W2 & W3 --> AGG["Aggregator"] --> EXC{{fulfilment exceptions}} --> CS["Email CS"]
  T --> CRM["CRM flow: filter → upsert"] --> CRMAPI[(CRM API)]
```
