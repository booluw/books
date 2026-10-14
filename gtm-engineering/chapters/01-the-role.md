# Chapter 1. What a GTM Engineer Is

> "Every sales team is a data problem wearing a suit."

## What you will learn

- What "go-to-market" means, and what problem GTM engineering solves.
- What a GTM engineer actually does, week to week.
- How the role differs from RevOps, sales ops, marketing ops, sales engineering and growth engineering.
- Where the title came from and how fast it has spread *(as of October 2026)*.
- The skills map that the rest of the book teaches.

---

## 1.1 Go-to-market, defined

**Go-to-market (GTM)** is everything a company does to get its product into the hands of paying customers: deciding *who* to sell to, *how* to reach them, *what* to say, *who* on the team handles them, and *how* they are converted, onboarded and expanded. In B2B software the GTM organisation usually includes:

| Team | What it does |
|---|---|
| **Marketing** | Creates awareness and demand: content, ads, events, website, email. Produces **leads**, people who have shown interest. |
| **Sales development (SDRs/BDRs)** | Qualifies inbound leads and prospects outbound into target accounts to book **meetings**. (SDR = sales development representative; BDR = business development representative. Often interchangeable.) |
| **Sales (account executives, AEs)** | Runs the sales process from first meeting to signed contract. |
| **Customer success (CS) and account management** | Onboards customers, keeps them, and expands them (upsell, cross-sell, renewals). |
| **Operations (RevOps, sales ops, marketing ops)** | Runs the systems, data, processes and reporting behind all of the above. |

Each team depends on data and systems: lists of target companies, contact details, signals of buying intent, a CRM recording every interaction, rules for who gets which lead, emails sent at scale, dashboards showing what works. When these systems are weak, salespeople spend most of their time on research, data entry and chasing the wrong prospects. Salesforce's long-running *State of Sales* surveys have repeatedly found that sellers spend only around 30% of their time actually selling.

## 1.2 The problem GTM engineering solves

Consider a 120-person B2B software company selling to mid-sized logistics firms. Its GTM problems are typical:

1. **Who should we target?** There are maybe 40,000 logistics companies in North America. Which 3,000 are a good fit? Which of those are *in market* this quarter?
2. **Who are the people?** At each account, who is the VP of Operations? What is their verified email? Did they change jobs last month?
3. **When should we reach out?** The company just raised money, hired a new COO, posted jobs for "dispatch analyst", visited our pricing page twice, or started using a competitor's API. Each is a **signal**.
4. **What do we say?** A generic email gets ignored. A message that references the prospect's specific situation gets replies, but writing one by hand takes 15 minutes.
5. **Who handles it?** A demo request at 2:13 p.m. must reach the right AE (territory, segment, existing owner) within minutes. Research shows that responding within five minutes dramatically raises the chance of connecting.
6. **Did it work?** Which plays produce pipeline and revenue, not just replies?

Ten years ago, a company solved these with headcount: researchers, SDRs, ops analysts. Today a GTM engineer solves them with systems: an enrichment pipeline that builds and refreshes the target list; signal monitors that detect buying moments; AI research agents that write tailored first lines; routing automation that assigns leads in seconds; deliverability infrastructure that lands emails in inboxes; and data models that measure what converts.

> **A GTM engineer turns go-to-market strategy into automated, data-driven systems that find, engage and convert the right buyers, and keeps those systems reliable, compliant and measurable.**

## 1.3 Origin and growth of the title *(as of October 2026)*

- **Origin.** Clay, the data-enrichment and automation platform, says it coined "GTM engineering" in 2023. Its co-founder Varun Anand told Crunchbase News so, and Clay's own guides popularised the term. When Clay first used it, almost no one had heard of a GTM engineer.
- **Growth.** Bloomberry's analysis of more than 1,000 GTM engineering job listings (updated January 2026) reported postings up about 205% year on year from 2024 to 2025. RevGuild's 2026 market report found 244 US GTM Engineer postings in April 2026 alone, more than the previous seven months combined.
- **Concentration.** Much of the demand, training and credentialing runs through one vendor's ecosystem. RevGuild notes this explicitly, and it is worth remembering when reading growth claims that come from Clay. Clay itself was valued at $3.1 billion in its August 2025 Series C and at about $7.1 billion after a $115 million Series D reported in September 2026.

The role is new, so titles vary: GTM Engineer, Growth Engineer (GTM), Revenue Engineer, GTM Automation Engineer, Outbound Engineer, Growth Operations Engineer, Clay Engineer, and sometimes "RevOps Engineer".

## 1.4 What a GTM engineer does

The work clusters into seven areas. Each has a chapter in Part III.

| Area | Typical deliverables | Chapter |
|---|---|---|
| **Data and enrichment** | Target account lists (TAM), contact sourcing, waterfall enrichment, email verification, job-change tracking | 7 |
| **Signals** | Monitors for funding, hiring, tech-stack changes, website visits, product usage, champion moves; signal-to-action pipelines | 8 |
| **Scoring and routing** | ICP fit scores, intent scores, lead-to-account matching, round-robin and territory routing, speed-to-lead SLAs | 9 |
| **Outbound automation** | Sequences, AI-assisted personalisation, multichannel orchestration (email, LinkedIn, phone) | 10 |
| **Deliverability** | Sending domains, inboxes, DNS authentication, warmup, volume control, reputation monitoring | 11 |
| **Inbound and product-led** | Form enrichment, instant qualification, product-qualified leads (PQLs), warehouse-to-CRM syncs | 12 |
| **AI agents and tooling** | Research agents, AI SDR evaluation, internal GTM tools, MCP integrations | 13 |

Supporting all of it: **CRM engineering** (Chapter 14), **analytics** (Chapter 15), **compliance and security** (Chapter 16) and **stack management** (Chapter 17).

### A realistic week *(composite)*

| Day | Work |
|---|---|
| Monday | Pipeline review with the sales leader. Outbound reply rates fell from 4% to 1.5% last week. Diagnose: one sending domain's spam rate spiked in Google Postmaster Tools. Pause it and rebalance volume. |
| Tuesday | Build a new play: "companies that posted 3+ operations jobs in 30 days and use a legacy TMS." Source accounts, enrich contacts through a three-provider waterfall, verify emails, and draft AI-personalised first lines. QA 50 samples by hand. |
| Wednesday | Fix routing: enterprise demo requests from existing customers' subsidiaries were going to the SDR queue instead of the account owner. Add parent–child account matching. |
| Thursday | Ship a PQL alert: when a free-tier workspace adds 5+ users and connects an integration, create a task for the owning AE with context. Document it. |
| Friday | Report: last month's plays by meetings, pipeline and cost per meeting. Kill two underperforming plays. Credits review: enrichment spend is 30% over budget, so add caching for re-enrichment. |

Notice the mix: data engineering, operations, copywriting judgement, analytics and stakeholder management.

## 1.5 How it differs from neighbouring roles

| Role | Focus | Key difference from GTM engineering |
|---|---|---|
| **Sales operations** | Sales-team efficiency: forecasting, territories, quotas, compensation plans, CRM administration | Operates and analyses; usually does not build pipeline-generating automation. |
| **Marketing operations** | Marketing automation (HubSpot, Marketo), campaigns, lead management, attribution | Owns marketing systems; GTM engineering spans sales and marketing and leans to outbound and data. |
| **Revenue operations (RevOps)** | Cross-functional alignment of sales, marketing and CS: process, data governance, reporting | Manages and optimises existing systems and process; GTM engineers build net-new pipeline infrastructure. At small companies one person does both. |
| **Sales engineer / solutions engineer** | Pre-sales: demos, technical discovery and proofs of concept with prospects | Customer-facing in deals; GTM engineers are internal builders. |
| **Growth engineer** | Product-led growth: onboarding flows, experiments, activation in the product | Works inside the product; GTM engineers work in the commercial systems around it (they overlap on PLG). |
| **Data engineer / analytics engineer** | Warehouses, pipelines and models for analytics | Broader data platform; GTM engineers focus on GTM data and its activation. |
| **SDR** | Personally prospects and books meetings | GTM engineers build the systems that make SDRs (or AI agents) productive. |

One analysis of job postings concluded that GTM engineering and RevOps postings overlap heavily. The difference is emphasis: RevOps postings lead with CRM ownership, GTM engineering postings lead with automation and integration. Treat the boundary as a spectrum, from *operate* to *build*.

## 1.6 Where GTM engineers work

1. **Startups and scale-ups (most common).** A first or second GTM engineer reporting to the head of growth, the CRO (chief revenue officer) or a founder. Broad scope: everything from domain setup to dashboards.
2. **Larger B2B companies.** A GTM engineering team inside RevOps or growth, alongside Salesforce admins and analysts. More governance and specialisation.
3. **Agencies.** Outbound and "Clay agencies" build plays for many clients. Fast learning and high volume, but less ownership of long-term systems.
4. **Vendors.** GTM tool companies (Clay, Apollo, enrichment and signal vendors) hire GTM engineers for their own pipeline and as solutions experts for customers.
5. **Freelance and fractional.** Many practitioners work as fractional GTM engineers for several startups.

## 1.7 The skills map

The rest of the book teaches these skills. Rate yourself now, and again at the end. Chapter 19 turns gaps into a plan.

| Area | Foundational | Proficient | Advanced |
|---|---|---|---|
| **GTM fundamentals** (Ch. 3–4) | Knows funnel stages and motions | Defines ICPs and plays from data | Shapes GTM strategy with leadership |
| **Data modelling** (Ch. 5) | Knows CRM objects | Designs matching and dedup | Owns the GTM data model across CRM and warehouse |
| **Technical** (Ch. 6) | Spreadsheets, no-code automation, basic API calls | SQL, Python or JS, webhooks, JSON | Builds services, warehouse pipelines, internal tools |
| **Enrichment** (Ch. 7) | Uses one provider | Designs cost-aware waterfalls with verification | Runs TAM and data quality at scale |
| **Signals** (Ch. 8) | Uses intent dashboards | Builds signal pipelines | Designs scoring from signal-to-outcome data |
| **Scoring and routing** (Ch. 9) | Configures round robin | Builds fit and intent scoring, matching, SLAs | Calibrates models against conversion data |
| **Outbound** (Ch. 10) | Runs sequences | AI personalisation with QA | Designs a multichannel outbound system |
| **Deliverability** (Ch. 11) | Knows SPF/DKIM/DMARC exist | Sets up and monitors infrastructure | Diagnoses and recovers reputation |
| **Inbound and PLG** (Ch. 12) | Form enrichment | PQL models, reverse ETL | Warehouse-native GTM |
| **AI** (Ch. 13) | Uses AI research columns | Builds agents with evaluation | Designs safe agentic workflows |
| **CRM engineering** (Ch. 14) | Admin basics | Automation, hygiene jobs | Architecture and governance |
| **Analytics** (Ch. 15) | Reports on activity | Measures pipeline by play | Experiments and attribution |
| **Compliance and security** (Ch. 16) | Knows the rules exist | Implements opt-outs and LIAs | Designs compliant systems with legal |
| **Communication** | Clear updates | Translates strategy into specs | Influences GTM leadership |

## 1.8 Hype and reality

GTM engineering attracts a lot of vendor marketing ("replace three sales hires"). Keep a balanced view:

- **Automation amplifies strategy, good or bad.** A system that sends 10,000 well-personalised emails to the wrong audience produces 10,000 annoyed people and a damaged domain.
- **Data quality is the bottleneck.** AI personalisation built on wrong job titles and stale emails fails loudly.
- **Volume is not the goal.** Mailbox providers now penalise spammy behaviour hard (Chapter 11), and buyers are flooded with AI-written outreach. The best GTM engineers increase relevance, not just volume.
- **AI SDRs are useful but immature.** In March 2025, TechCrunch reported allegations that the AI SDR start-up 11x had shown logos of companies that said they were not customers and had overstated revenue. The company disputed some claims, and its founder later stepped down as CEO. Evaluate AI tools on measured outcomes, not claims (Chapter 13).
- **The fundamentals last.** Know your buyer, measure what matters, keep data clean, respect recipients and the law. These outlast every tool on the market.

---

## Summary

- Go-to-market is how a company finds, reaches and converts customers. GTM engineering builds the systems behind it.
- The title was coined by Clay in 2023 and grew rapidly through 2025–2026, though much of the ecosystem centres on one vendor.
- The work spans data and enrichment, signals, scoring and routing, outbound, deliverability, inbound and PLG, and AI agents, supported by CRM engineering, analytics and compliance.
- The role sits between RevOps (operate) and software engineering (build).

## Exercises

See [`exercises/01-the-role.md`](../exercises/01-the-role.md).

## Further reading

- Clay, *The GTM Engineering Guide* (clay.com).
- Bloomberry, "I analyzed 1,000+ GTM engineering jobs" (January 2026).
- RevGuild, *GTM Engineer Salary and Market Report 2026*.
- Crunchbase News coverage of Clay's funding rounds.
