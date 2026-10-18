# Chain replication

Source: [Chapter 6](../chapters/06-replication.md). Relevant chapters: 6.

```mermaid
flowchart LR
  W["Write"] --> H["Head"] --> M["Middle"] --> T["Tail"]
  T -- "ack" --> W
  R["Read"] --> T
```
