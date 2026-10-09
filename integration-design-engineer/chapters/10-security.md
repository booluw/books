# Chapter 10. Security, Identity and Compliance

> "Integrations are the plumbing of the enterprise, and attackers love plumbing: it reaches every room."

## What you will learn

- Why integrations are a high-value attack surface.
- Authentication mechanisms for machine-to-machine traffic: API keys, Basic auth, OAuth 2.0 and 2.1 grants, OpenID Connect, JWTs, mTLS, HMAC signatures, SAML and workload identity federation.
- Authorisation: scopes, least privilege, service accounts and multi-tenant isolation.
- Secrets management and rotation.
- The OWASP API Security Top 10 (2023) applied to integrations, including SSRF and unsafe consumption of APIs.
- Data protection in transit and at rest, data minimisation and logging hygiene.
- Compliance regimes you will meet: GDPR, HIPAA, PCI DSS 4.0.1, SOC 2, ISO 27001, DORA, NIS2 and data-residency rules.
- Threat modelling an integration.

---

## 10.1 Why integrations are a prime target

Integrations hold **powerful, long-lived credentials** to many systems at once: an iPaaS might have admin tokens for the ERP, CRM, HR system and bank. They move **sensitive data** in bulk. They are often built quickly, owned by small teams, and run unattended. Recent years have seen repeated supply-chain-style breaches in which attackers stole OAuth tokens or API keys belonging to an *integration* (a CI service, a SaaS-to-SaaS connector, a support-chat plugin) and used them to pull data from many customers' systems. The lesson: **an integration's credentials are as valuable as the union of everything they can reach.**

Core principles:

1. **Least privilege:** each integration gets only the scopes, objects and fields it needs.
2. **Separate identities:** one service identity per integration (never a shared "integration admin", never a person's account).
3. **Short-lived credentials** wherever possible; rotate the long-lived ones.
4. **Defence in depth:** network controls *and* authentication *and* authorisation *and* monitoring.
5. **Minimise data:** move only the fields needed; mask or tokenise sensitive ones.
6. **Assume breach:** log and monitor integration identities' behaviour so that misuse is detected.

---

## 10.2 Authentication mechanisms

### API keys

A static secret string sent in a header (`X-API-Key: …` or `Authorization: Bearer sk_live_…`).

- **Pros:** simple.
- **Cons:** long-lived, often over-privileged, easily leaked (logs, repositories, screenshots), and identify an application, not a user.
- **Good practice:** send them in headers (never in URLs, which end up in logs); use restricted or scoped keys where the provider offers them (Stripe restricted keys, for instance); rotate them; store them in a secrets manager; enable secret scanning in repositories (GitHub push protection, GitGuardian, trufflehog).

### HTTP Basic authentication

`Authorization: Basic base64(username:password)`. Acceptable only over TLS, with a dedicated service account and a strong, rotated password. Common with legacy and on-premises APIs and SOAP services.

### OAuth 2.0 and OAuth 2.1

**OAuth 2.0** (RFC 6749, 2012) is a framework for **delegated authorisation**: a client obtains an **access token** from an **authorisation server** to call a **resource server** (API), within a limited **scope**. **OAuth 2.1** consolidates a decade of security best practice (from RFC 9700, *OAuth 2.0 Security Best Current Practice*, January 2025) into one document. As of October 2026 it is still an IETF Internet-Draft (draft-ietf-oauth-v2-1), but most major identity providers already implement its rules:

- **PKCE** (Proof Key for Code Exchange, RFC 7636) is required for *all* authorisation-code clients.
- The **implicit grant** and the **resource owner password credentials grant** are removed.
- Redirect URIs must match exactly.
- Refresh tokens for public clients must be sender-constrained or rotated.
- Bearer tokens must not be sent in query strings.

The grants (flows) an integration engineer uses:

| Grant | Who is acting | Use in integrations |
|---|---|---|
| **Client credentials** | The application itself (no user) | Server-to-server integrations: your middleware calling an API as itself. The most common integration flow. |
| **Authorization code + PKCE** | A user, delegating to an app | SaaS product integrations ("Connect your Salesforce account"): the customer's admin logs in and consents; your app receives tokens to act on their behalf. Also AI agents acting for users (Chapter 18). |
| **Refresh token** | Continuation of a user grant | Obtain new access tokens without user interaction. Store refresh tokens encrypted; handle rotation (each use may return a new refresh token and invalidate the old one). |
| **JWT bearer assertion** (RFC 7523) | An app proving identity with a signed JWT | Salesforce JWT bearer flow, Google service accounts: no shared secret, the app signs with its private key. |
| **Device authorisation** (RFC 8628) | A user on a device with limited input | CLIs, TVs and IoT devices. |
| **Token exchange** (RFC 8693) | A service exchanging one token for another | Delegation chains: an API calls a downstream API on behalf of the original user, with a narrower token. Increasingly used for agents. |

A client-credentials request looks like:

```http
POST /oauth2/token HTTP/1.1
Host: auth.partner.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic base64(client_id:client_secret)

grant_type=client_credentials&scope=orders.read%20orders.write
```

```json
{"access_token": "eyJhbGciOiJSUzI1NiIs...", "token_type": "Bearer",
 "expires_in": 3600, "scope": "orders.read orders.write"}
```

**Token handling in integrations:**

- **Cache access tokens** until shortly before expiry. Fetching a new token per request is slow and may hit the token endpoint's rate limits.
- **Refresh proactively** (for example at 80% of lifetime) and handle a `401` by refreshing once.
- **Serialise refreshes** when many workers share a token, so you do not trigger refresh-token rotation races, where two workers refresh at once and one gets an invalidated token.
- **Store tokens encrypted** (per tenant in product integrations), and treat refresh tokens as passwords.
- **Handle revocation:** users and admins revoke grants; your integration must detect `invalid_grant` and prompt for reconnection, rather than retrying forever.

**Stronger client authentication** than shared secrets: `private_key_jwt` (the client signs an assertion), mTLS client authentication (RFC 8705), and **sender-constrained tokens** (mTLS-bound tokens, or **DPoP**, RFC 9449, which binds a token to a key the client holds, so a stolen token is useless without the key). Open banking (FAPI 2.0) requires these.

Other useful OAuth extensions: **Pushed Authorization Requests (PAR)**, RFC 9126; **Rich Authorization Requests (RAR)**, RFC 9396, for fine-grained permissions such as "pay £50 to account X"; **Authorization Server Metadata** (RFC 8414) for discovery; **Protected Resource Metadata** (RFC 9728, 2025), which lets an API advertise which authorisation server protects it (MCP uses it, Chapter 18); and **Dynamic Client Registration** (RFC 7591).

### OpenID Connect (OIDC)

**OIDC** is an identity layer on top of OAuth 2.0. It adds an **ID token** (a JWT describing the authenticated *user*), a UserInfo endpoint and discovery (`/.well-known/openid-configuration`). OAuth is about *authorisation* (what the app may do); OIDC is about *authentication* (who the user is). Integration engineers meet OIDC in SSO, in user-context integrations, and in **workload identity federation**.

### JSON Web Tokens (JWT)

A **JWT** (RFC 7519) is a signed (JWS) or encrypted (JWE) token: `header.payload.signature`, each part base64url-encoded. Claims include `iss` (issuer), `sub` (subject), `aud` (audience), `exp` (expiry), `iat` (issued at), `scope` and custom claims.

When you *validate* JWTs (as an API provider):

- Verify the **signature** with the issuer's published keys (JWKS endpoint), selecting the key by `kid`. **Reject `alg: none`**, and do not let the token choose between symmetric and asymmetric algorithms (algorithm-confusion attacks).
- Check `iss`, `aud`, `exp` and `nbf`, with small clock-skew leeway.
- Check scopes and claims for authorisation.
- Cache JWKS but refresh on an unknown `kid` (keys rotate).

JWTs are **readable by anyone** (only signed, not encrypted, by default). Never put secrets or unnecessary personal data in them.

### Mutual TLS (mTLS)

Covered in Chapter 3. As authentication, mTLS proves that the client holds a private key matching a certificate the server trusts. It is strong and transport-level, common in B2B, banking and service meshes. The operational burden is certificate lifecycle management.

### HMAC request signing

The client signs the request (method, path, timestamp, body hash) with a shared secret, and the server recomputes and compares. Examples include AWS Signature Version 4 (all AWS APIs) and webhook signatures (Chapter 7). HMAC protects integrity as well as authenticity, and with timestamps it prevents replay. **HTTP Message Signatures** (RFC 9421, 2024) standardises signing of HTTP messages.

### SAML

**SAML 2.0** is an XML-based federation standard (2005) mostly used for browser single sign-on in enterprises. Integration engineers meet it when configuring SSO for SaaS apps, and occasionally in SAML bearer assertion grants for APIs (some SAP and older enterprise systems).

### SCIM: identity provisioning as integration

**SCIM 2.0** (RFC 7643/7644) is a REST API standard for provisioning users and groups from an identity provider (Okta, Microsoft Entra ID, Google Workspace) into SaaS applications. "Hire to retire" automation, where HR creates an employee, the identity provider creates accounts in thirty apps, and termination removes them, is one of the most common and security-critical integrations in any company.

### Workload identity federation (secretless authentication)

Instead of storing a long-lived secret for a cloud provider, a workload presents a token from *its own* platform (a Kubernetes service-account token, a GitHub Actions OIDC token, an AWS role) and exchanges it for short-lived credentials in another platform. AWS IAM Roles Anywhere and OIDC federation, Azure workload identity federation and Google Workload Identity Federation all support this. **Prefer secretless authentication wherever both sides support it.** There is no secret to leak or rotate.

### Summary table

| Mechanism | Identity type | Strength | Operational cost | Typical use |
|---|---|---|---|---|
| API key | App | Low–medium | Low | Simple SaaS APIs |
| Basic auth | Service account | Low–medium | Low | Legacy, on-premises |
| OAuth client credentials (secret) | App | Medium | Medium | Server-to-server |
| OAuth client credentials (`private_key_jwt` / mTLS) | App | High | Medium–high | Finance, high-security |
| OAuth auth code + PKCE | User-delegated | High | Medium | Product integrations, agents |
| mTLS | App/host | High | High (certificates) | B2B, banking, mesh |
| HMAC signing | App | High (integrity + replay protection) | Medium | AWS, webhooks |
| Workload identity federation | Workload | High | Low once set up | Cloud-to-cloud, CI/CD |

---

## 10.3 Authorisation

Authentication proves *who*; authorisation decides *what they may do*.

- **Scopes:** request the narrowest scopes possible (`orders.read`, not `full_access`). As a provider, design granular scopes around resources and actions.
- **Integration users and permission sets:** in Salesforce, NetSuite, SAP, Workday and similar systems, create a dedicated integration user with a role or permission set granting only the required objects, fields and operations. Salesforce provides a special "Salesforce Integration" user licence and API-only users for this. Restrict login IP ranges where possible.
- **Object- and property-level authorisation** (as a provider): check that the caller may access *this specific record* (not just this endpoint) and *these specific fields*. These are OWASP API1 and API3, the most common API vulnerabilities.
- **Multi-tenant isolation** (product integrations): every token, cache entry, queue message and log line must be scoped to a tenant, and code paths must be impossible to cross. Test tenant isolation explicitly.
- **Policy engines:** OPA (Open Policy Agent), Cedar (AWS Verified Permissions) and OpenFGA (relationship-based, after Google's Zanzibar) externalise fine-grained authorisation.

---

## 10.4 Secrets management

Secrets include API keys, client secrets, private keys, certificates, database passwords, webhook signing secrets and SFTP keys.

- **Store** them in a secrets manager (HashiCorp Vault / OpenBao, AWS Secrets Manager, Azure Key Vault, Google Secret Manager, CyberArk, 1Password Secrets Automation, Doppler) or the iPaaS's secure credential store, never in code, configuration files committed to Git, iPaaS flow definitions, tickets or chat.
- **Inject** them at runtime; prefer short-lived **dynamic secrets** (Vault can mint database credentials per lease).
- **Rotate** on a schedule *and* on personnel changes or suspected exposure. Design for **zero-downtime rotation**: support two valid secrets during the overlap (old and new webhook secrets, two API keys).
- **Inventory** every credential: what it accesses, who owns it, when it expires, how to rotate it. Expired certificates and credentials are a leading cause of integration outages.
- **Scan** repositories, logs and container images for leaked secrets.
- **Hardware security modules (HSMs)** or cloud KMS hold signing keys for high-assurance use cases (payments, PKI).

---

## 10.5 OWASP API Security Top 10 (2023), applied to integrations

The OWASP API Security Top 10 was last updated in **2023** (the previous edition was 2019; no newer edition had been published as of October 2026). Every integration engineer should know it, from both sides of the API.

| # | Risk | What it means | Integration angle |
|---|---|---|---|
| **API1** | Broken Object Level Authorization (BOLA) | Changing `/orders/123` to `/orders/124` returns someone else's order | Multi-tenant integration APIs must check tenancy on every object |
| **API2** | Broken Authentication | Weak tokens, missing validation, credential stuffing | Validate JWTs properly; protect token endpoints |
| **API3** | Broken Object Property Level Authorization | Exposing or allowing writes to fields the caller should not see or change (merges 2019's Excessive Data Exposure and Mass Assignment) | Do not return entire records to integrations that need three fields; allow-list writable fields |
| **API4** | Unrestricted Resource Consumption | No limits on rate, size, pagination or cost | Rate limits, payload limits and max page sizes; protect against costly bulk requests |
| **API5** | Broken Function Level Authorization | Regular users can call admin functions | Separate admin and integration scopes |
| **API6** | Unrestricted Access to Sensitive Business Flows | Automated abuse of legitimate flows (ticket scalping, mass signup) | Business-level limits, anomaly detection |
| **API7** | Server-Side Request Forgery (SSRF) | Server fetches an attacker-supplied URL, reaching internal systems | **Webhooks, callback URLs, "import from URL" and file-fetch integrations are SSRF vectors** |
| **API8** | Security Misconfiguration | Verbose errors, missing TLS, permissive CORS, default credentials | Harden gateways and iPaaS endpoints |
| **API9** | Improper Inventory Management | Forgotten old API versions, undocumented endpoints, shadow integrations | Maintain an integration and API catalogue (Chapter 17) |
| **API10** | Unsafe Consumption of APIs | Trusting third-party API responses too much: following redirects blindly, not validating data, injecting it into queries | **The integration engineer's own risk:** validate and sanitise everything received from partners |

### SSRF defences (for webhook senders and URL fetchers)

- Resolve the hostname and **block private, loopback, link-local and cloud-metadata addresses** (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.169.254`, `::1`, `fc00::/7`, `fe80::/10`).
- Re-check after redirects, or disable redirects; beware **DNS rebinding** (resolve once and connect to that IP).
- Send outbound requests through an **egress proxy** with an allow-list or deny-list.
- Use IMDSv2 on AWS (session-token-protected metadata).

### Unsafe consumption defences

- Validate partner responses against schemas; enforce size limits.
- Never pass partner-supplied data into SQL, shell commands, templates or LLM prompts without escaping or isolation. This includes **prompt injection** through data that an AI agent reads (Chapter 18).
- Treat partner redirects and URLs in payloads as untrusted.
- Parse XML with external entities disabled (XXE) and entity-expansion limits.

---

## 10.6 Protecting data

### In transit

- TLS 1.2+ everywhere, including "internal" networks (zero trust).
- mTLS for high-value B2B and service-to-service links.
- **Message-level encryption** when data passes through intermediaries you do not trust, or must remain encrypted at rest in queues and files: PGP/GPG for files exchanged over SFTP (still standard in banking and payroll), S/MIME for AS2, JWE or field-level encryption for sensitive JSON fields.

### At rest

- Encrypt queues, topics, storage buckets, databases and backups (cloud defaults usually cover this; verify).
- **Message stores and DLQs contain production data.** Apply the same protections and retention limits as the source system.

### Data minimisation and masking

- Use the **Content Filter** pattern (Chapter 5): forward only fields the target needs.
- **Tokenise** sensitive values (card numbers, national IDs), so integrations handle tokens rather than raw data.
- **Mask in non-production:** never copy raw production personal data into test environments without anonymisation.

### Logging hygiene

Logs are the most common accidental data leak in integrations.

- **Never log** secrets, tokens, `Authorization` headers, full card numbers, passwords or full request bodies containing personal data by default.
- Use structured logging with **redaction** of known sensitive fields.
- Log **identifiers and metadata** (IDs, event types, status, sizes, trace IDs), not payloads, by default. Keep payloads, when needed for replay, in a protected message store with access control and retention.
- Remember iPaaS execution histories often store full payloads by default. Configure retention and masking.

---

## 10.7 Compliance regimes you will meet *(as of October 2026)*

You are not expected to be a lawyer, but you must recognise when a regime applies and what it implies for design.

| Regime | Scope | Integration implications |
|---|---|---|
| **GDPR** (EU) / **UK GDPR** | Personal data of people in the EU/UK | Lawful basis; data minimisation; **records of processing** (each integration is a processing activity); data processing agreements with vendors; **cross-border transfer** mechanisms (EU–US Data Privacy Framework, Standard Contractual Clauses); data-subject rights (erasure must propagate to every system the data was copied to); breach notification within 72 hours. |
| **CCPA / CPRA** (California) and other US state privacy laws | Personal information of residents | Similar rights; deletion and opt-out propagation. |
| **HIPAA** (US) | Protected Health Information (PHI) | **Business Associate Agreements (BAAs)** with every vendor touching PHI (including iPaaS and cloud); minimum necessary; audit logging; encryption. |
| **PCI DSS v4.0.1** | Payment card data | Keep card data **out of scope**: use tokenisation and hosted payment pages so integrations never see full card numbers (PANs). The standard's future-dated requirements became mandatory on 31 March 2025. |
| **SOC 2** (AICPA) | Service organisations' controls | Your integration platform and vendors should have SOC 2 Type II reports; your integrations are subject to change management, access control and monitoring controls. |
| **ISO/IEC 27001:2022** | Information security management systems | Similar control expectations; supplier security. |
| **SOX** (US public companies) | Financial reporting controls | Integrations feeding the general ledger are in scope: change control, reconciliation evidence, segregation of duties. |
| **DORA** (EU Digital Operational Resilience Act) | Financial entities in the EU, applying from **17 January 2025** | ICT risk management, incident reporting, resilience testing and **third-party (ICT provider) risk management**, including register of information on ICT providers such as iPaaS and cloud. |
| **NIS2** (EU) | Essential and important entities across sectors | Cybersecurity risk management, supply-chain security, incident reporting. |
| **EU Data Act** | Data from connected products and data-processing service switching; most provisions apply from **12 September 2025** | Users' rights to access and port device data; cloud-switching obligations, which affect integration portability. |
| **EU AI Act** | AI systems placed on the EU market, phased application from 2025 to 2027 | Relevant when integrations feed or are performed by AI systems: logging, transparency and human oversight for high-risk uses. |
| **Data residency / sovereignty** | Country rules (e.g. in the EU, India, China, the Middle East) and sector rules | Choose iPaaS regions and runtimes so that data does not leave permitted regions; many iPaaS platforms offer regional data planes or on-premises runtimes for this reason. |
| **FedRAMP** (US government cloud) | Cloud services used by US federal agencies | Only FedRAMP-authorised platforms may be used for federal data. |

**Practical approach:** for each integration, record in the design document what data categories it moves (personal, sensitive, payment, health, financial), the legal basis or contract that covers it, the regions it traverses, the retention of copies (logs, DLQs, stores) and the vendors involved. That table answers most audit questions.

---

## 10.8 Threat modelling an integration

Spend an hour threat-modelling every significant integration. A lightweight approach using **STRIDE**:

| Threat | Question for the integration | Example control |
|---|---|---|
| **S**poofing | Could someone impersonate the partner, or us? | mTLS, signed webhooks, OAuth with `private_key_jwt` |
| **T**ampering | Could data be modified in transit or in a queue or file drop? | TLS, message signatures, PGP, checksums |
| **R**epudiation | Could a party deny sending or receiving? | Signed receipts (AS2 MDNs), audit logs with trace IDs |
| **I**nformation disclosure | Could data leak through logs, DLQs, error messages or over-broad scopes? | Minimisation, redaction, least privilege |
| **D**enial of service | Could a flood or giant payload stop the flow? | Rate limits, size limits, queues, bulkheads |
| **E**levation of privilege | Could the integration's credentials be used for more than intended? | Narrow scopes, separate identities, monitoring of integration identities |

Draw the data-flow diagram, mark the **trust boundaries** (your network, the partner's, the internet, the iPaaS vendor's cloud), and ask the six questions at each boundary crossing. Record findings and mitigations in the design document ([`templates/integration-design-document.md`](../templates/integration-design-document.md) has a section for this).

---

## Summary

- Integration credentials are high-value targets: use least privilege, separate identities, short-lived tokens and secretless federation where possible.
- Know the authentication options: API keys, Basic, OAuth 2.0/2.1 grants (client credentials, auth code + PKCE, JWT bearer, token exchange), OIDC, JWT validation, mTLS, HMAC, SAML, SCIM.
- Manage secrets centrally, rotate them without downtime, and inventory their expiry.
- Apply the OWASP API Security Top 10 (2023) from both sides, especially BOLA, SSRF and unsafe consumption.
- Minimise and protect data in transit, at rest, in DLQs and in logs.
- Recognise compliance regimes and record data categories, regions and retention for every integration.
- Threat-model every significant integration with STRIDE at each trust boundary.

## Exercises

See [`exercises/10-security.md`](../exercises/10-security.md).

## Further reading

- Justin Richer and Antonio Sanso, *OAuth 2 in Action* (Manning, 2017).
- Neil Madden, *API Security in Action* (Manning, 2020).
- RFC 9700, *OAuth 2.0 Security Best Current Practice* (2025); the OAuth 2.1 draft (datatracker.ietf.org).
- OWASP API Security Top 10 2023 (owasp.org/API-Security).
- Adam Shostack, *Threat Modeling: Designing for Security* (Wiley, 2014).
- PCI Security Standards Council, PCI DSS v4.0.1 (2024).
