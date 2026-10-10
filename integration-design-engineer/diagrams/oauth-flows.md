# OAuth 2.0 / 2.1 flows used in integrations

Used in [Chapter 10](../chapters/10-security.md).

## Client credentials (server-to-server)

```mermaid
sequenceDiagram
  participant I as Integration (client)
  participant AS as Authorisation server
  participant API as Partner API (resource server)
  I->>AS: POST /token grant_type=client_credentials (client auth: secret, private_key_jwt or mTLS)
  AS-->>I: access_token (expires_in 3600, scope)
  Note over I: Cache the token until shortly before expiry
  I->>API: GET /orders (Authorization: Bearer token)
  API-->>I: 200 OK
  I->>API: GET /orders (token expired)
  API-->>I: 401
  I->>AS: Refresh once (new client_credentials request)
  AS-->>I: new access_token
```

## Authorisation code + PKCE (user-delegated, e.g. "Connect your CRM")

```mermaid
sequenceDiagram
  participant U as User's browser
  participant App as Your app (client)
  participant AS as Authorisation server
  participant API as CRM API
  App->>App: Create code_verifier and code_challenge (S256)
  App->>U: Redirect to /authorize (client_id, redirect_uri, scope, state, code_challenge)
  U->>AS: User signs in and consents to scopes
  AS->>U: Redirect to redirect_uri with code and state
  U->>App: code, state (check state matches)
  App->>AS: POST /token (code, code_verifier, client auth)
  AS-->>App: access_token + refresh_token
  App->>API: Call API as the user (Bearer access_token)
  Note over App: Store refresh_token encrypted per tenant. Handle rotation and invalid_grant.
```
