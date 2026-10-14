# Signal pipeline (Chapter 8)

`signals.py` turns raw signals into actions:

- **Normalise** domains and emails; reject unknown signal types.
- **De-duplicate** on type + entity + day, so the same funding round from two feeds counts once.
- **Score** with per-type weights and half-lives: `weight × 0.5^(age / half_life)`.
- **Act** when the account score crosses a threshold, with a **cool-down**; **hand-raisers** (demo requests, champion job changes) act immediately even inside a cool-down.
- **Suppress** customers in active deals, competitors and opt-outs.
- Every action lists the contributing signals as reasons.

```bash
python3 signals.py
python3 -m unittest -v
```
