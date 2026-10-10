# Exercises: Chapter 10, Security

## Questions

1. Which OAuth grant fits each case? (a) Nightly job syncing ERP to a data warehouse API. (b) A SaaS product reading a customer's Google Calendar. (c) A CLI tool on a developer laptop. (d) Your API calling a downstream API on behalf of the original user with narrower rights. (e) Salesforce server-to-server integration without a shared secret.
2. List six checks an API must perform when validating a JWT access token.
3. Your webhook-sending feature lets customers enter any URL. Describe how an attacker could abuse it and four defences.
4. Map each OWASP API Security Top 10 (2023) item to one control you would apply in an integration you are building.
5. An iPaaS flow logs full request and response bodies, including customer addresses, and retains execution history for 365 days. What are the risks, and what do you change?
6. Threat-model the webhook receiver in `examples/webhook-receiver` using STRIDE.
7. A partner's mTLS client certificate expires in 10 days and they will not rotate until it expires. What do you do?

## Solutions

1. (a) Client credentials. (b) Authorization code + PKCE. (c) Device authorization (or auth code + PKCE with a loopback redirect). (d) Token exchange (RFC 8693). (e) JWT bearer assertion flow (or client credentials with `private_key_jwt`).
2. Signature (with a key from the issuer's JWKS, chosen by `kid`, with an allowed algorithm and never `none`); `iss`; `aud`; `exp` (and `nbf`) with small leeway; required scopes or claims; token type (access, not ID token); optionally revocation or sender constraint (DPoP or mTLS binding).
3. SSRF: point the webhook at `http://169.254.169.254/` (cloud metadata) or internal admin services, and read responses or error messages. Defences: resolve and block private, loopback and link-local ranges (including after redirects and DNS rebinding); egress proxy with policy; disable redirects; do not echo response bodies to the customer; IMDSv2.
4. Example: API1 tenant and object checks on every read; API2 JWT validation and token endpoint protection; API3 response field allow-lists and writable-field allow-lists; API4 rate limits and page-size caps; API5 separate admin scopes; API6 business-flow limits; API7 SSRF egress controls; API8 hardened gateway defaults; API9 catalogue with versions and owners; API10 schema validation of partner responses.
5. Risks: personal data spread across a long-lived, widely accessible store; breach exposure; GDPR minimisation and retention violations; erasure requests that cannot be honoured. Change: log metadata and IDs only, mask payloads, restrict access, shorten retention (e.g. 14–30 days), and keep a separate, access-controlled message store only where replay requires it.
6. Spoofing: forged webhooks → HMAC verification. Tampering: modified body → HMAC over the raw body. Repudiation: provider denies sending → log webhook-id, timestamp and signature outcome. Information disclosure: error details or logs leak → generic 401 and redacted logs. Denial of service: floods and large bodies → size cap, rate limiting, queue. Elevation of privilege: secret leak lets attackers inject events → secret rotation, storage in a secrets manager, and downstream validation (fetch state from the provider).
7. Agree a rotation window in writing (escalate if needed); prepare to trust both old and new certificates (or both CAs) during overlap; set alerts at 7 and 1 days; plan a manual test immediately after their rotation; record the incident risk and the partner's decision; add certificate-expiry monitoring to the interface agreement.
