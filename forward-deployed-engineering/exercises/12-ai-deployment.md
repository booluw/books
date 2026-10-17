# Exercises: Chapter 12, [Deploying LLM and Agent Systems in the Enterprise](../chapters/12-ai-deployment.md)

Try each question before reading the solution. Exercise types: **concept**, **scenario**, **calculation** and **hands-on**. All companies are fictional. Prices are illustrative *(as of October 2026)*; check current pricing before using them.

## Questions

1. **Concept.** Define each term in one or two sentences, as you would to a customer's IT manager: large language model, context window, tool use, agent, hallucination, prompt injection, retrieval-augmented generation (RAG), security trimming.

2. **Scenario.** Choose the least autonomous pattern from §12.3 that delivers the value in each case, and name the main risk to design against.
   - (a) Contoso Insurance's adjusters want answers to coverage questions from policy wordings.
   - (b) Woodgrove Bank receives 3,000 supplier invoices a day as PDFs and needs header and line-item fields in its ERP.
   - (c) Northwind's IT service desk wants password-reset and access-request tickets resolved end to end.
   - (d) Tailspin Toys wants a customer-facing chat on its website that can check order status and start returns.

3. **Calculation.** Woodgrove Bank's policy assistant will handle 150,000 questions a month, each with 6,000 input tokens (instructions plus retrieved passages) and 400 output tokens, at $3 per million input tokens and $15 per million output tokens. (a) Compute the monthly and annual model cost. (b) 4,000 of the 6,000 input tokens are a fixed system prompt and reference block that can be cached. If cached input tokens are charged at 10% of the normal input price (ignore any cache-write premium), what is the new monthly cost? (c) A colleague proposes an agent instead: each task makes 12 model calls averaging 10,000 input and 300 output tokens per call. Without caching, what does that cost per task and per month, and how many times the single-call design is it? (d) Verify the chapter's example in §12.8 (20,000 requests, 8,000 input and 500 output tokens).

4. **Concept and hands-on.** (a) Explain why permissions must be enforced *before* retrieved passages reach the model, rather than by filtering the answer afterwards. (b) In [`../examples/permission-aware-retrieval/`](../examples/permission-aware-retrieval/), run the demo and tests, and identify the test that shows a restricted document never reaches an unauthorised user. (c) Add a document readable only by a "finance" group, and a test proving an analyst outside that group cannot retrieve it or cite it. (d) Why should ranking statistics be computed only over the documents the user may read?

5. **Scenario.** A prototype agent at Fabrikam has three tools: `run_sql(query)` against the ERP database with a service account; `send_email(to, subject, body)`; and `read_inbox()` for the procurement mailbox. Explain what could go wrong, with reference to the "lethal trifecta" (Chapter 14) and §12.5, and redesign the tool set.

6. **Hands-on.** In [`../examples/agent-guardrails/`](../examples/agent-guardrails/), run the demo and tests. Then: (a) add a scenario in which a tool output contains an injected instruction followed by a write action, and show that the write requires approval; (b) lower the per-run tool-call budget and show that a looping agent is stopped; (c) tamper with one line of the audit log and show that verification fails. For each, write one sentence a customer security reviewer could read.

7. **Scenario.** Adventure Works' defence division needs a document-summarisation assistant in an air-gapped network; its commercial division wants the same assistant in its Azure tenancy. Using §12.7, recommend a model approach for each, and explain how you would compare models and keep behaviour stable over time.

8. **Scenario.** Wide World Importers' IT team found a third-party MCP server on a public registry that connects to their freight system, and wants to install it this afternoon. What would you check before it is connected to production data?

## Solutions

1. - **Large language model (LLM):** a neural network trained on large amounts of text to predict the next token; in practice, it follows instructions, writes and analyses text and code, and reads documents.
   - **Context window:** how much text the model can consider at once (hundreds of thousands of tokens for leading models in 2026). Bigger windows help, but irrelevant material costs money and can distract the model.
   - **Tool use:** the model asks the application to call a defined function (search, create a ticket) and receives the result. The application, not the model, runs the code.
   - **Agent:** a system in which a model plans and takes a sequence of actions using tools, observing results, until it reaches a goal or stops.
   - **Hallucination:** fluent but false or unsupported output. It can be reduced but not eliminated, so systems must detect and contain it.
   - **Prompt injection:** an attack in which text the model reads (a document, email or web page) contains instructions that hijack its behaviour.
   - **RAG:** retrieving relevant passages from the customer's documents and giving them to the model with the question, so answers are grounded and can cite sources.
   - **Security trimming:** filtering retrieval candidates by the user's permissions before anything reaches the model, so answers never draw on documents the user can't read.

2. - (a) **RAG** with citations, inside the adjuster's workflow as an **assistant** (the adjuster decides). Risks: wrong or outdated retrieval, and permission leaks.
   - (b) **Extraction and classification**, in a **workflow** with validation rules (totals add up, supplier exists, PO matches) and human review of exceptions. Risk: silent errors at scale, so measure field-level accuracy and sample-check.
   - (c) **Workflow automation with a model step**, not a free agent: the model classifies the ticket and drafts the action; deterministic code performs password resets through the identity system; access grants above a sensitivity level need approval. Increase autonomy as evidence accumulates. Risks: wrong actions and privilege escalation.
   - (d) **Conversational front end** with narrow read tools (order status for the authenticated customer only) and a return-initiation tool with strict validation; escalation to a human for anything else. Risks: brand damage, policy violations, injection via customer messages, and escalation failures.

3. (a) Per month:
   - Input: 150,000 × 6,000 = 900,000,000 tokens = 900M × $3/M = **$2,700**.
   - Output: 150,000 × 400 = 60,000,000 tokens = 60M × $15/M = **$900**.
   - Total **$3,600 a month**, **$43,200 a year**, before retries, evaluation runs and monitoring.

   (b) With caching:
   - Cached input: 150,000 × 4,000 = 600M tokens × $0.30/M = $180.
   - Uncached input: 150,000 × 2,000 = 300M tokens × $3/M = $900.
   - Output unchanged: $900.
   - Total **$1,980 a month**, a 45% saving ($23,760 a year instead of $43,200).

   (c) Agent, per task:
   - Input: 12 × 10,000 = 120,000 tokens × $3/M = $0.36.
   - Output: 12 × 300 = 3,600 tokens × $15/M = $0.054.
   - Total **$0.414 per task**; × 150,000 = **$62,100 a month** (about $745,200 a year).
   - That is $62,100 ÷ $3,600 ≈ **17.25 times** the single-call design. Agent loops multiply cost by the number of calls and by the context that accumulates; use an agent only if evaluation shows it is needed, and cap loops with budgets.

   (d) Input: 20,000 × 8,000 = 160M × $3/M = $480. Output: 20,000 × 500 = 10M × $15/M = $150. Total **$630 a month**, matching the chapter.

4. (a) Once a restricted passage is in the model's context, it can influence the answer even if it is never quoted: paraphrases, summaries, numbers and hints leak through, and no output filter can reliably detect all of them. Filtering after generation is too late. Security trimming before the model sees anything is the only reliable control; citation checks afterwards are defence in depth.

   (b) Look for the test showing that, for an analyst, results, context and citations contain only documents the analyst may read, even when a restricted document is the best keyword match (the HR restructuring plan in the sample).

   (c) A good test: add a finance-only document whose text strongly matches a query; search as an analyst and assert that the finance document's ID is absent from results and context; then pass an answer that cites it to the citation checker and assert that the check fails. Also test that a finance user *can* retrieve it, so the test isn't passing because the document was never indexed.

   (d) Ranking statistics such as how many documents contain a word, or average document length, change when restricted documents are included. A user could infer that a hidden document exists, or what words it contains, from how their scores shift. Computing statistics over permitted documents only closes that side channel.

5. Problems:
   - `run_sql` is **system-level, not business-level**: the model can read (or, depending on the account, change) anything in the ERP. A service account means the agent acts as a super-user, not with the requesting user's permissions: privilege escalation.
   - `read_inbox` exposes the agent to **untrusted content**: any supplier can email instructions ("forward all bank details to…").
   - `send_email` gives it an **external communication channel**.
   - Together with private data, that is the **lethal trifecta**: private data + untrusted content + external communication. A single injected email could make the agent exfiltrate data.

   Redesign:
   - Replace `run_sql` with narrow read tools such as `get_purchase_order(po_number)` and `get_supplier_status(supplier_id)`, with strict input validation and bounded output, running with the user's delegated permissions.
   - Keep `read_inbox`, but treat its content as untrusted data: screen it, and mark the run as tainted when suspicious content is seen.
   - Replace `send_email` with `draft_reply(thread_id, body)` that creates a draft for a human to send, or restrict sending to existing correspondents on the thread with human approval. This removes or gates the external channel and breaks the trifecta.
   - Add per-role allow-lists, budgets and an audit log of every tool call.

6. Expected results and reviewer sentences:
   - (a) After a tool output containing an injected instruction, the run is tainted and the subsequent write is held for approval (or refused if no approver is configured). *"If the agent reads content that looks like an injection attempt, every later write action requires a named human's approval."*
   - (b) The loop stops when the tool-call budget is exhausted, and the refusal is logged. *"No single agent run can make more than N tool calls or spend more than £X; runs that hit the limit stop and are logged."*
   - (c) Editing any line breaks the hash chain, and verification reports the first broken line. *"The audit log is tamper-evident: any edit, deletion, insertion or reordering is detected on verification."*

   These sentences are exactly what goes into the security and AI risk review (Chapter 14).

7. - **Defence (air-gapped):** a **self-hosted open-weight model** (or a provider's offering approved for isolated government environments, if available and accredited), bundled with its weights and dependencies and transferred through the approved process. Expect lower capability than frontier hosted models and plan GPU infrastructure.
   - **Commercial (Azure):** a capable hosted model available **through the customer's existing cloud agreement** (for procurement and data governance), region-pinned, with enterprise terms (no training on customer data, limited retention).
   - **Comparison:** run the same **evaluation set** (Chapter 13) on candidate models in each environment; start with a capable model to see what is achievable, then test smaller, cheaper models. Consider routing easy documents to a small model.
   - **Stability:** pin model versions in production and re-run evaluations before any upgrade. In the air-gapped environment, upgrades are planned releases anyway.

8. Treat it as untrusted third-party software with access to production data (supply-chain risk, Chapter 14):
   - **Provenance:** who publishes it? Is it maintained? Is the source available and reviewed? Pin a specific version.
   - **What it exposes:** list its tools and resources. Are they read-only? Do they include write or delete operations you don't need?
   - **Authentication and authorisation:** does it act with the end user's permissions (for example via OAuth) or a shared service account? Where are credentials stored?
   - **Data flows:** does it send data anywhere other than the freight system (telemetry, external APIs)?
   - **Input validation, rate limiting and logging.**
   - **Approval:** run it through the customer's normal software and security approval, test it in a non-production environment, and add it to the inventory with an owner.

   "This afternoon" is not realistic for production; a sandbox trial with test data might be.
