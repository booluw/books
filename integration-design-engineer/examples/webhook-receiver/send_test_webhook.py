"""Sign and send a sample webhook to the local receiver (python receiver.py must be running)."""
import json
import time
import urllib.request
import uuid

from receiver import sign

SECRET = b"whsec_demo_secret"
body = json.dumps({"type": "order.paid", "data": {"order_id": "ORD-55821"}}).encode()
webhook_id = f"msg_{uuid.uuid4().hex}"
timestamp = int(time.time())

for attempt in (1, 2):  # send twice to show duplicate handling
    request = urllib.request.Request(
        "http://127.0.0.1:8080/webhooks/demo",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "webhook-id": webhook_id,
            "webhook-timestamp": str(timestamp),
            "webhook-signature": sign(SECRET, webhook_id, timestamp, body),
        },
    )
    with urllib.request.urlopen(request) as response:
        print(f"attempt {attempt}: HTTP {response.status}")   # 202, then 200 (duplicate)
