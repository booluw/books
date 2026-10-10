# Exercises: Chapter 2, History

## Questions

1. List the eight Fallacies of Distributed Computing. For each, give an integration failure it can cause.
2. With 12 systems connected point-to-point in both directions, how many directional interfaces could exist? How many with a hub and a canonical model?
3. Match each modern technology to the older idea it repackages: (a) iPaaS connectors, (b) unified APIs, (c) Temporal / Step Functions, (d) Backstage API catalogue, (e) CloudEvents.
4. Why did "smart endpoints, dumb pipes" emerge? What risk does it reintroduce?
5. Pick an organisation you know. Which integration eras are still visible in its estate?

## Solutions

1. Network reliable → lost requests without retries. Latency zero → chatty integrations time out. Bandwidth infinite → giant payloads fail. Network secure → plaintext credentials leak. Topology doesn't change → hard-coded IPs break after migration. One administrator → firewall changes no one coordinated. Transport cost zero → egress bills and per-call API fees. Network homogeneous → TLS versions and proxies differ between environments.
2. Point-to-point: n(n−1) = 12 × 11 = **132** directional interfaces (66 bidirectional pairs). Hub with canonical model: 2n = **24** mappings.
3. (a) EAI adapters; (b) canonical data model; (c) BPEL / process manager; (d) UDDI registry; (e) EDI standard envelopes / SOAP envelope (Envelope Wrapper).
4. ESBs accumulated business logic and became central bottlenecks, so microservices moved logic into services. The risk: every team reimplements cross-cutting concerns (retries, security, transformation) inconsistently, and point-to-point sprawl returns.
5. Personal answer.
