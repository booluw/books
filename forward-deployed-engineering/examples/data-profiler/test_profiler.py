import pathlib
import unittest

from profiler import (find_duplicate_keys, find_ragged_rows, is_placeholder, profile_column,
                      profile_csv, shape, value_type)

SAMPLE = pathlib.Path(__file__).parent / "sample.csv"


class ValueHelperTests(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(shape("CLM-1001"), "AAA-9999")
        self.assertEqual(shape("SW1A 1AA"), "AA9A 9AA")
        self.assertEqual(shape("clm-1013"), "aaa-9999")

    def test_shape_collapse_groups_different_lengths(self):
        self.assertEqual(shape("POL-48291", collapse=True), shape("POL-482913", collapse=True))

    def test_placeholders_are_case_and_space_insensitive(self):
        for v in ["N/A", " unknown ", "TBC", "0000-00-00", "null"]:
            self.assertTrue(is_placeholder(v), v)
        self.assertFalse(is_placeholder("Contoso"))

    def test_value_types(self):
        self.assertEqual(value_type("42"), "integer")
        self.assertEqual(value_type("980.50"), "decimal")
        self.assertEqual(value_type("2026-03-02"), "date")
        self.assertEqual(value_type("07/03/2026"), "date")
        self.assertEqual(value_type("yes"), "boolean")
        self.assertEqual(value_type("£1,200.00"), "text")


class ColumnProfileTests(unittest.TestCase):
    def test_null_and_placeholder_rates_are_separate(self):
        c = profile_column("x", ["a", "", None, "N/A", "b"])
        self.assertEqual((c.null_count, c.placeholder_count), (2, 1))
        self.assertAlmostEqual(c.null_rate, 0.4)
        self.assertAlmostEqual(c.missing_rate, 0.6)

    def test_numeric_min_max_is_numeric_not_alphabetic(self):
        c = profile_column("amount", ["9", "10", "100.5"])
        self.assertEqual(c.inferred_type, "decimal")
        self.assertEqual((c.min, c.max), ("9", "100.5"))

    def test_mixed_column_is_reported_as_mixed(self):
        c = profile_column("x", ["1", "2", "three", "four"])
        self.assertTrue(c.inferred_type.startswith("mixed"))

    def test_off_type_values_are_flagged(self):
        c = profile_column("d", ["2026-01-01"] * 9 + ["yesterday"])
        self.assertIn(("yesterday", "not a date", 1), c.suspicious)

    def test_sentinel_numbers_flagged(self):
        c = profile_column("amount", ["10", "20", "99999999"])
        self.assertIn(("99999999", "sentinel number", 1), c.suspicious)


class TableTests(unittest.TestCase):
    def test_duplicate_keys_ignore_case_and_padding(self):
        rows = [{"id": "A-1"}, {"id": "a-1 "}, {"id": "A-2"}]
        self.assertEqual(find_duplicate_keys(rows, "id"), {"A-1": 2})

    def test_ragged_rows(self):
        rows = [{"a": "1", "b": "2"}, {"a": "1", "b": "2", None: ["x"]}, {"a": "1", "b": None}]
        self.assertEqual(find_ragged_rows(rows), [3, 4])

    def test_sample_file_findings(self):
        p = profile_csv(str(SAMPLE))
        self.assertEqual(p.row_count, 20)
        self.assertEqual(p.key, "claim_id")
        self.assertEqual(p.duplicate_keys, {"CLM-1003": 2})
        self.assertEqual(p.ragged_rows, [7])                 # the unquoted '£1,200.00'
        claim_date = p.column("claim_date")
        self.assertEqual(claim_date.inferred_type, "date")
        reasons = {(v, r) for v, r, _ in claim_date.suspicious}
        self.assertIn(("0000-00-00", "placeholder"), reasons)
        self.assertIn(("yesterday", "not a date"), reasons)
        self.assertEqual(dict(p.column("claim_id").shapes)["aaa-9999"], 1)


if __name__ == "__main__":
    unittest.main()
