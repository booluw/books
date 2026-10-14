# Enrichment waterfall (Chapter 7)

`waterfall.py` tries email providers in order and stops at the first result that passes verification.

| Behaviour | Why |
|---|---|
| Verify after every provider; continue on `invalid` | A "found" email that bounces is worse than none |
| `catch_all` accepted only by policy | Catch-all domains can't be confirmed |
| Reject emails on a different domain from the company | Catches wrong-person matches |
| Provider errors give `retry_later` and are not cached | An outage isn't proof the email doesn't exist |
| Cache by normalised name + domain within a freshness window | Never pay twice |
| Budget cap per run | Credits are money |
| Source, verification and timestamp stored | Audit providers; refresh selectively |

```bash
python3 waterfall.py
python3 -m unittest -v
```
