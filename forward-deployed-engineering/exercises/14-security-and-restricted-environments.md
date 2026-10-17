# Exercises: Chapter 14, [Security, Compliance and Restricted Environments](../chapters/14-security-and-restricted-environments.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional. Regulations and frameworks are described for orientation *(as of October 2026)*; this is not legal advice.

## Questions

1. **Concept.** Match each item to its description, and say whether it is about the vendor, the processing, or AI risk management: SOC 2 Type II; ISO/IEC 42001; FedRAMP; DPIA; DORA; SR 11-7; NIST AI RMF; OWASP Top 10 for LLM Applications.
   - (i) a US supervisory guidance on model risk management in banking;
   - (ii) an audit report on a service organisation's controls operating over a period;
   - (iii) an international standard for an AI management system;
   - (iv) a US government authorisation programme for cloud services;
   - (v) an assessment GDPR requires for high-risk processing of personal data;
   - (vi) an EU regulation on operational resilience in the financial sector;
   - (vii) a voluntary US framework organised around govern, map, measure and manage;
   - (viii) a list of the most common technical risk categories for LLM systems.

2. **Scenario.** Rewrite each security-questionnaire answer so it is precise and honest, inventing plausible specifics where needed and flagging anything not yet in place.
   - (a) "All data is encrypted."
   - (b) "We follow industry best practice for access control."
   - (c) "The AI model does not store your data."
   - (d) "We have SOC 2." (Your company has a SOC 2 Type I report; the Type II audit period ends in four months.)

3. **Scenario.** For each agent at Woodgrove Bank, decide whether it has the "lethal trifecta" and, if so, how to break it.
   - (a) An internal policy assistant that reads the bank's intranet and answers staff questions in a chat window. It has no tools.
   - (b) A complaints agent that reads customer emails, looks up account history and can send replies to customers.
   - (c) A research agent that browses the public web and writes summaries into a shared drive that only the research team can read.

4. **Scenario.** Adventure Works' defence division wants your document-analysis platform in an air-gapped, classified network. Write a delivery plan covering people, software and model transfer, updates, observability and incident handling, using §14.6.

5. **Calculation.** (a) A customer's SOC discovers at 16:30 on Friday that a misconfigured storage bucket exposed personal data. Under GDPR, by when must the controller notify the regulator, where feasible? Who is the controller here, and what is the vendor's obligation if it is the processor? (b) In the air-gapped deployment, a release requires 2 working days to build and bundle, 3 days of internal testing, 5 working days for transfer and scanning at the cross-domain gateway, and 2 days of on-site testing. What is the minimum lead time for a fix, and what does it imply for how you work?

6. **Scenario.** On a train home from Tailspin Toys, you realise you left your customer-issued laptop in a café. It is encrypted, and you were logged into the customer's VPN an hour ago. Write down, in order, what you do in the next hour.

7. **Hands-on.** Fill in the key sections of [`../templates/security-and-ai-risk-review.md`](../templates/security-and-ai-risk-review.md) for a permission-aware policy assistant at Woodgrove Bank, using [`../examples/permission-aware-retrieval/`](../examples/permission-aware-retrieval/) and [`../examples/agent-guardrails/`](../examples/agent-guardrails/) as evidence: data flows, data classification, identity and access, AI-specific risks and controls, logging, and residual risks. For at least three controls, cite the test in the example that demonstrates it.

8. **Concept.** Explain SSO, SCIM, RBAC and "acting on behalf of the user". Why do customers care so much about the last two for AI agents?

## Solutions

1. | Item | Description | About |
   |---|---|---|
   | SOC 2 Type II | (ii) audit report on controls operating over a period (typically 6–12 months) | The vendor |
   | ISO/IEC 42001 | (iii) AI management system standard (2023) | The vendor (its AI management system) |
   | FedRAMP | (iv) US government cloud authorisation | The vendor (its cloud service) |
   | DPIA | (v) GDPR assessment for high-risk processing | The processing |
   | DORA | (vi) EU financial-sector operational resilience, applying from January 2025 | The processing (regulated entities and their ICT providers) |
   | SR 11-7 | (i) US model risk management guidance | The processing (the bank's model risk practice) |
   | NIST AI RMF | (vii) voluntary framework: govern, map, measure, manage | AI risk management |
   | OWASP Top 10 for LLM Applications | (viii) common LLM risk categories | AI risk management |

2. - (a) "Customer data at rest is encrypted with AES-256 using keys held in the customer's own AWS KMS; data in transit uses TLS 1.2 or higher; backups are encrypted with the same keys. Prompt logs are retained for 30 days in the customer's tenancy."
   - (b) "Users sign in through the customer's identity provider via SAML SSO; users and groups are provisioned with SCIM, so leavers lose access when they are disabled in Entra ID; access within the application is role-based and mapped to customer groups; administrative access to production is through the customer's PAM process, time-limited and logged."
   - (c) "Prompts and outputs are sent to [provider] through [cloud platform] in the EU (Frankfurt) region under an enterprise agreement that excludes training on customer data; the provider retains inputs for up to [N] days for abuse monitoring [or: zero retention is configured]; our application stores prompts, retrieved sources and outputs in the customer's tenancy for 90 days for audit." The original is probably untrue (the application, at least, logs data) and unanswerable as written.
   - (d) "We hold a SOC 2 Type I report dated [date], available under NDA. Our Type II audit period ends on [date], and we expect the report by [date]. In the meantime, we can provide our ISO 27001 certificate [if held] and our latest penetration-test summary." Don't over-claim: security teams remember inaccurate answers.

3. The trifecta is (1) access to private data, (2) exposure to untrusted content and (3) the ability to communicate externally.
   - (a) **No.** Private data yes; untrusted content mostly no (the intranet is internal, though a compromised or malicious internal page is possible); external communication **no**, since it has no tools. Residual risks are permission leaks (use security trimming) and internal content injection, so screen and log.
   - (b) **Yes.** Account history is private data; customer emails are untrusted content; sending replies is an external channel. An email could instruct the agent to send another customer's details. **Break it** by making replies drafts that a human approves before sending, and by restricting lookups to the account linked to the verified sender, so even a hijacked agent can only reveal the sender's own data.
   - (c) **Partly.** The public web is untrusted content; the shared drive is internal, so there is no external channel unless the agent can also fetch URLs with data in them (a web fetch can itself exfiltrate, by encoding data into a request). It has limited private data unless it can read the drive. Make sure it cannot read private data and cannot make arbitrary outbound requests containing data; restrict browsing to fetches without user-supplied parameters if possible.

4. Plan:
   - **People:** confirm which roles need security clearances; clearance takes months, so staff the engagement with cleared engineers or start the process at qualification. Plan for cleared customer staff to do hands-on work where you cannot.
   - **Software:** bundle everything (container images, dependencies, documentation) with a software bill of materials (SBOM) listing every component and version; sign the artefacts; scan them yourselves before submitting.
   - **Model:** choose a self-hostable open-weight model (or an accredited provider offering for classified environments, if one exists for this classification); evaluate it outside on unclassified analogue documents, then confirm inside on real documents with cleared staff; size GPU hardware early (hardware lead times).
   - **Transfer:** use the approved cross-domain process; expect days per transfer; batch changes.
   - **Updates:** plan them as releases on a schedule; no hot-fixes from a laptop; test thoroughly before transfer; include rollback.
   - **Observability:** logs and metrics stay inside; agree how problems will be diagnosed (often cleared customer staff run diagnostics and describe results); build good self-diagnostics and runbooks.
   - **Incidents:** agree with the customer's security team who can shut the system down (a kill switch), how evidence is preserved, and notification routes; run a tabletop exercise before go-live.

5. (a) GDPR requires the **controller** to notify the supervisory authority **within 72 hours of becoming aware** of a personal data breach, where feasible: **16:30 on Monday** (72 calendar hours, including the weekend). The controller is normally the **customer** (it decides the purposes of processing). The vendor, as **processor**, must notify the controller **without undue delay** after becoming aware, and should support the investigation. Check the contract's data processing agreement: it often sets a shorter contractual deadline (for example 24 or 48 hours) for the processor to notify the customer.

   (b) 2 + 3 + 5 + 2 = **12 working days**, about two and a half weeks, for even a one-line fix. Implications: invest heavily in testing before transfer; bundle fixes into planned releases; build configuration switches and feature flags into the release so some problems can be mitigated inside the environment without a new transfer; and ship good runbooks so cleared local staff can diagnose and work around problems.

6. In order:
   1. **Report it immediately** to the customer's security contact or service desk and to your own company's security team, before trying to recover it. Delay is worse than the incident.
   2. **Phone the café** and ask them to keep the laptop secure; arrange collection, but don't let recovery delay the report.
   3. **Help the customer revoke access:** sessions, VPN certificates or tokens, and any credentials cached on the device, following their instructions. Change your passwords from a trusted device.
   4. **Tell them what was on it:** which systems you had accessed, any local data (there should be none beyond what was approved), whether the disk is fully encrypted and the screen-lock settings.
   5. **Follow their incident process** (they may remote-wipe the device), and write a short factual timeline the same day.

7. A good review includes:
   - **Data flows:** user → SSO → assistant → retrieval index (documents with ACLs, synced from SharePoint) → model endpoint (region-pinned) → answer with citations; and which data crosses which boundary.
   - **Classification:** internal and confidential policy documents; HR-restricted documents excluded or ACL-protected.
   - **Identity and access:** SSO, SCIM, group-based ACLs, deny by default for documents with no ACL.
   - **AI risks and controls,** with evidence:
     - Permission leak → security trimming before ranking; *test showing restricted documents never reach unauthorised users* (permission-aware-retrieval).
     - Fabricated citations → citation checker; *test showing an answer citing a document not in the user's context fails* (permission-aware-retrieval).
     - Inference from ranking statistics → statistics over permitted documents only; *test showing scores are identical with and without hidden documents* (permission-aware-retrieval).
     - Excessive agency and injection (if tools are added) → allow-lists, approvals, budgets, taint after suspicious content; *guardrail tests* (agent-guardrails).
     - Unaccountable actions → tamper-evident audit log; *hash-chain verification test* (agent-guardrails).
   - **Logging:** questions, retrieved document IDs, answers, model version; retention per policy.
   - **Residual risks,** stated honestly: injection can be reduced but not eliminated; ACL sync lag (how quickly a removed permission takes effect); model behaviour changes on upgrade (mitigated by pinned versions and regression evaluations).

8. - **SSO (single sign-on):** users sign in through the customer's identity provider (Entra ID, Okta and others) via SAML or OpenID Connect, rather than separate passwords.
   - **SCIM:** a protocol for provisioning and de-provisioning users and groups automatically, so leavers lose access promptly.
   - **RBAC (role-based access control):** permissions granted to roles, mapped to the customer's groups.
   - **Acting on behalf of the user:** the system uses delegated tokens carrying the user's identity and permissions, rather than a powerful shared service account.

   Customers care about RBAC and delegated access for agents because an agent can be manipulated (prompt injection) or simply wrong. If it acts with a super-user account, any user can, through the agent, reach data and actions they couldn't reach directly: privilege escalation. Acting as the user means the customer's existing permissions bound the agent's blast radius, and audit logs show which person each action was taken for.
