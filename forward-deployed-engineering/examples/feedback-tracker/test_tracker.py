import unittest

from tracker import (HERE, Cluster, _report, FieldReport, cluster_reports, concepts, jaccard, load_reports,
                     prioritise)


def report(id, customer, problem, tags=(), arr=100_000, severity="medium"):
    return FieldReport(id, customer, "fde", "2026-09-01", problem, "", severity, arr, list(tags))


class ConceptTests(unittest.TestCase):
    def test_synonyms_and_phrases_normalise(self):
        self.assertEqual(concepts(report("1", "A", "Needs SAML via Okta")), {"sso"})
        self.assertEqual(concepts(report("2", "B", "Single sign-on please")), {"sso"})
        self.assertEqual(concepts(report("3", "C", "Users log in twice")), {"sso"})
        self.assertEqual(concepts(report("4", "D", "An audit trail of answers")), {"audit-log"})
        self.assertEqual(concepts(report("5", "E", "Export to Excel or CSV")), {"export"})

    def test_tags_are_lower_cased_and_merged(self):
        self.assertEqual(concepts(report("1", "A", "download results", tags=["Reporting "])),
                         {"reporting", "export"})

    def test_jaccard(self):
        self.assertEqual(jaccard({"a", "b"}, {"a"}), 0.5)
        self.assertEqual(jaccard(set(), set()), 0.0)


class ClusterTests(unittest.TestCase):
    def test_rule_of_three_counts_distinct_customers(self):
        reports = [report("1", "Contoso", "SSO", ["sso"]),
                   report("2", "Contoso", "SSO again", ["sso"]),
                   report("3", "Fabrikam", "Okta login")]
        c = cluster_reports(reports)
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0].recommendation, "WATCH")         # 3 reports, but only 2 customers
        reports.append(report("4", "Litware", "SAML", ["sso"]))
        self.assertEqual(cluster_reports(reports)[0].recommendation, "PRODUCTISE")

    def test_arr_counted_once_per_customer(self):
        c = Cluster([report("1", "Woodgrove", "x", arr=1_200_000),
                     report("2", "Woodgrove", "x", arr=1_200_000),
                     report("3", "Litware", "x", arr=280_000)])
        self.assertEqual(c.arr_affected, 1_480_000)

    def test_unrelated_needs_stay_apart(self):
        c = cluster_reports([report("1", "A", "Okta SSO"), report("2", "B", "Export to Excel")])
        self.assertEqual(len(c), 2)

    def test_prioritisation_order(self):
        big_one_off = Cluster([report("1", "A", "x", arr=5_000_000)])
        small_common = Cluster([report(str(i), c, "x", arr=10_000) for i, c in enumerate("BCD")])
        pair = Cluster([report("5", "E", "x", arr=50_000), report("6", "F", "x", arr=50_000)])
        ranked = prioritise([big_one_off, pair, small_common])
        self.assertEqual([c.recommendation for c in ranked], ["PRODUCTISE", "WATCH", "FIELD SOLUTION"])

    def test_bad_severity_rejected(self):
        with self.assertRaises(ValueError):
            _report({"id": "x", "customer": "A", "problem": "p", "severity": "urgent"})


class SampleTests(unittest.TestCase):
    def setUp(self):
        self.reports = load_reports(HERE / "field_reports.json") + load_reports(HERE / "more_reports.csv")
        self.ranked = prioritise(cluster_reports(self.reports))

    def test_loads_json_and_csv(self):
        self.assertEqual(len(self.reports), 14)
        csv_report = next(r for r in self.reports if r.id == "FR-011")
        self.assertEqual((csv_report.tags, csv_report.arr_affected), (["sso"], 280_000.0))

    def test_sample_priorities(self):
        summary = [(c.recommendation, len(c.customers), c.arr_affected) for c in self.ranked]
        self.assertEqual(summary, [
            ("PRODUCTISE", 4, 2_580_000),        # audit log of AI answers
            ("PRODUCTISE", 4, 2_430_000),        # SSO
            ("PRODUCTISE", 3, 590_000),          # export
            ("WATCH", 2, 550_000),               # SharePoint permissions
            ("FIELD SOLUTION", 1, 600_000),      # Welsh language
        ])
        self.assertIn("audit-log", self.ranked[0].label)

    def test_untagged_report_clusters_by_keywords(self):
        # FR-014 has no tags; 'SharePoint' in the text puts it with FR-007.
        sharepoint = next(c for c in self.ranked if "sharepoint" in c.label)
        self.assertEqual([r.id for r in sharepoint.reports], ["FR-007", "FR-014"])


if __name__ == "__main__":
    unittest.main()
