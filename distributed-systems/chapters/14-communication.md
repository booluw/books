# Chapter 14. Communication: RPC, Messaging, Logs and Delivery Guarantees

> "Exactly-once delivery is impossible. Exactly-once *processing* is engineering."

## What you will learn

- The main ways services communicate: request/response RPC, message queues, publish/subscribe and replicated logs.
- How RPC frameworks work (gRPC, REST, Thrift), and the "remote call looks local" trap.
- Encoding and schema evolution: how to change message formats without breaking running systems.
- Delivery semantics: at-most-once, at-least-once and "exactly-once", stated precisely.
- How to achieve effectively-once processing with idempotency, deduplication and transactional offsets.
- Ordering guarantees, backpressure and flow control.
- Change data capture and event sourcing as communication patterns.

---

## 14.1 Styles of communication

| Style | Shape | Coupling | Examples |
|---|---|---|---|
| **Request/response (RPC)** | Caller waits for a reply | Temporal: both must be up | gRPC, REST over HTTP, Thrift |
| **Message queue** | Producer sends; one consumer processes each message | Decoupled in time | RabbitMQ, Amazon SQS, ActiveMQ |
| **Publish/subscribe** | Producer publishes; every subscriber gets a copy | Decoupled in time and identity | Google Pub/Sub, SNS, NATS |
| **Replicated log (stream)** | Producers append to an ordered, durable log; consumers read at their own pace from an offset | Decoupled; replayable | Apache Kafka, Amazon Kinesis, Apache Pulsar, Redpanda |

The choice shapes failure behaviour. With RPC, if the callee is down, the caller fails (or retries). With messaging, the producer succeeds as long as the broker is up, and consumers catch up later, so failures are absorbed as **lag** rather than errors.

## 14.2 Remote procedure calls

**RPC** makes calling a function on another machine look like calling a local function: a client **stub** serialises the arguments, sends them, waits, and deserialises the result. Modern frameworks:

- **gRPC** (Google, open-sourced 2015): HTTP/2 transport, Protocol Buffers encoding, generated stubs in many languages, streaming in both directions, deadlines and cancellation built in.
- **REST/JSON over HTTP:** not RPC in the strict sense, but used that way by most internal APIs; simple and universal, with an OpenAPI description for tooling (the companion book's [`openapi` example](../../integration-design-engineer/examples/openapi/)).
- **Apache Thrift**, **Cap'n Proto**, **Connect** and others.

### Why "it looks local" is a trap

Waldo, Wyant, Wollrath and Kendall's "A Note on Distributed Computing" (Sun Microsystems, 1994) argued that hiding the network behind a local-looking call is dangerous, because remote calls differ fundamentally:

| Local call | Remote call |
|---|---|
| Nanoseconds | Milliseconds, with a long tail |
| Fails only if the program fails | May fail, time out, or succeed without telling you (Chapter 2 §2.1) |
| Arguments passed by reference | Arguments copied and encoded |
| Retrying is unnecessary | Retrying may duplicate side effects |

Good RPC frameworks make the remote nature visible: explicit deadlines, error codes for "unavailable" and "deadline exceeded", and no pretence that the call can't fail. Every RPC needs a timeout, a retry policy (only for idempotent calls, with backoff, Chapter 17) and a plan for partial failure.

## 14.3 Encoding and schema evolution

Services are deployed independently, so at any moment, old and new versions of a sender and receiver run side by side. Message formats must support:

- **Backward compatibility:** new code can read data written by old code.
- **Forward compatibility:** old code can read data written by new code (and ignore what it doesn't understand).

| Format | Schema | Evolution mechanism |
|---|---|---|
| **JSON** | Optional (JSON Schema) | Convention: add optional fields; never change meaning |
| **Protocol Buffers** | Required (`.proto`) | Fields identified by **number**; unknown fields are preserved and skipped; never reuse a number |
| **Apache Avro** | Required; writer's and reader's schemas both used at read time | Schema resolution matches fields by name, with defaults |
| **Thrift** | Required | Field IDs, like Protocol Buffers |

Rules that keep systems running:

1. Add fields as optional, with defaults.
2. Never change a field's type or meaning; add a new field instead.
3. Never reuse a field number or name for something else.
4. Remove fields only after no reader depends on them, and reserve their numbers.
5. Use a **schema registry** (for Avro or Protobuf on Kafka, for example) that checks compatibility before a new schema is accepted.

## 14.4 Message brokers and queues

A **message broker** accepts messages from producers, stores them, and delivers them to consumers. In a **work queue**, each message goes to one consumer among many, which processes it and **acknowledges** it; unacknowledged messages are redelivered (after a visibility timeout in SQS, or when the consumer's connection drops in RabbitMQ).

Two design consequences:

- **Redelivery means duplicates.** A consumer that processes a message and crashes before acknowledging will see it again. Consumers must be idempotent.
- **Redelivery reorders.** With several consumers, or with redelivery, messages are processed out of order. If order matters, use ordered queues (SQS FIFO with message group IDs, or partitions in a log).

Messages that fail repeatedly are moved to a **dead-letter queue** for inspection rather than blocking the queue forever.

## 14.5 Replicated logs

A **log-based** system like Kafka stores messages in an append-only, ordered, durable log, divided into **partitions** (Chapter 7). Each message in a partition has an **offset**. Consumers track their own position (offset) and can re-read from any point. Kafka's design (Kreps, Narkhede and Rao, NetDB 2011) and Jay Kreps's essay "The Log: What every software engineer should know about real-time data's unifying abstraction" (2013) popularised the log as the backbone connecting systems.

Properties:

- **Order within a partition**, not across partitions. Choose the partition key so that messages that must be ordered relative to each other (all events for one order, one account) share a partition.
- **Replayability:** a new consumer can process history; a buggy consumer can be fixed and re-run from an earlier offset.
- **Consumer groups:** partitions are divided among consumers in a group; the maximum useful parallelism is the number of partitions.
- **Retention** by time or size, or **compaction** (keep only the latest message for each key), which turns a topic into a changelog of the latest state.

Chapter 21 covers Kafka's replication and transactions in detail.

## 14.6 Delivery semantics

What guarantees can a messaging system give about how many times a message is delivered or processed?

| Guarantee | Meaning | How |
|---|---|---|
| **At-most-once** | Each message is processed zero or one times; may be lost | Send once, never retry; or acknowledge before processing |
| **At-least-once** | Each message is processed one or more times; never lost | Retry until acknowledged; acknowledge after processing |
| **Exactly-once** | Each message's **effect** happens exactly once | At-least-once delivery **plus** idempotent or transactional processing |

### ◆ Formal: why exactly-once *delivery* is impossible

Consider a sender and a receiver over a channel that may lose messages, where the receiver performs some external side effect on receipt. For the sender to ensure delivery, it must retry until it gets an acknowledgement. But the acknowledgement can be lost (Two Generals, Chapter 4 §4.2), so the sender can't distinguish "message lost" from "acknowledgement lost". If it retries, the receiver may perform the effect twice; if it doesn't, the message may be lost. No protocol makes the *network* deliver exactly once.

What's achievable is **exactly-once processing** (or "effectively once"): the **observable effect** of each message happens once, even though the message may be delivered several times. That requires the receiver to recognise duplicates, which requires state that is updated **atomically** with the effect.

### Techniques for effectively-once processing

1. **Idempotent operations.** "Set balance to £50" is idempotent; "add £10" isn't. Where possible, design messages as idempotent state assignments or use operations that are naturally idempotent (set insert, max).
2. **Deduplication by message ID.** Each message carries a unique ID. The consumer records processed IDs **in the same transaction** as the effect; on redelivery, it sees the ID and skips. The deduplication store must cover the redelivery window.
3. **Transactional offsets.** Store the consumer's position (offset) in the same database transaction as the effect. On restart, resume from the stored offset; any message after it hasn't had its effect yet.
4. **Broker transactions.** Kafka's **idempotent producer** (deduplicating retries by producer ID and sequence number) and **transactions** (atomically writing output messages and committing input offsets) give exactly-once semantics for read-process-write pipelines *within Kafka*. Effects outside Kafka (an email, a payment API call) still need idempotency on that side.
5. **The outbox pattern** (Chapter 9 §9.8) for publishing events atomically with database changes.

The general principle, from Pat Helland's "Idempotence Is Not a Medical Condition" (2012) and Tyler Treat's essays: **exactly-once is a property of the end-to-end system, not of a component.** Saltzer, Reed and Clark's **end-to-end argument** (1984) makes the same point in general: a guarantee like "processed exactly once" can only be fully implemented with knowledge held at the endpoints; lower layers can only help.

## 14.7 Ordering guarantees

| Guarantee | Meaning | Mechanism |
|---|---|---|
| **None** | Any order | Plain queues with multiple consumers |
| **FIFO per sender** | Messages from one sender arrive in send order | Sequence numbers; TCP per connection |
| **Per key / per partition** | Messages with the same key are ordered | Partitioned logs |
| **Causal** | If a message was sent after the sender received another, every receiver sees them in that order | Vector clocks or dependency tracking (Chapter 3) |
| **Total order** | All receivers see all messages in the same order | A single log, or consensus (**atomic broadcast**, which is equivalent to consensus) |

Total order broadcast is **equivalent to consensus**: given one, you can build the other. That's why a globally ordered log is as expensive as a consensus system, and why scalable systems order per partition instead.

## 14.8 Flow control and backpressure

If producers send faster than consumers can process, something must give. **Backpressure** propagates "slow down" from consumers to producers:

- TCP's flow control does it per connection.
- gRPC and HTTP/2 have per-stream flow-control windows.
- Reactive Streams and similar libraries make demand explicit ("send me 10 more").
- Queues absorb bursts, but a queue that grows without bound only delays the failure and adds latency. Bound queues, and decide what happens when they're full: block the producer, reject (load shedding), or drop the oldest.

Chapter 17 treats overload and backpressure in depth.

## 14.9 Change data capture and event sourcing

Two patterns turn data changes into messages:

- **Change data capture (CDC)** reads a database's replication log (Chapter 6 §6.2) and publishes every committed change as an event. Debezium is a widely used open-source CDC platform. CDC lets other systems (search indexes, caches, analytics) stay in sync without dual writes, because the database's own commit order is the source of truth.
- **Event sourcing** stores the sequence of business events ("ItemAddedToCart", "OrderPlaced") as the primary record, and derives current state by replaying them. It gives a complete audit trail and the ability to rebuild state with new logic, at the cost of more complex queries (usually served from derived read models, an approach known as **CQRS**, Command Query Responsibility Segregation) and careful schema evolution of old events.

Both rely on the log as the system of record: the idea in Kreps's essay that "the log is the database".

---

## Summary

- Services communicate by RPC (temporally coupled), queues and pub/sub (decoupled), or replicated logs (decoupled and replayable).
- Remote calls aren't local calls: give every one a deadline, retry only idempotent calls, and plan for "succeeded but I don't know".
- Evolve schemas compatibly: optional fields, stable field numbers, no reuse, registry checks.
- Exactly-once delivery is impossible over a lossy network (Two Generals); exactly-once processing is achieved with at-least-once delivery plus idempotency, deduplication or transactional offsets, end to end.
- Order only what must be ordered, usually per key or partition; total order broadcast is equivalent to consensus.
- Bound queues and propagate backpressure. CDC and event sourcing use the log as the source of truth.

## Exercises

See [`exercises/14-communication.md`](../exercises/14-communication.md).

## Further reading

- Jim Waldo, Geoff Wyant, Ann Wollrath and Sam Kendall, "A Note on Distributed Computing", Sun Microsystems Laboratories (1994).
- Jay Kreps, "The Log: What every software engineer should know about real-time data's unifying abstraction" (LinkedIn Engineering, 2013).
- Jay Kreps, Neha Narkhede and Jun Rao, "Kafka: a Distributed Messaging System for Log Processing", NetDB (2011).
- J. H. Saltzer, D. P. Reed and D. D. Clark, "End-to-End Arguments in System Design", *ACM TOCS* (1984).
- Pat Helland, "Idempotence Is Not a Medical Condition", *ACM Queue* (2012).
- Martin Kleppmann, *Making Sense of Stream Processing* (O'Reilly, 2016).
