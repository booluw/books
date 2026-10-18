# LLM evaluation harness (Chapters 12 and 13)

## The problem

You have built an AI feature for Contoso Insurance's claims team: it classifies claims, answers coverage questions with citations to policy wording, and extracts structured fields from notes. Next week someone will change the prompt, or the vendor will release a new model. How do you know the change made things better and not worse?

A large language model (**LLM**) is **non-deterministic** in practice: the same input can produce different outputs, and a change that improves one kind of question can quietly break another. Unit tests that check one exact answer are not enough. The answer is an **eval** (evaluation): a fixed set of realistic cases, each with checks, run against the system on every change. An **eval harness** is the code that runs the cases, grades the outputs and reports the results.

For an FDE, the eval set is also a contract with the customer: it turns "it should answer coverage questions well" into "≥ 90% of these 200 agreed cases pass, and every high-risk case passes".

## Terms

- **Eval case:** one input plus the checks its output must pass. Stored one per line in a **JSONL** file (JSON Lines: one JSON object per line), which is easy to diff and append to.
- **System under test:** the thing being evaluated: prompt + model + retrieval + post-processing. Here, any function `str -> str`.
- **Grader:** a function that checks an output and returns pass/fail with a reason.
- **LLM-as-judge:** using a second model, given a **rubric** (written criteria), to grade outputs that keyword checks cannot, such as tone. Judges are themselves imperfect; check them against human grades.
- **Slice:** a subset of cases sharing a tag (`classification`, `high-risk`). Aggregate scores hide slice regressions.
- **Regression:** a change that makes a previously passing behaviour fail.

## What `harness.py` provides

| Piece | What it does |
|---|---|
| `load_cases()` | Reads and validates `eval_set.jsonl` (ids unique; `id`, `input`, `checks` required) |
| `grade_exact` | Exact match after trimming, lower-casing and collapsing whitespace |
| `grade_contains` | Keyword checks: `all` must appear, `any` at least one, `none` must not appear |
| `grade_json_fields` / `grade_json_values` | Output parses as JSON (fences tolerated); required fields have the right types; chosen fields have the right values |
| `grade_citations` | At least `min` citations in the form `[doc:ID]`, and each cited ID is in the `allowed` list |
| judge checks | `{"type": "judge", "rubric": "..."}` calls a pluggable `judge(case, output, rubric)`; with no judge configured the check fails rather than silently passing |
| `run_eval()` | Runs every case; a case passes only if all its checks pass; a system exception fails that case without stopping the run |
| `RunResult.by_tag()` | Pass rate per slice plus `all` |
| `compare_runs()` | Flags slices whose pass rate drops by more than a threshold (default 5 points), and any drop at all in protected slices (default `high-risk`); lists newly failing and newly passing cases |

`fake_model_v1` and `fake_model_v2` are deterministic fakes standing in for two prompt versions, and `fake_judge` stands in for an LLM judge, so everything runs offline.

## The sample result

`eval_set.jsonl` has 12 cases. Version 1 passes 11 (92%); version 2 fixes a classification but drops one citation and cites a policy section that doesn't exist, so it passes 10 (83%):

```
slice                    v1         v2   delta
all                     92%        83%     -8%  <-- REGRESSION
classification          75%       100%    +25%
coverage-qa            100%        50%    -50%  <-- REGRESSION
high-risk              100%        75%    -25%  <-- REGRESSION
```

## Run it

```bash
python3 harness.py
python3 harness.py --fail-on-regression    # exits 1 on regression: use as a CI gate
python3 -m unittest -v
```

## Extending it

- **Real system.** Replace the fake with a function that calls your model with your prompt and retrieval. Record model name, prompt version and temperature with each run.
- **Repeat runs.** Run each case several times and report the pass rate per case, to measure flakiness.
- **Real judge.** Implement `judge()` with a model call that returns a verdict and reasons; validate it against a few dozen human-graded outputs before trusting it.
- **Saved runs.** Write each `RunResult` to JSON so you compare against the last released version, not just two in-memory runs.
- **Cost and latency.** `CaseResult.latency_ms` is recorded; add token counts and cost, and gate on p95 latency too (see `readiness-gate/`).
- **Statistics.** With small slices, a one-case change moves the pass rate a lot. Report counts alongside percentages and grow the eval set where decisions are close.

## Limitations

- Keyword and exact-match graders are brittle: a correct answer phrased differently fails. Use them where wording is constrained, and judges or human review elsewhere.
- The eval set is only as good as its cases. Build it with the customer from real traffic, include the hard and high-risk cases, and add every production failure as a new case.
- Passing an offline eval is necessary, not sufficient: monitor the live system too (Chapter 13).
