# Deduplication and lead-to-account matching (Chapter 5)

`matching.py` provides:

- `registrable_domain()`: URL, hostname or email to registrable domain, handling multi-part suffixes such as `co.uk`. Production code should use the full Public Suffix List (`tldextract`).
- `is_free_email_domain()`: never match accounts on gmail.com and friends.
- `normalise_company_name()` and `name_similarity()`: strip legal suffixes and accents; token and sequence similarity.
- `match_lead_to_account()`: domain → additional domains → fuzzy name, with tie-breaking among duplicates (owned, open opportunities, customer) and a `needs_review` flag for borderline fuzzy matches.
- `ultimate_parent()`: walk the hierarchy for routing to global owners.
- `find_duplicate_accounts()`: same-domain and high-similarity-name pairs.

```bash
python3 -m unittest -v
```
