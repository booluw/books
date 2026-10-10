# The four integration styles

File transfer, shared database, remote procedure invocation and messaging (Hohpe and Woolf).

Used in [Chapter 5](../chapters/05-integration-styles-and-patterns.md).

```mermaid
flowchart LR
  subgraph FT["1. File Transfer"]
    A1["App A"] -- writes file --> F[(File / SFTP)]
    F -- reads file --> B1["App B"]
  end
  subgraph SD["2. Shared Database"]
    A2["App A"] --> DB[(Shared DB)]
    B2["App B"] --> DB
  end
  subgraph RPC["3. Remote Procedure Invocation"]
    A3["App A"] -- request --> B3["App B"]
    B3 -- response --> A3
  end
  subgraph MSG["4. Messaging"]
    A4["App A"] -- message --> Q[[Channel]]
    Q -- message --> B4["App B"]
  end
```
