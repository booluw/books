"""Map a Shopify-style order to a simplified ERP sales order.

Demonstrates the rules from Chapter 4: decimal money (never float), currency
minor units, UTC timestamps vs local business dates, explicit null/absent
handling, truncation with warnings, code-value maps and error codes.

Run the tests with:  python -m unittest discover -s . -p "test_*.py"
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

# ISO 4217 minor units for the currencies we accept.
MINOR_UNITS = {"USD": 2, "EUR": 2, "GBP": 2, "JPY": 0, "KWD": 3}

# Value map: storefront shipping method -> ERP shipping item. Kept as data,
# so business users could maintain it outside code.
SHIP_METHOD_MAP = {
    "standard": "SHIP-STD",
    "express": "SHIP-EXP",
    "next_day": "SHIP-NDA",
}

ADDR_LINE_MAX = 40  # target field length, in characters


class MappingError(Exception):
    """A business/data error: the record must go to the error queue, not be retried."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


@dataclass
class MappingResult:
    record: dict
    warnings: list[str] = field(default_factory=list)


def to_decimal(value, currency: str) -> Decimal:
    """Parse a money amount given as a string; quantise to the currency's minor units."""
    if isinstance(value, float):
        # Floats have already lost precision; refuse them rather than guess.
        raise MappingError("MAP-MONEY-001", "monetary amounts must be strings, not floats")
    places = MINOR_UNITS[currency]
    quantum = Decimal(1).scaleb(-places)  # e.g. 0.01 for 2 places, 1 for 0 places
    return Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP)


def normalise_text(value: str | None) -> str | None:
    """NFC-normalise and trim. None stays None (absent is not the same as empty)."""
    if value is None:
        return None
    return unicodedata.normalize("NFC", value).strip()


def truncate(value: str | None, limit: int, field_name: str, warnings: list[str]) -> str | None:
    if value is not None and len(value) > limit:
        warnings.append(f"{field_name} truncated from {len(value)} to {limit} characters")
        return value[:limit]
    return value


def business_date(instant_iso: str, store_tz: str) -> str:
    """Convert an instant to the *local* business date of the store.

    An order placed at 2026-10-09T23:30:00-07:00 belongs to 9 October in
    Los Angeles, even though it is already 10 October in UTC.
    """
    instant = datetime.fromisoformat(instant_iso.replace("Z", "+00:00"))
    if instant.tzinfo is None:
        raise MappingError("MAP-DATE-001", "timestamp has no UTC offset")
    return instant.astimezone(ZoneInfo(store_tz)).date().isoformat()


def map_order(order: dict, store_tz: str = "America/Los_Angeles") -> MappingResult:
    warnings: list[str] = []

    currency = order.get("currency")
    if currency not in MINOR_UNITS:
        raise MappingError("MAP-CUR-001", f"unsupported currency {currency!r}")

    lines = order.get("line_items") or []
    if not lines:
        raise MappingError("MAP-LINE-001", "order has no line items")

    ship = order.get("shipping_address")
    if ship is None:
        raise MappingError("MAP-ADDR-001", "shipping address is required")

    addr1 = truncate(normalise_text(ship.get("address1")), ADDR_LINE_MAX, "addr1", warnings)
    if not addr1:
        raise MappingError("MAP-ADDR-002", "address1 is empty")

    method = order.get("shipping_method", "standard")
    if method not in SHIP_METHOD_MAP:
        raise MappingError("MAP-SHIP-001", f"no ERP shipping item for method {method!r}")

    erp_lines = []
    total = Decimal(0)
    for i, line in enumerate(lines):
        sku = normalise_text(line.get("sku"))
        if not sku:
            raise MappingError("MAP-LINE-002", f"line {i} has no SKU")
        qty = int(line["quantity"])
        if qty < 1:
            raise MappingError("MAP-LINE-003", f"line {i} has quantity {qty}")
        rate = to_decimal(line["price"], currency)
        amount = rate * qty
        total += amount
        erp_lines.append({"item": sku.upper(), "quantity": qty, "rate": str(rate), "amount": str(amount)})

    declared = to_decimal(order["subtotal_price"], currency)
    if declared != total:
        raise MappingError("MAP-TOT-001", f"line total {total} != declared subtotal {declared}")

    record = {
        "externalId": f"SHOP-{order['id']}",          # upsert key: makes the write idempotent
        "tranDate": business_date(order["created_at"], store_tz),
        "currency": currency,
        "subtotal": str(total),
        "shipMethod": SHIP_METHOD_MAP[method],
        "shipAddress": {
            "addr1": addr1,
            "addr2": truncate(normalise_text(ship.get("address2")), ADDR_LINE_MAX, "addr2", warnings),
            "city": normalise_text(ship.get("city")),
            "zip": normalise_text(ship.get("zip")),
            "country": (ship.get("country_code") or "").upper(),
        },
        "items": erp_lines,
    }
    # Absent optional fields are omitted rather than sent as null, so a
    # partial update never wipes data in the target (Chapter 4, nulls vs absence).
    if record["shipAddress"]["addr2"] is None:
        del record["shipAddress"]["addr2"]
    return MappingResult(record=record, warnings=warnings)
