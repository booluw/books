# Exercises

One file per chapter, each with questions followed by full worked solutions. Try the questions before reading the solutions.

Each file mixes four kinds of exercise:

- **Concept:** check that you can define and explain the chapter's ideas.
- **Scenario:** make a judgement in a realistic FDE situation.
- **Calculation:** work the numbers (margins, value estimates, token costs, evaluation and impact statistics).
- **Hands-on:** use the runnable code in [`../examples/`](../examples/) and the documents in [`../templates/`](../templates/).

All companies in the exercises (Contoso, Fabrikam, Northwind, Tailspin Toys, Woodgrove Bank, Wide World Importers, Adventure Works) are fictional, and all figures are illustrative unless the chapter cites a source. Facts that change over time are dated *(as of October 2026)*.

To run the examples' tests before the hands-on exercises, from the repository root:

```bash
python3 forward-deployed-engineering/examples/run_all_tests.py
```

| Chapter | Exercises |
|---|---|
| 1. [What a Forward Deployed Engineer Is](../chapters/01-the-role.md) | [01-the-role.md](01-the-role.md) |
| 2. [From Palantir's Deltas to the AI Deployment Boom](../chapters/02-history.md) | [02-history.md](02-history.md) |
| 3. [The Business of Forward Deployment](../chapters/03-business.md) | [03-business.md](03-business.md) |
| 4. [The Engagement Lifecycle](../chapters/04-engagement-lifecycle.md) | [04-engagement-lifecycle.md](04-engagement-lifecycle.md) |
| 5. [Discovery and Problem Decomposition](../chapters/05-discovery-and-decomposition.md) | [05-discovery-and-decomposition.md](05-discovery-and-decomposition.md) |
| 6. [Scoping, Success Criteria and Statements of Work](../chapters/06-scoping.md) | [06-scoping.md](06-scoping.md) |
| 7. [Stakeholders, Politics and Trust](../chapters/07-stakeholders.md) | [07-stakeholders.md](07-stakeholders.md) |
| 8. [Communication: Demos, Writing and Hard Conversations](../chapters/08-communication.md) | [08-communication.md](08-communication.md) |
| 9. [The FDE Technical Toolkit](../chapters/09-toolkit.md) | [09-toolkit.md](09-toolkit.md) |
| 10. [Enterprise Data in the Wild](../chapters/10-enterprise-data.md) | [10-enterprise-data.md](10-enterprise-data.md) |
| 11. [Configure, Extend or Change the Product](../chapters/11-configure-extend-change.md) | [11-configure-extend-change.md](11-configure-extend-change.md) |
| 12. [Deploying LLM and Agent Systems in the Enterprise](../chapters/12-ai-deployment.md) | [12-ai-deployment.md](12-ai-deployment.md) |
| 13. [Evaluation and Measuring Business Impact](../chapters/13-evaluation-and-impact.md) | [13-evaluation-and-impact.md](13-evaluation-and-impact.md) |
| 14. [Security, Compliance and Restricted Environments](../chapters/14-security-and-restricted-environments.md) | [14-security-and-restricted-environments.md](14-security-and-restricted-environments.md) |
| 15. [Production Readiness, Operations and Handover](../chapters/15-production-and-handover.md) | [15-production-and-handover.md](15-production-and-handover.md) |
| 16. [Turning Field Work into Product](../chapters/16-field-to-product.md) | [16-field-to-product.md](16-field-to-product.md) |
| 17. [Building and Running an FDE Organisation](../chapters/17-running-an-fde-org.md) | [17-running-an-fde-org.md](17-running-an-fde-org.md) |
| 18. [Life as an FDE: Pace, Travel, Ethics and Sustainability](../chapters/18-life-as-an-fde.md) | [18-life-as-an-fde.md](18-life-as-an-fde.md) |
| 19. [Becoming a Forward Deployed Engineer](../chapters/19-career.md) | [19-career.md](19-career.md) |
| 20. [Case Studies](../chapters/20-case-studies.md) | [20-case-studies.md](20-case-studies.md) |

## Where the hands-on exercises use each example and template

For Chapters 1–14 (the files for Chapters 15–20 will add their own uses, notably `readiness-gate` and `feedback-tracker`):

| Example or template | Used in exercises for chapters |
|---|---|
| [`data-profiler`](../examples/data-profiler/) | 9 |
| [`record-linkage`](../examples/record-linkage/) | 10 |
| [`permission-aware-retrieval`](../examples/permission-aware-retrieval/) | 12, 14 |
| [`agent-guardrails`](../examples/agent-guardrails/) | 12, 14 |
| [`llm-eval-harness`](../examples/llm-eval-harness/) | 1, 13 |
| [`impact-calculator`](../examples/impact-calculator/) | 3, 5, 13 |
| [`readiness-gate`](../examples/readiness-gate/) | 1 |
| [`discovery-guide.md`](../templates/discovery-guide.md), [`problem-decomposition-canvas.md`](../templates/problem-decomposition-canvas.md) | 5 |
| [`success-plan.md`](../templates/success-plan.md) | 1, 4, 6 |
| [`statement-of-work.md`](../templates/statement-of-work.md) | 6 |
| [`weekly-update.md`](../templates/weekly-update.md) | 1, 4 |
| [`executive-brief.md`](../templates/executive-brief.md) | 8 |
| [`field-report.md`](../templates/field-report.md) | 8, 11 |
| [`security-and-ai-risk-review.md`](../templates/security-and-ai-risk-review.md) | 14 |
