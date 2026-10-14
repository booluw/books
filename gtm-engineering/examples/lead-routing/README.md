# Lead routing (Chapter 9)

`router.py` encodes rules of engagement in order:

1. Disqualify spam, competitors, and free-email leads with no company.
2. Existing customer → account manager (or the CS queue if the AM has left).
3. Open opportunity → opportunity owner.
4. Owned account with an active owner → account owner.
5. Territory + segment → **weighted, availability-aware round robin** (skips out-of-office reps and reps at their daily cap; never assigns to deactivated reps).
6. Nobody available → fallback queue and alert.

Every decision returns a reason string for the audit log. The round-robin pointer lives in a store object; the tests show it surviving a "restart".

```bash
python3 -m unittest -v
```
