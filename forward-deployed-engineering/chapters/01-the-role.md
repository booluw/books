# Chapter 1. What a Forward Deployed Engineer Is

> "One capability, many customers" versus "one customer, many capabilities."
> (Palantir's description of the difference between a product engineer and a forward deployed engineer)

## What you will learn

- What a forward deployed engineer (FDE) is, in plain terms.
- Why the role exists: the gap between a product's potential and a customer's results.
- What FDEs actually do, week by week, and what they produce.
- How FDEs differ from software engineers, solutions engineers, sales engineers, consultants, implementation engineers and customer success engineers.
- The many titles the role appears under, and how to read a job posting.
- The skills the rest of this book teaches.

---

## 1.1 A first definition

> **A forward deployed engineer is a software engineer who works directly with a customer, often embedded in their organisation, to deliver a working solution to one of the customer's most important problems, using (and extending) their company's product, and who feeds what they learn back into that product.**

Each part of the definition matters:

| Phrase | What it means in practice |
|---|---|
| *Software engineer* | FDEs write production code. They are engineers first, held to engineering standards. |
| *Works directly with a customer* | Their day is spent with customer staff (operators, analysts, IT, executives), not only with colleagues. |
| *Often embedded* | Sometimes on site for weeks; sometimes remote but with access to the customer's systems and people. |
| *Working solution* | Not a demo, a slide deck or advice. A system that people use to do real work. |
| *Most important problems* | FDEs are expensive. They are deployed where the value is high. |
| *Using (and extending) their company's product* | FDEs are not freelance developers; they deliver through a platform and push it forward. |
| *Feeds back into the product* | The loop from field to product is what separates an FDE from a consultant. |

The military metaphor in "forward deployed" is deliberate: the engineer is stationed at the front line, close to where the problem is, rather than at headquarters.

## 1.2 Why the role exists

### The deployment gap

Powerful software often fails to create value at a specific customer. Not because the software is bad, but because of everything between the software and the outcome:

- **Data:** the customer's data is spread across dozens of systems, inconsistent, undocumented and access-controlled.
- **Integration:** the product must connect to legacy systems, identity providers and workflows nobody fully understands.
- **Problem definition:** the customer knows something is painful, but not precisely what to build or how success will be measured.
- **Organisation:** the people who would use the solution are busy, sceptical or politically opposed. The people who bought it are not the people who must use it.
- **Security and compliance:** reviews, approvals and restricted environments slow everything down.
- **Adoption:** a working system nobody uses has no value.

A product team at headquarters cannot see these obstacles, let alone remove them. A forward deployed engineer can.

### Why generative AI made the role explode

Large language models (LLMs) widened the deployment gap. They are general-purpose, so customers must decide *what* to use them for. Their output is probabilistic, so quality must be measured, not assumed. And they are most valuable when connected to private data and tools, which are exactly the hard parts listed above.

In 2025, MIT's NANDA initiative published *The GenAI Divide: State of AI in Business 2025*. It reported that 95% of the organisations in its research saw no measurable return from generative-AI initiatives, attributing the gap mainly to implementation (brittle workflows and poor fit with daily operations) rather than model quality. The report's sample was modest, and its authors described it as directional rather than definitive, but its headline was widely cited. Its message matched what many vendors saw: **the bottleneck had moved from the model to deployment.** AI companies responded by hiring engineers whose job is to close that gap.

### Demand, by the numbers *(as of October 2026)*

- **Postings:** CNBC, citing labour-market analytics firm Lightcast, reported US FDE postings rising from fewer than 200 in 2023 to about 1,200 in 2025, and to more than 7,300 in the first nine months of 2026, with consultancies (Deloitte, Accenture, KPMG) and Google among the biggest posters. Indeed data reported by Business Insider showed FDE postings in April 2026 up roughly 7× on a year earlier.
- **Programmes:** OpenAI launched the OpenAI Deployment Company in May 2026, a majority-owned subsidiary built around embedded engineers, seeded by acquiring the AI consultancy Tomoro (reported at roughly 150 FDEs and deployment specialists). AWS announced a $1 billion forward deployed engineering unit in June 2026, with pods of five or six engineers working with customers for roughly 45-day engagements. Anthropic announced the $100 million Claude Frontier Academy in October 2026, to train 10,000 "frontier deployed engineers" at partner and customer organisations by the end of 2027.
- **Pay:** median advertised US salaries for FDE roles were reported around $190,000–$200,000 in 2026 (Chapter 19 has detail and caveats).

Some of the growth is relabelling: roles that used to be called "solutions engineer" or "implementation engineer" acquired the fashionable title. §1.6 shows how to tell the difference.

## 1.3 What FDEs actually do

The work follows an **engagement lifecycle** (Chapter 4): understand the customer, pick and frame the problem, build, prove value, take it to production, hand over, and feed lessons back. Within that, typical activities are:

| Activity | Examples | Chapter |
|---|---|---|
| **Discovery** | Shadow operators on a shift; interview executives; map current workflows; inventory systems and data | 5 |
| **Problem decomposition** | Turn "reduce our supply-chain risk" into a set of buildable, measurable workflows | 5 |
| **Scoping and success criteria** | Agree what will be built, by when, and how success will be measured | 6 |
| **Stakeholder management** | Find champions, address blockers, keep sponsors informed | 7 |
| **Data integration** | Connect to ERP, CRM, databases, file shares; clean and model data | 10 |
| **Building** | Configure the platform; write integrations, pipelines, applications, agents and UIs | 9, 11, 12 |
| **AI deployment** | Retrieval, tool use, prompt and agent design, guardrails | 12 |
| **Evaluation** | Build evaluation sets; measure quality; measure business impact | 13 |
| **Security and compliance** | Security questionnaires, architecture reviews, restricted networks | 14 |
| **Production and handover** | Monitoring, runbooks, training, transition to customer or support teams | 15 |
| **Product feedback** | Write field reports; generalise custom code into product features | 16 |
| **Communication** | Demos, weekly updates, executive readouts, difficult conversations | 8 |

### A realistic week *(composite)*

An FDE embedded with a regional hospital network, deploying an AI platform to reduce the time nurses spend on discharge paperwork:

| Day | Work |
|---|---|
| Monday | On site. Shadow two discharge nurses for a morning. Discover that half the delay is waiting for pharmacy reconciliation, not paperwork. Update the problem statement with the clinical sponsor. |
| Tuesday | Write a connector to the electronic health record's FHIR API in the hospital's test environment. Fight with an expired service-account certificate. Pair with the hospital's integration engineer. |
| Wednesday | Build an evaluation set of 120 de-identified discharge summaries with a nurse educator. Run the current prompt pipeline: 81% acceptable; failure modes cluster around medication lists. |
| Thursday | Security review meeting: answer questions on data flow, retention and model hosting region. Agree that no protected health information leaves the hospital's cloud tenancy. Adjust the architecture. |
| Friday | Weekly update to the executive sponsor: progress, the pharmacy finding, risks, next week's plan. Write a field report for the product team: "Medication reconciliation is a recurring blocker; three hospital customers have asked for it." |

The week mixes ethnography, integration, AI engineering, security, writing and product thinking. That breadth is the job.

## 1.4 What FDEs produce

FDE output is not just code. A successful engagement leaves behind:

1. **A working system in production**, used by real people.
2. **Measured impact**: a before-and-after on agreed metrics.
3. **Documentation and a handover**, so the customer (or a support team) can operate it.
4. **A trained, confident customer team.**
5. **Product improvements**: features, connectors, templates or fixes merged into the core product.
6. **Field knowledge**: reports, reusable patterns and references that make the next deployment faster.
7. **Commercial outcomes**: a renewal, an expansion, a reference customer.

## 1.5 How the role differs from neighbouring roles

| Role | Primary focus | Writes production code for the customer? | Typical time with one customer | Carries a sales quota? | Feeds product? |
|---|---|---|---|---|---|
| **Software engineer (product)** | Build features for many customers | No (indirectly) | None | No | Is the product |
| **Forward deployed engineer** | Deliver a working solution for one customer's important problem, via the product | **Yes** | Weeks to years | Usually no | **Yes, systematically** |
| **Solutions engineer / sales engineer** | Technical case for the sale: demos, proofs of concept, architecture advice | Prototypes | Days to weeks, pre-sale | Often shares a target | Informally |
| **Solutions architect** | Design the solution across many accounts | Rarely | Days to weeks | Sometimes | Informally |
| **Implementation / onboarding engineer** | Configure and integrate the product as it exists | Configuration, light code | Weeks | No | Occasionally |
| **Customer success engineer / TAM** | Ongoing technical health, adoption, support escalation | Rarely | Ongoing, many accounts | Sometimes renewals | Occasionally |
| **Management or technology consultant** | Advice, process design, project delivery; leaves when the project ends | Sometimes | Weeks to months | No | No (not their product) |
| **Professional services engineer** | Billable custom work for customers | Yes | Project-based | Utilisation target | Rarely |

**Two tests** separate a real FDE role from a relabelled one:

1. **Does the person build and ship production systems for the customer?** If the role never touches production, it is a solutions or advisory role, whatever the title.
2. **Is there a deliberate loop back into the product?** If custom work never becomes product, the role is professional services.

Palantir's own framing is useful: a product engineer's focus is "one capability, many customers"; an FDE's is "one customer, many capabilities".

## 1.6 Titles and how to read a posting

Titles you will meet *(as of October 2026)*:

| Title | Where |
|---|---|
| Forward Deployed Software Engineer ("Delta") | Palantir |
| Deployment Strategist ("Echo") | Palantir: the paired, less code-focused role that owns the customer's operational problem and adoption |
| Forward Deployed Engineer | OpenAI, Anthropic, AI start-ups, Salesforce, Databricks, Scale AI and others |
| Forward Deployed AI Engineer | AI platforms and consultancies |
| Frontier Deployed Engineer | Anthropic's Claude Frontier Academy credential for partner and customer engineers |
| Applied AI Engineer / Applied Engineer | AI labs and start-ups |
| Deployment Engineer, Embedded Engineer, Field Engineer | Various |
| Solutions Engineer (Forward Deployed) | Vendors emphasising post-sale delivery |

Read past the title. Look for:

- **"Ship to production" / "own deployments end to end"** → FDE.
- **"Support the sales cycle" / "run demos and proofs of concept"** → solutions engineering.
- **"Travel 25–75%" / "on site with customers"** → embedded FDE.
- **"Partner with product to generalise solutions"** → a healthy feedback loop.
- **"Billable" / "utilisation"** → professional services.
- **"Security clearance required"** → government or defence FDE work (Chapter 14).

## 1.7 Two flavours: FDE and deployment strategist

Palantir pairs two roles, and many AI companies have copied the pattern:

| | Forward deployed engineer (Delta) | Deployment strategist (Echo) |
|---|---|---|
| Core skill | Building: data, code, systems | Understanding the operation: workflows, politics, adoption |
| Owns | Technical delivery | The problem framing, stakeholder alignment, change management, value story |
| Background | Software engineering | Consulting, operations, domain expertise, product management |
| Overlap | Both do discovery, both talk to customers, both care about outcomes | |

Smaller companies combine both in one person. Larger engagements split them. Either way, **both skill sets are required**, which is why this book covers people and process as seriously as code.

## 1.8 The skills map

Rate yourself now and at the end of the book. Chapter 19 turns the gaps into a plan.

| Area | Foundational | Proficient | Advanced |
|---|---|---|---|
| **Software engineering** (Ch. 9) | Ships features in one stack | Polyglot; reads unfamiliar codebases quickly | Designs systems under heavy constraints |
| **Data** (Ch. 10) | SQL, scripting | Integrates messy enterprise sources; models data | Designs data platforms for customers |
| **Product judgement** (Ch. 11, 16) | Uses the platform as designed | Knows when to configure vs build vs change product | Shapes the product roadmap from the field |
| **AI deployment** (Ch. 12) | Calls model APIs | Builds RAG and agents with guardrails | Designs safe, evaluated agentic systems at scale |
| **Evaluation and impact** (Ch. 13) | Spot-checks output | Builds eval sets and impact measurements | Designs experiments executives trust |
| **Security** (Ch. 14) | Follows rules | Passes security reviews; designs for compliance | Delivers in restricted and classified environments |
| **Operations** (Ch. 15) | Deploys | Production-ready with monitoring and runbooks | Hands over systems that run for years |
| **Discovery** (Ch. 5) | Asks questions | Decomposes ambiguous problems | Finds the problem worth solving before the customer does |
| **Scoping** (Ch. 6) | Follows a plan | Writes success criteria and scopes | Negotiates scope under commercial pressure |
| **Stakeholders** (Ch. 7) | Works with a contact | Maps and manages stakeholders | Builds executive trust; navigates politics |
| **Communication** (Ch. 8) | Clear updates | Strong demos and documents | Executive readouts that change decisions |
| **Resilience** (Ch. 18) | Copes with travel | Manages ambiguity and pressure | Sustains high performance for years |

---

## Summary

- An FDE is a software engineer who works directly with (often inside) a customer to deliver a production solution to an important problem through their company's product, and feeds lessons back to the product.
- The role exists because of the deployment gap: data, integration, problem definition, organisation, security and adoption stand between software and outcomes. Generative AI widened that gap and triggered a hiring boom in 2025–2026.
- FDEs differ from solutions engineers (pre-sale, prototypes), implementation engineers (configure as is), consultants (advise and leave) and professional services (billable custom work) by shipping production systems *and* systematically feeding the product.
- Many organisations pair FDEs with deployment strategists who own problem framing and adoption.

## Exercises

See [`exercises/01-the-role.md`](../exercises/01-the-role.md).

## Further reading

- Palantir blog, "Dev versus Delta: Demystifying engineering roles at Palantir" and "A Day in the Life of a Palantir Forward Deployed Software Engineer."
- Gergely Orosz, "What are Forward Deployed Engineers, and why are they so in demand?" *The Pragmatic Engineer* (August 2025).
- MIT NANDA, *The GenAI Divide: State of AI in Business 2025*.
- CNBC, "AWS, Anthropic race to deploy army of specialized engineers key to proving AI spending will pay off" (15 October 2026).
