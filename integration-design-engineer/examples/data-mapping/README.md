# Data mapping with golden-file tests (Chapters 4 and 15)

`mapping.py` turns a Shopify-style order into a simplified ERP sales order and applies Chapter 4's rules:

- Money is parsed from **strings** into `Decimal` and rounded half-up to the currency's **ISO 4217 minor units** (JPY 0, USD 2, KWD 3). Floats are rejected.
- `tranDate` is the order's **local business date** in the store's IANA time zone, not the UTC date.
- Text is **NFC-normalised** and trimmed. Over-long address lines are **truncated with a warning**.
- **Absent optional fields are omitted**, not sent as `null`, so a partial update cannot wipe target data.
- Shipping methods go through a **value map**.
- Data problems raise `MappingError` with a stable **error code** (`MAP-ADDR-001`, …), which routes the record to a business error queue instead of a retry loop.
- `externalId` is derived from the source ID, so the ERP write can be an **idempotent upsert**.

## Run

```bash
python3 -m unittest -v
```

## Add a regression case

Drop `fixtures/<case>.input.json` and `fixtures/<case>.expected.json` into the folder. The golden-file test picks them up automatically.
