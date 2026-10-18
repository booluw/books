# Exercises: Chapter 11, [Configure, Extend or Change the Product](../chapters/11-configure-extend-change.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional and all figures illustrative.

## Questions

1. **Concept.** Draw (or list) the ladder in §11.2 from rung 0 to rung 4, plus declining. For each rung, give one advantage, one disadvantage and one example from an AI platform deployment.

2. **Scenario.** Place each request on the ladder and justify your choice.
   - (a) Contoso wants the AI assistant's answers to use the company's tone of voice and refuse questions about competitors.
   - (b) Woodgrove Bank needs the agent to look up account balances in its core banking system, which the product has no connector for. The product supports custom tools via MCP servers.
   - (c) Northwind wants a bespoke warehouse-floor tablet app that shows the platform's pick recommendations alongside data from three other systems.
   - (d) Fabrikam, and now two other manufacturers, need the platform's document parser to handle multi-page engineering drawings with title blocks.
   - (e) Tailspin Toys asks you to change the product's role-based access control so that their regional managers can see each other's data on alternate Tuesdays.

3. **Scenario.** Adventure Works asks for an "approval step before any purchase order over £10,000 is sent to the supplier". Walk through rung 0: what questions would you ask, and what alternative needs might be behind the request?

4. **Hands-on.** You have built an extension at Wide World Importers that receives the platform's `shipment.updated` webhook and enriches it with customs data. Design a set of **contract tests** (at least five) that would catch a product upgrade breaking the extension, and say when they should run. Then list two further practices from §11.4 you would apply to this extension.

5. **Calculation.** Fabrikam's FDE team supports 12 customers, each with 3 one-off customisations built inside customer-specific code. Each customisation needs 2 FDE-days of re-testing and repair at every product release, and the product ships 6 releases a year. An FDE has about 225 working days a year. (a) How many FDE-days a year does maintenance consume, and how many FDEs is that? (b) Generalising these customisations into product features would cost 60 FDE-days once, after which each customer needs 0.25 days per customisation per release for configuration checks. What is the first-year total, and what is the saving? (c) What does this say about the "just this once" decision?

6. **Scenario.** You join an engagement at Contoso and find: a branch of the product repository named `contoso-prod`; Contoso running four releases behind; security fixes applied twice; one FDE "who knows how it all works" leaving next month. Write a plan to back out of the fork, following §11.7.

7. **Hands-on.** Write a field report using [`../templates/field-report.md`](../templates/field-report.md) proposing the engineering-drawing parser in question 2(d) as a product change. Include the problem, evidence, impact, the other customers affected and a proposed generalisation. Then write the three-sentence message you would send the Fabrikam sponsor explaining the plan and what they should and should not expect on timing.

8. **Concept.** Why does §11.3 make it a hard rule never to implement custom security or data-model changes by patching product internals for one customer? Give two concrete ways such a patch could fail.

## Solutions

1. | Rung | Advantage | Disadvantage | AI-platform example |
   |---|---|---|---|
   | 0 Question the need | Many requests disappear once the real need is understood | Takes discovery time; can feel like pushback | "We need a custom approval step" turns out to mean "auditors need evidence of review", which an audit log satisfies |
   | 1 Configure | Supported, upgrade-safe, maintainable by customer admins | Limited to what the product exposes | Prompt templates, model selection, thresholds, permission roles |
   | 2 Extend | Custom logic inside a contract the product team maintains | Limited by the extension point; still needs an owner | A custom tool for the agent exposed through an MCP server |
   | 3 Build alongside | Doesn't touch the core; upgrade-safe if APIs are stable | Another system to run, monitor and hand over | A separate ingestion service that pushes documents into the platform via its API |
   | 4 Change the product | Everyone benefits; no customer-specific maintenance | Slower; must fit design, quality bar and roadmap | Adding a new document parser to the core |
   | Decline | Protects the product and team capacity | Disappoints the customer unless you offer a path | Refuse a one-off feature; offer a partner, workaround or priced work |

2. - (a) **Configure (rung 1).** System prompt, tone instructions and topic restrictions are configuration on most AI platforms. Keep the configuration in version control and test it with the evaluation set.
   - (b) **Extend (rung 2).** Build an MCP server exposing a narrow business-level tool (`get_account_balance(account_id)`), acting with the user's permissions (Chapter 12). It uses a supported extension point.
   - (c) **Build alongside (rung 3).** A separate app consuming the platform's API plus the other systems. Treat it as a real service with tests, CI, monitoring and an owner.
   - (d) **Change the product (rung 4).** Three customers have the need: the rule of three is met. Prototype as an extension if Fabrikam can't wait, then propose the generalised parser with evidence.
   - (e) **Decline or reframe.** It touches the product's security model, which must never be patched for one customer. Question the need first (rung 0): perhaps a shared "regional managers" group or a cross-region report solves it through configuration. If it is a real general need, it becomes a properly designed product change, not a customer patch.

3. Questions: "What happened that made you want this? Tell me about the last time." "Who would approve, and what would they check?" "Is this a policy requirement, an audit finding, or a preference?" "What happens today for orders over £10,000?" "Is £10,000 a fixed figure or does it vary by category or supplier?"

   Possible needs behind it: an audit finding requiring evidence of a second review of high-value commitments (an audit log plus a report may satisfy it); fraud concerns about new suppliers (a rule for new or changed suppliers, not all orders over £10,000); budget control (a budget-check integration rather than a human step); or an existing approval in the ERP that the platform's orders bypass (route orders through the ERP's existing workflow). Many of these are satisfied by configuration or by the customer's own systems.

4. Contract tests (run against each new product release in a test environment before production upgrade, and on a schedule against production-like environments):
   1. The `shipment.updated` webhook payload still contains the fields the extension reads (`shipment_id`, `status`, `updated_at`, line items) with the expected types.
   2. The webhook signature header and signing algorithm still verify with the configured secret.
   3. The platform API used to write enrichment back accepts the extension's request shape and returns the expected status code.
   4. Error responses (invalid shipment ID, unauthorised token) still use the documented status codes and error body.
   5. Unknown additional fields in the payload are tolerated (the extension must not break when the product adds fields).
   6. Duplicate deliveries of the same event are handled idempotently (webhooks are typically at-least-once).
   7. Pagination or rate-limit headers on the API behave as documented.

   Further practices: **pin and track** SDK and API versions and subscribe to deprecation notices; **feature-flag** the enrichment so it can be switched off without a deploy; **fail safe** (if enrichment fails, the shipment still flows, with a warning); **isolate** customer logic behind a clean interface.

5. (a) 12 customers × 3 customisations × 2 days × 6 releases = **432 FDE-days a year**. 432 ÷ 225 ≈ **1.9 FDEs**: almost two engineers doing nothing but keeping one-offs alive.

   (b) Ongoing after generalisation: 12 × 3 × 0.25 × 6 = **54 FDE-days a year**. First-year total = 60 + 54 = **114 FDE-days**. First-year saving = 432 − 114 = **318 FDE-days** (about 1.4 FDEs). From year two, the saving is 432 − 54 = 378 days a year.

   (c) "Just this once" looks cheap because the cost is paid later and spread across every release. Multiplied by customers, customisations and releases, it consumes a large share of the team. That is the agency trap in arithmetic. It also argues for reserving an explicit field-to-product budget (Chapter 3 §3.6): the 60 days pays back within the first year.

   (These simplifications assume all customisations generalise; in reality some won't, and the inventory in §11.5 tells you which.)

6. Plan:
   1. **Inventory the differences** between `contoso-prod` and the current product: diff the branch, list every change, and interview the departing FDE **this week** while they are still there (record the session; write ADRs for each decision).
   2. **Classify each difference:** now available as configuration; can become an extension; should become product; no longer needed.
   3. **Plan the migration** to the current product plus configuration and extensions, with tests (including an evaluation set for AI behaviour) that prove behaviour is preserved. Use a test environment with a copy of Contoso's configuration.
   4. **Get sponsor buy-in:** upgrading brings Contoso four releases of security fixes and new features; position it as a benefit, with a dated plan and a rollback path.
   5. **Prevent recurrence:** record every remaining custom component in the customer-code inventory with an owner; review why the fork was created (incentives, deadlines) and fix the process.

   Immediately: make sure security fixes are applied to `contoso-prod` while the migration runs; Contoso cannot wait months for them.

7. A strong field report states the **problem** ("manufacturing customers can't use document Q&A on engineering drawings, because the parser treats multi-page drawings as images and ignores title-block metadata"), not just "support drawings". **Evidence:** example drawings (with permission, or synthetic equivalents), the failure rate on Fabrikam's evaluation set, and the workaround built. **Impact:** users affected, deals or renewals at stake, how often it occurs. **Other customers:** the two other manufacturers, named (rule of three met). **Generalisation:** a drawing-aware parser that extracts title-block fields (part number, revision, author) as metadata and splits pages into referenced chunks.

   Sponsor message, for example: "We've built an interim extension so your team can use drawings now; it is tested and supported until the product feature replaces it. We've proposed a standard drawing parser to our product team, supported by two other manufacturers with the same need. Product changes follow our release process, so I can't promise a date, but I'll update you when it's scheduled and we'll migrate you from the interim version when it ships."

8. Security and the core data model are where errors are most dangerous and least visible. A customer-specific patch bypasses the product team's design review, security testing and future fixes, so customer-specific security code is "where vulnerabilities live".

   Ways it could fail: (1) a later product release changes the permission-check code path, the patch silently stops applying (or applies wrongly), and users see data they shouldn't; (2) the patch introduces an access-control bypass that the product's security tests don't cover, because they don't know it exists, and penetration tests on the standard product miss it. Data-model patches add (3) migrations that fail at upgrade and corrupt or strand customer data. The safe path is a properly designed product change.
