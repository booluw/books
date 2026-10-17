# Discovery Guide: <Customer>: <Engagement name>

*Version: <n> · Date: <YYYY-MM-DD> · Prepared by: <FDE name(s)>*

## How to use this template

- **Purpose:** plan, run and synthesise discovery so that you understand how the customer's operation actually works before you decide what to build. Discovery exists to prevent the most expensive FDE mistake: building the wrong thing well.
- **When:** Phase 1 (Discover) of the [engagement lifecycle](../chapters/04-engagement-lifecycle.md), typically the first one to three weeks. Discovery never fully stops; reuse the note format and question banks throughout.
- **Owner:** the lead FDE (or deployment strategist, where there is one).
- **Sign-off:** the synthesis (Part 7) is agreed with the customer's executive sponsor at the discovery readout. The interview plan is shared with the customer's day-to-day owner, who usually helps book sessions.
- **Feeds into:** the [problem decomposition canvas](problem-decomposition-canvas.md) and the [success plan](success-plan.md).

Background reading: [Chapter 5](../chapters/05-discovery-and-decomposition.md).

---

## Part 1. Preparation checklist

*Complete before the first customer meeting. Tick each item and note where you put the result.*

| # | Item | Done | Notes / link |
|---|---|---|---|
| 1 | Read the annual report, investor presentations and regulatory filings; list stated strategic priorities and risks | ☐ | |
| 2 | Read recent press releases and industry coverage | ☐ | |
| 3 | Scan the customer's job postings for named systems and pain ("experience with <legacy system> required") | ☐ | |
| 4 | Read the deal history: what sales promised, what the customer asked for, proof-of-concept results, objections | ☐ | |
| 5 | Talk to the account executive and any previous FDE or solutions engineer on the account | ☐ | |
| 6 | Learn the domain vocabulary; build a glossary of terms you will hear | ☐ | |
| 7 | Write down 2–3 hypotheses: "We think the biggest opportunity is <X> because <Y>." | ☐ | |
| 8 | Draft the stakeholder list across levels (Part 2) and ask the customer owner to fill gaps | ☐ | |
| 9 | Confirm confidentiality rules, recording policy and what you may observe (especially in regulated settings) | ☐ | |
| 10 | Request early read access to sample artefacts (reports, forms, spreadsheets, process documents) | ☐ | |
| 11 | Start access requests that will take longest (accounts, VPN, data permissions); access is the hidden critical path | ☐ | |

**Hypotheses** *(record them so you can see later which were wrong):*

1. <Hypothesis 1>
2. <Hypothesis 2>
3. <Hypothesis 3>

**Glossary started:** <link>

---

## Part 2. Interview plan by stakeholder level

*Talk across levels and functions. Talk to the front line early: executives describe the process as designed; operators know the process as performed. Aim for at least two people per row so one voice does not dominate.*

| Level | Name | Role | What we want to learn | Format (interview / shadow / workshop) | Date | Interviewer | Status |
|---|---|---|---|---|---|---|---|
| Executive sponsor | | | Strategic goals, budget, definition of success, politics | Interview, 45 min | | | |
| Middle managers | | | Where the process breaks; metrics they are judged on; resource constraints | Interview, 45–60 min | | | |
| Front-line operators | | | How work is really done; workarounds; tools they love and hate | Shadow ½ day + interview | | | |
| IT and data owners | | | Systems, data access, integration, past failures | Interview, 60 min, technical | | | |
| Security, risk, legal, compliance | | | Approval processes, red lines, timelines | Interview, 45 min | | | |
| Sceptics | | | Real risks; reasons adoption could fail | Interview, 30–45 min, 1:1 | | | |

*Sceptics are usually the people whose work will change most. Ask the customer owner directly: "Who is least likely to welcome this, and why?" Interview them one to one, without their manager present.*

**Example (filled):**

| Level | Name | Role | What we want to learn | Format | Date | Interviewer | Status |
|---|---|---|---|---|---|---|---|
| Front-line operators | Priya S. | Senior claims adjuster, Woodgrove Bank Insurance | How coverage questions are resolved today; side spreadsheets | Shadow ½ day + 30 min interview | 2026-11-04 | <FDE> | Booked |

---

## Part 3. Interview principles (read before every session)

- **Ask about the past, not hypotheticals.** "Tell me about the last time…" produces facts; "Would you use…?" produces polite yeses.
- **Follow the work.** "What happened next? Who did you ask? Where did you look that up?"
- **Ask for artefacts.** "Can you show me the spreadsheet?"
- **Quantify.** How often, how long, how many people.
- **Listen for emotion.** Frustration, fear and pride point to what matters.
- **Don't pitch.** Discovery is not a demo. If asked about the product, answer briefly and return to their work.
- **Write it up the same day,** with verbatim quotes.

**Session structure (45–60 minutes):**

| Minutes | Step |
|---|---|
| 0–5 | Introductions; purpose; confidentiality; permission to take notes (and to record, if agreed) |
| 5–10 | Their role, team and responsibilities in their words |
| 10–40 | Core questions (Part 4); follow the work; ask for artefacts |
| 40–50 | "What did I not ask that I should have?" · "Who else should I talk to?" |
| 50–60 | Summarise back what you heard; agree any follow-ups and artefacts to send |

---

## Part 4. Question banks

*Pick 5–8 questions per session. Do not read the list aloud; use it as a prompt.*

### Executives

- What are the top three outcomes you are accountable for this year?
- If this engagement succeeds wildly, what is different in 12 months? How would you know?
- How is that measured today, and who owns the number?
- What has been tried before? Why didn't it work?
- Who else needs to be convinced? Who might resist?
- What budget and people can you commit, and from when?
- What would make you cancel this project?
- How do you want to hear about progress, and how often?

### Middle managers

- Walk me through a typical week for your team. Where does the time go?
- Which metrics are you measured on? Which are hardest to hit?
- Where do errors or delays come from? Show me an example from last week.
- Which cases or exceptions consume a disproportionate share of effort?
- If you had two extra people, what would you have them do?
- What reports do you produce or receive, and which do you actually use?
- How would a change in your team's workflow be approved and rolled out?

### Front-line operators

- Show me how you do <task>, step by step, on a real case.
- What do you do when <exception> happens?
- Which tools or spreadsheets do you keep on the side? Why?
- Which data do you double-check before you trust it?
- What is the most annoying part of your day?
- Who do you wait for, and how do you chase them?
- What would you never trust a computer to do here?
- If you could change one thing about this process, what would it be?

### IT and data owners

- Which systems are involved in this process? Who owns each?
- What interfaces exist (APIs, exports, database access, files)? What breaks?
- How do we get access, realistically, and how long does it take?
- Which data is sensitive or regulated? How is it classified?
- Where are the environments (cloud, on-premises, air-gapped)? What is the deployment process?
- What has the security team rejected before, and why?
- What monitoring, identity and logging standards must a new system meet?
- Who would support this system after we leave?

### Security, risk, legal and compliance

- What is your review process for a new vendor or system, step by step, and how long does each step take?
- Which documents do you need from us (security questionnaire, SOC 2 report, ISO 27001 certificate, data processing agreement, penetration test)?
- What are the red lines: data that may never leave a region or network, uses of AI you will not approve?
- What is your position on sending data to third-party model providers? On retention by the provider?
- Which regulations and internal policies apply to this use case?
- Who signs off, and who can escalate a stalled review?

### Sceptics

- What worries you about this project?
- What happened the last time a new system arrived in your team?
- What would the system have to get right for you to rely on it?
- What would make your job worse?
- If this fails, why will it have failed?

*Treat sceptics as your best source of risk information, not as obstacles. Record their concerns in the risk register and tell them later what you did about them.*

---

## Part 5. Shadowing observation sheet

*Sit with people while they work for half a day or a shift. Ask permission, explain your purpose, take notes rather than recordings unless agreed, and follow the customer's rules on what you may observe. One sheet per session.*

| Field | Entry |
|---|---|
| Person / role | |
| Team / location | |
| Date and time window | |
| Work observed (process, case types) | |
| Observer | |
| Confidentiality constraints | |

### Step log

| Time | Step / action | System or tool used | Duration | Waiting on (person / system) | Workaround observed | Exception? (Y/N, what) | Notes / quotes |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |

### Observation prompts

*Tick what you saw and describe it.*

| Prompt | Seen? | Detail |
|---|---|---|
| **Workarounds:** sticky notes, personal spreadsheets, copy-paste between systems | ☐ | |
| **Exceptions:** cases that take far longer than the norm | ☐ | |
| **Hidden dependencies:** phone calls, emails, waiting for another team | ☐ | |
| **Real timing** versus the process document | ☐ | |
| **Trust:** data people double-check, data they rely on | ☐ | |
| **Rework:** steps repeated because of errors upstream | ☐ | |
| **Artefacts** worth collecting (with permission) | ☐ | |

**Example (filled step log row):**

| Time | Step / action | System or tool used | Duration | Waiting on | Workaround | Exception? | Notes / quotes |
|---|---|---|---|---|---|---|---|
| 10:12 | Checks whether flood damage is covered under endorsement | Policy admin system + PDF schedule | 14 min | Underwriting (emailed, no reply by end of session) | Personal spreadsheet of "tricky endorsements" | Y: endorsement not in system | "Half my week is waiting for underwriting to answer emails like this." |

---

## Part 6. Note-taking format

*One note per interview or session, written up the same day. Keep raw notes separate from interpretation.*

```
Session:        <interview / shadow / workshop>
Date:           <YYYY-MM-DD>
Person / role:  <name, role, team>  (or anonymised ID if agreed)
Interviewer(s): <names>
Consent:        notes ☐   recording ☐   quotes attributable ☐ / anonymised ☐

1. Context
   <their role, team size, responsibilities in their words>

2. What they told us (facts, with numbers)
   - <fact> (frequency / duration / volume)
   - ...

3. Verbatim quotes
   - "<quote>"
   - ...

4. Artefacts seen or received
   - <artefact>: <where stored>

5. Pain points and workarounds
   - <pain point>: <evidence>

6. Our interpretation (clearly marked as ours)
   - <interpretation>

7. Hypotheses supported / challenged
   - H<n>: supported / challenged / no evidence because <reason>

8. Follow-ups
   - [ ] <action> (owner, date)

9. Who else to talk to
   - <name / role>: <why>
```

*Store notes where the customer's confidentiality rules allow. Do not paste customer data into personal tools or unapproved AI assistants.*

---

## Part 7. Synthesis

*Synthesise after each batch of five or so sessions, not only at the end.*

### Step 1. Gather and tag

Put every fact, quote and observation on its own line (a spreadsheet or sticky notes). Tag each with source, level and theme.

| # | Observation / quote | Source (session ID) | Level | Theme | Quantified? |
|---|---|---|---|---|---|
| | | | | | |

### Step 2. Cluster into themes

| Theme | Number of sources | Levels represented | Strongest evidence |
|---|---|---|---|
| | | | |

*A theme backed by one executive's opinion is weaker than one backed by five operators and a system log. Note disagreements between levels; they are often the most important finding.*

### Step 3. Map the current state

Produce three maps (see [Chapter 5 §5.6](../chapters/05-discovery-and-decomposition.md)):

- [ ] **Workflow map:** steps, actors, decisions, handoffs, systems, time per step, error points (Mermaid swimlane).
- [ ] **Systems map:** each system's owner, technology, data held, interfaces, access process.
- [ ] **Data inventory:**

| Data source | Contents | Volume | Freshness | Quality (observed) | Sensitivity | Legal basis | Access path | Owner |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

### Step 4. List candidate problems

| # | Candidate problem | Business driver it affects | Evidence (themes, sources) | Rough value | Initial feasibility concerns |
|---|---|---|---|---|---|
| | | | | | |

### Step 5. Check hypotheses

| Hypothesis | Verdict | Evidence |
|---|---|---|
| H1 | Supported / rejected / unclear | |
| H2 | | |
| H3 | | |

### Step 6. Decompose and score

Take the top candidates into the [problem decomposition canvas](problem-decomposition-canvas.md).

### Step 7. Discovery readout

*A short document plus a 30-minute readout to the sponsor. Executives should leave able to explain the plan to their peers.*

1. **What we learned**, in the customer's language, with quotes.
2. **Current-state maps:** workflow, systems, data.
3. **Problem decomposition** with value and feasibility estimates.
4. **Recommended first use case** with rationale, and a backlog of others.
5. **Risks and constraints.**
6. **Proposed success criteria** (carry into the [success plan](success-plan.md)).

| Readout date | Attendees | Agreed? | Changes requested |
|---|---|---|---|
| | | Yes / with changes / no | |

**Sponsor agreement:** <name, role> · <date> · <"The team can explain our operation in our own words": yes / no>
