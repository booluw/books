# A safe webhook receiver (Chapters 7 and 10)

`receiver.py` verifies webhooks that follow the **Standard Webhooks** convention (`webhook-id`, `webhook-timestamp`, `webhook-signature: v1,<base64 HMAC-SHA256>`). It:

1. computes the HMAC over the **raw body bytes** (the tests show that re-serialised JSON fails);
2. uses a **constant-time** comparison;
3. rejects timestamps outside a **5-minute** window (replay protection);
4. accepts **old and new secrets** during rotation;
5. caps the body at 256 KiB (`413`);
6. **de-duplicates** on `webhook-id` (a duplicate gets `200` and is not re-queued);
7. **enqueues and returns `202` immediately**, while a worker thread processes events.

```bash
python3 receiver.py              # terminal 1
python3 send_test_webhook.py     # terminal 2: prints 202 then 200 (duplicate)
python3 -m unittest -v
```
