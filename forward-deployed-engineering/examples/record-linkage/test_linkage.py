import unittest

from linkage import (HERE, Record, block_keys, candidate_pairs, classify, evaluate, jaro,
                     jaro_winkler, link, load_labels, load_records, normalise_name,
                     normalise_phone, normalise_postcode, score_pair)


class NormalisationTests(unittest.TestCase):
    def test_company_suffixes_case_and_punctuation(self):
        self.assertEqual(normalise_name("Fabrikam, Inc."), "fabrikam")
        self.assertEqual(normalise_name("CONTOSO LIMITED"), normalise_name("Contoso Ltd"))
        self.assertEqual(normalise_name("The Adventure Works Group plc"), "adventure works")

    def test_accents_and_ampersand(self):
        self.assertEqual(normalise_name("Café Müller & Söhne GmbH"), "cafe muller and sohne")

    def test_postcode_and_phone(self):
        self.assertEqual(normalise_postcode("sw1a 1aa"), "SW1A1AA")
        self.assertEqual(normalise_phone("+44 20 7946 0002"), normalise_phone("020 7946 0002"))


class SimilarityTests(unittest.TestCase):
    def test_jaro_known_values(self):
        # Classic textbook examples.
        self.assertAlmostEqual(jaro("MARTHA", "MARHTA"), 0.9444, places=4)
        self.assertAlmostEqual(jaro_winkler("MARTHA", "MARHTA"), 0.9611, places=4)
        self.assertAlmostEqual(jaro_winkler("DWAYNE", "DUANE"), 0.84, places=2)

    def test_bounds(self):
        self.assertEqual(jaro_winkler("contoso", "contoso"), 1.0)
        self.assertEqual(jaro("abc", ""), 0.0)
        self.assertEqual(jaro("abc", "xyz"), 0.0)

    def test_missing_fields_do_not_penalise(self):
        a = Record("a", "Northwind Traders", "M1 1AE", "f@northwind.example", "0161 496 0003")
        b = Record("b", "Northwind Traders", "M1 1AE", "f@northwind.example", "")
        score, fields = score_pair(a, b)
        self.assertEqual(score, 1.0)
        self.assertIsNone(fields["phone"])


class LinkingTests(unittest.TestCase):
    def setUp(self):
        self.crm = load_records(HERE / "crm.csv")
        self.billing = load_records(HERE / "billing.csv")
        self.labels = load_labels(HERE / "labels.csv")

    def test_blocking_reduces_comparisons_but_keeps_true_pairs(self):
        pairs = {(a.id, b.id) for a, b in candidate_pairs(self.crm, self.billing)}
        self.assertLess(len(pairs), len(self.crm) * len(self.billing) / 4)
        self.assertTrue(self.labels <= pairs)

    def test_block_keys(self):
        self.assertEqual(block_keys(Record("x", "Contoso Ltd", "SW1A 1AA")), {"pc:SW1A", "nm:cont"})

    def test_thresholds(self):
        self.assertEqual(classify(0.95), "match")
        self.assertEqual(classify(0.80), "review")
        self.assertEqual(classify(0.50), "non-match")

    def test_sample_results(self):
        cands = {(c.left_id, c.right_id): c.decision for c in link(self.crm, self.billing)}
        self.assertEqual(cands[("C2", "B2")], "match")          # punctuation + suffix + phone format
        self.assertEqual(cands[("C8", "B9")], "match")          # typo: Litware / Litwear
        self.assertEqual(cands[("C4", "B4")], "review")         # different email: a person decides
        self.assertNotIn(("C6", "B6"), cands)                   # different branch: not linked
        self.assertNotIn(("C1", "B10"), cands)                  # same postcode, different firm

    def test_one_to_one(self):
        cands = link(self.crm, self.billing)
        self.assertEqual(len({c.left_id for c in cands}), len(cands))
        self.assertEqual(len({c.right_id for c in cands}), len(cands))

    def test_precision_and_recall(self):
        cands = link(self.crm, self.billing)
        auto = evaluate(cands, self.labels)
        self.assertEqual((auto.true_positives, auto.false_positives, auto.false_negatives), (7, 0, 1))
        self.assertAlmostEqual(auto.recall, 7 / 8)
        with_review = evaluate(cands, self.labels, include_review=True)
        self.assertEqual((with_review.precision, with_review.recall), (1.0, 1.0))

    def test_lower_review_threshold_trades_precision_for_recall(self):
        cands = link(self.crm, self.billing, review=0.6, one_to_one=False)
        e = evaluate(cands, self.labels, include_review=True)
        self.assertEqual(e.recall, 1.0)
        self.assertLess(e.precision, 1.0)                       # Contoso Pharmaceuticals vs Litwear


if __name__ == "__main__":
    unittest.main()
