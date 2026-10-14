# Exercises: Chapter 10, Outbound

## Questions

1. Write a play brief (template) for "companies that just opened a new warehouse".
2. Design stop conditions and reply handling for a 4-step sequence.
3. Run `examples/safe-personalization`. Add a check that rejects lines over 25 words, and a check for a competitor name list. Write tests.
4. Rewrite this email to follow §10.6: "Hi {first_name}, I hope this email finds you well! Our revolutionary AI platform is a game-changer for logistics. Can we book a 30-minute demo this week?"
5. Which metrics would you put on a play scorecard, and why not opens?

## Solutions

1. Should include hypothesis, audience, signal source (news, permits, job posts), why now, angle, offer, channels, exclusions, volume, QA, compliance, metrics and kill criteria.
2. Stop on any reply, meeting booked, unsubscribe, bounce, opportunity created or customer. Handle positive (alert, book), referral (add contact), not now (task in N months), not interested (suppress for a period), unsubscribe (global suppression), OOO (pause), wrong person (re-source).
3. Hands-on.
4. Example: "Hi Jane, noticed Acme is opening the Dallas hub in Q1. New sites usually mean dispatch plans get rebuilt from scratch. We helped Northpeak cut planning time by a third during their last opening. Worth comparing notes?" (Only use claims you can verify.)
5. Contacts, delivered, bounce, positive reply rate, meetings held, opportunities, pipeline, cost per meeting, unsubscribes. Opens are inflated by Apple Mail Privacy Protection, and tracking pixels can hurt deliverability.
