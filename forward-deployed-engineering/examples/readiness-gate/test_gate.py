import copy
import json
import pathlib
import unittest

from gate import GO, GO_WITH_CONDITIONS, NO_GO, evaluate, run_check, validate_checklist

SAMPLE = json.loads((pathlib.Path(__file__).parent / "checklist.json").read_text(encoding="utf-8"))


def sample():
    return copy.deepcopy(SAMPLE)


def item(checklist, item_id):
    return next(i for i in checklist["items"] if i["id"] == item_id)


def complete(checklist, item_id):
    i = item(checklist, item_id)
    i["status"] = "done"
    i["evidence"] = ["https://contoso.example/evidence"]


class GateTests(unittest.TestCase):
    def test_sample_is_go_with_conditions(self):
        r = evaluate(sample())
        self.assertEqual(r.verdict, GO_WITH_CONDITIONS)
        self.assertEqual([c.item_id for c in r.conditions], ["DR-1", "HAND-1"])
        self.assertEqual(r.conditions[0].due, "2026-11-30")
        self.assertEqual(len(r.notes), 1)                       # the minor training item
        self.assertEqual(len(r.passed), 10)

    def test_everything_done_is_go(self):
        c = sample()
        for i in c["items"]:
            complete(c, i["id"])
        self.assertEqual(evaluate(c).verdict, GO)

    def test_blocker_without_evidence_is_no_go(self):
        c = sample()
        item(c, "SEC-1")["evidence"] = []
        r = evaluate(c)
        self.assertEqual(r.verdict, NO_GO)
        self.assertIn("SEC-1", r.blocking[0])
        self.assertIn("no evidence link", r.blocking[0])

    def test_blocker_not_done_is_no_go_even_with_evidence(self):
        c = sample()
        item(c, "DATA-1")["status"] = "in_progress"
        self.assertEqual(evaluate(c).verdict, NO_GO)

    def test_eval_pass_rate_below_threshold_is_no_go(self):
        c = sample()
        c["metrics"]["eval_pass_rate"] = 0.87
        r = evaluate(c)
        self.assertEqual(r.verdict, NO_GO)
        self.assertIn("eval_pass_rate = 0.87 fails >= 0.9", r.blocking[0])

    def test_missing_metric_fails_the_check(self):
        c = sample()
        del c["metrics"]["high_risk_eval_pass_rate"]
        self.assertIn("not reported", evaluate(c).blocking[0])

    def test_latency_over_target_becomes_a_condition(self):
        c = sample()
        c["metrics"]["p95_latency_ms"] = 3400
        item(c, "OPS-5")["due"] = "2026-11-15"
        r = evaluate(c)
        self.assertEqual(r.verdict, GO_WITH_CONDITIONS)
        self.assertIn("OPS-5", [x.item_id for x in r.conditions])

    def test_major_without_due_date_or_owner_is_no_go(self):
        c = sample()
        del item(c, "DR-1")["due"]
        self.assertEqual(evaluate(c).verdict, NO_GO)
        c = sample()
        item(c, "HAND-1")["owner"] = ""
        self.assertEqual(evaluate(c).verdict, NO_GO)

    def test_overdue_condition_is_no_go(self):
        c = sample()
        item(c, "DR-1")["due"] = "2026-10-01"
        r = evaluate(c)
        self.assertEqual(r.verdict, NO_GO)
        self.assertIn("overdue", r.blocking[0])

    def test_minor_items_never_change_the_verdict(self):
        c = sample()
        complete(c, "DR-1")
        complete(c, "HAND-1")
        r = evaluate(c)
        self.assertEqual(r.verdict, GO)
        self.assertEqual(len(r.notes), 1)


class CheckTests(unittest.TestCase):
    def test_run_check_literal_and_metric_target(self):
        m = {"rate": 0.9, "p95": 2000, "target": 3000}
        self.assertIsNone(run_check({"metric": "rate", "op": ">=", "value": 0.9}, m))
        self.assertIsNotNone(run_check({"metric": "rate", "op": ">", "value": 0.9}, m))
        self.assertIsNone(run_check({"metric": "p95", "op": "<=", "metric_target": "target"}, m))

    def test_invalid_checklist(self):
        c = sample()
        c["items"].append(dict(item(c, "SEC-1")))                 # duplicate id
        c["items"][0]["severity"] = "critical"
        errors = validate_checklist(c)
        self.assertTrue(any("duplicate" in e for e in errors))
        self.assertTrue(any("severity" in e for e in errors))
        self.assertEqual(evaluate(c).verdict, NO_GO)


if __name__ == "__main__":
    unittest.main()
