# Chapter 2. From Sales Ops to GTM Engineering: A Short History

> "Every wave of sales technology promised to remove the busywork. Every wave also created a new job: running the technology."

## What you will learn

- How B2B go-to-market evolved from Rolodexes to AI agents.
- Which ideas from each era still shape today's systems.
- Why GTM engineering appeared in the early 2020s.

---

## 2.1 Era 1: Relationships and Rolodexes (to the 1980s)

Selling was personal and local. Salespeople kept contacts on index cards in a **Rolodex**, prospected by phone and by mail, and managed territories by geography. Lists of prospects came from directories, trade associations and purchased mailing lists. **Direct mail** and **telemarketing** were the "outbound" channels.

What survives: territories, quotas and the idea of the sales **pipeline**, deals moving through stages.

## 2.2 Era 2: Contact management and early CRM (1980s–1990s)

Software replaced the Rolodex: **ACT!** (1987) and **GoldMine** brought contact management to PCs. **Siebel Systems** (1993) built enterprise CRM and sales-force automation (SFA) and dominated the 1990s. Database marketing grew, and companies began scoring and segmenting customers.

What survives: the CRM data model of accounts, contacts, opportunities and activities (Chapter 5).

## 2.3 Era 3: Cloud CRM and marketing automation (1999–2010)

- **Salesforce** (founded 1999) moved CRM to the cloud with its "No Software" campaign, opening it to companies of every size. Its AppExchange (2005) created an ecosystem of add-ons.
- **Marketing automation** platforms appeared: **Eloqua** (1999, acquired by Oracle in 2012), **Marketo** (2006, acquired by Adobe in 2018), **Pardot** (2007, acquired by ExactTarget and then Salesforce) and **HubSpot** (2006), whose founders popularised **inbound marketing**: attract buyers with content, then nurture them.
- **Lead scoring** and the **marketing qualified lead (MQL)** became standard. SiriusDecisions' **Demand Waterfall** (2006) gave a common vocabulary for funnel stages.
- **Data providers** such as Jigsaw (crowd-sourced contacts, bought by Salesforce in 2010 and later Data.com), ZoomInfo (founded as DiscoverOrg in 2007; merged 2019) and InsideView sold contact and company data.

What survives: MQLs, lead scoring and nurture programmes, and the split between marketing automation and CRM.

## 2.4 Era 4: Predictable revenue and sales development (2011–2018)

- Aaron Ross and Marylou Tyler's *Predictable Revenue* (2011) described Salesforce's outbound process. It popularised **specialised roles**: SDRs prospect, AEs close, CSMs retain.
- **Sales engagement platforms** automated multi-step email and call **sequences** (also called *cadences*): **Outreach** (2014), **Salesloft** (2011) and **Yesware**.
- **Sales intelligence** grew: LinkedIn Sales Navigator (2014), DiscoverOrg and ZoomInfo, Clearbit (enrichment APIs, 2015).
- **Account-based marketing (ABM)** rose: target named accounts with coordinated sales and marketing. Platforms included Engagio, Terminus, **Demandbase** and **6sense** (predictive and intent analytics).
- **Intent data** emerged. **Bombora**'s publisher co-op (2014) tracks which companies research which topics.
- **Sales operations** became a strategic function, and conversation intelligence (Gong, 2015) recorded and analysed calls.

What survives: the SDR/AE/CSM model, sequences, intent data, ABM, and the "sales tech stack" of 10–20 tools.

## 2.5 Era 5: RevOps and the modern data stack (2018–2022)

- **Revenue operations (RevOps)** merged sales ops, marketing ops and CS ops into one function owning the full revenue process and its data.
- **Product-led growth (PLG)**: companies such as Slack, Zoom, Atlassian, Figma and Notion let users adopt a product before talking to sales. That created **product-qualified leads (PQLs)** and the need to sync product data into the CRM.
- The **modern data stack** (Chapter 12) arrived: cloud warehouses (Snowflake, BigQuery), ELT (Fivetran), dbt, and **reverse ETL** (Hightouch, Census), which syncs warehouse models back into Salesforce and HubSpot.
- No-code automation (Zapier, Make) let operations people wire tools together without engineers.
- **Clay** launched (founded 2017; product pivot to spreadsheet-style enrichment around 2022), combining many data providers, web scraping and later AI into one programmable table.

What survives: warehouse-centric GTM data, RevOps as a function, PLG signals.

## 2.6 Era 6: Generative AI and GTM engineering (2023–present)

- **Large language models** (ChatGPT, November 2022; Claude, March 2023, and others) made it cheap to research accounts and write personalised messages at scale. Clay's **Claygent** web-research agent and AI columns put this in the hands of operations people.
- **Clay coined "GTM engineer" in 2023**, describing builders who combine data, automation and AI to create pipeline. Postings grew rapidly through 2025 and 2026 (Chapter 1).
- **Email-provider crackdowns:** in February 2024, Google and Yahoo began enforcing bulk-sender requirements (authentication, one-click unsubscribe, spam rates below 0.3%). Microsoft followed for Outlook.com consumer domains from May 2025. High-volume, low-quality outbound became much harder (Chapter 11).
- **AI SDRs** (11x, Artisan, and agents from incumbents such as Salesforce Agentforce and HubSpot Breeze) promised autonomous prospecting, with mixed results and some controversy (Chapter 13).
- **Consolidation:** HubSpot acquired Clearbit (December 2023), which became Breeze Intelligence inside HubSpot. Clari and Salesloft merged, closing in December 2025. ZoomInfo repositioned itself as a "GTM" platform.
- **Security wake-up call:** in August 2025, attackers tracked as UNC6395 stole OAuth tokens from the Salesloft Drift integration and used them to pull data from hundreds of organisations' Salesforce instances (Chapter 16).
- **Agents and MCP:** GTM vendors began exposing their data and actions to AI assistants through the Model Context Protocol. Salesloft and Clari launched an MCP server in April 2026, and Salesforce announced API and MCP access to its platform capabilities in 2026.

## 2.7 Patterns that repeat

| Pattern | Then | Now |
|---|---|---|
| Buy a list, blast it | Mailing lists, telemarketing | Bulk scraped lists through cold-email tools, now punished by mailbox providers |
| Score leads | MQL points for form fills | Fit plus intent plus product signals, sometimes with ML |
| Specialise roles | SDR / AE / CSM | Human plus agent division of labour |
| Integrate the stack | AppExchange apps, point integrations | Clay tables, iPaaS, warehouse plus reverse ETL, MCP |
| Data decays | Rolodex cards go stale | B2B contact data decays roughly 20–30% per year (an industry rule of thumb), hence continuous re-enrichment |
| Volume vs relevance | More calls per day | More emails per day vs signal-based, relevant outreach |

Every era rediscovers the same truth: **relevance beats volume**, and **data quality decides whether automation helps or hurts**.

---

## Summary

- B2B GTM moved from Rolodexes, through CRM and marketing automation, sales engagement and ABM, RevOps and the modern data stack, to generative AI.
- GTM engineering emerged around 2023, when AI, programmable data platforms and warehouse tooling let one technical person build what used to take a team.
- Mailbox-provider rules, buyer fatigue, consolidation and security incidents now shape what good GTM engineering looks like.

## Exercises

See [`exercises/02-history.md`](../exercises/02-history.md).

## Further reading

- Aaron Ross and Marylou Tyler, *Predictable Revenue* (2011).
- Brian Halligan and Dharmesh Shah, *Inbound Marketing* (2009).
- Mark Roberge, *The Sales Acceleration Formula* (2015).
- Wes Bush, *Product-Led Growth* (2019).
