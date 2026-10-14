# Chapter 19. Becoming a GTM Engineer

> "Show, don't tell. A portfolio of working plays beats any certificate."

## What you will learn

- Entry paths into GTM engineering and which skills transfer.
- A 6-month learning roadmap with portfolio projects.
- Credentials and communities *(as of October 2026)*.
- Salaries and market data, with caveats.
- How to build a portfolio, write a résumé and pass interviews, including a take-home exercise.
- Career paths beyond the role.

---

## 19.1 Entry paths

| Background | Strengths | Gaps to close |
|---|---|---|
| **SDR / BDR** | Knows buyers, messaging, outbound reality | Data, automation, SQL/Python, systems thinking |
| **Sales ops / RevOps / marketing ops** | CRM, process, reporting | Building net-new automation; code; enrichment and signals; deliverability |
| **Software / data engineer** | Code, data pipelines, APIs | GTM fundamentals (Chapters 3–4), copy judgement, stakeholder skills with sales |
| **Growth marketer** | Experiments, funnels, copy | CRM data model, outbound infrastructure, code |
| **Agency / freelancer (Clay or outbound agency)** | High volume of plays, many tools | Depth in governance, measurement, long-term ownership |
| **Graduate / career changer** | Fresh start | Everything; follow the roadmap |

Many GTM engineers start by **automating their own SDR or ops work**, then become the team's go-to builder.

## 19.2 A 6-month roadmap

Assumes roughly 8–10 hours a week. Adjust to your background.

### Month 1: GTM fundamentals and data model

- Read Chapters 1–5. Learn the funnel vocabulary and metrics by heart.
- Create free HubSpot and Salesforce Developer Edition accounts; build accounts, contacts, deals; explore their APIs.
- **Project 1:** reverse-funnel model for a real or hypothetical company (spreadsheet or [`examples/funnel-metrics/`](../examples/funnel-metrics/)).

### Month 2: data and enrichment

- Learn Clay (Clay University, free tiers) or an equivalent; learn SQL basics.
- Build a TAM for a niche: 200–500 companies with custom AI-researched attributes, deduplicated and scored.
- **Project 2:** TAM + ICP scoring with explainable scores and a short write-up of the ICP hypothesis.

### Month 3: signals and outbound

- Build a signal monitor (hiring or funding) and a play brief.
- Set up a sending domain with SPF, DKIM and DMARC (on a domain you own; send only legitimate, compliant messages, or use a test environment).
- **Project 3:** a full play: list, enrichment waterfall, verification, safe AI personalisation with QA, and a sequence design. Show sample outputs and your QA process. You don't need to send at scale to demonstrate the system.

### Month 4: code and integrations

- Python or JavaScript basics; APIs and webhooks; a scheduled job.
- **Project 4:** an inbound pipeline: a webhook receives a form submission → enrichment → lead-to-account matching → routing decision → CRM upsert (use the examples in this book as a base).

### Month 5: analytics and AI evaluation

- SQL funnel analysis by cohort; an experiment design with sample-size calculation.
- Build an LLM classification step with an evaluation set (persona classification or reply categorisation).
- **Project 5:** an evaluation report comparing two prompts or models on accuracy and cost.

### Month 6: compliance, polish and job search

- Read Chapter 16; write an LIA for one of your plays; add suppression logic to your systems.
- Polish the portfolio; write two public posts about what you built and learned.
- Apply, network, and do mock interviews (§19.5).

## 19.3 Credentials and communities *(as of October 2026)*

- **Clay:** Clay University offers courses and cohorts. Clay ran certification tracks (for example Automated Outbound and Automated Inbound, assessed by reviewing a submitted table), but its certification page indicated new applications were **paused** pending a new version of the programme. Check the current status. Clay also runs a "Clay Experts" partner network for agencies and freelancers.
- **CRM credentials:** Salesforce Administrator and Platform App Builder (Trailhead); HubSpot Academy certifications (free).
- **Data:** dbt Fundamentals; basic SQL courses.
- **Tool certifications:** Outreach, Salesloft, Apollo and others offer user certifications. They are less valuable than a portfolio.
- **Communities:** Clay's community, RevGuild, Pavilion (GTM leaders), RevOps Co-op, Wizards of Ops, and LinkedIn GTM-engineering creators. Many practitioners share public playbooks.

As with all new roles, **portfolios and references matter more than certificates.** RevGuild noted that much of the field's credentialing routes through a single vendor, so broad skills (SQL, code, CRM, deliverability, compliance) keep you portable.

## 19.4 Salaries and market *(as of October 2026)*

There is no mature, independent salary survey for GTM engineering yet. Figures come from job-posting analyses and recruiters, many with commercial interests:

| Source | Finding |
|---|---|
| Bloomberry (1,000+ US postings, January 2026) | Median base about **$127,500**; senior total compensation reported around $210k–$280k |
| Cargo (509 postings with disclosed pay, April–July 2026) | Median about **$159k**; middle 50% $135k–$190k; mid-level ~$155k, senior ~$175k, staff ~$219k |
| RevGuild (71 disclosed salaries, 2026) | Top states New York (~$170k) and California (~$165k) |
| Betts Recruiting | National range roughly $100k–$180k; San Francisco $180k–$300k |

Takeaways: US base salaries for mid-level GTM engineers cluster roughly in the **$125k–$160k** range in 2026 postings, with senior and staff roles, AI companies and San Francisco and New York paying well above $200k. Only a minority of postings disclose pay, so treat all figures as indicative. Outside the US, data is thin; one vendor estimate for Germany spans roughly €48k–€145k+.

Demand: Bloomberry reported postings up about 205% from 2024 to 2025, and RevGuild counted 244 US postings in April 2026 alone. Growth is real, but concentrated in venture-backed B2B software and partly driven by one vendor's ecosystem. Build skills that transfer if the title evolves.

## 19.5 Portfolio, résumé and interviews

### Portfolio

A strong portfolio (a website, Notion page or GitHub repo) shows 3–5 projects, each with:

- the **business problem** and hypothesis;
- a **data flow diagram**;
- **screenshots or code** (tables, workflows, scripts);
- **QA and compliance** steps;
- **results** (real metrics if you ran it; otherwise expected metrics and how you would measure them);
- **what you'd do differently.**

Redact personal data from screenshots. Never publish scraped personal data.

### Résumé

Lead with outcomes: "Built signal-based outbound plays generating $2.1M pipeline in two quarters at $48 per meeting held", "Cut inbound speed-to-lead from 4 hours to 3 minutes; demo-to-opportunity rate rose 22%", "Reduced enrichment spend 38% with waterfall ordering and caching." List tools, but don't lead with them.

### Interview formats

1. **Screening:** your background and why GTM engineering.
2. **Case or design:** "Design an outbound system for selling X to Y", or "Our inbound conversion is poor; diagnose."
3. **Technical:** SQL queries, a small scripting task, API or webhook questions, or building in Clay live.
4. **Take-home:** build a small play or TAM (typically 3–6 hours; ask for scope limits).
5. **Stakeholder interview** with a sales leader: can you speak their language?

### Sample questions and answer outlines

**"Design a system to book meetings with VPs of Engineering at Series B–D fintechs."**
Clarify ICP, capacity and targets → TAM from funding data, filtered for fintech, with headcount and engineering-team-size thresholds → personas (VP Eng, Head of Platform) → signals (hiring platform engineers, new CTO, compliance deadlines, tech-stack changes) → waterfall enrichment and verification → exclusions and suppression → message angles per signal with grounded AI snippets and QA → secondary domains and inbox capacity math → sequence with LinkedIn touches → reply handling and routing to AEs → metrics, holdout, kill criteria → compliance (country rules) → cost per meeting estimate.

**"Our reply rate collapsed last week. What do you check?"**
Deliverability first (bounces, Postmaster spam rate, DNS changes breaking SPF or DKIM, blocklists, a new list source, link and tracking changes, volume spikes), then list quality and targeting, then copy. Compare across domains and inboxes to isolate the cause.

**"How would you evaluate an AI SDR vendor?"**
Controlled pilot vs a holdout on meetings held and pipeline; quality audit of every output sample; deliverability impact; controls (approval, caps, suppression); data terms; total cost; references verified directly (Chapter 13).

**"Write SQL for meeting-to-opportunity conversion by ICP tier for Q3 meetings."**
Cohort on meetings held in Q3; left join opportunities created within 90 days at the same account; group by tier; count distinct; note incomplete cohorts.

**"Walk me through SPF, DKIM and DMARC."**
SPF lists authorised senders (one record, 10-lookup limit, envelope sender); DKIM signs messages with a key published in DNS; DMARC sets policy and requires alignment with the From domain, with reporting. Mention 2024–2025 provider requirements (Chapter 11).

**"How do you route a demo request from someone at a subsidiary of an existing customer?"**
Match by domain to subsidiary → resolve parent via hierarchy → customer-first rule → route to the account manager (or the agreed owner) → notify with context → SLA timer.

More, with outlines, in [`exercises/19-career.md`](../exercises/19-career.md).

## 19.6 Career paths

- **Senior / staff GTM engineer:** owns architecture across the GTM stack; leads warehouse-native GTM.
- **Head of GTM engineering / growth engineering:** leads a team.
- **RevOps leadership:** broader operational ownership.
- **Growth or demand-generation leadership:** strategy plus systems.
- **Founder / agency:** many GTM engineers start agencies or tools.
- **Adjacent engineering:** data engineering, integration engineering (see this repository's other book), AI engineering.

---

## Summary

- People enter GTM engineering from SDR, ops, engineering, growth and agency backgrounds; close your specific gaps.
- Follow a 6-month roadmap of fundamentals, data, signals and outbound, code and integrations, analytics and AI evaluation, then compliance, with a portfolio project each month.
- Credentials exist (Clay, CRM, dbt), but portfolios and references matter more; Clay's certifications were paused at the time of writing.
- 2026 US base salaries cluster around $125k–$160k for mid-level roles, higher for senior roles; the data is thin and partly vendor-sourced.
- Present outcomes, show QA and compliance thinking, and practise system-design, diagnosis, SQL and evaluation questions.

## Exercises

See [`exercises/19-career.md`](../exercises/19-career.md).

## Further reading

- Bloomberry, RevGuild, Cargo and Betts Recruiting market reports (2026).
- Clay University; HubSpot Academy; Salesforce Trailhead.
