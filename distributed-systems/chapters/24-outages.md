# Chapter 24. Learning from Outages

> "Every outage is a lesson someone else already paid for. Read the bill."

## What you will learn

- How to read a public post-incident report and extract the distributed-systems lesson.
- Eight major outages, each connected to the principles in this book.
- The recurring patterns: global changes, hidden dependencies, retry storms, metastability, races in control planes and loss of the tools needed to recover.
- Design and operational practices that address them.

The accounts below are summarised from the companies' own public post-incident reports and reputable coverage. They simplify complex events; read the original reports (listed in Further reading) for full detail.

---

## 24.1 How to read a post-incident report

For each incident, ask:

1. **Trigger:** what started it? (Often a routine change.)
2. **Propagation:** why did it spread beyond the component that failed?
3. **Sustaining effect:** why didn't it stop when the trigger stopped? (Chapter 17 §17.9.)
4. **Detection and recovery:** what slowed diagnosis and repair?
5. **Principle:** which idea from this book would have prevented or contained it?

## 24.2 Amazon S3, us-east-1, February 2017

**What happened.** While debugging a billing system issue, an engineer ran an established playbook command intended to remove a small number of servers from an S3 subsystem. An input was entered incorrectly, and a larger set of servers was removed, including servers supporting two critical subsystems: the **index** subsystem (metadata and location of all objects in the region) and the **placement** subsystem (allocation of storage for new objects). Both needed a full restart. They hadn't been fully restarted in the larger regions for many years, and S3 had grown enormously in the meantime, so the restart and safety checks took far longer than expected: several hours. Many other AWS services and countless websites that depended on S3 in that region failed. AWS's own Service Health Dashboard couldn't be updated for part of the incident, because it depended on S3.

**Lessons.**
- **Tools must limit blast radius.** AWS changed the tool to remove capacity more slowly and to refuse to take a subsystem below its minimum required capacity.
- **Recovery paths decay if unexercised.** A restart procedure not run at current scale is an untested procedure (Chapter 23).
- **Partition large subsystems into cells** so that any one restart is small (Chapter 17 §17.5).
- **Status and recovery tooling must not depend on the thing that failed.**

## 24.3 GitHub, October 2018

**What happened.** Routine maintenance to replace failing optical equipment caused a **43-second loss of connectivity** between GitHub's US East Coast network hub and its primary US East Coast data centre. GitHub's MySQL topology manager (Orchestrator, using Raft among its own nodes) saw the primaries as unreachable and **promoted replicas in the US West Coast** data centre to be primaries for several clusters. When connectivity returned, the East Coast primaries had accepted writes during the brief window that weren't on the new West Coast primaries, and applications in the East now wrote across the country with much higher latency. GitHub chose to preserve data integrity over availability: it degraded the service for about 24 hours while it restored from backups, replayed the divergent writes and resynchronised replicas.

**Lessons.**
- **Short partitions can cause long outages** (Chapter 2 §2.4). Failover is an irreversible action taken under uncertainty.
- **Asynchronous replication plus failover loses or forks writes** (Chapter 6 §6.2). Without fencing the old primaries (Chapter 12), both sides accepted writes.
- **Failover policy must encode topology:** promoting a primary in a different region changed latency for every write, which the applications weren't designed for.
- GitHub's write-up is a model of choosing **consistency over availability** deliberately and explaining why.

## 24.4 Cloudflare, July 2019

**What happened.** A new rule for Cloudflare's web application firewall contained a regular expression that caused **catastrophic backtracking**, consuming 100% of CPU on every HTTP-serving core. The rule was deployed **globally at once**, through a system designed to push WAF rule updates quickly (for responding to new threats), so CPU exhaustion hit Cloudflare's whole network within minutes and traffic dropped by about 80% for 27 minutes. Recovery used a global kill switch for the WAF rules.

**Lessons.**
- **Global, simultaneous configuration changes are the most dangerous changes** (Chapter 19 §19.8). Configuration is code and deserves staged rollout.
- **Bound resource use per request** (regular-expression engines with linear-time guarantees, CPU limits per rule).
- **Kill switches** must exist, be tested and not depend on the failing path.

## 24.5 Facebook, October 2021

**What happened.** During routine maintenance, a command intended to assess the capacity of Facebook's global backbone network **unintentionally took down all the connections** in the backbone, disconnecting its data centres from each other and from the internet. An audit tool meant to block such commands had a bug that let it through. Facebook's DNS servers were designed to **withdraw their BGP route announcements** when they couldn't reach the data centres (a sensible health check in normal times), so Facebook's DNS disappeared from the internet and its domains stopped resolving. Facebook, Instagram, WhatsApp and Messenger were down for about six hours. Recovery was slowed because remote access and internal tools also depended on the network that was down; engineers had to work physically in data centres, where security protections (designed to be hard to bypass) slowed access.

**Lessons.**
- **Health checks that remove capacity can amplify failure** (Chapter 18 §18.6): every DNS server withdrew itself at once, because they shared the same failing dependency.
- **Safety checks need testing too** (the audit tool).
- **Out-of-band access** (management networks, physical access procedures) must not depend on the production network.
- **Recovery can overload systems:** Facebook described carefully bringing load back to avoid power and cache surges as billions of clients reconnected (Chapter 18 §18.4).

## 24.6 AWS us-east-1, December 2021

**What happened.** According to AWS's summary, an automated activity to scale capacity of a service hosted in AWS's main network triggered **unexpected behaviour from a large number of clients inside the internal network**, causing a large surge of connection activity that overwhelmed the networking devices between the internal network and the main AWS network. Communication between the networks suffered high latency and errors, which caused clients to **retry**, increasing the load further: a congestion collapse. AWS's internal monitoring, which ran on the internal network, was impaired, slowing diagnosis. Many AWS services and their customers in us-east-1 were affected for several hours.

**Lessons.**
- **Retries and reconnection storms sustain overload** (metastable failure, Chapter 17 §17.9).
- **Back-off behaviour of clients is a system property**: a latent bug in how many clients responded to errors only mattered when they all saw errors together.
- **Monitoring must not share fate** with what it monitors.

## 24.7 CrowdStrike, July 2024

**What happened.** CrowdStrike pushed a content update (a "channel file") for its Falcon endpoint security sensor to Windows hosts worldwide. The file caused the sensor's kernel-mode component to read out of bounds, crashing Windows on about **8.5 million devices** (Microsoft's estimate). Airlines, hospitals, banks and broadcasters were disrupted. Because the crash happened at boot, many machines needed manual remediation, sometimes complicated by disk encryption recovery keys.

**Lessons.** Although not a classic "distributed system" bug, this is the largest-scale example of the most common outage pattern in this chapter:
- **Content and configuration updates were pushed to every host at once**, without staged rollout. CrowdStrike's post-incident review committed to staged deployment of content updates and customer control over update timing.
- **Validation must match production behaviour:** the content validator didn't catch the mismatch that caused the out-of-bounds read.
- **Privileged components need fail-safe behaviour** for bad input.

## 24.8 Google Cloud, June 2025

**What happened.** According to Google's incident report, a new feature was added to **Service Control**, the system that checks API requests for policy and quota across Google Cloud, without a feature flag. Weeks later, a policy change containing unintended blank fields was written to a regional Spanner table and **replicated globally within seconds**. Every Service Control instance that processed it hit a null-pointer path that crashed it, in every region, causing widespread API errors across Google Cloud and services built on it for several hours. A "red button" kill switch was rolled out within about 40 minutes, but in the large us-central1 region, Service Control tasks restarting together created a **herd effect** on the underlying Spanner database, prolonging recovery there, because the restart logic lacked randomised exponential backoff.

**Lessons.**
- **Globally replicated configuration is a global change** (Chapter 6): replication spread the poison in seconds.
- **Feature flags and staged enablement** for new code paths (Chapter 19 §19.8).
- **Fail open or degrade** for non-critical checks when their inputs are invalid.
- **Restarts need jittered backoff** (Chapter 17 §17.3) to avoid stampeding shared dependencies.

## 24.9 AWS us-east-1, October 2025

**What happened.** According to AWS's post-event summary, a **latent race condition** in the automated system that manages DNS records for DynamoDB's regional endpoint caused the endpoint's DNS record to become **empty**. The system had independent "enactor" processes applying DNS plans; one enactor was unusually delayed while applying an **older** plan, a second enactor applied a **newer** plan and then ran clean-up of old plans, which deleted the plan the delayed enactor had just applied, removing all IP addresses for the endpoint. Clients and AWS services couldn't resolve DynamoDB in us-east-1. After DNS was manually restored, a second problem emerged: an EC2 subsystem that manages leases for the physical servers hosting instances (which depended on DynamoDB) had fallen so far behind that, when it resumed, it entered **congestive collapse**, timing out and retrying work faster than it could complete it, until operators throttled it and restarted hosts. Network load balancer health checks then misjudged capacity as new instances came up. Recovery across many services took most of a day.

**Lessons.**
- **Control planes are distributed systems too**, with the same races as data planes. The race is a stale-plan overwrite that a **fencing token** or version check (Chapter 12 §12.5) on the DNS update would have rejected; it's exactly the bug the `LockWithFencing` model in Chapter 5 finds.
- **Metastable recovery**: a backlog after the trigger was fixed kept a dependent system overloaded (Chapter 17 §17.9). Recovery needed load to be cut far below normal first.
- **Hidden dependency chains**: DNS → DynamoDB → EC2 lease management → instance launches → load balancer health → many services.
- AWS's remediation included disabling the automation globally until the race was fixed, adding safeguards against applying stale plans, and adding rate limiting to the EC2 subsystem's recovery.

## 24.10 Recurring patterns

| Pattern | Incidents | Defences | Chapter |
|---|---|---|---|
| A change applied everywhere at once | Cloudflare 2019, CrowdStrike 2024, Google Cloud 2025, Facebook 2021 | Staged rollout, canaries, feature flags, cells, validation | 19 |
| Failover or automation acting on uncertain information | GitHub 2018, AWS 2025 | Fencing, consensus-based decisions, conservative timeouts, human approval for irreversible steps | 2, 6, 12 |
| Retries and reconnection storms | AWS 2021, Google Cloud 2025, AWS 2025 | Retry budgets, jitter, backoff on restarts, load shedding | 17 |
| Metastable states after the trigger | AWS 2021, AWS 2025, S3 2017 (slow restart) | Break feedback loops; test recovery at scale; throttled restarts | 17, 23 |
| Health checks that remove all capacity | Facebook 2021 | Cap ejections; consider shared-dependency failure | 18 |
| Monitoring and tooling sharing fate | S3 2017, Facebook 2021, AWS 2021 | Independent out-of-band paths | 22 |
| Unexercised recovery procedures | S3 2017, Facebook 2021 | Game days, chaos experiments, regular restarts | 23 |

The common thread is not exotic algorithms. It's the core ideas of this book applied to the *operation* of systems: assume partial failure and uncertainty, bound blast radius, make actions idempotent and fenced, don't let reactions amplify faults, and test the paths you hope never to use.

---

## Summary

- Read post-incident reports for trigger, propagation, sustaining effect, detection and recovery, and principle.
- S3 2017: a mistyped capacity command and a slow cold restart; limit tool blast radius and exercise recovery.
- GitHub 2018: a 43-second partition triggered cross-region failover and forked writes; consistency was chosen over availability during repair.
- Cloudflare 2019, CrowdStrike 2024 and Google Cloud 2025: global configuration or content changes without staging.
- Facebook 2021: a backbone command plus self-withdrawing DNS took everything offline, and recovery tools shared fate.
- AWS 2021 and 2025: retry storms and congestive collapse; in 2025, a stale-plan race in DNS automation that fencing would have prevented.
- Recurring defences: staged change, fencing and consensus for automation, retry budgets and jitter, capped health-check ejection, independent tooling, and practised recovery.

## Exercises

See [`exercises/24-outages.md`](../exercises/24-outages.md).

## Further reading

- Amazon Web Services, "Summary of the Amazon S3 Service Disruption in the Northern Virginia (US-EAST-1) Region" (March 2017).
- GitHub, "October 21 post-incident analysis" (GitHub blog, October 2018).
- Cloudflare, "Details of the Cloudflare outage on July 2, 2019" (Cloudflare blog).
- Facebook Engineering, "More details about the October 4 outage" (October 2021).
- Amazon Web Services, "Summary of the AWS Service Event in the Northern Virginia (US-EAST-1) Region" (December 2021 and October 2025).
- CrowdStrike, "Channel File 291 Incident: Root Cause Analysis" (August 2024).
- Google Cloud, "Google Cloud Service Health incident report" for the 12 June 2025 Service Control incident.
- Dan Luu, "Post-mortems" (github.com/danluu/post-mortems), a curated collection.
