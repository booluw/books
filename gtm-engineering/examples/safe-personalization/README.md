# Safe AI personalisation (Chapters 10 and 13)

`personalize.py` validates an LLM's JSON output for one relevance line before it goes into a human-written template:

- valid JSON with `line`, `evidence_url`, `evidence_quote`, `confidence`;
- evidence URL on the company's own domain (or a trusted feed), with lookalike domains rejected;
- every number in the line must appear in the quoted evidence (no invented "$40M raise");
- banned phrases, including surveillance language such as "I noticed you visited our website";
- unfilled placeholders; length limit; confidence threshold;
- the line must be about the recipient.

Failures fall back to segment copy. Tier 1 contacts always need human review, and `in_qa_sample()` picks a deterministic QA sample per batch.

```bash
python3 personalize.py
python3 -m unittest -v
```
