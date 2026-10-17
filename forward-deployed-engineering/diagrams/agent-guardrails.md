# Agent tool call with guardrails

Relevant chapters: [12](../chapters/12-ai-deployment.md), [14](../chapters/14-security-and-restricted-environments.md). Example: [`agent-guardrails`](../examples/agent-guardrails/).

```mermaid
sequenceDiagram
  participant U as User
  participant A as Agent (model)
  participant G as Guard
  participant H as Human approver
  participant T as Tool / system
  participant L as Audit log
  U->>A: Request
  A->>G: Tool call (name, arguments)
  G->>G: Allow-list, validation, budget checks
  alt Read action
    G->>T: Execute with user's permissions
  else Irreversible or above threshold
    G->>H: Approval request with evidence
    H-->>G: Approve or reject
    G->>T: Execute if approved
  end
  T-->>G: Result
  G->>G: Screen output for injection
  G->>L: Append hash-chained record
  G-->>A: Result (or refusal)
  A-->>U: Response
```
