# Chapter 18. Life as an FDE: Pace, Travel, Ethics and Sustainability

> "The job will take everything you give it. Decide in advance what you won't give."

## What you will learn

- What a week, a month and a year as an FDE actually look like.
- The rewards and the costs of the role, honestly.
- How to manage travel, context switching and intense engagements sustainably.
- The ethical questions FDEs face, and a framework for handling them.
- How to keep growing technically while working in the field.

---

## 18.1 What the work feels like

Palantir's engineering blog, in its "day in the life" posts, describes FDE days that move between writing code, sitting with analysts, meeting customer leadership, and debugging data pipelines, often on site. Accounts from FDEs at AI labs and start-ups in 2025–2026 describe a similar mix, with more time on model evaluation and agent design.

A composite week on a production deployment:

| Day | Morning | Afternoon |
|---|---|---|
| Monday | Travel to customer; planning with customer owner | Unblock access requests; pairing with customer engineer |
| Tuesday | Shadow two claims adjusters | Build: retrieval fixes from what you saw |
| Wednesday | Evaluation run; read failures | Security review call; update threat model |
| Thursday | Demo to pilot users | Field report to product team; travel home |
| Friday | Deep work: pipeline hardening (remote) | Weekly update; plan next week |

The texture: high variety, high autonomy, high visibility, frequent interruption, and a direct line between your work and someone's day getting better.

## 18.2 Rewards

People who love the role usually cite:

- **Impact you can see.** You watch people use what you built, and the numbers move.
- **Learning speed.** A new industry, new systems and new problems every few months. Former FDEs often describe learning more in two years than in five elsewhere.
- **Ownership and autonomy.** You're trusted to make decisions on the ground.
- **Breadth.** Engineering, data, AI, product, communication and business, all in one role.
- **Career options.** FDE experience leads to product management, founding companies, engineering leadership and executive roles (Chapter 19). Many Palantir alumni went on to found companies.
- **Compensation**, which in 2025–2026 rose as demand outstripped supply (Chapter 19).

## 18.3 Costs

The costs are real, and better faced in advance:

- **Travel.** Some roles are mostly on site; others mostly remote with periodic visits. Travel strains relationships, health and routines. Ask about expected travel before accepting a role, and get it in numbers (for example "up to 50%" or "one week per month").
- **Context switching.** Customers, product team, sales and support all want your time. Deep work is hard to protect.
- **Pressure.** Deadlines tied to deals, executives watching, problems in production you're expected to fix.
- **Ambiguity.** No one hands you a spec. That's the job, but it's tiring.
- **Being the outsider.** You're inside the customer but not of it, and away from your own team.
- **Technical breadth versus depth.** Rapid rotation can leave you feeling you never go deep (§18.6).
- **Emotional labour.** Managing frustrated stakeholders, absorbing blame for things outside your control, staying positive in difficult engagements.

Commentators in 2026 noted that FDE roles at AI start-ups can be particularly intense, because the FDE is often central to closing and keeping revenue.

## 18.4 Sustainability

### Personal practices

- **Protect deep work.** Block focus time and defend it. Batch meetings.
- **Set travel boundaries** with your manager: maximum nights per month, recovery days after long trips, flexibility for life events.
- **Keep routines portable:** exercise, sleep and food habits that survive hotel rooms.
- **Write things down** so your memory isn't the system of record. It reduces stress and helps handover.
- **Escalate early.** Many FDE crises are made worse by trying to absorb them alone (Chapter 8 §8.9).
- **Take real breaks between engagements.** Plan them; they won't happen otherwise.
- **Find peers.** Other FDEs understand the job in a way your customer and your product team can't.

### Warning signs of burnout

**Burnout** is chronic workplace stress that hasn't been successfully managed. The World Health Organization's ICD-11 classification describes it by three dimensions: exhaustion, cynicism or detachment from the job, and reduced professional effectiveness. Watch for: dreading customer calls, cynicism about the customer or your own company, persistent fatigue, small mistakes increasing. Talk to your manager, use your leave, and ask for a rotation. A good FDE organisation will treat this as a capacity problem to solve, not a personal failing (Chapter 17 §17.9).

## 18.5 Ethics

FDEs work close to consequential decisions: who gets a loan, which claims are paid, how police or military resources are deployed, which patients are flagged. The proximity creates ethical responsibility, and sometimes ethical discomfort.

Palantir is the canonical example of the debate: its work with immigration enforcement, defence and intelligence agencies has drawn protests and employee concern, while the company has argued that supporting democratic governments and their institutions is a moral commitment. AI labs have faced their own debates over military and government work. Whatever your view, you'll work in this territory, and you should think about it before you're in the room.

### Questions to ask yourself

- **Purpose:** what is this deployment for? Who benefits, and who could be harmed?
- **Legitimacy:** is it lawful, and is it consistent with the customer's stated policies and my company's?
- **Proportionality:** are the risks to people proportionate to the benefit?
- **Fairness:** could it treat groups of people unfairly? Have we measured it (Chapter 13)?
- **Transparency:** do the people affected know, where they should?
- **Accountability:** is there a human accountable for consequential decisions, and a way to appeal?
- **My red lines:** what would I refuse to work on?

### Common situations

| Situation | Approach |
|---|---|
| Asked to bypass a security or privacy control "to hit the deadline" | Decline; offer alternatives; escalate if pressed (Chapter 14) |
| Customer wants to use the system for a purpose beyond what was approved | Raise it with your lead and the customer's compliance team; don't silently enable it |
| Evaluation shows the system performs worse for a group of people | Report it to the sponsor and your company; don't ship until it's understood and addressed |
| Sales wants you to demo a capability that doesn't exist | Refuse to misrepresent; offer an honest demo (Chapter 7 §7.5) |
| You learn something that suggests wrongdoing at the customer | Follow your company's legal and ethics escalation process; don't investigate alone |
| Personal moral objection to a customer or use case | Raise it early with your manager; many companies allow you to step away from specific work |

### Use the institutions

Most companies have codes of conduct, acceptable-use policies for their products, ethics or responsible-AI review processes, and confidential reporting channels. Know them before you need them. AI providers' usage policies set limits on how their models may be used; an FDE deploying those models should know the relevant limits.

## 18.6 Growing technically in the field

The breadth of FDE work can leave engineers feeling technically shallow. Ways to keep growing:

- **Pick a depth area** (data infrastructure, security, retrieval, evaluation, a particular industry) and seek engagements that use it.
- **Productise your field work** (Chapter 16): building the generalised version is a deep engineering exercise.
- **Rotate** through a product team periodically.
- **Write:** internal design docs, playbook chapters, external posts where allowed. Writing turns experience into understanding.
- **Teach:** onboarding new FDEs forces you to explain what you do and why.
- **Keep a learning log:** after each engagement, record the technical things you learned and the questions you couldn't answer.

---

## Summary

- FDE work is varied, autonomous and visible, with a direct line from your work to user impact.
- Its rewards (impact, learning, ownership, breadth, career options, pay) come with real costs (travel, context switching, pressure, ambiguity, outsider status, emotional labour).
- Sustain yourself by protecting deep work, setting travel boundaries, writing things down, escalating early, taking real breaks and finding peers. Recognise burnout and treat it as a capacity problem.
- FDEs work close to consequential decisions. Ask about purpose, legitimacy, proportionality, fairness, transparency and accountability; know your red lines and your company's escalation routes.
- Keep growing technically by choosing a depth area, productising, rotating, writing, teaching and keeping a learning log.

## Exercises

See [`exercises/18-life-as-an-fde.md`](../exercises/18-life-as-an-fde.md).

## Further reading

- Palantir blog, "A Day in the Life of a Palantir Forward Deployed Software Engineer."
- Cal Newport, *Deep Work* (2016).
- Christina Maslach and Michael Leiter, *The Burnout Challenge* (2022).
- World Health Organization, "Burn-out an 'occupational phenomenon'" (2019), on the ICD-11 definition.
- Kate Crawford, *Atlas of AI* (2021), for a critical view of AI's social context.
