# Exercises: Chapter 9, Data Integration

## Questions

1. ETL or ELT? (a) Loading 50 SaaS sources into Snowflake for analytics. (b) Loading employee data into a payroll provider that must never receive unmasked national IDs of contractors. (c) Daily bank statement files into the ERP.
2. Why does query-based CDC (`updated_at > :last`) miss deletes and intermediate states? Which CDC method captures both?
3. Run Debezium with PostgreSQL in Docker (follow the Debezium tutorial). Update a row three times quickly. How many change events do you see? What fields does each contain?
4. Two-way sync of contacts between CRM and marketing automation: propose field ownership for email, phone, lead score, lifecycle stage and unsubscribe flag.
5. What problem does a PostgreSQL replication slot cause if the CDC connector is down for a week? How do you prevent and recover from it?
6. Write a minimal data contract (YAML) for an `orders` dataset: schema, owner, freshness SLA, quality rules and change policy.

## Solutions

1. (a) ELT (raw data in, transform with dbt). (b) ETL: mask or filter before load. (c) Neither, really: an operational file integration with validation, likely ISO 20022 `camt.053` parsing and ERP import, best treated as application integration.
2. Query-based CDC sees only the current row: deleted rows are gone and multiple updates between polls collapse to one. Log-based CDC (WAL, binlog, redo log) captures both.
3. Three update events (op `u`), each with `before` and `after` row images (depending on replica identity), `source` metadata (LSN, transaction ID, timestamp) and `ts_ms`.
4. Example: email owned by CRM (or by the system where the person self-serves); phone by CRM; lead score by marketing automation (computed); lifecycle stage owned by marketing until the "SQL" (sales-qualified lead) stage, then by CRM; unsubscribe flag owned by marketing automation and **always propagated** (compliance).
5. WAL is retained for the slot and can fill the disk, threatening the primary database. Prevent: monitor slot lag and size, set `max_slot_wal_keep_size`, and alert. Recover: if the slot is dropped or WAL is lost, re-snapshot (incremental snapshots in Debezium).
6. Example:
```yaml
dataset: sales.orders
owner: orders-team@example.com
schema:
  - {name: order_id, type: string, required: true, unique: true}
  - {name: customer_id, type: string, required: true}
  - {name: total, type: decimal(18,2), required: true, rule: ">= 0"}
  - {name: currency, type: string, required: true, rule: "ISO 4217"}
  - {name: updated_at, type: timestamp_tz, required: true}
freshness: "data no older than 30 minutes, 99% of the time"
quality: ["no duplicate order_id", "every customer_id exists in customers"]
change_policy: "additive changes with 2 weeks' notice; breaking changes require new version and 3 months' overlap"
classification: [pii-indirect, financial]
```
