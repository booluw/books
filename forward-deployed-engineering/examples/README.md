# Examples

Runnable companions to the chapters. Everything uses **only the Python standard library** (Python 3.11+, tested with 3.13). There is nothing to install, and no API keys are needed: models, judges and human approvers are simulated with deterministic fakes, which you swap for real clients.

Each folder has a README explaining the problem it solves for an FDE, the terms it uses, how to run and extend it, and its limitations. Company names (Contoso, Fabrikam, Northwind Traders, Woodgrove Bank and others) are fictional.

| Folder | Chapter | What it teaches |
|---|---|---|
| [`data-profiler/`](data-profiler/) | 10 | Profiling a customer's CSV extract before building on it: null and placeholder rates, inferred types, min/max, top values, pattern shapes (`AAA-9999`), suspicious values, duplicate keys and ragged rows |
| [`record-linkage/`](record-linkage/) | 10 | Matching customer records across two systems: normalisation, blocking, Jaro-Winkler similarity, weighted field scores, match / review / non-match thresholds, precision and recall against labelled pairs |
| [`llm-eval-harness/`](llm-eval-harness/) | 12, 13 | An offline evaluation harness: JSONL eval set, pluggable system under test, exact / keyword / JSON-field / citation graders, a pluggable judge, pass rates by slice, and regression detection between two runs |
| [`permission-aware-retrieval/`](permission-aware-retrieval/) | 12, 14 | BM25 retrieval with security trimming before ranking, deny-by-default ACLs, context building with `[doc:ID]` labels, and a citation checker |
| [`agent-guardrails/`](agent-guardrails/) | 12, 14 | A guard for agent tool calls: per-role allow-lists, argument validation, read / write / irreversible actions, human approval, per-run budgets, a hash-chained audit log, and prompt-injection tripwires |
| [`impact-calculator/`](impact-calculator/) | 3, 5 | Customer value, payback, ROI and sensitivity; deal gross margin with FDE cost. Reproduces the book's worked examples exactly |
| [`readiness-gate/`](readiness-gate/) | 4, 15 | A production go/no-go gate from a JSON checklist: blockers, majors as dated conditions, minors, evidence links and numeric checks |
| [`feedback-tracker/`](feedback-tracker/) | 16 | Turning field reports into a product priority list: concept normalisation, clustering, per-customer de-duplication, the rule of three, ranking by ARR affected |

## Run every test

From the repository root:

```bash
python3 forward-deployed-engineering/examples/run_all_tests.py
```

Each folder also runs on its own: `python3 -m unittest -v`, and each has a demo: `python3 <module>.py`.

| Folder | Demo |
|---|---|
| `data-profiler/` | `python3 profiler.py sample.csv` |
| `record-linkage/` | `python3 linkage.py` |
| `llm-eval-harness/` | `python3 harness.py` (add `--fail-on-regression` to use as a CI gate) |
| `permission-aware-retrieval/` | `python3 retrieval.py` |
| `agent-guardrails/` | `python3 guardrails.py` |
| `impact-calculator/` | `python3 impact.py` |
| `readiness-gate/` | `python3 gate.py checklist.json` |
| `feedback-tracker/` | `python3 tracker.py` |

## A note on production use

These examples teach logic. Production systems also need persistent storage, secrets management, identity integration, rate limiting, logging, monitoring and the security and data-protection controls from Chapter 14. Treat each as a starting point to adapt with the customer, not a finished component.
