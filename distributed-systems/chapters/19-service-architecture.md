# Chapter 19. Service Architecture: Microservices, Discovery and Meshes

> "Microservices trade complexity inside the code for complexity between the code."

## What you will learn

- Monoliths, modular monoliths and microservices: what each optimises, and when splitting is worth it.
- How to draw service boundaries around data ownership.
- Synchronous and asynchronous interaction between services, and the availability arithmetic of call graphs.
- Service discovery, API gateways and service meshes.
- Deploying distributed services safely: rolling, blue-green and canary releases, and backward compatibility.
- Common anti-patterns: the distributed monolith, chatty services and shared databases.

---

## 19.1 Why architecture is a distributed-systems topic

The moment one application becomes two services talking over a network, every problem in Parts I–III applies between them: partial failure, retries, ordering, consistency and transactions. Architecture decisions decide **how many** of those network boundaries exist and **where**, and so how much distributed-systems complexity a team must manage.

## 19.2 Monoliths and microservices

| Style | Description | Strengths | Weaknesses |
|---|---|---|---|
| **Monolith** | One deployable unit with one database | Simple to develop, test, deploy and debug; in-process calls; local transactions | Teams contend for one codebase and release; one failure domain; scales as a unit |
| **Modular monolith** | One deployable unit with strictly separated internal modules and interfaces | Most monolith benefits plus clear boundaries; an easy path to extraction later | Discipline needed to keep modules separate |
| **Microservices** | Many small services, each owning its data, deployed independently | Independent deployment and scaling; team autonomy; fault isolation | Network calls everywhere; distributed transactions; operational overhead; harder testing and debugging |

Microservices are primarily an **organisational** tool: they let many teams ship independently (Conway's law, 1968: systems tend to mirror the communication structure of the organisations that build them). For a small team, they usually cost more than they return. A well-known example: in 2023 the Amazon Prime Video team wrote that moving a video-monitoring service from a distributed serverless design to a single process cut its infrastructure cost by about 90%. The lesson isn't that monoliths are better, but that **every network boundary has a cost**, and boundaries should be drawn where they pay for themselves.

## 19.3 Drawing boundaries

The most important rule: **each service owns its data, and no other service reads or writes that data directly.** Other services go through the owner's API or consume its events. Shared databases couple services invisibly: a schema change in one breaks others, and no service can guarantee its own invariants.

Good boundaries:

- follow **business capabilities** or **bounded contexts** (from Eric Evans's domain-driven design, 2003): ordering, payments, inventory, shipping;
- keep **transactions inside one service**: if two pieces of data must change atomically, they probably belong together (Chapter 9);
- minimise **chatty** interactions: if completing one user request requires dozens of calls between two services, the boundary is probably wrong;
- align with **team ownership**: one team per service (a team may own several).

## 19.4 Synchronous call graphs and availability

Chapter 1 §1.7 showed that serial dependencies multiply unavailability. In a microservice system, a user request may traverse a **call graph** of many services. If the request needs all of ten services, each 99.9% available, the request is about 99.0% available. Deep synchronous chains also add latency (each hop adds network time and its own tail) and spread failures (a slow service ties up threads in every caller above it).

Ways to reduce the damage:

- **Prefer asynchronous interaction** for anything that doesn't need an immediate answer: publish an event and let downstream services react (Chapter 14).
- **Cache or replicate reference data locally** (for example, keep a local copy of product data, updated from events) instead of calling the owner on every request.
- **Degrade gracefully** when optional dependencies fail: show the page without recommendations.
- **Apply the resilience patterns** of Chapter 17 at every call: timeouts, deadlines, bounded retries, circuit breakers, bulkheads.
- **Keep critical paths short**: map the services involved in your most important user journeys, and challenge every synchronous dependency on them.

## 19.5 Service discovery

Services run as many instances whose addresses change as they scale, fail and redeploy. **Service discovery** lets callers find current, healthy instances.

| Approach | How | Examples |
|---|---|---|
| **DNS** | A name resolves to instance addresses | Kubernetes Services (cluster DNS), Consul DNS, cloud private DNS |
| **Client-side discovery** | The client queries a registry and load-balances itself | Consul or etcd plus a client library; gRPC's xDS client support |
| **Server-side discovery** | The client calls a load balancer, which knows the instances | Cloud load balancers; Kubernetes Services with kube-proxy |
| **Service mesh** | A sidecar proxy beside each instance handles discovery and routing | Istio, Linkerd, Consul service mesh |

DNS is universal but its caching makes it slow to react: clients may keep using a dead address until its TTL expires, and some clients cache longer than the TTL. Registries with watches react in seconds but need client support.

## 19.6 API gateways

An **API gateway** is the entry point for external clients. It typically handles authentication, rate limiting, request routing to internal services, protocol translation (for example HTTP/JSON externally to gRPC internally), and sometimes response aggregation. A variation, **backend for frontend** (BFF), provides one gateway per client type (web, mobile), each shaped to that client's needs. Gateways centralise cross-cutting concerns, but must be kept thin; business logic in the gateway becomes a bottleneck owned by no one.

## 19.7 Service meshes

A **service mesh** moves networking concerns out of application code into infrastructure. Each service instance gets a **sidecar proxy** (most commonly **Envoy**), and all traffic flows through the sidecars. A **control plane** (Istio's istiod, for example) configures the proxies using APIs such as Envoy's **xDS**.

What a mesh provides:

- **Mutual TLS** between all services, with automatic certificate issuance and rotation (service identity, often following the **SPIFFE** standard).
- **Traffic management:** load balancing (including power of two choices, Chapter 18), retries, timeouts, circuit breaking, outlier detection, canary routing by percentage or header.
- **Observability:** uniform metrics, logs and traces for every call (Chapter 22).
- **Policy:** which services may call which.

The costs: extra latency per hop (typically sub-millisecond to a few milliseconds), resource use for thousands of proxies, and operational complexity. Mesh-managed retries can multiply with application retries (Chapter 17 §17.3), so retry policy must be decided in one place. Newer designs reduce the overhead: Istio's **ambient mode** (generally available in 2024) replaces per-pod sidecars with per-node proxies for basic features, and **proxyless gRPC** lets gRPC clients take xDS configuration directly.

## 19.8 Deploying safely

In a distributed system, a deployment is a period during which **old and new versions run together**. Every change must be safe in that mixed state.

### Release strategies

| Strategy | How | Rollback |
|---|---|---|
| **Rolling update** | Replace instances a few at a time | Roll forward or back, instance by instance |
| **Blue-green** | Run the new version (green) alongside the old (blue); switch traffic at once | Switch traffic back |
| **Canary** | Send a small percentage of traffic to the new version; watch metrics; increase gradually | Route traffic away from the canary |
| **Feature flags** | Deploy code dark; enable behaviour per user or cohort at runtime | Turn the flag off |

Canaries should be **automated**: compare the canary's error rate and latency with the baseline and halt the rollout automatically on regression. Many large-scale outages (Chapter 24) were caused by changes, especially configuration changes, applied everywhere at once without a canary.

### Compatibility rules

- **APIs:** add fields, don't remove or change them; version when you must break (Chapter 14 §14.3).
- **Database schemas:** use **expand and contract** migrations. Add the new column (expand), deploy code that writes both and reads either, backfill, switch reads, then remove the old column (contract) once no running code uses it.
- **Events and messages:** consumers must accept both old and new formats for as long as both may be in flight or in retained logs.
- **Rollback must work:** the previous version must handle data written by the new one. Test rollbacks, not just rollouts.

## 19.9 Anti-patterns

| Anti-pattern | Symptoms | Remedy |
|---|---|---|
| **Distributed monolith** | Services must be deployed together; one change touches many services | Redraw boundaries; merge tightly coupled services |
| **Shared database** | Several services read and write the same tables | Assign ownership; expose APIs or events |
| **Chatty services** | Many fine-grained calls per user request | Coarser APIs; local read models; merge services |
| **Synchronous chains everywhere** | High latency; cascading failures | Asynchronous events; caching; graceful degradation |
| **No ownership** | Nobody on call for a service; outdated dependencies | One owning team per service, with an operational budget |
| **Nanoservices** | More services than engineers | Merge; prefer a modular monolith |

---

## Summary

- Architecture decides how many network boundaries exist, and so how much distributed-systems complexity you take on.
- Monoliths are simplest; modular monoliths add boundaries without network costs; microservices buy independent deployment and team autonomy at significant cost. Draw boundaries where they pay.
- Each service owns its data; keep transactions inside services; align boundaries with business capabilities and teams.
- Synchronous call graphs multiply unavailability and latency: prefer events, local read models and graceful degradation, and apply resilience patterns at every call.
- Service discovery (DNS, registries, meshes), API gateways and service meshes provide routing, security and observability between services; meshes add per-hop costs and must not double up retries.
- Deploy with canaries, flags and expand-and-contract migrations, keeping every change safe while old and new versions coexist, and test rollback.

## Exercises

This chapter has no exercises of its own. Its practical work (timeouts, retries, breakers and safe rollout) is exercised in Chapters 17 and 22, and the design-review checklist in Appendix D applies it to your own system.

## Further reading

- Sam Newman, *Building Microservices* (2nd edition, O'Reilly, 2021) and *Monolith to Microservices* (2019).
- Melvin E. Conway, "How Do Committees Invent?", *Datamation* (1968).
- Eric Evans, *Domain-Driven Design* (Addison-Wesley, 2003).
- Marcin Kolny, "Scaling up the Prime Video audio/video monitoring service and reducing costs by 90%", Prime Video Tech blog (2023).
- Martin Fowler, "MonolithFirst" (martinfowler.com, 2015).
- Envoy and Istio documentation (envoyproxy.io, istio.io).
