# Exercises: Chapter 11, Deliverability

## Questions

1. Your SPF is `v=spf1 include:_spf.google.com include:sendgrid.net include:mailgun.org include:servers.mcsv.net include:spf.protection.outlook.com include:_spf.salesforce.com ~all`. What risk do you check first? Use `examples/email-auth-checker` with a zone you construct.
2. Explain DMARC alignment with an example that passes SPF but fails DMARC.
3. Plan infrastructure for 600 cold emails a day starting in 4 weeks.
4. Postmaster shows spam rate 0.4% on one domain. What do you do?
5. Does a startup sending 800 cold emails a day need to follow Gmail's bulk-sender rules?

## Solutions

1. The 10-DNS-lookup limit (nested includes can push you over, causing permerror), and also that only one SPF record exists.
2. The sequencer sends with envelope sender `bounce@vendor-mail.com` (SPF passes for vendor-mail.com) but the From is `jane@example-mail.com`, and DKIM is signed by vendor-mail.com. Neither authenticated domain aligns with example-mail.com, so DMARC fails. Fix: custom return-path and DKIM on your domain.
3. ~600 ÷ 40 per inbox = 15 inboxes; ~6–8 secondary domains at 2–3 inboxes each; register now, configure SPF, DKIM and DMARC plus MX; warm for 3–4 weeks ramping from 5–10 a day; start campaigns at partial volume with the most relevant segments; monitor.
4. Pause cold sends on the domain; check list source, bounces, recent copy and volume changes; check authentication; resume slowly with highly relevant contacts once below 0.1%; retire the domain if it doesn't recover; keep the primary domain isolated.
5. The bulk threshold (~5,000/day to Gmail) may not apply, but authentication, low complaint rates, easy opt-out and list hygiene apply to everyone's reputation, and enforcement keeps tightening, so follow them anyway.
