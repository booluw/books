# Exercises: Chapter 5, Data Model

## Questions

1. Normalise: `HTTPS://WWW.Shop.Acme.co.uk/en/`, `bob@mail.eu.acme.com`, `acme.com.`, `jane@gmail.com`.
2. A demo request arrives from `li@acme-logistics.de` (company "Acme Logistik"). Your CRM has "Acme Logistics GmbH" (domain acme-logistics.de, owner Lee) and "ACME Logistics" (domain acme-logistics.de, no owner). What should matching return, and what clean-up is needed?
3. Write survivorship rules for merging two duplicate accounts.
4. Why must you never auto-create accounts from free-email domains?
5. Design the field-ownership table for: employee count, account owner, lifecycle stage, fit tier, phone number.

## Solutions

1. `acme.co.uk`, `acme.com`, `acme.com`, `gmail.com` (free email: do not use as a company).
2. Match by domain; tie-break to the owned record (Lee's) and flag the unowned duplicate for merge review (`examples/dedupe-and-matching` does this).
3. Example: survivor = record with open opportunities, else owned by an active user, else oldest; fields: non-empty wins, then most recent from trusted source; never overwrite human-edited notes; merge activity and contacts; log old IDs for integrations.
4. Thousands of unrelated people share them; you'd create a giant false "gmail.com" account and misroute leads.
5. Employee count: enrichment job (read-only for reps). Account owner: routing/territory process (changes via request). Lifecycle stage: marketing automation rules + sales conversion. Fit tier: scoring job / warehouse sync. Phone: enrichment initially, reps may correct, with source tracked.
