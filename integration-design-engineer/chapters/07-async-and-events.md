# Chapter 7. Asynchronous and Event-Driven Integration

> "Don't call us, we'll call you."
> (the Hollywood Principle, and the essence of events)

## What you will learn

- Queues, topics and logs: the three shapes of messaging, and the brokers that implement them (RabbitMQ, Amazon SQS/SNS, Azure Service Bus, Google Pub/Sub, Apache Kafka, Amazon EventBridge and others).
- Delivery guarantees (at-most-once, at-least-once, "exactly-once") and what they really mean.
- Ordering, partitioning, consumer groups and backpressure.
- Event design: thin versus fat events, event schemas, CloudEvents and AsyncAPI.
- Webhooks: designing them as a provider and consuming them safely.
- Event-driven architecture patterns: event notification, event-carried state transfer, event sourcing and CQRS.

---

## 7.1 Why asynchronous?

Chapter 5 introduced messaging as the most resilient integration style. Asynchronous integration gives you:

1. **Temporal decoupling.** The consumer can be down; messages wait.
2. **Load levelling.** A burst of 10,000 orders becomes a queue drained at the ERP's sustainable rate.
3. **Fan-out.** One event, many independent consumers, and the producer does not know or care who they are.
4. **Failure isolation.** A slow consumer does not slow the producer.
5. **Natural retry and dead-lettering.**

The costs: eventual consistency, more moving parts, harder debugging, and the need to handle duplicates and out-of-order delivery. This chapter teaches you to pay those costs well.

---

## 7.2 Queues, topics and logs

### Queue (point-to-point)

Each message goes to **one** consumer. Once acknowledged, it is deleted. Several consumers on one queue are **competing consumers** that share the load.

Use for **commands and work distribution**: "process this order", "send this email".

### Topic (publish/subscribe)

Each message is delivered to **every subscription**. Each subscription usually behaves like its own queue. Use for **events** that many systems care about.

A common cloud pattern is **topic → queue per subscriber** (SNS → SQS fan-out; Azure Service Bus topic → subscriptions; Google Pub/Sub topic → subscriptions). Each consumer gets its own durable queue with its own retry and dead-letter behaviour.

### Log (stream)

Messages are appended to an ordered, durable, **replayable** log and kept for a retention period (days, forever, or compacted to the latest value per key). Consumers track their own **offset** (position) and can rewind. Kafka, Amazon Kinesis, Azure Event Hubs, Redpanda, Apache Pulsar and Google Pub/Sub with seek and replay work this way.

Use for **event streaming**: high volume, multiple consumers reading at their own pace, replay for recovery or for new consumers, and stream processing.

| | Queue | Topic + subscriptions | Log |
|---|---|---|---|
| Consumers per message | One | One per subscription | Any number of consumer groups |
| After consumption | Deleted | Deleted per subscription | Retained until retention expires |
| Replay | No (except DLQ redrive) | Limited | Yes: seek to any offset or time |
| Ordering | Usually best-effort (FIFO variants exist) | Per subscription, best-effort | Strict **per partition** |
| Per-message ack / redelivery | Yes | Yes | Offset commits (per partition); Kafka share groups add per-record acks |
| Typical products | RabbitMQ, SQS, Azure Service Bus queues, IBM MQ, ActiveMQ | SNS, Service Bus topics, Pub/Sub, RabbitMQ exchanges | Kafka, Kinesis, Event Hubs, Pulsar, Redpanda |

---

## 7.3 The broker landscape *(as of October 2026)*

| Broker | Model | Notes |
|---|---|---|
| **Apache Kafka** | Partitioned log | The de facto event-streaming standard. **4.0 (March 2025)** removed ZooKeeper (KRaft only). **4.1 (September 2025)** previewed share groups. **4.2 (early 2026)** made **Queues for Kafka** (KIP-932 share groups) production-ready, adding per-record acknowledgement and redelivery so many consumers can share a partition. Commercial: **Confluent** (acquired by IBM, closed 17 March 2026), Amazon MSK, Azure Event Hubs (Kafka-compatible endpoint), Aiven, Redpanda (Kafka-compatible, C++), WarpStream (acquired by Confluent in 2024; object-storage-based). |
| **RabbitMQ** | Exchanges and queues (AMQP 0-9-1); also streams | Flexible routing (direct, topic, fanout, headers exchanges). **Quorum queues** (Raft-based) are the recommended durable queue type; classic mirrored queues were removed in 4.0 (2024). RabbitMQ 4.x also speaks AMQP 1.0 natively. |
| **Amazon SQS** | Queue | Standard (at-least-once, best-effort order, nearly unlimited throughput) and **FIFO** (ordered per message group, de-duplication within 5 minutes). Max message 1 MiB since August 2025. Visibility timeout, DLQ with redrive. |
| **Amazon SNS** | Topic | Fan-out to SQS, Lambda, HTTP, email and SMS; FIFO topics; message filtering. |
| **Amazon EventBridge** | Event bus with rules | Content-based routing rules, SaaS partner event sources, schema registry, archive and replay, **Pipes** (point-to-point source → filter → enrich → target), **Scheduler**. |
| **Amazon Kinesis Data Streams** | Log | Shards; AWS-native streaming. |
| **Azure Service Bus** | Queues and topics (AMQP 1.0) | Sessions (ordered groups), duplicate detection, scheduled messages, dead-lettering, transactions. The enterprise workhorse on Azure. |
| **Azure Event Grid** | Event routing (push) | Reactive routing; supports CloudEvents; MQTT broker support. |
| **Azure Event Hubs** | Log | Kafka-compatible endpoint; capture to storage. |
| **Google Cloud Pub/Sub** | Topic/subscription | Push or pull; ordering keys; exactly-once delivery option for pull subscriptions; seek and replay. |
| **IBM MQ** | Queue | Transactional, extremely reliable; dominant in banking and mainframe estates. |
| **Apache ActiveMQ (Classic / Artemis)** | Queue/topic (JMS, AMQP, MQTT, STOMP) | Common in Java estates; Amazon MQ offers managed ActiveMQ and RabbitMQ. |
| **Solace PubSub+** | Event mesh | Multi-protocol, hybrid; strong in capital markets. |
| **NATS / JetStream** | Lightweight pub/sub plus streams | Simple, fast; popular in cloud-native and edge. |
| **Apache Pulsar** | Log + queue | Segmented storage (BookKeeper), multi-tenancy, geo-replication. |
| **MQTT brokers** (HiveMQ, EMQX, Mosquitto) | Pub/sub for IoT | Lightweight; QoS levels 0, 1 and 2. |
| **Redis Streams** | Log-like | Lightweight; durability depends on configuration. |

How to choose:

- **Simple work queue on AWS:** SQS. **Fan-out on AWS:** SNS → SQS, or EventBridge when you need content-based rules or SaaS sources.
- **Enterprise messaging on Azure:** Service Bus. **Event routing:** Event Grid. **Streaming:** Event Hubs.
- **High-volume event streaming, replay, stream processing or CDC:** Kafka (managed if at all possible).
- **Complex routing, request/reply and moderate volume, self-hosted:** RabbitMQ.
- **Existing banking or mainframe estate:** IBM MQ is probably already there.

---

## 7.4 Delivery guarantees

Every messaging system offers one of three guarantees *between broker and consumer*:

| Guarantee | Meaning | How it happens |
|---|---|---|
| **At-most-once** | Never duplicated, may be lost | Consumer acknowledges *before* processing; a crash loses the message. |
| **At-least-once** | Never lost, may be duplicated | Consumer acknowledges *after* processing; a crash after processing but before the ack causes redelivery. |
| **Exactly-once** | Neither lost nor duplicated | Only possible *within a closed system* with transactions (Kafka transactions for consume-transform-produce inside Kafka; Pub/Sub exactly-once within its acknowledgement deadline). |

**Integration engineers design for at-least-once delivery plus idempotent consumers.** That combination produces "**effectively-once**" processing. The moment your consumer has a side effect *outside* the broker (an API call, a database write, an email), the broker's exactly-once guarantees no longer cover it. Your consumer must de-duplicate (Chapter 8).

### Acknowledgements, visibility timeouts and redelivery

- **SQS:** a received message becomes invisible for the **visibility timeout**. If the consumer does not delete it in time, it reappears for another consumer. Set the timeout longer than your worst-case processing time, or extend it while working. Otherwise you will process messages twice *concurrently*.
- **RabbitMQ:** manual `ack`/`nack`; unacknowledged messages are redelivered when the channel closes. **Prefetch** (`basic.qos`) limits unacknowledged messages per consumer, which is essential backpressure.
- **Kafka consumer groups:** consumers commit offsets per partition. Committing *after* processing gives at-least-once. A failure on one record blocks the partition unless you move it aside (retry topic or DLQ). Share groups (Kafka 4.2) add per-record acknowledgement, release and reject.
- **Azure Service Bus:** *peek-lock* mode with complete/abandon/dead-letter; a lock duration with renewal; `MaxDeliveryCount` before automatic dead-lettering.

---

## 7.5 Ordering

Global ordering does not scale, so most systems offer **ordering within a key**:

- **Kafka:** ordered within a partition. The **message key** determines the partition (`hash(key) % partitions`), so all events for `order_id=123` land in one partition, in order. Changing the partition count changes the key mapping. Plan partition counts up front.
- **SQS FIFO:** ordered within a **message group ID**.
- **Azure Service Bus:** ordered within a **session**.
- **Google Pub/Sub:** ordered within an **ordering key**.

Ordering is fragile in practice. Retries, parallel consumers, DLQ redrives and producers in multiple regions all reorder messages. **Design consumers that tolerate disorder** wherever possible:

- Include a **version number or sequence** per entity in each event; ignore events older than the version you have already applied.
- Make events **state-based** ("order 123 is now `shipped`, version 7") rather than purely delta-based ("add 2 to quantity").
- Or treat the event as a **notification** and fetch the current state from the source (§7.7).

---

## 7.6 Consumer scaling and backpressure

- **Kafka:** parallelism is capped by partition count *per consumer group* (with classic consumer groups). Ten partitions means at most ten active consumers. Share groups lift this cap.
- **Queues:** add competing consumers; respect the downstream's capacity.
- **Backpressure:** the downstream (ERP, SaaS API) sets the real throughput limit. Limit consumer concurrency to the downstream's rate limit. Do not autoscale consumers into a `429` storm.
- **Consumer lag** (messages waiting, or the offset gap) is the key health metric (Chapter 16). Rising lag means consumers cannot keep up.

---

## 7.7 Designing events

### Event types

Martin Fowler distinguishes several meanings of "event-driven":

1. **Event notification:** a thin message ("order 123 changed") that tells subscribers something happened. Subscribers call back for details. *Loose coupling, extra calls.*
2. **Event-carried state transfer:** the event carries the full relevant state ("order 123: status shipped, lines…, address…"). Subscribers need not call back and can maintain local copies. *Fewer calls, larger events, schema coupling.*
3. **Event sourcing:** the system of record *is* the sequence of events; current state is derived by replaying them.
4. **CQRS:** separate models for writes (commands) and reads (queries), often connected by events.

### Thin versus fat events

| | Thin ("notification") | Fat ("state transfer") |
|---|---|---|
| Payload | ID, type, timestamp | Full entity snapshot or rich delta |
| Consumers | Must call the source API for details | Self-sufficient |
| Ordering issues | Avoided: always fetch the latest | Must handle out-of-order versions |
| Source load | Callback traffic | None |
| Privacy | Minimal data in transit | More personal data copied around |
| Schema coupling | Low | High |

Many SaaS webhooks are thin (or include a partial object) precisely because the provider cannot know what each consumer needs, and because fetching the current state sidesteps ordering problems.

### Anatomy of a good event

```json
{
  "specversion": "1.0",
  "id": "01J9ZK8V6T3Q4M2N7XWJ5B8C1D",
  "source": "https://orders.acme.com",
  "type": "com.acme.order.shipped.v1",
  "subject": "orders/ORD-55821",
  "time": "2026-10-09T14:20:03Z",
  "datacontenttype": "application/json",
  "dataschema": "https://schemas.acme.com/order-shipped/v1.json",
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "data": {
    "order_id": "ORD-55821",
    "order_version": 7,
    "carrier": "DHL",
    "tracking_number": "JD014600006281234567",
    "shipped_at": "2026-10-09T14:19:51Z"
  }
}
```

This is a **CloudEvents 1.0** envelope (structured JSON mode). **CloudEvents** is a CNCF *graduated* specification (January 2024) for describing event metadata in a common way. It defines required attributes (`id`, `source`, `specversion`, `type`), optional ones (`subject`, `time`, `datacontenttype`, `dataschema`) and **bindings** for HTTP, Kafka, AMQP, MQTT, NATS and more. In *binary mode*, attributes travel as protocol headers (`ce-id`, `ce-type`…) and the body is just `data`. Azure Event Grid, Google Eventarc, Knative and many others support it natively. Adopting it costs little and helps routing, tooling and tracing.

Event-design rules:

- **Name events in the past tense** for facts that happened in the business domain: `OrderShipped`, not `UpdateOrder` or `OrderTableRowChanged`.
- **A unique event ID** (for de-duplication) and an **event time**.
- **The entity ID and a version or sequence** (for ordering).
- **Version the event type** (`.v1`) and evolve compatibly (Chapter 4).
- **Include a trace context** for observability.
- **Do not leak internal implementation:** database column names and internal enums become public contracts the day you publish them.
- **Minimise personal data,** especially in long-retention logs. Kafka topics with infinite retention and personal data make GDPR erasure very hard. Consider thin events, tokenisation or "crypto-shredding" (encrypt per subject and delete the key on erasure).

### Domain events versus integration events

Inside a service, **domain events** can be fine-grained and change freely. Events published *to other teams or systems* are **integration events**, public contracts that deserve stability, documentation and governance. Translate between the two at the boundary.

---

## 7.8 Describing asynchronous APIs: AsyncAPI

**AsyncAPI** is the OpenAPI equivalent for event-driven and message-based APIs. **AsyncAPI 3.0** (December 2023) reorganised the specification around reusable **channels** and **operations** (`send` / `receive`), and fixed the confusing publish/subscribe perspective of 2.x. It describes:

- **servers** (brokers, with protocol bindings for Kafka, AMQP, MQTT, WebSockets, HTTP, SNS/SQS and more);
- **channels** (topics and queues) and their addresses;
- **messages**, with payload schemas (JSON Schema, Avro, Protobuf) and headers;
- **operations** that an application sends or receives;
- **security schemes**.

A sample is in [`examples/asyncapi/order-events.yaml`](../examples/asyncapi/order-events.yaml). Tools generate documentation, code and validators from it. As of Arazzo 1.1 (May 2026), workflow descriptions can reference AsyncAPI operations alongside OpenAPI ones.

Event catalogues such as EventCatalog, the AsyncAPI Studio, Confluent Stream Catalog and the EventBridge schema registry help teams *discover* events, the async equivalent of a developer portal.

---

## 7.9 Webhooks

A **webhook** is an HTTP callback: when something happens, the provider `POST`s an event to a URL the consumer registered. Webhooks are the dominant push mechanism for SaaS (Stripe, GitHub, Shopify, Slack, Twilio, HubSpot and nearly every other SaaS platform).

### Consuming webhooks safely

```mermaid
sequenceDiagram
  participant P as Provider
  participant R as Receiver endpoint
  participant Q as Queue
  participant W as Worker
  P->>R: POST /webhooks/provider (signed event)
  R->>R: Verify signature + timestamp
  R->>Q: Enqueue raw event
  R-->>P: 2xx (fast, < a few seconds)
  Q->>W: Deliver
  W->>W: De-duplicate on event ID
  W->>P: (optional) GET current state of resource
  W->>W: Process; record event ID as done
```

1. **Verify authenticity.** Most providers sign the payload with **HMAC-SHA256** using a shared secret (Stripe's `Stripe-Signature`, GitHub's `X-Hub-Signature-256`, Shopify's `X-Shopify-Hmac-Sha256`). Others use asymmetric signatures, mTLS or OAuth. The **Standard Webhooks** specification (backed by Svix, Zapier, Twilio, ngrok and others) standardises `webhook-id`, `webhook-timestamp` and `webhook-signature` headers. Compute the HMAC over the **raw request body bytes**. Re-serialising parsed JSON changes the bytes and breaks verification. Use a **constant-time comparison**.
2. **Reject replays:** check that the signed timestamp is recent (for example within 5 minutes), and de-duplicate on the event ID.
3. **Acknowledge fast.** Providers time out quickly (often within 5–30 seconds) and retry. Persist or enqueue, return `2xx`, and process asynchronously.
4. **Be idempotent.** Providers deliver at-least-once; you *will* receive duplicates.
5. **Do not trust ordering.** Use versions, or fetch current state.
6. **Expect gaps.** Providers give up after their retry schedule (Stripe retries for up to 3 days in live mode; GitHub does not automatically redeliver failed deliveries, though you can redeliver them manually or through its API). Run **periodic reconciliation** against the provider's list API to catch missed events.
7. **Secure the endpoint:** HTTPS only; verify signatures before parsing; cap the body size; optionally allow-list provider IPs (when published); never expose internal error details in the response.
8. **Support secret rotation:** accept signatures from both old and new secrets during rotation.

A runnable, tested receiver is in [`examples/webhook-receiver/`](../examples/webhook-receiver/).

### Providing webhooks well

If your platform sends webhooks:

- Sign every payload, and include an event ID, a type, a timestamp and an API version.
- Retry with exponential backoff over hours to days; then disable the endpoint and notify the owner.
- Offer a **delivery log, manual redelivery and replay** in your UI or API.
- Let consumers subscribe to specific event types.
- Keep payloads modest; consider thin events plus fetch.
- **Defend against SSRF:** consumers give you URLs, so do not let them point your sender at your internal network (block private IP ranges, resolve and check DNS, use an egress proxy). Chapter 10.
- Document everything in your OpenAPI (`webhooks` object, OAS 3.1+) or AsyncAPI document.
- Consider standards: Standard Webhooks and CloudEvents.
- Managed webhook-sending services (Svix, Hookdeck, Convoy) exist if you would rather not build this.

### Webhooks versus polling versus streaming

| Mechanism | Latency | Efficiency | Reliability | Complexity |
|---|---|---|---|---|
| Polling (`updated_since`) | Interval-bound | Wasteful when little changes | High (consumer-controlled) | Low |
| Webhooks | Seconds | High | Medium (missed events possible) | Medium |
| Webhooks + periodic reconciliation | Seconds | High | **High** | Medium |
| Streaming (Kafka, SSE, WebSockets, gRPC streams) | Sub-second | High | High (with offsets/replay) | Higher |

---

## 7.10 Event-driven architecture patterns

### Event sourcing

State is stored as an append-only sequence of events (`OrderPlaced`, `LineAdded`, `OrderShipped`), and current state is a fold over them. Benefits: complete audit history, temporal queries and easy projections. Costs: complexity, schema evolution of historical events, and snapshots for performance. It is used in some financial, logistics and collaborative systems. It is not a default choice.

### CQRS

Separate the write model from one or more read models (projections) updated from events. This is common in integration as a **materialised view** pattern: consume events from several systems to build a local read-optimised store (for example, a "customer 360" view) instead of calling five APIs at query time.

### The event mesh and event gateway

Large organisations connect brokers across regions, clouds and on-premises sites into an **event mesh** (Solace, Kafka with MirrorMaker 2 or Cluster Linking, multi-broker routing), with **event gateways** that apply API-management-style controls (authentication, quotas, policy) to event streams. Expect API management and event management to converge further (Chapter 11).

### Stream processing

Engines such as **Apache Flink**, **Kafka Streams**, **ksqlDB**, Spark Structured Streaming and cloud equivalents (Amazon Managed Service for Apache Flink, Google Dataflow / Apache Beam, Azure Stream Analytics) filter, join, aggregate and enrich events in flight: fraud detection, real-time inventory, enrichment before delivery to SaaS. Chapter 9 covers the data side.

---

## 7.11 Common mistakes

| Mistake | Consequence | Remedy |
|---|---|---|
| Assuming exactly-once | Duplicate side effects (double emails, double charges) | Idempotent consumers |
| Visibility timeout shorter than processing time | Concurrent double processing | Size it properly; extend while working |
| Poison message blocks a partition | Entire partition stalls | Retry topic and DLQ; skip and record |
| Unbounded retries | Hot loops, cost spikes | Max attempts with backoff, then DLQ |
| Nobody watches the DLQ | Silent data loss | Alerts on DLQ depth; a redrive runbook |
| Events as database row dumps | Internal schema becomes a public contract | Design integration events deliberately |
| Huge payloads | Broker limits, slow consumers | Claim check pattern |
| Too few Kafka partitions | Cannot scale consumers | Plan for peak; consider share groups |
| Personal data in infinitely retained topics | Privacy and compliance exposure | Minimise, tokenise, set retention |
| Webhook handler does all work inline | Provider timeouts produce retries, which produce duplicates | Enqueue and acknowledge fast |

---

## Summary

- Queues distribute work, topics fan out events, and logs retain and replay streams. Pick the broker by model, volume and environment.
- Design for **at-least-once delivery with idempotent consumers**; treat "exactly-once" claims carefully.
- Ordering holds only per key or partition, and even that is fragile. Design consumers to tolerate disorder with versions or fetch-latest.
- Use CloudEvents for envelopes and AsyncAPI 3 for contracts. Distinguish internal domain events from public integration events.
- Consume webhooks by verifying signatures over the raw body, acknowledging fast, de-duplicating, and reconciling periodically. Provide webhooks with signing, retries, replay and SSRF protection.

## Exercises

See [`exercises/07-async-and-events.md`](../exercises/07-async-and-events.md).

## Further reading

- Martin Fowler, "What do you mean by 'Event-Driven'?" (2017).
- Neha Narkhede, Gwen Shapira, Todd Palino et al., *Kafka: The Definitive Guide*, 2nd edition (O'Reilly, 2021).
- Adam Bellemare, *Building Event-Driven Microservices*, 2nd edition (O'Reilly, 2025).
- AsyncAPI 3.0 specification (asyncapi.com); CloudEvents specification (cloudevents.io); Standard Webhooks (standardwebhooks.com).
- KIP-932: Queues for Kafka.
