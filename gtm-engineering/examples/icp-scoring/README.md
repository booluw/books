# ICP fit scoring (Chapter 4)

`icp_scoring.py` scores accounts against an ICP with transparent rules. Every point comes with a reason (`+25 640 employees (core band 200-2,000)`), and the model version is stored with the score, so sellers can see *why* an account is Tier 1 and you can change the model safely.

- Disqualifiers (no domain, competitor, existing customer) override points.
- Unknown values are recorded as unknown, not guessed.

```bash
python3 icp_scoring.py sample_accounts.csv
python3 -m unittest -v
```

Calibrate the weights against closed-won and closed-lost data each quarter (Chapter 4 §4.5).
