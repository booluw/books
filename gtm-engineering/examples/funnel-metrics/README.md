# Funnel metrics and experiment statistics (Chapters 3 and 15)

`funnel.py` includes:

- `ReverseFunnel`: from a revenue target back to opportunities, meetings, replies and emails (reproduces Chapter 3's worked example).
- CAC, CAC payback, LTV, NRR, pipeline velocity, coverage and cost per meeting (Appendix B).
- `sample_size_per_arm()`: contacts needed to detect a change in reply rate (2% to 3% needs about 3,800 per arm).
- `two_proportion_test()`: z and p-value for comparing two variants.

```bash
python3 funnel.py
python3 -m unittest -v
```
