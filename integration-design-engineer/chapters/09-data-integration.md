# Chapter 9. Data Integration: ETL, ELT, CDC and Streaming

> "Data is a liability until it is in the right place, in the right shape, at the right time."

## What you will learn

- The difference between *application integration* and *data integration*, and why the line is blurring.
- ETL versus ELT, batch versus streaming, full versus incremental loads.
- Change Data Capture (CDC): log-based, trigger-based and query-based, with Debezium as the reference implementation.
- The modern data stack: Fivetran, Airbyte, dbt, warehouses, lakehouses and reverse ETL.
- Bidirectional sync, conflict resolution and master data management (MDM).
- Data quality, data contracts and lineage.

---

## 9.1 Application integration versus data integration

| | Application integration | Data integration |
|---|---|---|
| Purpose | Drive operational business processes | Consolidate data for analytics, reporting, ML and AI |
| Granularity | Individual transactions and events | Datasets, tables, files |
| Latency | Seconds | Minutes to a day (increasingly near real time) |
| Typical tools | APIs, message brokers, iPaaS | ETL/ELT tools, CDC, warehouses, orchestration (Airflow, Dagster) |
| Typical owner | Integration / platform team | Data engineering team |
| Failure impact | Business process stops | Reports wrong or late |

The worlds are converging. CDC feeds both microservices and warehouses; reverse ETL pushes analytical results back into operational SaaS; iPaaS vendors offer data pipelines; data-platform vendors offer application connectors. Salesforce's acquisition of Informatica (closed November 2025) and IBM's acquisition of Confluent (closed March 2026) both reflect this convergence. An Integration Design Engineer needs working fluency in both.

---

## 9.2 ETL and ELT

- **ETL (Extract, Transform, Load):** extract from sources, transform in a separate engine (Informatica PowerCenter, IBM DataStage, Talend, SSIS, custom code), then load into the target. This was the classic approach when warehouse compute was expensive.
- **ELT (Extract, Load, Transform):** load raw data into a cloud warehouse or lakehouse first, then transform with SQL inside it (typically with **dbt**). Cheap, elastic warehouse compute made this the default for analytics in the late 2010s.

ELT advantages: raw data is kept (you can re-transform when logic changes); transformation is version-controlled SQL; analysts can contribute. ETL is still right when data must be cleansed, masked or reduced *before* it lands (privacy, cost, regulatory), or when the target is an operational system rather than a warehouse.

### Load strategies

| Strategy | How | When |
|---|---|---|
| **Full load** | Copy everything every time; replace the target | Small tables; sources with no change tracking; periodic integrity checks |
| **Incremental (high-water mark)** | Extract rows where `updated_at > last_max` | Most API and database sources; watch for the pitfalls in Chapter 6 (clock skew, ties, deletes) |
| **CDC** | Read the source's change log | Large, busy databases; deletes required; low latency |
| **Snapshot + CDC** | Initial consistent snapshot, then stream changes | Standard Debezium and Fivetran pattern |

### Loading patterns in the target

- **Append-only** raw tables with ingestion timestamps (immutable history).
- **Merge / upsert** into current-state tables (`MERGE INTO … USING … ON key`).
- **Slowly Changing Dimensions (SCD)** in warehouses: Type 1 (overwrite), Type 2 (new row per version with valid-from and valid-to dates), and others. dbt *snapshots* implement Type 2.
- **Soft deletes** (`_deleted = true`) rather than physical deletes, so history and downstream syncs remain consistent.

---

## 9.3 Change Data Capture (CDC)

CDC captures inserts, updates and deletes from a database as a stream of change events.

| Method | How | Pros | Cons |
|---|---|---|---|
| **Query-based** | Poll with `WHERE updated_at > ?` | Simple; works anywhere | Misses deletes and intermediate states; needs a reliable timestamp column; loads the source |
| **Trigger-based** | Database triggers write changes to a shadow table | Captures deletes | Adds write overhead; triggers are fragile |
| **Log-based** | Read the database's transaction log: PostgreSQL WAL (logical decoding), MySQL binlog, SQL Server CDC / transaction log, Oracle redo logs (LogMiner / XStream), MongoDB change streams, Db2 | Complete (including deletes), low overhead, ordered, low latency | Requires database privileges and configuration; log retention must be managed; schema changes need handling |

**Debezium** (Red Hat, open source) is the reference log-based CDC platform. It runs as Kafka Connect source connectors, as Debezium Server (sending to Kinesis, Pub/Sub, Pulsar, Redis, HTTP and more) or embedded in an application. Each change event contains `before` and `after` row images, the operation (`c`, `u`, `d`, `r` for snapshot reads), source metadata (log position, transaction ID) and a timestamp. Commercial and managed alternatives include Oracle GoldenGate, Qlik Replicate, Fivetran (including HVR), AWS DMS, Google Datastream, Azure Data Factory CDC, Striim, Estuary and Confluent's managed connectors.

### CDC design considerations

- **CDC exposes your internal schema.** Raw CDC events are table rows, not business events. Use the **outbox pattern with CDC** (Chapter 8) to publish deliberate integration events, or transform CDC streams into business events with stream processing before other teams consume them.
- **Initial snapshots** of large tables take time and load. Debezium's incremental snapshots (watermark-based) can run concurrently with streaming.
- **Schema evolution:** column additions and type changes must flow through the pipeline. Use a schema registry.
- **Log retention:** if the CDC connector is down longer than the database keeps its logs (PostgreSQL replication slots can fill a disk; MySQL binlogs expire), you must re-snapshot. Monitor slot and lag.
- **Transactions:** a business transaction may produce several change events. Debezium can emit transaction metadata so consumers can group them.
- **Deletes and tombstones:** in Kafka, a delete is followed by a tombstone (null value) so log compaction can remove the key.

---

## 9.4 The modern data stack *(as of October 2026)*

| Layer | Purpose | Examples |
|---|---|---|
| **Ingestion / EL** | Managed connectors from SaaS and databases into the warehouse | Fivetran (merged with dbt Labs; announced October 2025, completed June 2026), Airbyte (open source + cloud), Stitch, Hevo, Estuary, Informatica, Matillion, AWS Glue, Azure Data Factory, Google Cloud Data Fusion; open-source dlt (data load tool) for code-first pipelines |
| **Streaming ingestion** | Real-time | Kafka Connect, Debezium, Kinesis Firehose, Snowpipe Streaming, BigQuery Storage Write API |
| **Storage / compute** | Warehouse or lakehouse | Snowflake, Google BigQuery, Databricks, Amazon Redshift, Microsoft Fabric, ClickHouse; open table formats **Apache Iceberg**, Delta Lake and Apache Hudi |
| **Transformation** | SQL modelling, testing, documentation | dbt (Core and Cloud), SQLMesh, Coalesce, Dataform |
| **Orchestration** | Scheduling and dependencies | Apache Airflow, Dagster, Prefect, cloud schedulers |
| **Reverse ETL / activation** | Push modelled data back into SaaS tools | Hightouch, Census (Fivetran agreed to acquire it in May 2025), plus CDPs (Segment, mParticle, RudderStack) |
| **Quality and observability** | Tests, anomaly detection, lineage | dbt tests, Great Expectations, Soda, Monte Carlo, OpenLineage |
| **Catalogue and governance** | Discovery, ownership, access | Unity Catalog, Apache Polaris, DataHub, Collibra, Alation, Atlan, Informatica |

**Open table formats** (Iceberg especially) let multiple engines read and write the same data in object storage. This changes integration: instead of copying data between platforms, systems increasingly *share* tables. "Zero-copy" or "zero-ETL" features (Salesforce Data Cloud zero-copy, Snowflake and Databricks data sharing, AWS zero-ETL integrations from Aurora to Redshift) reduce pipeline building, but they do not remove the need to understand semantics, freshness and access control.

---

## 9.5 Reverse ETL and operational analytics

**Reverse ETL** syncs modelled warehouse data back into operational systems: a "lead score" or "customer lifetime value" calculated in Snowflake is written to Salesforce, HubSpot, Zendesk or ad platforms. It is integration in every sense, with the usual concerns:

- **Upsert keys** and identity resolution between the warehouse and the SaaS tool.
- **Rate limits** of the target API; batching; incremental diffs (send only rows that changed since the last sync).
- **Field ownership:** do not overwrite fields that humans maintain in the CRM.
- **Failure reporting** per row.

---

## 9.6 Bidirectional sync and conflict resolution

Two-way sync ("keep contacts in Salesforce and HubSpot identical") is one of the hardest integration problems. Questions to answer:

1. **Ownership:** which system is the source of truth, per entity *and per field*? Ideally each field has exactly one writer.
2. **Loop prevention:** a change synced from A to B triggers B's change event, which syncs back to A, and so on forever. Techniques: tag changes made by the integration user and ignore them; compare values and skip no-op updates; track the last-synced hash per record.
3. **Conflicts:** both sides changed the same field since the last sync. Strategies:
   - *Source-of-truth wins* (simplest; recommended).
   - *Last writer wins*, by timestamp (clock skew makes it unreliable; per-field timestamps help).
   - *Merge rules* per field.
   - *Manual review queue.*
4. **Deletes and merges:** if a user merges two duplicate contacts in the CRM, what happens to the two linked records in the other system?
5. **Initial alignment:** how are existing records matched before sync starts (matching rules on email, domain, tax ID), and who reviews uncertain matches?

**Design advice:** avoid true bidirectional sync of the same field whenever possible. Partition ownership by field or by lifecycle stage (for example, marketing owns a lead until it becomes an opportunity; then sales owns it).

---

## 9.7 Master Data Management (MDM)

**Master data** is the core shared entities: customers, products, suppliers, employees, locations and the chart of accounts. **MDM** is the discipline (and software) for maintaining a single trusted version.

MDM styles (after Gartner's classification):

| Style | Description |
|---|---|
| **Registry** | Keeps only a cross-reference index of identities across systems; data stays in the sources. |
| **Consolidation** | Copies data into a hub to build a golden record for reporting; sources are not updated. |
| **Coexistence** | The golden record is synchronised back to sources; several systems can still author. |
| **Centralised (transactional)** | The MDM hub is the only authoring system; it publishes to all consumers. |

Key MDM capabilities are **matching** (deterministic and probabilistic identity resolution), **merging and survivorship rules** (which source wins for each attribute), stewardship workflows and hierarchy management. Vendors include Informatica MDM (now part of Salesforce), Reltio, Semarchy, Profisee, Stibo Systems (strong in product data), SAP Master Data Governance, Tamr and Syndigo.

For integration engineers, MDM matters because it defines **who owns identities** and gives you the **cross-reference** (Chapter 4) you need to map records between systems.

---

## 9.8 Data quality

Bad data is the leading cause of integration errors that are not infrastructure failures. Dimensions of data quality:

| Dimension | Example check |
|---|---|
| Completeness | Required fields present; no missing days in a daily feed |
| Validity | Values conform to type, format and allowed ranges (ISO country codes, positive quantities) |
| Accuracy | Values match reality (address verification) |
| Consistency | The same fact agrees across systems (reconciliation) |
| Uniqueness | No duplicate customers or orders |
| Timeliness / freshness | Data arrived within its SLA |
| Integrity | References resolve (every order line references an existing product) |

Where to enforce:

- **At the boundary,** with schema validation of inbound payloads (reject early, with clear errors).
- **In pipelines,** with tests (dbt tests, Great Expectations, Soda) that fail or warn.
- **By monitoring** freshness and volume anomalies (Chapter 16).

### Data contracts

A **data contract** is an agreement between a data producer and its consumers about schema, semantics, quality expectations, SLAs and change management, often expressed in machine-readable form (for example, the **Open Data Contract Standard (ODCS)**, maintained by the Linux Foundation's Bitol project) and checked in CI. Data contracts apply API-style discipline to datasets and event streams. They are especially useful at the boundary between application teams (who change schemas) and data teams (who depend on them).

### Lineage

**Lineage** records where data came from and how it was transformed. **OpenLineage** (an LF AI & Data project) is an open standard for emitting lineage events from pipelines (Airflow, Spark, dbt, Flink), consumed by catalogues such as Marquez, DataHub and others. Lineage lets you answer "if this source field changes, what breaks?", which is essential for impact analysis.

---

## 9.9 Batch versus streaming: how to decide

| Question | Batch | Streaming |
|---|---|---|
| Is minutes-to-hours latency acceptable? | Yes | No |
| Is the source only available as files or periodic exports? | Yes | — |
| Is the processing naturally windowed (daily close, payroll)? | Yes | — |
| Do consumers need to react to individual events? | — | Yes |
| Is operational simplicity the priority? | Yes | — |
| Is volume steady and high, so continuous processing is cheaper than spikes? | — | Yes |

Many organisations use a **hybrid**: stream for operational freshness, batch for heavy reprocessing and reconciliation. Do not stream because it is fashionable. A reliable nightly batch beats a fragile streaming pipeline.

---

## 9.10 Data integration for AI

Retrieval-augmented generation (RAG) and AI agents add new integration consumers:

- **Ingestion into vector or hybrid search indexes:** connectors that pull documents from SharePoint, Google Drive, Confluence and Zendesk, chunk them, embed them and keep them in sync, including **permissions**. Respecting source-system access-control lists in the index is the hardest part.
- **Freshness and deletion:** a document deleted or restricted in the source must disappear from the index quickly.
- **Live tool access via MCP** (Chapter 18) as an alternative to copying data: the agent queries the system of record at question time, under the user's permissions.
- **Real-time context:** streaming platforms position themselves as the "real-time context layer" for agents, which is part of the rationale IBM gave for buying Confluent.

---

## Summary

- Data integration moves datasets for analytics and AI; application integration moves transactions for processes. You need both.
- ELT into cloud warehouses is the analytics default; ETL remains for pre-load cleansing and operational targets.
- Log-based CDC (Debezium and others) is the most complete way to capture database changes. Publish deliberate integration events (outbox) rather than raw table changes to other teams.
- Avoid bidirectional sync of the same field; define ownership; handle loops, conflicts, merges and deletes.
- MDM defines identity and ownership; data quality checks and data contracts keep pipelines honest; lineage enables impact analysis.

## Exercises

See [`exercises/09-data-integration.md`](../exercises/09-data-integration.md).

## Further reading

- Joe Reis and Matt Housley, *Fundamentals of Data Engineering* (O'Reilly, 2022).
- Martin Kleppmann and Chris Riccomini, *Designing Data-Intensive Applications*, 2nd edition (O'Reilly, 2026), chapters on replication, stream processing and batch processing.
- Ralph Kimball and Margy Ross, *The Data Warehouse Toolkit*, 3rd edition (Wiley, 2013).
- Debezium documentation (debezium.io), especially the outbox event router.
- Chad Sanderson and Mark Freeman, *Data Contracts: Developing Production-Grade Pipelines at Scale* (O'Reilly, 2025).
