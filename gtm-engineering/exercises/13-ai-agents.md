# Exercises: Chapter 13, AI Agents

## Questions

1. Rank by AI maturity for production use: autonomous AI SDR, title-to-persona classification, account research brief, full-email generation, reply classification.
2. Design an evaluation for an LLM step that answers "Does this company sell to enterprise customers?" from its website.
3. A research agent can browse the web and also send emails. What's the risk? Redesign it.
4. Design an 8-week AI SDR pilot with a holdout.
5. Your persona classifier misses 4% of "unsubscribe" replies. Why is that unacceptable, and what do you do?

## Solutions

1. Most to least mature: classification ≈ reply classification > research brief > full-email generation > autonomous AI SDR.
2. 150 labelled companies (YES/NO/UNKNOWN with evidence); metrics: accuracy, precision and recall for YES, UNKNOWN rate, evidence validity, cost per row; compare prompt and model versions; monitor monthly.
3. Prompt injection from web pages could instruct it to send emails or leak data. Separate it: the research agent has read-only tools and outputs structured findings; deterministic code and a human approve and send.
4. Randomise comparable accounts into AI, existing process and holdout arms; define meetings held and pipeline as primary metrics; approval for the first weeks, then sampling; enforce suppression in your own code; track spam complaints, quality errors and total cost.
5. Missed unsubscribes mean continuing to email people who opted out, a legal and reputational failure. Add keyword rules as a high-recall backstop, tune for recall on that class, route ambiguous replies to humans, and audit.
