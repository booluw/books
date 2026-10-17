# Chapter 3. The Business of Forward Deployment

> "Services that make the product more repeatable are an investment. Services that don't are a cost."

## What you will learn

- Why companies pay for expensive engineers to work inside customers, and when it pays off.
- The economics: gross margin, customer acquisition, expansion, retention and time to value.
- The debate: "trading margin for moat" versus "if you need FDEs, your product doesn't work."
- Commercial models for FDE work: bundled, paid pilots, statements of work, outcome-based and partner-delivered.
- The agency trap, and how to avoid it.
- The metrics an FDE function should be judged on.

An FDE who understands the business can make better decisions every day: which problems to take on, when to say no, what to productise, and how to explain their value.

---

## 3.1 Why companies deploy engineers into customers

Forward deployment is expensive: senior engineers, often travelling, working on one customer at a time. Companies do it because, in the right circumstances, it produces outcomes that cheaper approaches cannot:

1. **Winning deals that would otherwise be lost.** Complex buyers will not commit without seeing the product work on their own data. An FDE-led pilot or bootcamp proves it.
2. **Faster time to value.** The sooner a customer gets measurable results, the sooner they expand and the less likely they are to churn.
3. **Expansion.** Embedded engineers see the next problem before anyone else does. Many FDE-heavy companies grow mainly through expansion inside existing customers ("land and expand"), producing high **net revenue retention (NRR)**.
4. **Retention and switching costs.** A system woven into a customer's operations, with data pipelines and workflows built around it, is hard to rip out.
5. **Product discovery.** FDEs find the features that matter in real environments, and are a source of product insight that surveys and analytics cannot provide.
6. **Category creation.** When the product category is new (as with enterprise AI agents in 2024–2026), customers don't yet know how to use it. FDEs teach the market.
7. **Reference customers.** One successful, visible deployment can sell a dozen more in the same industry.

## 3.2 The economics

### Gross margin

**Gross margin** = (revenue − cost of delivering the product) ÷ revenue. Software companies are valued highly partly because their gross margins are high: commonly 70–80% or more. Services businesses (consulting, outsourcing) typically run at much lower gross margins, often cited around 30–40%. If FDE salaries are counted as cost of revenue, an FDE-heavy company's gross margin falls toward services levels.

### A simple model

Consider an AI platform deal:

| Item | Value |
|---|---|
| Annual contract value (ACV), year 1 | $600,000 |
| Platform delivery cost (hosting, inference, support) | $120,000 |
| FDE time: 2 FDEs × 50% of the year × $350,000 fully loaded cost | $350,000 |

Year-1 gross margin = (600 − 120 − 350) ÷ 600 ≈ **22%**. Painful.

Now suppose that because the deployment works, the customer expands to $1.5M ACV in year 2 and $2.5M in year 3, while FDE involvement drops to 0.5 FDE as the system stabilises and the reusable parts become product:

| Year | ACV | Platform cost (20%) | FDE cost | Gross margin |
|---|---|---|---|---|
| 1 | $600k | $120k | $350k | 22% |
| 2 | $1.5M | $300k | $175k | 68% |
| 3 | $2.5M | $500k | $175k | 73% |

*(Illustrative numbers.)* Three-year gross margin ≈ 65% ($2.98M gross profit on $4.6M revenue). And if the customer would not have bought at all without the FDE-led deployment, the comparison is with **zero** revenue. An impact calculator that models scenarios like this is in [`examples/impact-calculator/`](../examples/impact-calculator/).

The model only works if (a) customers expand substantially, (b) FDE effort per customer falls over time, and (c) what FDEs build becomes reusable product for the next customer. When any of those fail, the business becomes a low-margin consultancy.

### Unit economics leaders track

| Metric | Why it matters |
|---|---|
| **Time to first value** (days from contract to first measurable outcome) | Predicts expansion and retention |
| **Net revenue retention (NRR)** of FDE-deployed customers | Shows whether deployments drive expansion |
| **FDE cost as % of revenue** per customer over time | Should fall as deployments mature |
| **Revenue (or ARR) per FDE** | A productivity measure for the function |
| **Win rate** of FDE-supported pilots vs unsupported | Shows the sales impact |
| **Productisation rate** (share of field-built components that become product) | Measures the feedback loop (Chapter 16) |
| **Deployment time** for the Nth customer in a segment | Should fall as patterns become product |

## 3.3 The debate

### "Trading margin for moat"

Supporters argue forward deployment is a deliberate investment:

- a16z has described "services-led growth" in AI: start-ups accepting services-heavy early revenue because embedding with customers produces data, workflows and trust that become defensible over time.
- Palantir's long-term result (a large platform business that grew from a field-heavy model) is the canonical example.
- In new categories, customers cannot self-serve, so somebody must do deployment. If the vendor does it, the vendor learns.

### "If you need FDEs, your product doesn't work"

Critics argue that persistent forward deployment hides product weakness:

- Decagon, an AI customer-service company, publicly bet *against* heavy forward deployment, with its leadership arguing that embedding engineers long-term means the software doesn't work. It was reported to have passed $100 million in annualised revenue with a more product-led approach.
- Venture investors warn that FDE-heavy companies can look more like consultancies than software companies, with lower margins and valuations.
- Customers may become dependent on vendor engineers, and growth becomes limited by hiring.

### A synthesis

The right question is not "FDEs, yes or no?" but **"do our services make the product more repeatable, reusable and defensible over time?"** Signs of a healthy model:

- FDE effort per customer falls over the customer's lifetime.
- Deployment time per customer falls over the company's lifetime.
- A steady stream of field work becomes product features, templates and connectors.
- Customers' own teams become capable of extending the solution.

Signs of an unhealthy model:

- Every customer gets a bespoke codebase.
- FDEs are permanently assigned to customers for maintenance.
- The product roadmap ignores field reports.
- FDE headcount grows linearly with revenue.

## 3.4 Commercial models

How customers pay for FDE work affects incentives:

| Model | How it works | Pros | Cons |
|---|---|---|---|
| **Bundled** | FDE time included in the platform licence (often for strategic accounts) | Simple; aligned with adoption | Costs hidden; easy to over-serve |
| **Paid pilot / proof of value** | Fixed fee for a short engagement with agreed success criteria, often credited against a contract | Customer commitment; filters unserious buyers | Pressure to over-promise in a short window |
| **Bootcamp** | Intensive days-long workshop building use cases on customer data (Palantir AIP model) | Fast proof; strong sales tool | Must convert to production work afterwards |
| **Statement of work (SOW)** | Separately priced delivery project | Costs recovered; explicit scope | Pulls toward billable services; scope disputes |
| **Outcome-based** | Fees tied to measured outcomes (tickets resolved, hours saved) | Strong alignment | Measurement disputes; risk on vendor |
| **Partner-delivered** | Consultancies or partners deploy; vendor FDEs support or certify them (Anthropic's academy model; OpenAI's partner programme) | Scales beyond headcount | Less learning for the vendor; quality varies |
| **Build-operate-transfer** | Vendor builds and runs it, then transfers it to the customer team | Clear end state | Needs a capable customer team |

FDEs should know which model applies to their engagement. It determines what "done" means, how scope changes are handled, and whose time is being spent.

## 3.5 When forward deployment makes sense

Use this checklist:

| Factor | Favours FDEs | Favours self-serve / partners |
|---|---|---|
| Deal size | Large ACV, high expansion potential | Small ACV |
| Problem complexity | Integration-heavy, ambiguous, high-stakes | Well-understood, standard use cases |
| Category maturity | New category; customers can't self-serve | Mature category |
| Customer capability | Limited internal engineering | Strong internal teams or partners |
| Product maturity | Early; learning what to build | Mature; repeatable |
| Environment | Restricted (classified, regulated, on-prem) | Standard cloud SaaS |
| Strategic value | Reference customer, new vertical | Long tail |

## 3.6 The agency trap

The **agency trap** is when a product company slowly becomes a custom-development shop: every customer has a different fork, FDEs spend their time maintaining one-off code, and the product stagnates.

How it happens:

1. A big customer wants something the product doesn't do.
2. An FDE builds it quickly in customer-specific code ("just this once").
3. The next customer wants something slightly different; another one-off.
4. Maintenance of one-offs consumes FDE capacity; nobody has time to generalise.
5. Upgrades break customisations; customers fall behind; support burden grows.

How to avoid it (detailed in Chapters 11 and 16):

- **Configuration first:** solve with the platform's existing configuration and extension points where possible.
- **Extension points, not forks:** custom code lives in supported extension mechanisms (plugins, functions, connectors), not in a modified core.
- **The rule of three:** when the same need appears at three customers, it becomes a product feature.
- **Field-to-product budget:** reserve FDE and product time explicitly for generalisation.
- **No orphan code:** every piece of custom code has an owner and a support plan, or it isn't shipped.

## 3.7 What this means for the individual FDE

- **Know the commercial context** of your engagement: the ACV, the expansion opportunity, the renewal date, the commercial model.
- **Optimise for value, not hours.** Your goal is measurable impact quickly, not maximum engineering effort.
- **Make yourself less necessary over time.** Hand over, train, and productise.
- **Report impact in business terms** (Chapter 13): it justifies the investment in you.
- **Protect the product:** push back on one-off customisations that fork the platform.

---

## Summary

- Companies deploy engineers into customers to win complex deals, speed time to value, drive expansion and retention, discover product needs, and create new categories.
- FDE costs depress early gross margins. The model works when customers expand, FDE effort falls over time, and field work becomes reusable product.
- The debate ("margin for moat" vs "your product doesn't work") resolves to one question: do services make the product more repeatable?
- Commercial models (bundled, paid pilot, bootcamp, SOW, outcome-based, partner-delivered, build-operate-transfer) shape incentives and definitions of done.
- Avoid the agency trap with configuration first, extension points, the rule of three, a generalisation budget and no orphan code.

## Exercises

See [`exercises/03-business.md`](../exercises/03-business.md).

## Further reading

- a16z, "Services-Led Growth" (a16z.com).
- Eric Newcomer, "Decagon Hit $100 Million Betting Against Forward Deployed Engineers" (2026).
- Palantir annual reports and earnings calls (commercial growth and AIP bootcamps).
- Bessemer Venture Partners, *State of the Cloud* reports, on SaaS gross margin and NRR benchmarks.
