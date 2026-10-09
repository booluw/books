# Exercises: Chapter 18, AI and Integration

## Questions

1. Rewrite this tool description so a model can use it well: `{"name": "query", "description": "Runs a query", "inputSchema": {"type": "object", "properties": {"q": {"type": "string"}}}}`.
2. An agent reads customer emails, has access to the CRM, and can send emails. Apply the lethal-trifecta test and propose two design changes.
3. Run `examples/mcp-tool-server`. Add a `cancel_order` tool that is only allowed for orders in `processing` status, is idempotent, and requires a `confirm: true` argument. Write tests.
4. Explain why an MCP server must not pass the client's access token through to downstream APIs.
5. What changed in the MCP 2026-07-28 revision that makes servers easier to scale, and why?
6. List five ways you would use AI tools to speed up an ESB migration, and the verification step for each.

## Solutions (outline)

1. For example: name `search_orders`, description "Search the signed-in customer's orders by status and date range. Read-only. Returns at most 20 orders with id, date, status and total.", schema with `status` enum, `from`/`to` dates and a `limit` maximum, with `additionalProperties: false`.
2. It has all three legs: private data, untrusted content and external communication. Changes: remove free-form email sending (allow only templated replies to the original sender after human approval); restrict CRM access to the sender's own record; add egress allow-lists and monitoring.
3. Hands-on.
4. The token's audience is the MCP server, not the downstream API (audience confusion). Passthrough lets the downstream API accept tokens it should not, bypasses the MCP server's own authorisation and audit, and enables confused-deputy attacks. The server should use its own credentials or token exchange with correct audiences and scopes.
5. The initialize handshake and protocol-level sessions were removed (a stateless core), so any instance can serve any request behind a plain load balancer, without sticky sessions or shared session state; routing headers also let gateways route without parsing bodies.
6. Inventory extraction from configuration exports (verify against runtime logs); explaining XSLT or maps (verify with golden-file tests); generating target-platform mappings (verify with tests and business sign-off); drafting runbooks and docs (review by on-call engineers); generating test payloads (verify with production samples).
