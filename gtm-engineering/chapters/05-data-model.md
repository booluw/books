# Chapter 5. The GTM Data Model: CRMs, Identity and Matching

> "The CRM is the source of truth. That's why it lies so convincingly."

## What you will learn

- The core objects in Salesforce and HubSpot, and how they relate.
- Identity in GTM data: company domains, people, emails, CRM IDs and external IDs.
- Lead-to-account matching, deduplication and merges.
- Account hierarchies (parents, subsidiaries, regional entities).
- Where GTM data lives (CRM, engagement tool, warehouse, enrichment tool) and how to keep it consistent.

---

## 5.1 Why the data model matters

Almost every GTM engineering failure is ultimately a data-model failure: duplicate accounts mean two reps call the same company; unmatched leads mean demo requests go to the wrong person; missing hierarchy means a subsidiary of your biggest customer is cold-prospected. Before you automate, understand the model.

## 5.2 Core CRM objects

### Salesforce (standard objects)

| Object | Represents | Key relationships |
|---|---|---|
| **Lead** | An unqualified person (often not yet linked to an account) | Converts into Contact + Account (+ Opportunity) |
| **Account** | A company (or a person, with Person Accounts) | Parent Account (hierarchy); has Contacts, Opportunities |
| **Contact** | A person at an Account | Belongs to Account; linked to Opportunities via Contact Roles |
| **Opportunity** | A potential deal | Belongs to Account; has Stage, Amount, Close Date, Owner |
| **Campaign** / **Campaign Member** | A marketing initiative / a Lead or Contact's membership in it | Used for attribution |
| **Task** / **Event** (Activities) | Calls, emails, meetings | Related to Lead/Contact and Account/Opportunity |
| **User** | A CRM user (rep) | Owns records |

The **Lead vs Contact** split is a long-standing Salesforce design: leads are people not yet associated with an account; contacts are. Many companies route inbound leads by first **matching them to existing accounts** (§5.5) so they do not sit as orphaned leads. Some companies avoid leads altogether and create contacts directly.

### HubSpot (standard objects)

| Object | Represents |
|---|---|
| **Contact** | A person (no separate Lead object; "lead status" and "lifecycle stage" properties track progress; HubSpot also introduced a Leads object for prospecting workflows) |
| **Company** | An organisation; HubSpot can auto-associate contacts to companies by **email domain** |
| **Deal** | A potential sale, in a pipeline with stages |
| **Ticket** | A support case |
| **Activities / engagements** | Emails, calls, meetings, notes, tasks |
| **Custom objects** | Available on higher tiers |

Associations link objects many-to-many, with labels (for example, "Decision maker").

### Other CRMs

Attio, Pipedrive, Close, Microsoft Dynamics 365 and others follow similar patterns. AI-native CRMs (Attio and newer entrants) emphasise flexible data models and built-in enrichment.

### Custom fields GTM engineers usually add

- Fit score, tier, score version and components
- ICP segment
- Enrichment source and date per key field
- Intent and signal fields (latest signal, signal date, signal type)
- Product usage summaries (for PLG)
- External IDs from other systems (warehouse ID, Clay row ID, product workspace ID)
- Do-not-contact and consent flags, with source and date (Chapter 16)

## 5.3 Identity: what makes two records "the same"?

| Entity | Best keys | Pitfalls |
|---|---|---|
| **Company** | **Primary web domain** (normalised: lowercase, strip `www.`, protocol and path) | Multiple domains (regional `.de`, `.co.uk`, product brands); rebrands; shared domains (gmail.com is not a company); subsidiaries with their own domains; companies without websites |
| **Company (alternative)** | LinkedIn company URL or ID, registry numbers (e.g. DUNS, Companies House number), provider IDs | Not always available; provider IDs differ |
| **Person** | **Work email** (lowercased) | People change jobs (same person, new email); aliases (`j.doe@` vs `jane@`); personal emails |
| **Person (alternative)** | LinkedIn profile URL | Vanity URLs change; scraping restrictions (Chapter 16) |
| **CRM record** | CRM IDs (Salesforce 18-char ID; HubSpot record ID) | Change on merge; differ per sandbox |

**Rule:** choose explicit keys for each entity, store them in dedicated, normalised fields, and use them for **upserts** (update if exists, else insert). Never match on free-text company names alone.

### Domain normalisation

```
"https://www.Acme-Logistics.com/about"  → "acme-logistics.com"
"ACME-LOGISTICS.COM."                     → "acme-logistics.com"
"jane@eu.acme-logistics.com"              → "acme-logistics.com"   (email domain, subdomain stripped)
"acme.co.uk"                              → "acme.co.uk"           (keep the public suffix correctly)
```

To strip subdomains correctly you need the **Public Suffix List** (so `acme.co.uk` is not reduced to `co.uk`). Libraries such as `tldextract` (Python) and `psl` (JavaScript) use it. The example in [`examples/dedupe-and-matching/`](../examples/dedupe-and-matching/) includes a small built-in suffix list for illustration.

### Free and personal email domains

`gmail.com`, `outlook.com`, `yahoo.com`, `icloud.com`, `proton.me` and hundreds of others are not companies. Keep a **free-email domain list** and never auto-create or match accounts on them. Inbound sign-ups from personal emails need other signals (enrichment by email, IP, or asking for the company).

## 5.4 Deduplication and merging

Duplicates arrive from imports, integrations, form fills, enrichment tools and humans. Strategies:

1. **Prevent:** match before create (upsert by key); validate forms; restrict who can import.
2. **Detect:** exact matching on normalised keys; **fuzzy matching** on names (token-based similarity, removing legal suffixes such as Inc, Ltd, GmbH, LLC) combined with domain, phone or address; specialised tools (Salesforce Duplicate Rules, HubSpot duplicate management, DemandTools, Cloudingo, RingLead/ZoomInfo Operations, Dedupely).
3. **Merge with survivorship rules:** which record survives (oldest? the one with open opportunities? the one owned by an active rep?) and which field values win (most recent? from a trusted source? non-empty?).
4. **Audit:** keep a log of merges. Merges change IDs and can break integrations that stored the old ID.

Be careful with automated merges. A wrong merge (two different "Acme" companies) is harder to undo than a duplicate. Use high thresholds for automatic merges, and queue uncertain matches for human review.

## 5.5 Lead-to-account matching

When a new lead arrives (`jane.doe@eu.acme-logistics.com`, company "ACME Logistics GmbH"), find the existing account:

1. **Domain match:** normalised email domain = account domain, or one of the account's **additional domains**.
2. **Hierarchy:** if the domain belongs to a subsidiary, link to the subsidiary *and* know the ultimate parent (for routing to the global account owner).
3. **Fuzzy name match** as a fallback, especially for personal emails or ambiguous domains, with a confidence score.
4. **Tie-breaking:** if several accounts match (duplicates!), prefer the one with an owner, open opportunities, or the most activity, and flag the duplicate.
5. **No match:** create a new account (if ICP-fit) or leave as a lead for qualification.

Commercial tools such as **LeanData**, **Default**, **Chili Piper**, **RingLead** and **Traction Complete** specialise in matching and routing in Salesforce. HubSpot's domain auto-association handles the simple case. A runnable matcher is in [`examples/dedupe-and-matching/`](../examples/dedupe-and-matching/).

## 5.6 Account hierarchies

Enterprise customers are families of entities: a global parent, regional subsidiaries, acquired brands. Hierarchy matters for:

- **Routing:** a lead from a subsidiary of a named account goes to that account's owner.
- **Exclusion:** do not cold-prospect subsidiaries of current customers without coordination.
- **Reporting:** total revenue and whitespace per corporate family.

Sources include enrichment providers' corporate linkage data (D&B family trees, ZoomInfo and others) and manual curation for top accounts. Store the `ultimate_parent_domain` on every account for simple grouping.

## 5.7 Where GTM data lives

| System | Holds | Notes |
|---|---|---|
| **CRM** | Accounts, contacts, deals, ownership, activities | System of record for commercial relationships and ownership |
| **Marketing automation** (HubSpot, Marketo, Pardot) | Email engagement, forms, nurture, consent | May be the system of record for subscription and consent status |
| **Sales engagement** (Outreach, Salesloft, Apollo, Instantly, Smartlead) | Sequences, emails, calls | Syncs activities and status to CRM |
| **Enrichment / workflow** (Clay and others) | Working tables of accounts and contacts with enrichment results | Often a staging area, not a system of record |
| **Product database / analytics** | Users, workspaces, usage events | System of record for product behaviour |
| **Warehouse** (Snowflake, BigQuery, Databricks, Postgres) | Copies of all of the above, modelled together | Best place for analysis, scoring and the "golden" customer view |
| **Billing** (Stripe, Chargebee, Zuora) | Subscriptions, revenue | System of record for revenue |

The two common architectures:

1. **CRM-centric:** tools read from and write to the CRM; the CRM holds the truth. Simple, but CRM data models and API limits constrain you.
2. **Warehouse-centric ("warehouse-native GTM"):** all sources land in the warehouse; models compute scores, segments and signals; **reverse ETL** pushes results to the CRM and tools (Chapter 12). More powerful and analysable; needs data engineering skills.

Most growing companies move from (1) toward (2).

### Field ownership

For every important field, decide **which system owns it**: who may write it, and who only reads it. For example: *Employee count*, owned by the enrichment job and not editable by reps; *Account owner*, owned by routing and territory logic, changed only through a defined process; *Lifecycle stage*, owned by marketing automation rules plus sales conversions. Write this down. Conflicting writers cause "flapping" values and broken automation. (The integration book's [Chapter 9](../../integration-design-engineer/chapters/09-data-integration.md) covers bidirectional sync and conflict rules in depth.)

## 5.8 Data quality metrics

Track, at least monthly:

- **Completeness:** % of accounts with domain, industry, employee count, owner; % of contacts with verified email and title.
- **Validity:** % of emails passing verification; % of domains that resolve.
- **Uniqueness:** duplicate rate for accounts and contacts.
- **Freshness:** % of records enriched in the last 6–12 months.
- **Consistency:** % of contacts whose email domain matches their account domain.

Show these on a dashboard. Data quality that is not measured degrades silently.

---

## Summary

- Learn the CRM objects (Salesforce Lead/Account/Contact/Opportunity; HubSpot Contact/Company/Deal) and their relationships.
- Use explicit, normalised identity keys: domain for companies (with Public Suffix List handling and free-email exclusion), email for people, CRM and external IDs for records.
- Prevent, detect and carefully merge duplicates with survivorship rules. Prefer human review for uncertain matches.
- Match leads to accounts by domain, hierarchy and fuzzy name, with tie-breaking rules.
- Decide where each kind of data lives and which system owns each field. Measure data quality.

## Exercises

See [`exercises/05-data-model.md`](../exercises/05-data-model.md).

## Further reading

- Salesforce data model documentation (developer.salesforce.com); HubSpot CRM object documentation (developers.hubspot.com).
- Public Suffix List (publicsuffix.org).
- *The Integration Design Engineer*, Chapters 4 (identifiers and mapping) and 9 (bidirectional sync and MDM).
