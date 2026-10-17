# Chapter 19. Becoming a Forward Deployed Engineer

> "The interview is a short deployment. Treat it like one."

## What you will learn

- Who becomes an FDE, and the common routes in.
- What the market looks like in 2026: employers, roles and pay, with caveats.
- How FDE interview loops work, including Palantir-style decomposition and learning rounds, and how to prepare.
- How to build a portfolio that shows FDE skills.
- A typical career ladder, and where FDEs go next.
- A 90-day plan for your first FDE role, and a learning roadmap.

Market and pay data in this chapter are *as of October 2026*, and come mostly from job-posting aggregators, recruiters and self-reported compensation sites. Treat them as indicative ranges, not facts.

---

## 19.1 Routes in

FDEs come from many backgrounds. The common routes:

| Background | Strengths to emphasise | Gaps to close |
|---|---|---|
| **Product / software engineer** | Engineering depth; shipping | Customer communication; ambiguity; enterprise data and security |
| **Start-up generalist** | Breadth; ownership; speed | Enterprise processes; documentation discipline |
| **Data engineer / analyst** | Data wrangling; SQL; pipelines | Application engineering; customer-facing work |
| **Solutions / sales engineer** | Customer skills; demos; product knowledge | Production engineering; owning delivery end to end |
| **Consultant (technical)** | Discovery; stakeholders; structure | Hands-on engineering depth |
| **ML / AI engineer** | Models; evaluation | Enterprise integration; stakeholders |
| **Domain expert who codes** (clinician, analyst, military, finance) | Credibility; domain knowledge | Software engineering rigour |
| **New graduate** | Learning speed; energy | Experience. Palantir and some others hire graduates into FDE roles; most AI start-ups prefer experienced engineers |

Internal moves are often the easiest route: product engineers volunteering for customer escalations, or solutions engineers taking on delivery, at a company that already has an FDE function.

## 19.2 The market *(as of October 2026)*

### Employers

- **Palantir**, which still uses the title **Forward Deployed Software Engineer (FDSE)**, alongside Deployment Strategist roles.
- **AI labs:** OpenAI (including the OpenAI Deployment Company), Anthropic (applied AI and forward deployed roles), Google DeepMind and others.
- **Cloud providers:** AWS's forward deployed engineering unit (Chapter 2) and equivalent teams elsewhere.
- **AI application start-ups** in legal, customer service, finance, healthcare, coding and agents.
- **Data and enterprise software vendors.**
- **Consultancies and systems integrators**, which became among the largest posters of FDE-titled jobs in 2026 (Chapter 2), and partner organisations training engineers through programmes such as Anthropic's Claude Frontier Academy.
- **Defence and government technology companies**, often requiring security clearance.

Chapter 1 §1.6 gives tests for telling genuine FDE roles from relabelled ones. Apply them to every posting.

### Pay

Reported compensation varies widely by company, level, location and source:

- **Advertised base salaries in the US** for FDE roles clustered around a median of roughly $190,000–$200,000 in 2026, according to aggregators analysing job postings (for example, Recruiting From Scratch reported a $195,000 median across 924 postings). Postings ranged from about $125,000 to over $300,000 in base pay; AI labs' advertised ranges were at the top (postings analysed by third parties showed ranges such as $185,000–$300,000 at OpenAI and $280,000–$320,000 at Anthropic, plus equity).
- **Total compensation** (base plus bonus plus equity) can be much higher at well-funded AI companies, especially at senior levels, because of equity. Self-reported figures on compensation sites vary by level and company.
- **UK:** Levels.fyi reported a median total compensation of about £163,000 for Forward Deployed Software Engineers in the UK (April 2026), with a middle-50% range of roughly £130,000–£224,000. This is a self-reported sample skewed towards well-paying employers.
- **Consultancy FDE roles** typically pay less than AI-lab roles, and are often closer to existing consulting grades.

Caveats: aggregator methodologies are opaque; self-reported data skews towards high-paying firms; equity values are uncertain; and titles cover very different jobs. Check current data on sites such as Levels.fyi for specific companies and levels, and compare offers on total compensation, travel expectations and equity terms.

## 19.3 The interview loop

FDE loops vary, but most combine the elements in Chapter 17 §17.4. From the candidate's side:

### Recruiter and hiring-manager screens

Expect "why FDE?" Strong answers connect your history to the role's core: building for real users, working through ambiguity, liking variety and customer contact. Weak answers focus on the title or the pay. Ask about travel, engagement length, team structure, and how field work reaches the product.

### Coding

Usually practical rather than puzzle-heavy: parsing and transforming data, building a small API or service, working with messy inputs. Candidate reports for Palantir's FDSE loop suggest coding difficulty around easy-to-medium, with more weight on clarity and working code than on algorithmic tricks. Practise:

- reading CSV or JSON, cleaning and aggregating data;
- implementing small services with error handling;
- explaining your code as you write it.

### Decomposition

The signature FDE interview, especially at Palantir. You get a vague, real-world prompt ("A hospital wants to reduce emergency department wait times. How would you help?") and must turn it into structure: goals, metrics, users, data, a model of the domain, and a plan. Third-party guides and candidate reports describe Palantir's version as roughly an hour, sometimes with live modelling or code, and interviewers may add a requirement partway through to test whether the design adapts.

How to approach it (Chapter 5 §5.7 is the method):

1. **Clarify the goal and who cares about it.** Ask questions before proposing solutions.
2. **Define measurable outcomes** and how you'd baseline them.
3. **Break the outcome into drivers** (where does the wait time come from?).
4. **Identify users, decisions and data** for each driver.
5. **Sketch a data model** of the key objects and relationships.
6. **Propose a first slice** that delivers value quickly, and how it extends.
7. **Name risks:** data access, privacy, adoption, safety.
8. **Adapt** when the interviewer changes the problem. They're testing whether your structure bends or breaks.

Candidates who treat it as a consulting case (frameworks, no data or system thinking) or as a pure coding task (jumping to implementation) both do poorly. The interviewer wants to see ambiguous problems turned into data-driven, buildable steps.

### Learning

Palantir and some other companies test how fast you learn something unfamiliar. Candidate reports describe being taught a new concept, API or simple query language during the interview, then asked to use it. Advice:

- Ask clarifying questions; restate the concept in your own words.
- Start with simple uses and build up.
- Think aloud, so the interviewer can see your model forming.
- Treat the interviewer as a resource, the way you'd treat a customer expert.

### System design and integration

"Design a system that lets a bank's analysts ask questions over their internal documents, respecting permissions." Expect follow-ups on security, data access, evaluation, scale and handover. Use Part III of this book as your checklist: data (Chapter 10), extension choices (11), AI architecture (12), evaluation (13), security (14) and operations (15).

### Customer simulation and behavioural

Role-plays with a sceptical stakeholder, a scope dispute, or a failing demo, plus behavioural questions ("tell me about a time you delivered with incomplete information"). Use specific stories, structured as situation, task, action, result (STAR), with numbers. Prepare stories on:

- delivering under ambiguity;
- winning over a sceptic;
- delivering bad news;
- saying no to a customer or colleague;
- a technical decision you'd make differently now;
- a time you turned something one-off into something reusable.

Appendix D has a question bank.

## 19.4 A portfolio that shows FDE skills

Public evidence helps, especially for career changers:

- **An end-to-end deployment project:** take a public messy dataset (government open data, for example), profile and clean it, build a useful tool for a real audience, evaluate it, and write it up as a case study with problem, approach, results and lessons. This book's examples are starting points.
- **An AI system with evaluation:** a RAG or agent project with an eval set, graders and a results table, not just a demo video.
- **Writing:** a short design doc or post explaining a decision you made and why. FDE hiring managers value clear writing.
- **Customer-like work you've done:** internal tools built for colleagues in other functions, volunteer projects for non-profits, freelance integrations. Describe the users, the outcome and what you learned.

Respect confidentiality: never publish employer or client data or code.

## 19.5 Career ladder

Levels vary by company. A typical shape:

| Level | Scope | Signals |
|---|---|---|
| **FDE I / associate** | Workstreams within an engagement, with guidance | Ships reliably; learns fast; communicates clearly |
| **FDE II** | Leads the technical side of a small engagement | Independent delivery; good customer judgement |
| **Senior FDE** | Leads complex engagements; mentors | Shapes scope and success; drives productisation |
| **Staff / principal FDE** | Multiple engagements or an industry; architecture and playbook | Patterns across customers; major product influence |
| **FDE manager / director** | Teams and the function | Hiring, capacity, outcomes, the product loop (Chapter 17) |

### Where FDEs go next

- **Product management:** FDEs know customers and problems deeply. A common move.
- **Product engineering:** often on the team that productises field work.
- **Engineering leadership:** FDE leadership or broader engineering management.
- **Founding a company:** Palantir's alumni network is famous for founders; field experience reveals problems worth building companies around.
- **Solutions architecture, consulting or customer-facing executive roles.**
- **Domain specialisation:** becoming the go-to engineer for an industry (healthcare data, defence, financial services).

## 19.6 Your first 90 days

| Period | Focus |
|---|---|
| **Days 1–30** | Learn the product deeply (build a realistic sandbox deployment); read the playbook and past engagement retrospectives; shadow a live engagement; meet product managers for your areas |
| **Days 31–60** | Own a workstream on an engagement; deliver something users touch; write your first weekly updates and field report; run your first discovery interviews with a senior colleague |
| **Days 61–90** | Lead a small engagement or a significant piece of a large one; contribute one improvement to the playbook or a reusable component; ask for feedback from your lead and, if possible, the customer |

## 19.7 A learning roadmap

Use the skills map in Chapter 1 §1.8 to rate yourself, then work on the gaps:

| Gap | Resources in this book | Practice |
|---|---|---|
| Customer skills | Chapters 5–8; templates | Interview three people about their work; write up what you learned using the discovery guide |
| Data | Chapter 10; data-profiler and record-linkage examples | Profile and link two public datasets |
| AI deployment | Chapters 12–13; retrieval, guardrails and eval-harness examples | Build a permission-aware RAG over a document set with an eval suite |
| Security | Chapter 14; security review template | Write a security and AI risk review for your project |
| Production | Chapter 15; readiness-gate example | Run your project through the readiness gate; write a runbook |
| Product judgement | Chapters 11 and 16; feedback-tracker example | Write a field report for a tool you use daily |
| Business | Chapter 3; impact-calculator example | Build an impact case for a process you know |

### Credentials

Formal credentials matter less than demonstrated work, but some help: cloud certifications (AWS, Azure, Google Cloud) for infrastructure credibility; security fundamentals; and, from 2027, vendor programmes such as Anthropic's Claude Frontier Academy credential for engineers at partner organisations. Commentators have noted these are vendor-specific; weigh them by what your target employers value.

---

## Summary

- FDEs come from product engineering, start-ups, data, solutions engineering, consulting, AI and domain expertise. Each route has strengths to emphasise and gaps to close.
- In 2026, employers span Palantir, AI labs, cloud providers, AI start-ups, software vendors, consultancies and defence technology. Reported US median base pay is around $190,000–$200,000, with wide variation; treat all pay data cautiously.
- Interview loops combine practical coding, decomposition, learning, system design, customer simulation and behavioural rounds. Decomposition rewards turning ambiguity into data-driven, buildable steps that adapt to change.
- Build a portfolio with an end-to-end deployment, an evaluated AI system and clear writing.
- Careers progress from workstreams to engagements to industries and functions, and lead to product, engineering leadership, founding and specialist roles.
- Plan your first 90 days around product depth, a shipped user-facing win, and a contribution back to the playbook.

## Exercises

See [`exercises/19-career.md`](../exercises/19-career.md).

## Further reading

- Levels.fyi, Forward Deployed Software Engineer compensation pages (levels.fyi).
- Recruiting From Scratch, "Forward Deployed Engineer Salary in 2026" (job-posting analysis).
- Exponent, "Palantir Forward Deployed Engineer Interview" guide (tryexponent.com), a third-party guide.
- Gayle Laakmann McDowell, *Cracking the Coding Interview* (6th edition, 2015), for coding round practice.
- Alex Xu, *System Design Interview* (2020), adapted for enterprise deployment design.
