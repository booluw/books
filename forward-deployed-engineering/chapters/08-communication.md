# Chapter 8. Communication: Demos, Writing and Hard Conversations

> "In the field, the work isn't done until the right people understand it."

## What you will learn

- Why communication is a core technical skill for an FDE, not a soft extra.
- How to write the documents FDEs live by: weekly updates, executive briefs, design notes and field reports.
- How to run demos that build belief rather than suspicion.
- How to explain technical ideas to non-technical audiences without condescension.
- How to handle hard conversations: delays, bad news, saying no, and incidents.
- How to communicate across cultures, time zones and remote teams.

---

## 8.1 Why communication is part of the job

A product engineer's work is mostly judged by code reviewers and users. An FDE's work is also judged by executives who will never read the code, security teams who need precise answers, front-line users who need to trust a tool, and product managers who need to understand a field problem without visiting the field. If those people don't understand what you did, the work fails to land: it isn't adopted, funded, approved or productised.

Palantir's own descriptions of the FDE role emphasise this: the engineer must be able to talk to an analyst in the morning and an executive in the afternoon. Hiring loops for FDE roles commonly test written and spoken communication alongside coding (Chapter 19).

## 8.2 Principles

1. **Answer first.** State the conclusion, then the support. Barbara Minto's *Pyramid Principle* calls this top-down communication. Busy readers may stop after the first paragraph; make sure it contains what they need.
2. **Know the audience and the decision.** Before writing or speaking, ask: who is this for, and what do I want them to know, decide or do?
3. **Use their words.** Speak in the customer's business terms. "Claims cycle time" not "pipeline latency".
4. **Quantify.** "Faster" is weak. "Median handling time fell from 25 to 7 minutes on 412 cases" is strong.
5. **Be honest about uncertainty.** Say what you know, what you don't, and how confident you are.
6. **Write things down.** Spoken agreements drift; written ones can be checked.
7. **Shorter is better**, but not at the cost of the decision-relevant detail.

## 8.3 The weekly update

The **weekly update** is the FDE's heartbeat. Sent every week, to the customer owner and sponsor (and your internal team), it keeps everyone aligned and creates a written record. Template: [`templates/weekly-update.md`](../templates/weekly-update.md).

Structure:

```
Subject: [Customer] [Project] weekly update — week 5 — status AMBER

Summary (3 lines)
  Coverage summaries are live for 15 pilot adjusters. Usage is good (72% of eligible
  claims). Status is amber because policy-system API access for endorsements is
  two weeks late, which puts the week-8 milestone at risk.

Progress against success criteria
  - Cycle time (pilot team): 8.1 days median, from 9.0 baseline (target 6.0 by week 10)
  - Adoption: 72% of eligible claims (target 70% by week 6) ✅
  - Quality: 91% correct on 200-claim evaluation set (target 90%) ✅

Done this week / next week
Decisions needed (with owner and date)
Risks and blockers (with owner and next step)
```

### Status colours

Most enterprises use **RAG** status: **red** (off track, needs intervention), **amber** (at risk, being managed), **green** (on track). Two rules:

- **Don't stay green until you're red.** A project that goes from green to red without passing through amber tells the sponsor you either didn't know or didn't say. Amber is your friend: it is how you ask for help in time.
- **Explain the colour.** Every non-green status names the cause, the impact and what is needed.

## 8.4 The executive brief

Executives need a one-page view: what happened, what it means, and what they need to do. Template: [`templates/executive-brief.md`](../templates/executive-brief.md).

| Section | Content |
|---|---|
| **Headline** | One sentence: the result and its significance |
| **Results** | Two to four quantified outcomes in business terms |
| **What's next** | The next phase and its expected value |
| **Asks** | Specific decisions or help needed, with dates |
| **Risks** | The top two or three, with mitigations |

Write it so that the executive can forward it to their own boss unchanged. That is the best compliment an executive brief can receive.

## 8.5 Design notes and decision records

For technical decisions that the customer's engineers will inherit, write short design notes. A widely used lightweight format is the **architecture decision record (ADR)**, described by Michael Nygard in 2011:

```
# ADR 007: Use a read replica for policy data

Status: Accepted (2026-09-14)
Context: The policy admin system's production database is at 80% CPU at peak.
         The DBA team will not allow analytical queries against it.
Decision: Read from the nightly-refreshed replica. Coverage summaries may lag
          policy changes by up to 24 hours.
Consequences: Endorsements added today won't appear until tomorrow. Adjusters
              see a "data as of" timestamp. Revisit if CDC becomes available.
```

ADRs are invaluable at handover (Chapter 15). Six months later, nobody remembers why the system reads from a replica, and without the record someone will "fix" it and take down the policy database.

## 8.6 Field reports

The **field report** carries learning from the customer to your product team. It is the instrument of the feedback loop (Chapter 16). Template: [`templates/field-report.md`](../templates/field-report.md).

A good field report:

- describes the **problem**, not just the requested feature;
- shows **evidence**: quotes, screenshots, data, the workaround you built;
- quantifies **impact**: how many users, how much revenue at stake, how often;
- notes **other customers** with the same need (the rule of three);
- proposes a **generalisation**, if you have one.

Product teams receive many requests. Field reports that are specific, evidenced and quantified get acted on; vague ones ("customer X wants better search") don't.

## 8.7 Demos

A demo is the moment a customer sees whether their investment is working. Demos build belief when they show real progress on the customer's own problem, and destroy it when they look staged.

### Principles

- **Use their data.** A demo on the customer's real (or realistic, approved) data is worth ten on synthetic data. They will recognise the cases and test you on them.
- **Show the workflow, not the feature.** Walk through a real task from the user's point of view: "Here's a claim that came in yesterday. Here's what Sara did before; here's what she does now."
- **Start with the outcome.** "This week, pilot adjusters handled 412 claims with the coverage panel; median time on coverage questions dropped from 25 to 7 minutes. Let me show you how."
- **Let a user drive** when you can. A front-line user demonstrating the system to their own management is the most persuasive demo there is.
- **Show failure modes honestly.** "Here's a case it gets wrong, and here's how the adjuster sees that." It builds trust and pre-empts the sceptic's question.
- **Rehearse.** Run through the demo the day before on the same environment. Have a recording as backup.
- **End with asks and next steps.**

### Demo anti-patterns

| Anti-pattern | Why it backfires |
|---|---|
| Hard-coded "happy path" that only works on prepared examples | Someone asks for a different case and it breaks in front of the sponsor |
| Showing features nobody asked for | Signals you weren't listening |
| Forty minutes of slides before the software | The audience loses interest; it looks like there's nothing to show |
| Hiding latency or errors by editing a recording | Discovered later, it destroys credibility |
| Demoing AI as magic | Raises expectations the production system can't meet |

### Demoing AI systems

AI outputs vary. Prepare for it:

- Test the demo cases repeatedly, at the temperature and configuration you'll use live.
- Explain upfront that outputs vary slightly and how quality is measured (Chapter 13).
- Show citations and sources: they let the audience judge the answer.
- Have a curated set of difficult cases ready to show how the system handles uncertainty ("I can't find coverage information for this endorsement").

## 8.8 Explaining technical ideas to non-technical people

Most stakeholders don't need to understand how the system works; they need to understand what it does, how far to trust it, and what it means for them.

Techniques:

- **Analogy, then precision.** "Retrieval works like a very fast research assistant who finds the relevant pages of the policy before answering. It only answers from those pages, and it shows you which ones it used."
- **Concrete examples over abstractions.** Show one real case end to end.
- **Translate metrics.** "91% correct on our test set" means "about one in eleven summaries will have an error, which is why the adjuster still checks the cited clause."
- **Avoid jargon, or define it once.** Never say "RAG", "embeddings" or "hallucination" without a plain-language definition.
- **Check understanding** by asking what they'd tell their team, not "does that make sense?" (which people always answer yes).
- **Don't condescend.** Non-technical stakeholders are expert in their own domain. Treat the conversation as an exchange of expertise.

## 8.9 Hard conversations

### Delivering bad news

Bad news gets worse with age. A structure that works:

1. **State it plainly.** "We won't hit the week-8 milestone."
2. **Explain the cause briefly**, without blame. "The endorsements API access is two weeks late, and we can't produce complete summaries without it."
3. **Give the impact.** "The pilot will run two weeks longer, and the week-10 measurement moves to week 12."
4. **Offer options** with a recommendation. "We can launch with summaries flagged 'endorsements not included', or wait. I recommend launching flagged, because the base policy covers 80% of questions."
5. **Say what you need.** "Can you help us escalate the API access to the platform director?"

Do it in person or by call for significant news, then follow up in writing.

### Saying no

You will be asked to do things that are out of scope, unwise, unsafe or impossible. Effective refusals:

- **Acknowledge the need behind the request.** "I understand you need the board pack to include these figures."
- **Explain the reason**, briefly. "Writing directly to the ledger isn't covered by the security approval, and an error would be hard to reverse."
- **Offer an alternative.** "I can produce an export that your finance team reviews and imports."
- **Point to the agreed process** for anything bigger (change control, Chapter 6).

### Disagreeing with a customer expert

When an SME says the system's output is wrong, they may be right, wrong, or both (the system may be right on the data it saw, which is itself wrong). Treat it as an investigation: "Can you show me the case? Let's look at what the system saw." Never argue with an expert in front of their colleagues.

### Incidents

When something breaks in production (Chapter 15):

1. **Acknowledge quickly**, even before you know the cause. "We're aware the coverage panel is failing to load. We're investigating and will update by 11:00."
2. **Update on a schedule**, even if there's no news.
3. **Separate fixing from blame.** Root-cause analysis comes later.
4. **Follow up with a written incident report:** timeline, impact, cause, fix and prevention. A blameless format (focused on systems, not people) is standard practice.

## 8.10 Meetings

FDEs attend many meetings. Make them worth it:

- **Every meeting has a purpose and an owner.** Send the agenda in advance, including the decision you need.
- **Working sessions beat status meetings.** Spend customer time on building, reviewing and deciding; put status in writing.
- **Summarise in writing afterwards:** decisions, actions, owners, dates. Within 24 hours.
- **Protect makers' time.** Block days or half-days for focused engineering. Clustered meetings let you build.

## 8.11 Communicating across cultures and distance

FDEs work with customers in many countries and organisational cultures, and often split time between on site and remote.

- **Directness varies.** In some cultures, "that may be difficult" means no. In others, blunt criticism is a sign of respect. Learn the norms; when in doubt, ask a trusted local colleague. Erin Meyer's *The Culture Map* is a practical guide.
- **Hierarchy varies.** In some organisations, junior staff won't contradict a manager in a meeting. Talk to them separately.
- **Language.** If you're working in a second language for the customer (or they are for you), write more, speak more slowly, and confirm decisions in writing.
- **Time zones.** Overlap hours are precious; use them for conversation and decisions, and asynchronous writing for everything else.
- **Remote engagement.** When you're not on site, over-communicate: share screens, record short video walkthroughs, and keep a shared channel active. Being visible matters.

---

## Summary

- Communication determines whether field work is adopted, funded, approved and productised. It is part of the FDE's technical job.
- Answer first; know your audience and the decision; use their words; quantify; be honest about uncertainty; write it down.
- The weekly update, executive brief, decision records and field reports are the FDE's core documents. Templates are provided.
- Demos should use the customer's data, show the workflow and the outcome, let users drive, and show failure modes honestly.
- Explain technology through analogies, examples and translated metrics, without jargon or condescension.
- Deliver bad news early with options; say no by acknowledging the need and offering alternatives; handle incidents with fast acknowledgement and scheduled updates.

## Exercises

See [`exercises/08-communication.md`](../exercises/08-communication.md).

## Further reading

- Barbara Minto, *The Pyramid Principle* (1987).
- Michael Nygard, "Documenting Architecture Decisions" (2011), the original ADR post.
- Erin Meyer, *The Culture Map* (2014).
- Kerry Patterson et al., *Crucial Conversations* (3rd edition, 2021).
- Google, *Site Reliability Engineering* (2016), chapter on postmortem culture.
