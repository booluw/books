# Chapter 4. ICP, TAM and Segmentation

> "If you're selling to everyone, you're selling to no one."

## What you will learn

- What an Ideal Customer Profile (ICP) is, and how to derive one from data rather than opinion.
- Buyer personas and the buying committee.
- How to build a Total Addressable Market (TAM) list of real accounts.
- Firmographic, technographic, behavioural and "custom" attributes, and where they come from.
- Fit scoring, tiering and segmentation.

---

## 4.1 Definitions

- **ICP (Ideal Customer Profile):** a description of the *companies* most likely to buy, succeed and expand. For example: "US and Canadian third-party logistics providers with 200–2,000 employees, running a legacy transport management system, with a dedicated operations-analytics function."
- **Persona:** a description of the *people* involved in buying: titles, responsibilities, pains, goals. For example: "VP Operations, measured on cost per shipment, frustrated by manual dispatch."
- **TAM (Total Addressable Market):** in finance, the total revenue opportunity. In GTM engineering, usually the concrete **list of every account that matches your ICP**, the universe your systems target. Related terms: **SAM** (serviceable addressable market, the part you can actually serve) and **SOM** (serviceable obtainable market, what you can realistically win).
- **Segment:** a subset of the TAM handled differently (by size, industry, region or motion).
- **Tier:** a priority level within the TAM (Tier 1 = best fit, highest-touch).

## 4.2 Deriving the ICP from data

Founders and sales leaders usually have a gut-feel ICP. A GTM engineer's job is to **test it against data**.

**Method:**

1. **Export closed-won and closed-lost opportunities** (and, if available, churned customers and best expanders) for the last 1–3 years, with amounts, cycle lengths and outcomes.
2. **Enrich every account** with candidate attributes: employee count, revenue band, industry, HQ country, funding stage, growth rate (headcount change), tech stack, hiring activity, business model (B2B/B2C), ownership (public, PE-backed, VC-backed).
3. **Compare distributions** of each attribute between won and lost deals, and between high- and low-value customers. Compute **win rate by segment**, **ACV by segment**, **sales cycle by segment**, and **retention or NRR by segment**.
4. **Look for the intersections** where win rate, deal size and retention are all high. That is the ICP core.
5. **Check sample sizes.** Twelve deals in a segment is an anecdote, not a pattern. Be explicit about confidence.
6. **Validate qualitatively** with the sales team and by reading call notes: *why* did those deals close?
7. **Write it down** (template: [`templates/icp-definition.md`](../templates/icp-definition.md)) with must-haves, nice-to-haves and disqualifiers, and revisit it quarterly.

A simple, explainable analysis, such as win-rate tables by attribute, beats an opaque model for this purpose: the output has to persuade humans.

### Disqualifiers matter as much as qualifiers

Examples: companies too small to afford you, regions you cannot serve or sell into legally, industries with regulatory blockers, competitors, existing customers (for net-new plays), companies in active churn or dispute, and anyone who opted out of contact.

## 4.3 Attributes and where they come from

| Category | Examples | Typical sources |
|---|---|---|
| **Firmographic** | Industry (NAICS/SIC or a provider's taxonomy), employee count, revenue, HQ location, founding year, ownership, funding | Enrichment providers (ZoomInfo, Apollo, Clearbit/Breeze, PeopleDataLabs, Crunchbase, LinkedIn), company websites, registries |
| **Technographic** | CRM, cloud provider, analytics tools, competitor products in use | BuiltWith, Wappalyzer, HG Insights, job descriptions, DNS records (MX, SPF includes), public code |
| **Growth and change** | Headcount growth, new funding, new executives, office openings, M&A | Enrichment, news, Crunchbase, job-change data, LinkedIn |
| **Hiring** | Open roles by function and keyword | Job boards and careers pages (scraped or via providers) |
| **Behavioural / intent** | Website visits, content engagement, third-party research topics, review-site activity | Your analytics, reverse-IP de-anonymisation, Bombora, G2, 6sense (Chapter 8) |
| **Product usage** | Sign-ups, active users, features adopted | Your product database and warehouse (Chapter 12) |
| **Custom / AI-derived** | "Do they offer same-day delivery?", "Do they sell to enterprise?", "Do they have a public API?" | Website research with AI agents (Chapter 13), with verification |

**Custom attributes are where GTM engineers create advantage.** Every competitor can buy "employee count". Few will systematically answer "does this company run its own fleet?" across 40,000 websites. That kind of attribute often predicts fit better than standard firmographics.

### Data quality warnings

- **Industry codes are noisy.** Providers classify companies differently; a "software" company may be a services firm. Use several signals.
- **Employee counts disagree** between providers and LinkedIn, sometimes by 2×. Use ranges, not exact thresholds, and record the source.
- **Revenue is often estimated** for private companies. Treat it as a weak signal.
- **Everything decays.** Companies grow, shrink, merge and die. Refresh on a schedule (Chapter 7).

## 4.4 Building the TAM list

Steps:

1. **Seed** the universe from one or more sources: a provider's company search with ICP filters, industry directories, government registries, marketplaces or integration partner directories, lookalikes of best customers, scraped lists (respecting terms of service, Chapter 16).
2. **Normalise and de-duplicate** companies by **domain** (the most reliable company key), handling subsidiaries, regional domains and rebrands (Chapter 5).
3. **Enrich** missing attributes (Chapter 7).
4. **Apply qualifiers and disqualifiers.**
5. **Score fit** (§4.5) and assign **tiers**.
6. **Exclude** existing customers, open opportunities (for net-new plays), competitors, partners, and do-not-contact accounts.
7. **Load** into the CRM (accounts) or a warehouse table, with owner assignment where applicable (Chapter 9).
8. **Refresh** periodically: new companies appear, others leave the ICP.

Size sanity check: a TAM of 300 accounts suggests account-based, highly researched outreach. A TAM of 300,000 suggests automated, signal-triggered plays. Compare the TAM with your sales capacity: if each AE can actively work about 150 accounts and you have 10 AEs, only about 1,500 accounts can be **actively worked** at any time. Tiering decides which.

## 4.5 Fit scoring and tiering

A **fit score** estimates how well an account matches the ICP, independent of timing. (Timing is **intent**, Chapter 8.)

### Rules-based scoring

Assign points per attribute, with weights that reflect the win-rate analysis:

| Attribute | Condition | Points |
|---|---|---|
| Industry | 3PL / freight forwarding | +30 |
| Employees | 200–2,000 | +25; 100–199 or 2,001–5,000: +10 |
| Region | US or Canada | +15 |
| Tech | Uses a legacy TMS | +20 |
| Hiring | ≥ 2 open operations roles | +10 |
| Disqualifier | Competitor or existing customer | Exclude |

Tiers: ≥ 80 = Tier 1, 55–79 = Tier 2, 30–54 = Tier 3, < 30 = not ICP.

Advantages: transparent, easy to explain and adjust. Disadvantages: weights are guesses until calibrated.

### Calibrating and modelling

- **Calibrate** weights against outcomes: compare win rates by score band each quarter. If Tier 1 does not win much more often than Tier 3, the score is not working.
- **Statistical models** (logistic regression, gradient-boosted trees) trained on won and lost accounts can improve ranking when you have enough data, typically hundreds of outcomes. Watch for **leakage**: attributes that only exist *because* the account became a customer, such as "uses our integration".
- **Lookalike modelling** ranks accounts by similarity to best customers (for example, nearest neighbours on firmographic and technographic features). It is useful when outcomes are few.

Whatever the method: **keep it explainable**, **store the score with its version and components** (so sellers can see *why* an account is Tier 1), and **review it regularly**.

A runnable rules-based scorer with explanation output is in [`examples/icp-scoring/`](../examples/icp-scoring/).

## 4.6 Personas and the buying committee

For each segment, identify which roles to contact:

| Role in purchase | Example titles | What they care about |
|---|---|---|
| Economic buyer | COO, VP Operations | Cost, risk, strategic fit |
| Champion | Director of Operations, Head of Dispatch | Solving daily pain, career win |
| Technical evaluator | IT Director, Systems Architect | Integration, security, effort |
| End users | Dispatch managers | Ease of use |
| Blockers / gatekeepers | Procurement, Security, Legal | Terms, compliance, risk |

Translate personas into **title-matching rules** for sourcing contacts: lists of include and exclude keywords, seniority levels and departments. Titles are messy ("Head of Ops", "Operations Lead", "VP, Ops & Fulfilment"). Normalise them with keyword rules or AI classification, and review a sample by hand (Chapters 7 and 13).

**Multithreading**, engaging several committee members, is consistently associated with higher win rates in enterprise sales. Your systems should source several personas per account, not just one.

## 4.7 Segmentation drives everything downstream

Segments and tiers determine:

- **Routing:** which team or rep (Chapter 9).
- **Play selection:** Tier 1 gets researched, multichannel, human-reviewed outreach; Tier 3 gets automated, signal-triggered sequences.
- **Budget:** how many enrichment credits to spend per account.
- **Reporting:** pipeline and conversion by segment.

Keep segment logic in **one place** (a field computed by one job, or one warehouse model). Do not copy it into five tools.

---

## Summary

- The ICP describes companies most likely to buy, succeed and expand. Personas describe the people. Derive both from closed-won and closed-lost data, then validate with sales.
- Use firmographic, technographic, growth, hiring, intent, product and custom AI-derived attributes. Custom attributes are where you create advantage.
- Build the TAM as a deduplicated, enriched, scored and tiered account list, refreshed regularly and sized against sales capacity.
- Keep fit scoring explainable, versioned and calibrated against outcomes. Keep segment logic in one place.

## Exercises

See [`exercises/04-icp-and-tam.md`](../exercises/04-icp-and-tam.md).

## Further reading

- April Dunford, *Obviously Awesome* (2019), on positioning and best-fit customers.
- Geoffrey Moore, *Crossing the Chasm* (3rd edition, 2014), on target segments.
- Clay's guides on TAM building and custom signals.
