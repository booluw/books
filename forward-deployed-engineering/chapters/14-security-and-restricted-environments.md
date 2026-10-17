# Chapter 14. Security, Compliance and Restricted Environments

> "The security team isn't blocking your project. They're the people who'll be blamed if it goes wrong."

## What you will learn

- Why security and compliance competence is a core FDE skill, not a specialism.
- How enterprise security reviews work, and how to pass them faster.
- The vocabulary of compliance: certifications, regulations and frameworks FDEs meet most.
- Specific security risks of AI systems, and the controls for each.
- How to work in restricted environments: on-premises, air-gapped, classified and sovereign.
- Personal security discipline for engineers with privileged access to customer systems.

This chapter describes frameworks and laws for orientation, *as of October 2026*. It is not legal advice; customers' legal and compliance teams decide what applies.

---

## 14.1 Why this is core

Forward deployment began in Palantir's work with intelligence and defence agencies (Chapter 2), where security was the first requirement, not an afterthought. In commercial enterprise work, and especially in AI, the pattern holds:

- **Security reviews are often the longest item on the critical path.** A deployment that is ready in six weeks may wait three months for approval.
- **FDEs hold privileged access** to customer systems and data. A mistake or compromise affects the customer directly.
- **AI adds new risks** that many security teams are still learning to assess. An FDE who can explain them clearly, and bring controls, speeds approval.

An FDE who treats security as someone else's job will be slow, and eventually dangerous.

## 14.2 How enterprise security reviews work

Most large organisations assess new vendors and systems through some combination of:

1. **Vendor risk assessment:** a security questionnaire about your company (standard ones include the Shared Assessments **SIG** questionnaire and the Cloud Security Alliance **CAIQ**), plus evidence such as certifications and penetration-test summaries.
2. **Architecture or design review:** how the specific deployment works: data flows, hosting, access, encryption, integration points.
3. **Data protection review:** what personal data is processed, on what legal basis, where, by whom, for how long. Under GDPR, high-risk processing requires a **data protection impact assessment (DPIA)**.
4. **AI or model risk review** (increasingly common): the use case's risk level, model provenance, evaluation evidence, human oversight, monitoring. In banking, this often sits within existing **model risk management** practice (in the US, supervisory guidance SR 11-7).
5. **Penetration test or security testing** before production, for some deployments.
6. **Change approval** through a change advisory board (CAB) for production changes.

### Passing faster

- **Start in the scoping phase** (Chapter 6). Ask the security contact what they'll need and how long it takes.
- **Bring a complete pack** up front: architecture diagram, data-flow diagram, data inventory with classifications, access model, encryption, logging, hosting regions, sub-processors, certifications, AI-specific controls. Template: [`templates/security-and-ai-risk-review.md`](../templates/security-and-ai-risk-review.md).
- **Answer precisely.** "Data is encrypted" is weak. "Data at rest is encrypted with AES-256 using keys in the customer's AWS KMS; in transit with TLS 1.2+" is answerable.
- **Don't over-claim.** If something isn't in place, say so and give the plan. Security teams remember inaccurate answers.
- **Reuse:** your company should maintain a standard security pack and a library of answered questionnaires. Contribute improvements back.
- **Design to the customer's standards** from the start, so the review confirms rather than discovers.

## 14.3 Compliance vocabulary

### Certifications and attestations (about the vendor)

| Name | What it is |
|---|---|
| **SOC 2** (Type I / Type II) | An audit report (US, AICPA) on a service organisation's controls for security, availability, processing integrity, confidentiality and privacy. Type II covers operation over a period (typically 6–12 months) |
| **ISO/IEC 27001** | International standard for an information security management system; certification by accredited auditors |
| **ISO/IEC 42001** | International standard (2023) for an AI management system |
| **FedRAMP** | US government programme authorising cloud services for federal use, at Low, Moderate or High impact levels |
| **Cyber Essentials** (UK), **IRAP** (Australia), **C5** (Germany) | National assurance schemes often required in the public sector |
| **PCI DSS** | Payment card industry standard, if card data is involved |

### Regulations (about the processing)

| Regulation | Scope | Why FDEs meet it |
|---|---|---|
| **GDPR / UK GDPR** | Personal data of people in the EU / UK | Legal basis, minimisation, DPIAs, data subject rights, international transfers |
| **EU AI Act** | AI systems placed on the EU market or used in the EU | Risk-based obligations. Prohibitions applied from February 2025; obligations for general-purpose AI models from August 2025; most high-risk obligations phased in from August 2026 onwards. Uses such as employment decisions and credit scoring are classed as high-risk |
| **HIPAA** (US) | Protected health information handled by covered entities and their business associates | Business associate agreements (BAAs); safeguards |
| **Financial regulation** | Banks, insurers, investment firms | Model risk management, operational resilience (e.g. the EU's **DORA**, applying from January 2025), outsourcing rules |
| **Sector and national rules** | Government, defence, critical infrastructure | Security clearances, data sovereignty, export controls |

The EU AI Act's timeline has been subject to proposed adjustments; check the current position with the customer's counsel before relying on any date.

### Frameworks for AI risk

- **NIST AI Risk Management Framework** (AI RMF 1.0, January 2023), with its Generative AI Profile (July 2024): a voluntary US framework organised around govern, map, measure and manage.
- **OWASP Top 10 for LLM Applications:** the most common technical risk categories for LLM systems (prompt injection, sensitive information disclosure, excessive agency and others).
- **MITRE ATLAS:** a knowledge base of adversary tactics against AI systems.

## 14.4 AI-specific risks and controls

| Risk | Description | Controls |
|---|---|---|
| **Prompt injection** | Untrusted content (documents, emails, web pages, tool outputs) contains instructions that hijack the model | Least-privilege tools; human approval for consequential actions; separating trusted instructions from untrusted data; screening; never give an agent both untrusted input and unrestricted exfiltration paths |
| **Sensitive data disclosure** | The model reveals data the user shouldn't see | Permission-aware retrieval (Chapter 12 §12.4); output filtering; minimal context |
| **Excessive agency** | The agent has more permissions or autonomy than needed | Narrow tools; act as the user; allow-lists; budgets; approvals |
| **Data leaving the boundary** | Prompts and data sent to a provider outside agreed terms or regions | Enterprise agreements with no training and limited retention; region-pinned endpoints; private networking; self-hosting where required |
| **Insecure output handling** | Model output executed as code or SQL, or rendered as HTML | Treat output as untrusted input; parameterise; sandbox |
| **Supply chain** | Compromised models, packages, MCP servers or plugins | Approved sources; pinned versions; review of third-party servers |
| **Model errors in high-stakes decisions** | Wrong outputs affect people's rights or safety | Human oversight; evaluation by segment; documentation; appeal routes |
| **Lack of auditability** | Can't reconstruct why the system did something | Log inputs, sources, outputs, tool calls, approvals and model versions |

A useful rule for agents, sometimes called the **"lethal trifecta"** after Simon Willison's 2025 framing: an agent that combines (1) access to private data, (2) exposure to untrusted content, and (3) the ability to communicate externally can be tricked into leaking data. Remove at least one of the three for any agent you deploy, or put a human approval on the external channel.

## 14.5 Identity and access

- **Single sign-on (SSO)** through the customer's identity provider (Microsoft Entra ID, Okta, Ping and others) using SAML or OpenID Connect. Customers rarely accept separate passwords.
- **Provisioning** users and groups automatically (often via the **SCIM** protocol), so leavers lose access promptly.
- **Role-based access control (RBAC)**, mapped to the customer's groups.
- **Least privilege** for service accounts: scoped to specific resources, rotated, monitored.
- **Act on behalf of the user** where possible (delegated tokens) rather than with a powerful shared account, so the customer's existing permissions apply (Chapter 12 §12.5).
- **Privileged access** (production admin) through the customer's privileged access management process, time-limited and logged.

## 14.6 Restricted environments

Many of the most valuable FDE deployments happen in environments that restrict connectivity or location.

| Environment | Description | Implications |
|---|---|---|
| **Customer cloud tenancy** | Deployed into the customer's own cloud account | Customer controls network and keys; you need their platform team's help |
| **Private networking** | No public internet path; private endpoints only | Plan connectivity for model APIs, package registries, monitoring |
| **On-premises** | In the customer's own data centre | Hardware lead times; older platforms; manual change windows |
| **Sovereign cloud** | Cloud regions operated under national control (for example for EU sovereignty requirements) | Limited service and model availability |
| **Air-gapped** | Physically disconnected from external networks | Everything (software, models, updates, dependencies) must be transferred through approved media and processes |
| **Classified** | Government systems at a security classification | Personnel clearances; accredited facilities; strict procedures |

### Working air-gapped

- **Bundle everything:** container images, dependencies, model weights, documentation. Generate a software bill of materials (**SBOM**) listing every component and version.
- **Transfer through the approved process**, often with scanning and approval at a cross-domain gateway. Expect days.
- **Choose models that can be self-hosted:** open-weight models, or providers' offerings for isolated government regions (major cloud providers and AI labs offer models in government and classified regions *as of October 2026*).
- **Plan updates as releases:** you can't hot-fix from your laptop. Test thoroughly before transfer.
- **Observability on the inside:** logs and metrics stay in the environment; agree how you'll diagnose problems remotely (often you can't).
- **Clearances:** in classified work, only cleared personnel may access systems. Clearance processes take months; plan staffing accordingly.

## 14.7 Personal security discipline

FDEs carry credentials and data for some of the most sensitive systems in the economy. Personal habits matter:

- Use **customer-issued devices** and accounts where provided; follow their policies exactly.
- **Never copy customer data to personal devices**, personal cloud storage or unapproved AI tools.
- Use a **password manager** and hardware security keys; never share credentials.
- **Separate engagements:** different credentials, workspaces and, ideally, devices or profiles per customer.
- Be careful in public: screens on trains, calls in cafés, badges in photos.
- **Report incidents immediately** (lost laptop, suspected phishing, accidental data exposure). Delay is worse than the incident.
- **Offboard cleanly:** at the end of an engagement, return devices, revoke your access, delete local copies as agreed, and confirm in writing.

## 14.8 Incident response

Agree before production who does what when there's a security incident:

- How the customer's security operations centre (SOC) reaches your company, and vice versa.
- Notification timelines (contracts and regulations often require notification within fixed periods; GDPR sets 72 hours for notifying the regulator of a personal data breach, where feasible).
- Who can shut down the system (a **kill switch**) and how.
- How logs and evidence are preserved.

Practise it: a short tabletop exercise with the customer's security team before go-live finds the gaps cheaply.

---

## Summary

- Security and compliance are core FDE skills; reviews are often the critical path, and FDEs hold privileged access.
- Prepare complete, precise security packs early; design to the customer's standards; don't over-claim.
- Know the vocabulary: SOC 2, ISO 27001 and 42001, FedRAMP; GDPR, the EU AI Act, HIPAA, DORA; NIST AI RMF, OWASP LLM Top 10, MITRE ATLAS.
- AI risks (prompt injection, disclosure, excessive agency, boundary leaks, insecure output handling, supply chain) need specific controls; avoid the lethal trifecta.
- Integrate with the customer's identity: SSO, SCIM, RBAC, least privilege, acting as the user.
- Restricted environments (on-premises, sovereign, air-gapped, classified) need bundled releases, SBOMs, self-hostable models, and staffing with clearances.
- Keep strict personal security discipline, and agree incident response before production.

## Exercises

See [`exercises/14-security-and-restricted-environments.md`](../exercises/14-security-and-restricted-environments.md).

## Further reading

- OWASP, *Top 10 for Large Language Model Applications* (2025).
- NIST, *AI Risk Management Framework 1.0* (2023) and *Generative AI Profile* (NIST AI 600-1, 2024).
- Regulation (EU) 2024/1689 (the AI Act), and the European Commission's AI Act guidance pages.
- Simon Willison, "The lethal trifecta for AI agents" (June 2025).
- MITRE ATLAS (atlas.mitre.org).
- Board of Governors of the Federal Reserve System, SR 11-7, "Guidance on Model Risk Management" (2011).
