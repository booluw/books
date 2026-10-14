# Chapter 13. AI Agents in Go-to-Market

> "An AI SDR is a junior employee who works at the speed of light and never asks a question. Supervise accordingly."

## What you will learn

- Where AI creates real value in GTM today, and where it doesn't (yet).
- The building blocks: classification, extraction, research agents, generation, and agents with tools.
- AI SDRs: what they promise, what the evidence shows, and how to evaluate them.
- Evaluation: test sets, metrics, human review and regression testing for prompts.
- Guardrails: grounding, validation, approval steps, spend limits, prompt-injection defences and data protection.
- MCP and the agent-ready GTM stack.

---

## 13.1 Where AI helps most *(as of October 2026)*

| Task | Maturity | Notes |
|---|---|---|
| **Classification** (industry, persona from title, reply intent, ICP questions) | High | Fast, cheap, measurable. Start here |
| **Extraction** (pull facts from a website, job post, filing into structured fields) | High | Ground on fetched content; require evidence |
| **Research summarisation** (account briefs for reps before calls) | High | Saves reps time; needs evidence links |
| **Personalised snippets** (one or two lines inside a template) | Medium–high | With validation and QA (Chapter 10) |
| **Full email generation** | Medium | Quality varies; risk of sameness and errors |
| **Reply handling** (classify, draft responses) | Medium–high | Human approval for positive replies |
| **Call and meeting intelligence** (summaries, CRM updates, deal risk) | High | Gong, Clari/Salesloft, Fathom, Avoma and CRM-native tools |
| **Autonomous prospecting agents (AI SDRs)** | Low–medium | Mixed results; strong supervision needed |
| **Data hygiene** (normalise titles, dedupe suggestions, fill gaps) | Medium–high | Human review for merges |
| **Internal GTM copilots** (ask questions of CRM and warehouse data) | Medium | Data access control is critical |

The pattern: AI is strongest on **narrow, grounded, verifiable** tasks and weakest on **open-ended, unsupervised, customer-facing** ones.

## 13.2 Building blocks

1. **Prompted classification and extraction:** input text or fields go to the model, which returns structured output (JSON schema), validated by code.
2. **Research agents:** a model that can search the web and read pages, deciding which pages to visit to answer a question (Clay's Claygent, custom agents built with model APIs and browsing or search tools). They are more powerful than single prompts, but slower, costlier and less predictable.
3. **Generation:** drafting text from evidence and instructions.
4. **Tool-using agents:** models that can call tools (CRM read and write, enrichment, email send, calendar). These need the most guardrails (§13.5).

Design principle: **use the simplest building block that solves the problem.** A keyword check beats an LLM call; an LLM classification beats an agent; an agent that drafts beats one that sends.

## 13.3 AI SDRs

**AI SDR** products (11x, Artisan, Regie.ai, AiSDR, Qualified's Piper for inbound, and agents inside Salesforce Agentforce, HubSpot Breeze and Apollo) claim to research prospects, write and send sequences, handle replies and book meetings with little human involvement.

The evidence is mixed:

- In March 2025 TechCrunch reported allegations that 11x had displayed logos of companies that said they were not customers (including ZoomInfo, which said it ran a short trial and had not authorised the logo) and that its reported ARR counted contracts customers could exit within a trial break clause. 11x disputed parts of the reporting. Its founder stepped down as CEO in May 2025.
- Industry commentary through 2025–2026 describes high churn of AI SDR deployments after initial trials, with hybrid models (AI researches and drafts, humans review and own relationships) performing more reliably than fully autonomous ones.
- Incumbents moved in. HubSpot launched Breeze agents, including a Prospecting Agent, repriced to outcome-based billing in April 2026. Salesforce reported strong Agentforce adoption. Clay announced an Inbound SDR Agent in preview at its October 2026 Sculpt event.

**How to evaluate an AI SDR (or any agent) honestly:**

1. **Define the outcome:** meetings *held* with ICP-fit prospects and pipeline created, not emails sent.
2. **Run a controlled pilot:** split comparable accounts between the agent and your existing process for 6–8 weeks.
3. **Audit quality:** read a random sample of everything it sends. Check factual accuracy, tone, compliance (opt-outs honoured?) and brand risk.
4. **Measure deliverability impact:** spam complaints and domain reputation.
5. **Count total cost:** licence, data, infrastructure, human supervision time.
6. **Check controls:** approval workflows, sending limits, suppression lists, audit logs, data handling terms.
7. **Verify references** yourself; don't rely on logo walls.

## 13.4 Evaluation: treat prompts like code

Every AI step in production needs an **evaluation set** and a **metric**.

1. **Build a labelled set:** 50–200 real examples with correct answers (persona labels, ICP answers with evidence, reply categories) or quality ratings (for generated lines).
2. **Define metrics:** accuracy and precision/recall for classification (by class, especially rare important ones such as "unsubscribe"); "UNKNOWN" rate; factual error rate and rubric scores for generation; cost and latency per row.
3. **Run the set on every change** of prompt, model or input format. Compare with the previous version.
4. **Use LLM-as-judge carefully:** a second model can score outputs against a rubric, but calibrate it against human ratings first.
5. **Monitor in production:** sample outputs weekly; track drift (for example, more UNKNOWNs after a website-scraper change).

| Version | Persona accuracy | "Unsubscribe" recall | Cost / 1k rows |
|---|---|---|---|
| v1 (prompt only) | 86% | 91% | $0.40 |
| v2 (+ few-shot examples) | 93% | 97% | $0.55 |
| v3 (smaller model + examples) | 92% | 97% | $0.12 |

*(Illustrative.)* Version 3 is the right production choice: nearly the same quality at about a fifth of the cost. Missing an unsubscribe is a compliance failure, so recall on that class matters most.

## 13.5 Guardrails

| Risk | Guardrail |
|---|---|
| **Hallucinated facts** in messages | Ground on fetched evidence; require evidence URLs; validate claims against sources; fall back to generic copy |
| **Off-brand or inappropriate content** | Style rules; banned-phrase lists; human review sampling; Tier 1 always human-approved |
| **Runaway volume or spend** | Per-run and daily caps on sends, enrichment credits and model tokens; alerts |
| **Wrong recipients** | Exclusion and suppression checks *in code*, before any send; never trust the agent alone |
| **Prompt injection** | Agents that read web pages or emails can be manipulated by text such as "ignore your instructions and…". Don't give research agents send or write tools; treat fetched content as data; restrict tools per agent; require approval for actions |
| **Data leakage** | Send models only the data they need; check the provider's data-use terms (no training on your data, retention, region); never put secrets or sensitive personal data in prompts |
| **Compliance** | Agents must honour opt-outs and jurisdiction rules (Chapter 16); log everything they do |
| **Unattributable actions** | Audit logs: who (which agent version) did what, when and why |

The safest architecture separates **thinking** from **doing**: agents propose (a drafted email, a CRM update), deterministic code validates, and a human or a policy approves before anything leaves the building.

## 13.6 MCP and the agent-ready GTM stack

The **Model Context Protocol (MCP)** (see *The Integration Design Engineer*, [Chapter 18](../../integration-design-engineer/chapters/18-ai-and-the-future.md)) lets AI assistants call tools and read data through a standard interface. In 2026 many GTM vendors exposed MCP servers. For example, Salesloft and Clari launched one in April 2026 so assistants such as Claude, ChatGPT and Microsoft Copilot can read pipeline and call data, and Salesforce announced API and MCP access across its platform.

For GTM engineers this means:

- Reps can ask an assistant "What's happening with Acme? Draft a follow-up," and the assistant pulls CRM, call and email context.
- You can build **internal GTM tools** quickly by exposing your warehouse models and actions as MCP tools.
- **Security and governance matter more:** decide which tools each assistant may use, with which user's permissions; prefer read-only tools; audit actions. The Drift breach (Chapter 16) shows how much damage over-privileged integration tokens can do.

---

## Summary

- AI is strongest at grounded classification, extraction and research summaries; weakest at unsupervised, customer-facing autonomy.
- Use the simplest building block that works; separate thinking (agents propose) from doing (code and humans approve).
- Evaluate AI SDRs and agents with controlled pilots on meetings held and pipeline, quality audits, deliverability impact and total cost.
- Give every AI step an evaluation set and metrics; re-run on every change; monitor in production.
- Apply guardrails for hallucination, brand, spend, recipients, prompt injection, data leakage, compliance and auditability.
- MCP makes GTM data agent-accessible. Govern which tools and permissions agents get.

## Exercises

See [`exercises/13-ai-agents.md`](../exercises/13-ai-agents.md).

## Further reading

- TechCrunch reporting on 11x (March 2025) and subsequent coverage.
- Anthropic, OpenAI and Google documentation on structured outputs, tool use and evaluation.
- OWASP Top 10 for LLM Applications (prompt injection, excessive agency).
- Simon Willison's writing on prompt injection.
