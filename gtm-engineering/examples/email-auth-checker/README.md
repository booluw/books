# SPF and DMARC checker (Chapter 11)

`auth_checker.py` checks a domain's SPF and DMARC records, explaining each finding:

- **SPF:** missing record; multiple `v=spf1` records (permerror); `+all` or `?all`; no `all`; **recursive DNS-lookup count** against the 10-lookup limit (includes and redirects); missing include targets; include loops.
- **DMARC:** missing record; invalid or missing `p=`; `p=none` (monitor only); missing `rua=` reports; `pct` below 100; strict alignment.

It reads TXT records through a resolver function, so it runs offline. The docstring shows how to plug in `dnspython` for live checks.

```bash
python3 auth_checker.py
python3 -m unittest -v
```
