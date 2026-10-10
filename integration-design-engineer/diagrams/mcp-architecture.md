# MCP architecture for an enterprise

Hosts contain MCP clients; each client talks to one MCP server; servers call systems of record with their own credentials (no token passthrough).

Used in [Chapter 18](../chapters/18-ai-and-the-future.md).

```mermaid
flowchart LR
  subgraph Host["AI host application"]
    M["Model"]
    C1["MCP client"]
    C2["MCP client"]
  end
  User(["User"]) --> Host
  M <--> C1
  M <--> C2
  C1 -- "JSON-RPC over Streamable HTTP<br/>OAuth token for user" --> GW["MCP / AI gateway<br/>(authn, policy, quotas, audit)"]
  C2 -- "stdio (local tool)" --> LOCAL["Local MCP server"]
  GW --> S1["Orders MCP server"]
  GW --> S2["Tickets MCP server"]
  S1 -- "own credentials,<br/>per-user authorisation" --> ERP[("ERP / e-commerce")]
  S2 --> HD[("Help desk")]
  IdP["Identity provider /<br/>authorisation server"] -. "issues tokens" .-> C1
  S1 -. "validates tokens" .-> IdP
```
