import json
import unittest

from personalize import SEGMENT_LINES, Contact, in_qa_sample, render, validate_ai_output

C = Contact("jane", "Acme Logistics", "acme-logistics.com", "3pl", tier=2)


def ai(**kw):
    base = {"line": "Saw Acme Logistics is hiring 3 dispatch analysts.",
            "evidence_url": "https://acme-logistics.com/careers",
            "evidence_quote": "hiring 3 dispatch analysts", "confidence": "high"}
    base.update(kw)
    return json.dumps(base)


class ValidationTests(unittest.TestCase):
    def test_good_output_passes(self):
        line, problems = validate_ai_output(ai(), C)
        self.assertEqual(problems, [])
        self.assertIn("Acme Logistics", line)

    def test_invalid_json(self):
        self.assertEqual(validate_ai_output("Sure! Here's a line:", C), (None, ["output is not valid JSON"]))

    def test_invented_number_rejected(self):
        _, problems = validate_ai_output(ai(line="Congrats to Acme Logistics on the $40M raise."), C)
        self.assertTrue(any("not supported by evidence" in p for p in problems))

    def test_dollar_amount_is_not_a_placeholder(self):
        _, problems = validate_ai_output(ai(line="Acme Logistics just opened a $40M hub.",
                                            evidence_quote="opened a $40M hub"), C)
        self.assertEqual(problems, [])

    def test_banned_phrase_and_untrusted_evidence(self):
        _, problems = validate_ai_output(ai(line="Acme Logistics is a game-changer.",
                                            evidence_url="https://someblog.com/x"), C)
        self.assertTrue(any("banned phrase" in p for p in problems))
        self.assertIn("missing or untrusted evidence URL", problems)

    def test_subdomain_evidence_allowed(self):
        _, problems = validate_ai_output(ai(evidence_url="https://jobs.acme-logistics.com/123"), C)
        self.assertEqual(problems, [])

    def test_lookalike_domain_rejected(self):
        _, problems = validate_ai_output(ai(evidence_url="https://acme-logistics.com.evil.io/x"), C)
        self.assertIn("missing or untrusted evidence URL", problems)

    def test_placeholder_and_low_confidence(self):
        _, problems = validate_ai_output(ai(line="Hi {{first_name}} at Acme Logistics", confidence="low"), C)
        self.assertIn("unfilled placeholder", problems)
        self.assertTrue(any("confidence" in p for p in problems))

    def test_surveillance_language_is_banned(self):
        _, problems = validate_ai_output(ai(line="I noticed you visited our website, Acme Logistics."), C)
        self.assertTrue(any("banned phrase" in p for p in problems))


class RenderTests(unittest.TestCase):
    def test_fallback_on_failure(self):
        r = render(C, ai(confidence="low"), "VP", "Sam")
        self.assertFalse(r.used_ai_line)
        self.assertIn(SEGMENT_LINES["3pl"], r.body)

    def test_no_ai_output_uses_segment_line(self):
        r = render(C, None, "VP", "Sam")
        self.assertFalse(r.used_ai_line)
        self.assertTrue(r.body.startswith("Hi Jane,"))

    def test_tier_1_always_reviewed(self):
        tier1 = Contact("li", "Acme Logistics", "acme-logistics.com", "3pl", tier=1)
        self.assertTrue(render(tier1, ai(), "VP", "Sam").needs_human_review)
        self.assertFalse(render(C, ai(), "VP", "Sam").needs_human_review)


class SamplingTests(unittest.TestCase):
    def test_deterministic_and_roughly_at_rate(self):
        keys = [f"c{i}@x.com" for i in range(5000)]
        picked = [k for k in keys if in_qa_sample(k, "batch-42", 0.1)]
        self.assertTrue(400 < len(picked) < 600)
        self.assertEqual(picked, [k for k in keys if in_qa_sample(k, "batch-42", 0.1)])


if __name__ == "__main__":
    unittest.main()
