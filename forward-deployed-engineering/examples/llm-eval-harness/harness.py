"""An offline evaluation harness for an LLM feature (Chapters 12 and 13).

An *eval* is a test suite for a system whose output is not fully predictable.
Each eval case has an input and one or more *checks* (graders). We run the
system under test on every case, grade the outputs, aggregate pass rates by
tag ("slice"), and compare two runs so a prompt or model change that makes
things worse is caught before it ships.

Everything here runs offline: the "model" is a deterministic fake that returns
canned answers. Swap `fake_model_v1` for a function that calls your real model.

Usage:
    python3 harness.py                         # compare v1 (baseline) with v2 (candidate)
    python3 harness.py --fail-on-regression    # exit 1 if v2 regresses (use in CI)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time
from dataclasses import dataclass, field
from typing import Callable

HERE = pathlib.Path(__file__).parent

# A system under test takes the case input and returns text.
System = Callable[[str], str]
# A judge takes (case, output, rubric) and returns (passed, reason).
# In production this is usually a second model prompted with the rubric.
Judge = Callable[[dict, str, str], tuple[bool, str]]

CITATION_RE = re.compile(r"\[doc:([A-Za-z0-9_.-]+)\]")


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def load_cases(path: pathlib.Path | str) -> list[dict]:
    """Read a JSONL file: one JSON object per line. Blank lines and lines
    starting with # are ignored. Every case needs an id, an input and checks."""
    cases = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            case = json.loads(line)
            for key in ("id", "input", "checks"):
                if key not in case:
                    raise ValueError(f"line {n}: case missing {key!r}")
            case.setdefault("tags", [])
            cases.append(case)
    ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate case ids")
    return cases


# --------------------------------------------------------------------------
# Graders. Each returns (passed, reason). Reasons explain failures.
# --------------------------------------------------------------------------

def _norm(text: str) -> str:
    return " ".join(text.lower().split()).strip(" .")


def grade_exact(output: str, check: dict) -> tuple[bool, str]:
    """Exact match after trimming, lower-casing and collapsing whitespace."""
    ok = _norm(output) == _norm(check["value"])
    return ok, "" if ok else f"expected {check['value']!r}, got {output.strip()[:60]!r}"


def grade_contains(output: str, check: dict) -> tuple[bool, str]:
    """Keyword checks (case-insensitive):
    all  - every phrase must appear; any - at least one; none - none may appear."""
    text = output.lower()
    missing = [k for k in check.get("all", []) if k.lower() not in text]
    if missing:
        return False, f"missing {missing}"
    anys = check.get("any", [])
    if anys and not any(k.lower() in text for k in anys):
        return False, f"none of {anys}"
    forbidden = [k for k in check.get("none", []) if k.lower() in text]
    if forbidden:
        return False, f"forbidden {forbidden}"
    return True, ""


def parse_json_output(output: str):
    """Models often wrap JSON in ```json fences or add a sentence; take the
    first {...} block."""
    match = re.search(r"\{.*\}", output, re.DOTALL)
    if not match:
        raise ValueError("no JSON object found")
    return json.loads(match.group(0))


TYPE_CHECKS = {
    "str": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "bool": lambda v: isinstance(v, bool),
    "list": lambda v: isinstance(v, list),
    "null": lambda v: v is None,
}


def grade_json_fields(output: str, check: dict) -> tuple[bool, str]:
    """A small JSON-schema-like check: the output parses, every required field
    is present with the right type, and (optionally) no extra fields."""
    try:
        data = parse_json_output(output)
    except ValueError as e:                      # json.JSONDecodeError is a ValueError
        return False, f"invalid JSON: {e}"
    problems = []
    for name, type_name in check["fields"].items():
        if name not in data:
            problems.append(f"missing {name}")
        elif not TYPE_CHECKS[type_name](data[name]):
            problems.append(f"{name} should be {type_name}")
    if check.get("no_extra") and set(data) - set(check["fields"]):
        problems.append(f"extra fields {sorted(set(data) - set(check['fields']))}")
    return not problems, "; ".join(problems)


def grade_json_values(output: str, check: dict) -> tuple[bool, str]:
    """Specific fields must equal specific values."""
    try:
        data = parse_json_output(output)
    except ValueError as e:
        return False, f"invalid JSON: {e}"
    wrong = [f"{k}={data.get(k)!r} (want {v!r})" for k, v in check["values"].items() if data.get(k) != v]
    return not wrong, "; ".join(wrong)


def extract_citations(output: str) -> list[str]:
    return CITATION_RE.findall(output)


def grade_citations(output: str, check: dict) -> tuple[bool, str]:
    """At least `min` citations like [doc:ID]; if `allowed` is given, every
    citation must be in it (citing a document that doesn't support the answer
    is worse than citing nothing)."""
    cited = extract_citations(output)
    if len(cited) < check.get("min", 1):
        return False, f"{len(cited)} citation(s), need {check.get('min', 1)}"
    allowed = check.get("allowed")
    if allowed is not None:
        bad = [c for c in cited if c not in allowed]
        if bad:
            return False, f"cites {bad} not in {allowed}"
    return True, ""


GRADERS: dict[str, Callable[[str, dict], tuple[bool, str]]] = {
    "exact": grade_exact,
    "contains": grade_contains,
    "json_fields": grade_json_fields,
    "json_values": grade_json_values,
    "citations": grade_citations,
}


# --------------------------------------------------------------------------
# Running
# --------------------------------------------------------------------------

@dataclass
class CaseResult:
    id: str
    tags: list[str]
    output: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    latency_ms: float = 0.0


@dataclass
class RunResult:
    name: str
    results: list[CaseResult]

    @property
    def pass_rate(self) -> float:
        return sum(r.passed for r in self.results) / len(self.results) if self.results else 0.0

    def by_tag(self) -> dict[str, tuple[int, int, float]]:
        """tag -> (passed, total, pass rate). Every run also has an 'all' slice."""
        slices: dict[str, list[bool]] = {"all": [r.passed for r in self.results]}
        for r in self.results:
            for t in r.tags:
                slices.setdefault(t, []).append(r.passed)
        return {t: (sum(v), len(v), sum(v) / len(v)) for t, v in sorted(slices.items())}


def run_eval(cases: list[dict], system: System, name: str = "run",
             judge: Judge | None = None) -> RunResult:
    """Run every case through the system and grade it. A case passes only if
    all its checks pass. An exception from the system is a failure, not a crash:
    one bad case should not stop the run."""
    results = []
    for case in cases:
        start = time.perf_counter()
        try:
            output = system(case["input"])
        except Exception as e:                          # noqa: BLE001 - record and continue
            output, error = "", f"system error: {e!r}"
        else:
            error = None
        latency = (time.perf_counter() - start) * 1000
        failures = [error] if error else []
        if not error:
            for check in case["checks"]:
                if check["type"] == "judge":
                    if judge is None:
                        ok, why = False, "no judge configured"
                    else:
                        ok, why = judge(case, output, check["rubric"])
                else:
                    ok, why = GRADERS[check["type"]](output, check)
                if not ok:
                    failures.append(f"{check['type']}: {why}")
        results.append(CaseResult(case["id"], case["tags"], output, not failures, failures, latency))
    return RunResult(name, results)


# --------------------------------------------------------------------------
# Comparing runs
# --------------------------------------------------------------------------

@dataclass
class Comparison:
    slice_deltas: dict[str, tuple[float, float, float]]   # tag -> (baseline, candidate, delta)
    regressed_slices: list[str]
    newly_failing: list[str]                              # case ids: pass -> fail
    newly_passing: list[str]                              # case ids: fail -> pass

    @property
    def has_regression(self) -> bool:
        return bool(self.regressed_slices)


def compare_runs(baseline: RunResult, candidate: RunResult, threshold: float = 0.05,
                 protected_tags: tuple[str, ...] = ("high-risk",)) -> Comparison:
    """Flag a slice as regressed when its pass rate drops by more than
    `threshold`. For protected tags (such as high-risk cases) any drop at all
    counts: an aggregate improvement must not hide a worse answer on a
    question that matters."""
    base, cand = baseline.by_tag(), candidate.by_tag()
    deltas, regressed = {}, []
    for tag in sorted(set(base) | set(cand)):
        b = base.get(tag, (0, 0, 0.0))[2]
        c = cand.get(tag, (0, 0, 0.0))[2]
        deltas[tag] = (b, c, c - b)
        limit = 0.0 if tag in protected_tags else threshold
        if b - c > limit + 1e-9:
            regressed.append(tag)
    before = {r.id: r.passed for r in baseline.results}
    after = {r.id: r.passed for r in candidate.results}
    newly_failing = sorted(i for i in after if before.get(i) and not after[i])
    newly_passing = sorted(i for i in after if before.get(i) is False and after[i])
    return Comparison(deltas, regressed, newly_failing, newly_passing)


def format_report(baseline: RunResult, candidate: RunResult, cmp: Comparison) -> str:
    lines = [f"{'slice':16} {baseline.name:>10} {candidate.name:>10} {'delta':>7}"]
    for tag, (b, c, d) in cmp.slice_deltas.items():
        flag = "  <-- REGRESSION" if tag in cmp.regressed_slices else ""
        lines.append(f"{tag:16} {b:>10.0%} {c:>10.0%} {d:>+7.0%}{flag}")
    lines.append("")
    lines.append("Newly failing: " + (", ".join(cmp.newly_failing) or "none"))
    lines.append("Newly passing: " + (", ".join(cmp.newly_passing) or "none"))
    for r in candidate.results:
        if not r.passed:
            lines.append(f"  {r.id}: " + " | ".join(r.failures))
    lines.append("")
    lines.append("RESULT: " + ("REGRESSION - do not ship" if cmp.has_regression else "no regression"))
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Deterministic fakes, so the harness runs with no API key
# --------------------------------------------------------------------------

_V1 = {
    "cls-01": "escape_of_water",
    "cls-02": "theft",
    "cls-03": "storm",
    "cls-04": "accidental_damage",                                     # wrong: it's fire
    "qa-01": "Yes. Accidental damage to laptops is covered, subject to a £100 excess [doc:HC-200-s4].",
    "qa-02": "No. Damage from a gradual leak is not covered [doc:HC-200-s9].",
    "qa-03": "The buildings cover limit is £500,000 [doc:HC-200-s2].",
    "qa-04": "I'm sorry your claim was declined. Fences are excluded from storm cover [doc:HC-200-s6]. "
             "If you disagree, you can use our complaints process.",
    "ext-01": '{"customer": "Northwind Traders", "policy_number": "HC-200-118", '
              '"reported_on": "2026-03-02", "estimate_gbp": 1250}',
    "ext-02": '```json\n{"customer": "Fabrikam Ltd", "policy_number": "HC-200-342", '
              '"reported_on": "2026-03-04", "estimate_gbp": null}\n```',
    "safe-01": "Sorry, I can't help with that.",
    "safe-02": "I can only help with claims and policy questions.",
}

# v2 is a "new prompt": it fixes cls-04 but drops a citation and invents a section.
_V2 = dict(_V1)
_V2["cls-04"] = "fire"
_V2["qa-01"] = "Yes. Accidental damage to laptops is covered, subject to a £100 excess [doc:HC-200-s12]."
_V2["qa-03"] = "The buildings cover limit is £500,000."


def _fake(table: dict[str, str]) -> System:
    cases = {c["input"]: c["id"] for c in load_cases(HERE / "eval_set.jsonl")}

    def model(prompt: str) -> str:
        return table.get(cases.get(prompt, ""), "I don't know.")
    return model


fake_model_v1 = _fake(_V1)
fake_model_v2 = _fake(_V2)


def fake_judge(case: dict, output: str, rubric: str) -> tuple[bool, str]:
    """Stands in for an LLM judge. A real judge prompt would include the rubric
    and ask for a verdict with reasons; here we check for the rubric's ideas."""
    text = output.lower()
    needed = {"polite": ("sorry" in text or "apolog" in text),
              "fences excluded": "fence" in text and "exclud" in text,
              "complaints route": "complaint" in text}
    missing = [k for k, ok in needed.items() if not ok]
    return not missing, f"judge: missing {missing}" if missing else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the offline eval and compare two systems.")
    parser.add_argument("--threshold", type=float, default=0.05)
    parser.add_argument("--fail-on-regression", action="store_true")
    args = parser.parse_args()
    cases = load_cases(HERE / "eval_set.jsonl")
    v1 = run_eval(cases, fake_model_v1, "v1", judge=fake_judge)
    v2 = run_eval(cases, fake_model_v2, "v2", judge=fake_judge)
    cmp = compare_runs(v1, v2, threshold=args.threshold)
    print(f"{len(cases)} cases\n")
    print(format_report(v1, v2, cmp))
    return 1 if (args.fail_on_regression and cmp.has_regression) else 0


if __name__ == "__main__":
    sys.exit(main())
