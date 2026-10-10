# Order events: AsyncAPI 3.1 example (Chapter 7)

[`order-events.yaml`](order-events.yaml) describes two Kafka topics (`sales.order.placed.v1`, `sales.order.shipped.v1`):

- A **CloudEvents 1.0** envelope in Kafka *binary* mode (`ce_*` headers), with W3C `traceparent`.
- The **message key** (`order_id`), so per-order ordering holds within a partition.
- A documented **at-least-once** contract: de-duplicate on `ce_id`, discard stale `order_version`s.
- The schema-compatibility policy.
- mTLS security.

```bash
npx @asyncapi/cli validate order-events.yaml
```
