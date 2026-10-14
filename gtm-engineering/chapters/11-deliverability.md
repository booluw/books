# Chapter 11. Email Deliverability Engineering

> "It doesn't matter how good the email is if it lands in spam."

## What you will learn

- How mailbox providers decide between inbox, spam and rejection.
- Email authentication: SPF, DKIM, DMARC and alignment, plus MX, PTR, BIMI and MTA-STS basics.
- The bulk-sender requirements of Gmail, Yahoo and Microsoft *(as of October 2026)*.
- Infrastructure for cold outreach: sending domains, inboxes, warmup, volumes and rotation.
- Content and list factors; monitoring (Google Postmaster Tools and others); diagnosing and recovering from problems.

Deliverability is the most "engineering" part of outbound, and one of the most common reasons GTM engineers are hired. Mistakes here can damage the company's primary domain, which also carries invoices, password resets and executives' email.

---

## 11.1 How filtering works

When your message arrives, the receiving provider (Gmail, Outlook, Yahoo, or a corporate gateway such as Microsoft Defender, Proofpoint or Mimecast) evaluates:

1. **Authentication:** is the sender who it claims to be (SPF, DKIM, DMARC)?
2. **Reputation:** of the sending **domain** (the visible From domain and the DKIM signing domain), the **IP address**, and sometimes linked domains (URLs in the body).
3. **Engagement:** do recipients open, reply, move messages out of spam, or mark them as spam? Spam complaints are among the strongest negative signals.
4. **Content:** suspicious links, link shorteners, heavy HTML or images, spammy language, attachments, mismatched display names.
5. **Volume patterns:** sudden spikes from a new domain look like spam.
6. **List quality:** bounces to invalid addresses and hits on **spam traps** (addresses that never opt in, or abandoned addresses repurposed to catch bad lists).

Outcomes: **inbox**, **spam/junk**, **tabs** (Gmail Promotions or Updates), **deferral** (temporary 4xx error, retry later) or **rejection** (permanent 5xx error).

## 11.2 Authentication

### SPF (Sender Policy Framework, RFC 7208)

A DNS TXT record on the sending domain listing servers allowed to send for it:

```
example-mail.com.  TXT  "v=spf1 include:_spf.google.com include:sendgrid.net ~all"
```

- `include:` delegates to a provider's list. `~all` (softfail) or `-all` (fail) for everything else.
- **10 DNS-lookup limit:** each `include`, `a`, `mx`, `exists` and `redirect` counts. Exceeding 10 causes a `permerror`, so SPF fails. Common when many tools are added.
- **Only one SPF record per domain.** Two `v=spf1` records also cause a `permerror`.
- SPF checks the **envelope sender** (Return-Path / `MAIL FROM`), not the visible From header.

### DKIM (DomainKeys Identified Mail, RFC 6376)

The sending server signs messages with a private key. The public key is published in DNS at `selector._domainkey.domain`:

```
google._domainkey.example-mail.com.  TXT  "v=DKIM1; k=rsa; p=MIIBIjANBgkq..."
```

Use 2048-bit keys where supported. Each sending service (Google Workspace, Microsoft 365, your sequencer, your marketing tool) needs its own DKIM set up **for your domain**, not the vendor's default domain.

### DMARC (RFC 7489)

A policy record telling receivers what to do when authentication fails, and where to send reports:

```
_dmarc.example-mail.com.  TXT  "v=DMARC1; p=none; rua=mailto:dmarc@example.com; adkim=r; aspf=r"
```

- `p=none` (monitor), `p=quarantine` (spam folder), `p=reject` (block).
- **Alignment:** DMARC passes only if SPF or DKIM passes **and** the authenticated domain aligns with the visible **From** domain (relaxed alignment: same organisational domain; strict: exact match).
- `rua` aggregate reports show who sends as your domain. Use a DMARC report analyser (Valimail, dmarcian, Red Sift, PowerDMARC, EasyDMARC, Postmark's free tool and others).

### Other records worth knowing

- **MX:** where the domain receives mail. Sending domains should be able to receive replies.
- **PTR (reverse DNS)** for sending IPs: handled by Google, Microsoft and ESPs, but required by Gmail for bulk senders.
- **TLS** for transmission: required by Gmail for bulk senders.
- **MTA-STS / TLS-RPT:** enforce and report on TLS for inbound mail.
- **BIMI:** shows a brand logo in some inboxes; requires DMARC enforcement (`quarantine` or `reject`) and usually a Verified Mark Certificate.

A tool that parses and checks SPF and DMARC records (lookup counting, duplicate records, policy and alignment warnings) is in [`examples/email-auth-checker/`](../examples/email-auth-checker/).

## 11.3 Mailbox-provider requirements *(as of October 2026)*

### Gmail (Google) and Yahoo, enforced from February 2024

For **all senders:** SPF *or* DKIM; valid forward and reverse DNS for sending IPs; TLS; spam rate in Postmaster Tools kept below 0.3% (aim below 0.1%); messages formatted per RFC 5322.

For **bulk senders** (Google defines these as sending about **5,000+ messages a day to Gmail** accounts; once classified, a sender stays classified):

- **SPF and DKIM** and **DMARC** (at least `p=none`), with **alignment** of the From domain.
- **One-click unsubscribe** (`List-Unsubscribe` and `List-Unsubscribe-Post` headers per RFC 8058) for **marketing and subscribed** messages, with unsubscribes honoured within **2 days**.
- **Spam rate below 0.3%.** Above it, Gmail mitigation (help from Google) becomes unavailable until the rate stays below 0.3% for 7 consecutive days.

From **November 2025**, Google stated it was ramping up enforcement: non-compliant bulk traffic receives temporary (4xx) and permanent (5xx) rejections, not just spam-foldering.

### Microsoft (Outlook.com, Hotmail, Live): from May 2025

Microsoft announced in April 2025 that domains sending **more than 5,000 emails a day** to its consumer domains (outlook.com, hotmail.com, live.com) must pass **SPF, DKIM and DMARC** (at least `p=none`, aligned). From 5 May 2025, non-compliant messages are routed to Junk, with rejection (`550 5.7.515 Access denied, sending domain ... does not meet the required authentication level`) announced for a later date. Microsoft also recommends functional unsubscribe links, list hygiene and a valid sender address.

### What this means for cold outreach

Most cold-outreach programmes send well under 5,000 messages a day *per domain to Gmail*. But **the principles apply to everyone:** authenticate fully, keep complaint rates very low, make it easy to opt out, and keep lists clean. Providers' filters apply reputation logic regardless of the bulk-sender threshold, and enforcement has only tightened. Many teams include a `List-Unsubscribe` header and a plain-language opt-out line in cold emails too, which also helps legal compliance (Chapter 16).

## 11.4 Infrastructure for outbound

### Protect the primary domain

**Do not send cold outreach from your primary domain** (`example.com`). Use **secondary sending domains** that resemble the brand (`example-mail.com`, `tryexample.com`, `getexample.com`), redirecting their websites to the main site. If a secondary domain's reputation is damaged, the primary domain keeps working for customers, finance and executives.

The trade-off: secondary domains are a known cold-outreach pattern, and some recipients find them less trustworthy. Some companies with strong relevance and low volumes send carefully from the primary domain or a subdomain. Know the risk you are taking.

### Domains and inboxes

A common 2026 pattern (vendor guidance; treat as rules of thumb):

- **2–3 inboxes per sending domain.**
- **Roughly 30–50 cold emails per inbox per day**, including follow-ups. Fewer for new inboxes.
- **Scale with more domains and inboxes,** not more volume per inbox. For example, about 500 sends a day needs roughly 12–16 warmed inboxes across 5–8 domains.
- **Real mailboxes** on reputable providers (Google Workspace, Microsoft 365), with real names, profile photos, signatures and the ability to receive replies. Some teams use specialised infrastructure providers; check their reputation and terms.
- **Domain age:** new domains have no reputation. Register in advance, set up DNS, and warm up.

### Warmup

**Warmup** gradually builds sending reputation:

- Start low (about 5–10 emails a day) and ramp over about **2–4+ weeks** before full cold volume.
- **Warmup networks** (built into Instantly, Smartlead, Lemlist and others, or standalone tools) exchange emails between participating inboxes, generating opens and replies. They are widely used but controversial: providers may detect artificial patterns, and engagement with real recipients matters more.
- The best warmup is **real, wanted email** (to colleagues, existing contacts) and highly relevant first campaigns that earn replies.

### Rotation and throttling

Sequencers rotate sends across inboxes and spread them through the day with random intervals. Configure **daily caps per inbox**, **send windows** in recipients' time zones, and **automatic pausing** when bounce or complaint rates spike.

## 11.5 List and content hygiene

- **Verify every address** (Chapter 7). Keep bounce rates below about 2% (lower is better). Remove hard bounces immediately.
- **Avoid catch-all domains in bulk,** or send to them slowly.
- **Suppress** unsubscribes, complainers, competitors, existing customers (for cold plays) and prior "not interested" replies.
- **Target precisely:** relevance drives replies, and replies drive reputation.
- **Plain-text first emails;** few or no links; no link shorteners; no images or attachments; avoid open tracking on cold emails (tracking pixels and redirect domains can hurt). If you must track links, use a **custom tracking domain**.
- **Consistent From name and signature;** working reply-to.
- **Vary copy** across sends (spintax, AI variants, or several templates). Thousands of identical bodies look like a campaign, though variation is no substitute for relevance.

## 11.6 Monitoring

| Tool | What it shows |
|---|---|
| **Google Postmaster Tools** | Domain and IP reputation, spam rate, authentication and compliance status for Gmail traffic (requires enough volume) |
| **Microsoft SNDS** | IP-level data for Outlook.com (for dedicated IPs) |
| **DMARC reports** | Who sends as your domain; pass/fail |
| **Sequencer analytics** | Bounces, replies, per-inbox health |
| **Seed / placement tests** | Send to test inboxes to estimate inbox vs spam placement (GlockApps, Instantly and Smartlead placement tests, and others). Indicative only |
| **Blocklist monitors** | Spamhaus, Barracuda and other listings (MXToolbox and similar) |

Set **alerts**: spam rate > 0.1% (warning) or > 0.3% (critical); bounce rate > 2%; sudden drop in reply rate; blocklist listing; DMARC failures from a new source.

## 11.7 Diagnosing and recovering

**Symptom:** reply rate fell from 3% to 0.5% across a domain.

1. **Check authentication:** did a DNS change break SPF (too many lookups after adding a tool)? Did DKIM keys rotate? Use the checker example or `dig TXT`.
2. **Check reputation and spam rate** in Postmaster Tools.
3. **Check blocklists.**
4. **Check recent changes:** new list source (bounces?), new copy (links?), volume increase, new tracking domain.
5. **Placement test** on a few inboxes.
6. **Recover:** pause cold sends on the affected domain; fix the root cause; resume at low volume with the most engaged, most relevant audience; ramp slowly. If a domain is badly burned, retire it. Never let damage spread to the primary domain.

---

## Summary

- Filtering weighs authentication, domain and IP reputation, engagement (especially complaints), content, volume patterns and list quality.
- Configure SPF (one record, at most 10 lookups), DKIM (per service, your domain), and DMARC with alignment. Know MX, PTR, TLS, MTA-STS and BIMI basics.
- Gmail and Yahoo (from 2024, tightened from November 2025) and Microsoft (from May 2025) require authentication, low spam rates and easy unsubscribes for high-volume senders. Treat the principles as universal.
- Protect the primary domain; use warmed secondary domains and real inboxes at modest per-inbox volumes; rotate and throttle.
- Verify lists, suppress properly, send plain and relevant emails, monitor reputation, and recover methodically.

## Exercises

See [`exercises/11-deliverability.md`](../exercises/11-deliverability.md).

## Further reading

- Google, *Email sender guidelines* and FAQ (support.google.com/a/answer/81126 and /14229414).
- Yahoo Sender Hub (senders.yahooinc.com).
- Microsoft, "Strengthening Email Ecosystem: Outlook's New Requirements for High-Volume Senders" (Microsoft Tech Community, April 2025).
- RFC 7208 (SPF), RFC 6376 (DKIM), RFC 7489 (DMARC), RFC 8058 (one-click unsubscribe).
- M3AAWG best-practice documents (m3aawg.org).
