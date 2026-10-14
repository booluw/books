# Chapter 16. Compliance, Privacy, Platform Rules and Security

> "The fastest way to kill a GTM programme is a regulator, a lawsuit, a platform ban or a breach."

> **Not legal advice.** This chapter summarises rules to help you design systems and ask the right questions. Laws differ by country and change. Work with qualified counsel before running campaigns, especially across borders.

## What you will learn

- The main laws affecting B2B outreach and data: CAN-SPAM, GDPR and ePrivacy/PECR, CASL, US state privacy laws, and telephone rules.
- How to implement compliance in systems: lawful basis records, legitimate-interest assessments, opt-outs and global suppression, data-subject requests, retention.
- Platform rules: LinkedIn's terms on automation and scraping, mailbox-provider policies, and data-provider terms.
- Security for GTM systems: OAuth tokens, integration users, secrets, and lessons from the 2025 Salesloft Drift breach.

---

## 16.1 Why GTM engineers own this

Your systems decide who gets contacted, through which channel, with what data, and whether an opt-out is honoured. Lawyers write policy. **You implement it.** A compliant policy with a broken suppression sync is a violation.

## 16.2 Email outreach laws

### United States: CAN-SPAM Act (2003)

An **opt-out** regime. B2B commercial email does not need prior consent, but every commercial message must:

- use accurate header information (From, To, routing);
- use a non-deceptive subject line;
- identify the message as an advertisement where required (the rules for this differ by context; get advice);
- include a valid **physical postal address** of the sender;
- include a clear way to **opt out**, honour opt-outs within **10 business days**, and keep the mechanism working for at least 30 days after sending;
- not sell or transfer the addresses of people who opted out.

Penalties are per email (the FTC adjusts the maximum civil penalty annually for inflation; it exceeds $50,000 per violating email), and you are responsible for vendors sending on your behalf. Some US states have additional rules.

### European Union: GDPR plus ePrivacy rules

- **GDPR** governs processing of personal data, which includes a named work email (`jane.doe@company.com`) and job title. B2B prospecting usually relies on **legitimate interests** (Article 6(1)(f)), documented in a **Legitimate Interests Assessment (LIA)** that covers purpose, necessity and balancing. You must provide **transparency** (Article 14 notice when you obtained data from a third party, at the latest at first contact), honour **objections** to direct marketing absolutely (Article 21(3)), and respect data-subject rights (access, erasure).
- **ePrivacy rules** (the ePrivacy Directive, implemented differently in each member state) govern unsolicited electronic marketing. Some countries require **prior consent even for B2B email**; Germany's UWG §7 is commonly cited as strict. Others permit B2B outreach to work addresses under conditions. **Check each target country.** Vendor summaries disagree, so get local advice.

### United Kingdom: UK GDPR + PECR

PECR allows unsolicited marketing emails to **corporate subscribers** (companies) without consent, provided you identify yourself and offer an opt-out. **Sole traders and some partnerships are treated as individuals**, which requires consent. UK GDPR still applies to the personal data (legitimate interests, transparency, objection rights). The Data (Use and Access) Act 2025 amended parts of the UK regime. Follow ICO guidance as it updates.

### Canada: CASL

Canada's Anti-Spam Legislation is one of the strictest. Commercial electronic messages require **express or implied consent**, plus identification and an unsubscribe mechanism. A narrow implied-consent case covers addresses **conspicuously published** (or disclosed to you) without a statement refusing messages, *and* where the message is relevant to the person's business role. Penalties can be severe. Many teams exclude Canada from cold email or apply a strict policy.

### Australia and others

Australia's Spam Act requires consent (with an inferred-consent exception for conspicuously published business addresses relevant to the role). Brazil (LGPD), India (DPDP Act 2023, with rules being implemented), Singapore (PDPA and the Spam Control Act) and others each have their own rules. Build systems that apply **per-country policies**.

## 16.3 Phone and SMS

- **US TCPA:** restrictions on autodialled or prerecorded calls and texts, especially to mobile numbers, and Do-Not-Call rules. Penalties per call can be large, and class actions are common. B2B calls to mobiles are not automatically exempt.
- **UK PECR / EU rules:** live B2B marketing calls are generally allowed unless the number is registered with a do-not-call list (the UK's Corporate TPS for businesses; TPS for individuals and sole traders). Automated calls need consent.
- **SMS marketing** usually requires consent.

Design: store phone types; check DNC registries where required; restrict dialler modes; and keep call consent and suppression records.

## 16.4 Data sourcing and privacy laws

- **Data provenance:** know how your providers collected the data, and whether they meet GDPR transparency obligations. Contracts should state permitted use and storage.
- **US state privacy laws** (California CCPA/CPRA and a growing list of states): B2B contact data is covered in California since the B2B exemption expired on 1 January 2023. Honour access and deletion requests, and the right to opt out of "sale/sharing".
- **Data brokers:** some states (for example California's Delete Act, with a centralised deletion mechanism starting in 2026) regulate data brokers. This affects your providers and possibly you.
- **Website visitor identification** (Chapter 8) and tracking pixels raise consent requirements in the EU and UK (cookie consent) and litigation risk in the US. Get legal review.
- **AI processing:** sending personal data to model providers is processing too. Cover it in your records, DPAs and transparency notices.

## 16.5 Implementing compliance in systems

| Requirement | System implementation |
|---|---|
| **Global suppression list** | One list (email, domain, phone) checked **in code before every send, call, or sequence enrolment**, across *all* tools. Opt-outs from any channel propagate everywhere within hours, not days. |
| **Opt-out handling** | Unsubscribe link or reply detection (Chapter 10) → suppression list → stop sequences → CRM field `do_not_contact` with source and date. |
| **Country policies** | A rules table (country → allowed channels, consent requirement, notes); applied at list-building and send time using contact country. |
| **Lawful basis records** | Store on each contact: basis (legitimate interest or consent), source of data, date obtained, and LIA reference. |
| **Transparency** | A privacy notice link in emails; first-contact disclosure of data source where required. |
| **Data-subject requests** | A process to find a person across CRM, sequencer, enrichment tables, warehouse and spreadsheets, and to export or delete them; then suppress (keeping minimal data to prevent re-contact is generally permitted). |
| **Retention** | Delete or anonymise prospects who never engaged after N months; purge old enrichment tables. |
| **Vendor agreements** | DPAs with every tool processing personal data; check sub-processors and regions. |
| **Audit trail** | Logs of who was contacted, when, through which play and on which basis. |

Template: [`templates/legitimate-interest-assessment.md`](../templates/legitimate-interest-assessment.md).

## 16.6 Platform rules

### LinkedIn

LinkedIn's User Agreement prohibits using software, scripts, bots or browser extensions to scrape or automate activity on the site, and LinkedIn enforces actively:

- **Lawsuits:** in October 2025 LinkedIn sued ProAPIs and its CEO in federal court in Northern California, alleging a large-scale scraping operation using fake accounts and selling member data. (In the earlier *hiQ v. LinkedIn* litigation, which ended in 2022, a court found hiQ had breached LinkedIn's User Agreement.)
- **Tool and account restrictions:** LinkedIn restricts accounts that show automated behaviour, and has acted against automation vendors. Reports in 2026 described enforcement against HeyReach's company presence. These largely come from competitors' blogs, so treat the details cautiously.

Practical stance: understand that LinkedIn automation and scraping tools carry **terms-of-service, account and legal risk**; never risk executives' or key sellers' accounts; prefer official products (Sales Navigator, LinkedIn's APIs for approved partners) and manual or assisted actions; and don't store or resell scraped LinkedIn data.

### Mailbox providers

Bulk-sender rules (Chapter 11) are effectively platform law: violate them and your mail stops arriving.

### Data provider and tool terms

Enrichment contracts restrict how you may use and store data (for example, whether you may keep it in your CRM after the contract ends, or share it with other tools). AI and scraping tools may conflict with target websites' terms. Read the terms; involve legal for anything at scale.

## 16.7 Security for GTM systems

GTM stacks connect dozens of SaaS tools with powerful OAuth tokens and API keys. That makes them an attractive target.

### Case: the Salesloft Drift breach (August 2025)

- Between roughly 8 and 18 August 2025, a threat actor tracked by Google's Threat Intelligence Group as **UNC6395** used **stolen OAuth and refresh tokens** from Salesloft's Drift chat integration to access customers' **Salesforce** instances.
- The attackers ran queries against objects such as Accounts, Contacts, Cases and Opportunities, and searched the exfiltrated data for **secrets** (AWS access keys, passwords, Snowflake tokens) to pivot further. Google said it was aware of over 700 potentially impacted organisations. No Salesforce platform vulnerability was involved.
- Salesloft and Salesforce revoked Drift tokens. Google advised affected organisations to treat Salesforce data as compromised and rotate credentials. Salesloft later announced Drift's retirement.

**Lessons for GTM engineers:**

1. **Integration tokens are crown jewels.** Inventory every connected app and integration user. Remove unused ones. Scope permissions to the minimum objects and fields.
2. **Restrict connected apps:** in Salesforce, use connected-app policies (admin-approved users only, IP restrictions where possible); review OAuth grants regularly.
3. **Never store secrets in CRM records** (support cases, notes, custom fields). Scan for them.
4. **Monitor:** unusual API volumes, bulk queries by integration users, logins from unexpected IPs. Salesforce Shield / Event Monitoring and SIEM integration help.
5. **Have an incident plan:** revoke tokens, rotate credentials across downstream systems, preserve logs, notify as required.

### Everyday security hygiene

- Store API keys in a **secrets manager** or the tool's credential vault, never in Clay columns, docs or Slack.
- Use **separate integration users** per tool, with MFA on human accounts and SSO for the GTM tools.
- **Offboard** departing team members from every GTM tool (shadow tools are common).
- Review **who can export** CRM data; large exports are a data-loss vector.
- Vet vendors' security (SOC 2 Type II, ISO 27001), especially enrichment and AI tools receiving your CRM data.

---

## Summary

- CAN-SPAM (US) is opt-out; GDPR plus national ePrivacy rules (EU) require a lawful basis, transparency and absolute honouring of objections, with consent required in some countries; UK PECR permits B2B email to corporate subscribers; CASL (Canada) requires consent. Phone and SMS have their own strict rules.
- Implement compliance in systems: global suppression checked before every send, country policies, lawful-basis records, LIAs, data-subject request processes, retention and DPAs.
- LinkedIn prohibits scraping and automation and enforces through lawsuits and restrictions. Mailbox-provider and data-provider terms also bind you.
- Secure the GTM stack: inventory and minimise integration tokens, restrict connected apps, keep secrets out of the CRM, monitor and plan for incidents. The 2025 Drift breach is the cautionary tale.

## Exercises

See [`exercises/16-compliance-and-security.md`](../exercises/16-compliance-and-security.md).

## Further reading

- US FTC, *CAN-SPAM Act: A Compliance Guide for Business*.
- UK ICO guidance on PECR and on legitimate interests (ico.org.uk).
- European Data Protection Board guidelines on legitimate interests (2024) and on direct marketing.
- CRTC and Government of Canada CASL guidance (fightspam.gc.ca).
- Google Threat Intelligence Group / Mandiant, advisory on UNC6395 and Salesloft Drift (August 2025).
- LinkedIn User Agreement (linkedin.com/legal/user-agreement).
