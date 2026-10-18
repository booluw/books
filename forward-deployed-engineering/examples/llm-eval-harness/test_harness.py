import json
import os
import tempfile
import unittest

from harness import (HERE, CaseResult, RunResult, compare_runs, extract_citations, fake_judge,
                     fake_model_v1, fake_model_v2, grade_citations, grade_contains, grade_exact,
                     grade_json_fields, grade_json_values, load_cases, run_eval)


class GraderTests(unittest.TestCase):
    def test_exact_normalises_case_space_and_full_stop(self):
        self.assertTrue(grade_exact("  Theft. ", {"value": "theft"})[0])
        self.assertFalse(grade_exact("burglary", {"value": "theft"})[0])

    def test_contains_all_any_none(self):
        check = {"all": ["excess"], "any": ["£100", "£250"], "none": ["guaranteed"]}
        self.assertTrue(grade_contains("A £100 Excess applies.", check)[0])
        self.assertFalse(grade_contains("A £100 excess applies, guaranteed.", check)[0])
        ok, why = grade_contains("No excess info.", {"all": ["excess", "£100"]})
        self.assertFalse(ok)
        self.assertIn("£100", why)

    def test_json_fields_types_and_fences(self):
        check = {"fields": {"customer": "str", "estimate_gbp": "number"}}
        self.assertTrue(grade_json_fields('```json\n{"customer": "Contoso", "estimate_gbp": 10}\n```', check)[0])
        ok, why = grade_json_fields('{"customer": "Contoso", "estimate_gbp": "10"}', check)
        self.assertFalse(ok)
        self.assertIn("estimate_gbp should be number", why)
        self.assertFalse(grade_json_fields("not json", check)[0])
        self.assertFalse(grade_json_fields('{"customer": "C", "estimate_gbp": 1, "x": 2}',
                                           dict(check, no_extra=True))[0])

    def test_json_values(self):
        self.assertTrue(grade_json_values('{"a": 1}', {"values": {"a": 1}})[0])
        self.assertFalse(grade_json_values('{"a": 2}', {"values": {"a": 1}})[0])

    def test_citations_present_and_allowed(self):
        out = "Covered [doc:HC-200-s4] and [doc:HC-200-s7]."
        self.assertEqual(extract_citations(out), ["HC-200-s4", "HC-200-s7"])
        self.assertTrue(grade_citations(out, {"min": 2})[0])
        self.assertFalse(grade_citations("Covered.", {"min": 1})[0])
        self.assertFalse(grade_citations(out, {"allowed": ["HC-200-s4"]})[0])


class RunTests(unittest.TestCase):
    def setUp(self):
        self.cases = load_cases(HERE / "eval_set.jsonl")

    def test_sample_set_loads(self):
        self.assertEqual(len(self.cases), 12)

    def test_load_rejects_bad_cases(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps({"id": "x", "input": "hi"}) + "\n")
        self.addCleanup(os.unlink, f.name)
        with self.assertRaises(ValueError):
            load_cases(f.name)

    def test_baseline_pass_rates(self):
        run = run_eval(self.cases, fake_model_v1, "v1", judge=fake_judge)
        self.assertAlmostEqual(run.pass_rate, 11 / 12)
        self.assertEqual(run.by_tag()["classification"], (3, 4, 0.75))

    def test_judge_is_required_for_judge_checks(self):
        run = run_eval(self.cases, fake_model_v1, "v1")              # no judge
        qa4 = next(r for r in run.results if r.id == "qa-04")
        self.assertFalse(qa4.passed)
        self.assertIn("no judge configured", qa4.failures[0])

    def test_system_errors_are_failures_not_crashes(self):
        def broken(_prompt):
            raise TimeoutError("model timed out")
        run = run_eval(self.cases[:2], broken)
        self.assertEqual(run.pass_rate, 0.0)
        self.assertIn("TimeoutError", run.results[0].failures[0])

    def test_regression_detected_by_slice_and_case(self):
        v1 = run_eval(self.cases, fake_model_v1, "v1", judge=fake_judge)
        v2 = run_eval(self.cases, fake_model_v2, "v2", judge=fake_judge)
        cmp = compare_runs(v1, v2)
        self.assertTrue(cmp.has_regression)
        self.assertIn("coverage-qa", cmp.regressed_slices)
        self.assertNotIn("classification", cmp.regressed_slices)      # it improved
        self.assertEqual(cmp.newly_failing, ["qa-01", "qa-03"])
        self.assertEqual(cmp.newly_passing, ["cls-04"])

    def test_threshold_and_protected_tags(self):
        def run(name, outcomes):
            return RunResult(name, [CaseResult(str(i), [tag], "", ok) for i, (tag, ok) in enumerate(outcomes)])
        base = run("a", [("faq", True)] * 50 + [("high-risk", True)] * 50)
        cand = run("b", [("faq", True)] * 48 + [("faq", False)] * 2 +
                   [("high-risk", True)] * 49 + [("high-risk", False)])
        cmp = compare_runs(base, cand, threshold=0.05)
        self.assertNotIn("faq", cmp.regressed_slices)                 # 4% drop: within tolerance
        self.assertIn("high-risk", cmp.regressed_slices)              # any drop counts


if __name__ == "__main__":
    unittest.main()
