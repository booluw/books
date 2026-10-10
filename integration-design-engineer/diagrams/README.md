# Diagrams

Diagrams are written in [Mermaid](https://mermaid.js.org/), which renders on GitHub, GitLab and most Markdown tools. They are code, so they can be reviewed and diffed. Every diagram here has been checked with the Mermaid CLI.

| Diagram | Chapter |
|---|---|
| [History timeline](history-timeline.md) | 2 |
| [Journey of an HTTPS request](request-journey.md) | 3 |
| [Four integration styles](integration-styles.md) | 5 |
| [Order flow in EIP terms](order-flow-eip.md) | 5 |
| [Consuming webhooks safely](webhook-consumption.md) | 7 |
| [Idempotency key sequence](idempotency-key-sequence.md) | 8 |
| [Circuit breaker states](circuit-breaker.md) | 8 |
| [Transactional outbox](transactional-outbox.md) | 8 |
| [Saga with compensations](saga.md) | 8 |
| [OAuth flows](oauth-flows.md) | 10 |
| [Platform landscape](platform-landscape.md) | 11 |
| [Design process](design-process.md) | 14 |
| [Context diagram example](context-diagram-example.md) | 14 |
| [Sequence diagram with failure path](sequence-diagram-example.md) | 14 |
| [API-led connectivity](api-led-connectivity.md) | 17 |
| [Reference architecture](reference-architecture.md) | 17 |
| [MCP architecture](mcp-architecture.md) | 18 |
| [Learning roadmap](learning-roadmap.md) | 19 |

To render a diagram to SVG locally:

```bash
npx -p @mermaid-js/mermaid-cli mmdc -i diagram.mmd -o diagram.svg
```
