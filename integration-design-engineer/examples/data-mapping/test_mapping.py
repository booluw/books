"""Golden-file and edge-case tests for mapping.py (Chapter 4 and Chapter 15)."""
import json
import pathlib
import unittest

from mapping import MappingError, business_date, map_order, to_decimal

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


class GoldenFileTests(unittest.TestCase):
    """Every fixtures/<case>.input.json must map to fixtures/<case>.expected.json.

    Adding a regression case means adding two files; no code change is needed.
    """

    def test_golden_files(self):
        cases = sorted(FIXTURES.glob("*.input.json"))
        self.assertTrue(cases, "no fixtures found")
        for input_path in cases:
            name = input_path.name.removesuffix(".input.json")
            with self.subTest(case=name):
                order = json.loads(input_path.read_text(encoding="utf-8"))
                expected = json.loads((FIXTURES / f"{name}.expected.json").read_text(encoding="utf-8"))
                self.assertEqual(map_order(order).record, expected)

    def test_truncation_produces_warning(self):
        order = json.loads((FIXTURES / "unicode_truncation.input.json").read_text(encoding="utf-8"))
        result = map_order(order)
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("addr1 truncated", result.warnings[0])


class EdgeCaseTests(unittest.TestCase):
    def base_order(self, **overrides):
        order = json.loads((FIXTURES / "basic_usd.input.json").read_text(encoding="utf-8"))
        order.update(overrides)
        return order

    def test_float_money_is_rejected(self):
        with self.assertRaises(MappingError) as ctx:
            to_decimal(19.99, "USD")
        self.assertEqual(ctx.exception.code, "MAP-MONEY-001")

    def test_rounding_is_half_up_to_minor_units(self):
        self.assertEqual(str(to_decimal("1.005", "USD")), "1.01")
        self.assertEqual(str(to_decimal("1.0005", "KWD")), "1.001")
        self.assertEqual(str(to_decimal("1500.4", "JPY")), "1500")

    def test_local_business_date_differs_from_utc_date(self):
        # 06:30 UTC on 10 Oct is still 9 Oct in Los Angeles (UTC-7 in October).
        self.assertEqual(business_date("2026-10-10T06:30:00Z", "America/Los_Angeles"), "2026-10-09")

    def test_timestamp_without_offset_is_rejected(self):
        with self.assertRaises(MappingError):
            business_date("2026-10-10T06:30:00", "America/Los_Angeles")

    def test_missing_address_is_business_error(self):
        with self.assertRaises(MappingError) as ctx:
            map_order(self.base_order(shipping_address=None))
        self.assertEqual(ctx.exception.code, "MAP-ADDR-001")

    def test_subtotal_mismatch_is_detected(self):
        with self.assertRaises(MappingError) as ctx:
            map_order(self.base_order(subtotal_price="60.00"))
        self.assertEqual(ctx.exception.code, "MAP-TOT-001")

    def test_unknown_shipping_method(self):
        with self.assertRaises(MappingError) as ctx:
            map_order(self.base_order(shipping_method="drone"))
        self.assertEqual(ctx.exception.code, "MAP-SHIP-001")

    def test_large_id_survives_as_string(self):
        # 820982911946154508 > 2**53: a float-based JSON parser would corrupt it.
        record = map_order(self.base_order()).record
        self.assertEqual(record["externalId"], "SHOP-820982911946154508")

    def test_absent_optional_field_is_omitted_not_nulled(self):
        record = map_order(self.base_order()).record
        self.assertNotIn("addr2", record["shipAddress"])


if __name__ == "__main__":
    unittest.main()
