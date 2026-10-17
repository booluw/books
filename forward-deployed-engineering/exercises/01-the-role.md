# Exercises: Chapter 1, [What a Forward Deployed Engineer Is](../chapters/01-the-role.md)

Try each question before reading the solution. Exercise types: **concept** (check your understanding), **scenario** (make a judgement in a realistic situation), **calculation** (work the numbers) and **hands-on** (use the book's examples or templates). All companies are fictional.

## Questions

1. **Concept.** Without looking back at the chapter, write a one-sentence definition of a forward deployed engineer. Then check it against the chapter's definition: which of the seven phrases in §1.1 did you leave out, and what would go wrong in practice if a role lacked that element?

2. **Concept.** State the two tests that separate a real FDE role from a relabelled one. For each test, name the neighbouring role you are describing if the answer is "no".

3. **Scenario.** Classify each of these job-posting extracts as FDE, embedded FDE, solutions engineering or professional services, and explain which phrases decided it.
   - (a) Contoso: "Support account executives through the sales cycle. Run tailored demos and two-week proofs of concept. 20% travel."
   - (b) Fabrikam: "Own customer deployments end to end, from data integration to production. Partner with product to generalise solutions. On site with customers 50–75% of the time."
   - (c) Northwind Consulting: "Deliver bespoke integrations for clients. Billable role with an 80% utilisation target."
   - (d) Tailspin Toys AI: "Ship production agent workflows for enterprise customers, remotely, and contribute connectors back to the core platform."

4. **Scenario.** Woodgrove Bank bought an AI document-review platform six months ago. Usage is near zero. In a single meeting you hear: "The loan files are in three systems and one of them is a scanned archive"; "Security still haven't approved the model hosting region"; "Credit officers don't trust it, so they redo the work"; "Nobody agreed what 'better' would mean"; "The integration with our identity provider failed in testing"; "The people who signed the contract don't do the reviews." Map each statement to one of the six deployment-gap categories in §1.2 and say which one you would tackle first, and why.

5. **Calculation.** CNBC (citing Lightcast) reported US FDE postings of fewer than 200 in 2023, about 1,200 in 2025, and more than 7,300 in the first nine months of 2026 *(as of October 2026)*. (a) What minimum growth multiple does the 2023 → 2025 change represent? (b) Annualise the 2026 figure on a straight-line basis and compare it with 2025. (c) Give two reasons the true growth in FDE *work* may be smaller than these multiples suggest.

6. **Scenario.** Adventure Works, a 200-person software company, wants to hire one person to deploy its supply-chain planning product at three large manufacturers. The CEO asks whether to hire an FDE or a deployment strategist. Using §1.7, explain what each would own, what the risk of hiring only one profile is, and what you would recommend.

7. **Hands-on.** Rate yourself on every row of the skills map in §1.8 (foundational, proficient or advanced) and write one piece of evidence for each rating. Pick the two weakest areas that matter most for the kind of FDE role you want, and for each name the chapter of this book and one example folder in [`../examples/`](../examples/) or template in [`../templates/`](../templates/) you will use to improve. Keep the sheet; you will revisit it in Chapter 19.

## Solutions

1. **Model answer:** "A forward deployed engineer is a software engineer who works directly with a customer, often embedded with them, to deliver a working production solution to one of their most important problems through their company's product, and who feeds what they learn back into that product."

   The phrases most often left out, and what goes wrong without them:
   - *Software engineer*: without engineering standards the role drifts into advisory work, and what is built cannot survive production.
   - *Working solution*: without it the role produces demos and slide decks; the deployment gap stays open.
   - *Most important problems*: FDEs are expensive. Deploying them on low-value problems destroys the economics (Chapter 3).
   - *Using (and extending) the product*: without it the FDE becomes a freelance developer building one-off applications, the start of the agency trap.
   - *Feeds back into the product*: this is the most commonly omitted, and the most important. Without it the role is consulting or professional services; each deployment is as hard as the last.

2. **Test 1: does the person build and ship production systems for the customer?** If no, the role is solutions engineering, solutions architecture or advisory consulting, whatever its title. **Test 2: is there a deliberate loop back into the product?** If no, the role is professional services (billable custom work) or implementation engineering. Both tests must pass. A role that ships production code but never changes the product is a services role; a role that influences the product but never ships is product management or solutions engineering.

3. - (a) **Solutions engineering.** "Support the sales cycle", "demos" and "proofs of concept" are pre-sale signals; nothing mentions production or the product loop.
   - (b) **Embedded FDE.** "Own deployments end to end" and "to production" pass test 1; "partner with product to generalise" passes test 2; "on site 50–75%" means embedded.
   - (c) **Professional services.** "Bespoke", "billable" and "utilisation target" signal custom work sold by the hour, with no product loop (the firm has no product of its own).
   - (d) **FDE (remote).** It ships to production and contributes connectors back to the platform, so it passes both tests. "Remotely" shows that embedding is common but not required by the definition.

4. Mapping:

   | Statement | Category |
   |---|---|
   | Loan files in three systems, one scanned | **Data** |
   | Security haven't approved the hosting region | **Security and compliance** |
   | Credit officers redo the work | **Adoption** (rooted in trust) |
   | Nobody agreed what "better" means | **Problem definition** |
   | Identity-provider integration failed | **Integration** |
   | Signatories don't do the reviews | **Organisation** |

   **Tackle problem definition first.** Without an agreed outcome and baseline, you cannot prioritise the data work, cannot tell the credit officers what the tool is for, cannot write a security scope, and cannot show anyone that the fix worked. In practice you would also start the security conversation in parallel, because approvals are usually the longest item on the critical path (Chapters 4 and 14). The organisation and adoption problems are addressed through discovery with the credit officers themselves (Chapters 5 and 7).

5. (a) From fewer than 200 to about 1,200 is a multiple of **at least 1,200 ÷ 200 = 6×** in two years (more than 6× if the 2023 figure was well below 200).

   (b) Annualised 2026: 7,300 × 12 ÷ 9 ≈ **9,733 postings**, about **9,733 ÷ 1,200 ≈ 8.1×** the 2025 level. Straight-line annualisation is crude: hiring is seasonal and the trend was accelerating, so treat this as an order of magnitude, not a forecast.

   (c) Reasons the work grew less than the postings: **relabelling** (solutions and implementation roles retitled "FDE" because the title is fashionable); **reposting and duplicate postings** (one role advertised in several cities or by several recruiters); **consultancy pipeline hiring** (large firms posting speculatively for capacity they may not fill); and **postings are not hires**. The chapter itself flags relabelling, which is why §1.5's two tests matter.

6. - An **FDE** would own technical delivery: connecting to each manufacturer's ERP and planning data, configuring and extending the product, building integrations, and getting the system into production. A **deployment strategist** would own the operational problem: framing which planning decisions to improve, aligning planners and their managers, driving adoption and telling the value story.
   - **Risk of only an FDE:** systems that work technically but are not adopted, or that solve a problem nobody prioritised. **Risk of only a strategist:** clear plans and enthusiastic sponsors, but nothing ships, or what ships is fragile.
   - **Recommendation:** at a 200-person company with one hire, recruit an FDE with strong customer and discovery skills (the combined profile §1.7 describes for smaller companies), and give them explicit backing from a product manager or customer-success lead for stakeholder and adoption work. When the programme grows beyond two or three concurrent customers, add a strategist and split the roles.

7. Answers are personal. A good sheet has **evidence**, not just ratings ("Proficient in data: built a CDC pipeline from Postgres to Snowflake at my last job", not "Proficient in data"). Common, sensible choices:
   - A product engineer moving to FDE work often rates communication, scoping and stakeholders as foundational. Suitable resources: Chapters 6–8, with [`../templates/success-plan.md`](../templates/success-plan.md) and [`../templates/weekly-update.md`](../templates/weekly-update.md).
   - A solutions engineer often rates evaluation and operations as foundational. Suitable resources: Chapter 13 with [`../examples/llm-eval-harness/`](../examples/llm-eval-harness/), and Chapter 15 with [`../examples/readiness-gate/`](../examples/readiness-gate/).

   The reason to choose only two areas is focus: the skills map is wide by design, and nobody is advanced on every row.
