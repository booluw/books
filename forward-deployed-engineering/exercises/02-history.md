# Exercises: Chapter 2, [From Palantir's Deltas to the AI Deployment Boom](../chapters/02-history.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional unless named in the chapter.

## Questions

1. **Concept.** Field service engineers, systems integrators and sales engineers all worked close to customers before the FDE existed. What limitation did they share, and how did Palantir's model address it?

2. **Concept.** Explain Palantir's "Dev" and "Delta" distinction and the role of the "Echo". Why did Palantir hire Deltas to the same technical bar as Devs, rather than hiring cheaper implementation staff?

3. **Concept.** List the five reasons §2.4 gives for why generative AI changed the economics of deployment. For each, give a one-line example from an AI assistant that Woodgrove Bank wants to deploy for its mortgage underwriters.

4. **Calculation.** On its Q4 2023 earnings call, Palantir said it had run more than 560 AIP bootcamps for 465 organisations. (a) How many bootcamps per organisation is that on average? (b) What does the figure suggest about how bootcamps were used? (c) What can you *not* conclude from these two numbers alone?

5. **Calculation.** AWS described its FDE unit as pods of five or six engineers working with customers for roughly 45-day engagements *(as of October 2026)*. Assume, purely for illustration, 300 engineers in pods of six, and that each pod needs 10 calendar days between engagements for wrap-up and preparation. (a) How many pods are there? (b) How many complete engagements can one pod run in a year? (c) What is the unit's maximum annual engagement capacity? (d) Name two factors that would make real capacity lower.

6. **Scenario.** Compare the three 2026 responses: the OpenAI Deployment Company, the AWS FDE unit and Anthropic's Claude Frontier Academy. For each, say who employs the deployed engineers, one advantage, and one risk. Which would you expect to produce the strongest field-to-product feedback loop, and why?

7. **Scenario.** The founder of Tailspin Toys AI, a 40-person start-up selling AI agents to retailers, says: "We'll just do what the systems integrators did in the 2000s: customise for each client until the product matures." Using the lessons table in §2.5, write a short reply (five or six sentences) explaining the risk and what to do instead.

## Solutions

1. **Shared limitation: the people closest to customers rarely changed the product.** Customisations stayed with each customer; consultants left when projects ended; product teams heard about the field second-hand. The result was expensive, slow implementations and customisations that made upgrades painful.

   Palantir addressed it by (a) making field staff **software engineers** (Deltas) hired to the product engineers' bar, so they could build properly and contribute code, and (b) building an explicit **field-to-product loop**: repeated custom work was pulled back into the platform as features. For years it employed more Deltas than Devs, so the field was not an afterthought but the main source of product learning.

2. - **Dev:** a product engineer, focused on "one capability, many customers": building platform features that serve everyone.
   - **Delta:** a forward deployed engineer, focused on "one customer, many capabilities": using and extending the platform to solve one customer's problem.
   - **Echo:** a deployment strategist who owns the operational problem, institutional politics, workflow realities and adoption.

   Hiring Deltas to the Dev bar mattered because (a) the environments were the hardest possible (classified, fragmented, disconnected), so weak engineering would fail; (b) Deltas' code was meant to flow back into the product, so it had to meet product standards; and (c) Palantir explicitly did not want to become a consultancy, and cheaper implementation staff would have pushed it towards one-off configuration work with no product loop.

3. | Reason | Woodgrove Bank mortgage example |
   |---|---|
   | General-purpose capability: someone must find the few uses that matter | Of hundreds of possible uses, the team must choose (say) income-document verification over drafting customer letters |
   | Probabilistic output: quality must be measured | Extraction of salary figures from payslips must be tested on a labelled set; "it looked right in the demo" is not evidence |
   | Context is the product: value depends on private data and tools | The model is useful only when connected to the loan origination system, credit files and lending policy, with permissions |
   | New risks | Hallucinated affordability figures, prompt injection in uploaded documents, regulatory scrutiny of credit decisions (credit scoring is high-risk under the EU AI Act) |
   | Change management | Underwriters must change how they review files and trust a new tool; their managers' metrics may need to change |

4. (a) 560 ÷ 465 ≈ **1.2 bootcamps per organisation** on average.

   (b) Most organisations attended one bootcamp, and a minority attended more than one: there were 560 − 465 = 95 bootcamps beyond each organisation's first (if no organisation attended more than twice, 95 organisations attended twice). That is consistent with bootcamps as a **go-to-market tool**: a first, intensive proof on the customer's own data, with some customers returning for further use cases.

   (c) You cannot conclude the **conversion rate** (how many bootcamps became paying production deployments), the **revenue** attributable to them, how long each took, or whether the organisations were new or existing customers. Palantir credited bootcamps for its US commercial growth, but two counts alone do not prove that causal link. This is the evaluation-versus-impact distinction of Chapter 13 in miniature.

5. (a) 300 ÷ 6 = **50 pods**.

   (b) One cycle is 45 + 10 = 55 days. 365 ÷ 55 ≈ 6.6, so **6 complete engagements** per pod per year.

   (c) 50 × 6 = **300 engagements per year** at most.

   (d) Real capacity is lower because of: holidays, training and attrition; ramp-up time for new hires; engagements that overrun 45 days (access delays are the usual cause, Chapter 4); engineers pulled into pre-sales or support; and mismatches between pod skills and customer needs. It might also be organised differently (pods running overlapping engagements), so treat the arithmetic as a ceiling for planning, not a description of AWS's actual operation.

6. | | Who employs the engineers | Advantage | Risk |
   |---|---|---|---|
   | **OpenAI Deployment Company** | A majority-owned OpenAI subsidiary (seeded by acquiring Tomoro) | Direct control of quality; close to the model provider | Services-heavy economics; growth limited by hiring and acquisitions |
   | **AWS FDE unit** | AWS | Scale and short, standardised 45-day engagements; tied to existing cloud relationships | Short engagements may end before adoption and handover are secure |
   | **Claude Frontier Academy** | Partners and customers (Anthropic trains them) | Scales beyond Anthropic's headcount; capability stays at the customer | Vendor learns less directly; quality varies across partners; a vendor-specific credential |

   **Strongest feedback loop:** the in-house models (OpenAI's subsidiary and AWS's unit), because the engineers are employed by the vendor group and can be required to write field reports and contribute to the product. The academy model needs deliberate mechanisms (structured reporting from residencies, partner councils) to achieve the same loop, because the engineers' first loyalty is to their own employer. This mirrors the partner-delivered trade-off in Chapter 3 §3.4.

7. Model reply: "The systems-integrator model built a large industry, but it is the cautionary tale in our history, not the template. Per-client customisation without productisation created technical debt, low margins and upgrades so painful that customers fell years behind. If we copy it, every new retailer will cost as much to deploy as the first, and our margins will look like a consultancy's. Instead, let's do what Palantir did: deploy engineers deeply, but treat every piece of custom work as a candidate for the product, and generalise anything that three customers need. We should measure whether deployment time for each new retailer is falling; if it isn't, we're becoming an integrator. That keeps the field learning while building a product that gets easier to deploy."
