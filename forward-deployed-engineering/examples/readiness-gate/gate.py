"""Production go/no-go gate (Chapters 4 and 15).

Before a deployment goes live, the customer and the FDE team agree a
checklist: security sign-off, access control, monitoring, rollback, evaluation
results and so on. This module turns that checklist (JSON) into a decision
with reasons:

  GO                    - every item satisfied
  GO WITH CONDITIONS    - all blockers satisfied; some major items are not,
                          and each has an owner and a due date
  NO-GO                 - any blocker unsatisfied, or a major item that has no
                          owner or due date (an undated promise is not a condition)

An item is satisfied when its status is "done", it has at least one evidence
link, and its numeric check (if any) passes. Minor items never change the
verdict; they are listed so they are not forgotten.

Usage:
    python3 gate.py checklist.json      # exit code 0 for GO / GO WITH CONDITIONS, 1 for NO-GO
"""
from __future__ import annotations

import json
import operator
import pathlib
import sys
from dataclasses import dataclass, field
from datetime import date

SEVERITIES = ("blocker", "major", "minor")
OPS = {">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt, "==": operator.eq}

GO, GO_WITH_CONDITIONS, NO_GO = "GO", "GO WITH CONDITIONS", "NO-GO"


@dataclass
class Condition:
    item_id: str
    title: str
    owner: str
    due: str
    problems: list[str]


@dataclass
class GateResult:
    verdict: str
    blocking: list[str] = field(default_factory=list)       # reasons for NO-GO
    conditions: list[Condition] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)          # unsatisfied minor items
    passed: list[str] = field(default_factory=list)         # satisfied item ids


def validate_checklist(checklist: dict) -> list[str]:
    """Structural problems that make the checklist itself untrustworthy."""
    errors = []
    ids = [i.get("id") for i in checklist.get("items", [])]
    if not ids:
        errors.append("checklist has no items")
    if len(ids) != len(set(ids)):
        errors.append("duplicate item ids")
    for item in checklist.get("items", []):
        if item.get("severity") not in SEVERITIES:
            errors.append(f"{item.get('id')}: severity must be one of {SEVERITIES}")
        if not item.get("title"):
            errors.append(f"{item.get('id')}: missing title")
        check = item.get("check")
        if check and check.get("op") not in OPS:
            errors.append(f"{item.get('id')}: unknown operator {check.get('op')!r}")
    return errors


def run_check(check: dict, metrics: dict) -> str | None:
    """Evaluate a numeric check such as {"metric": "eval_pass_rate", "op": ">=", "value": 0.9}.
    The threshold may be a literal ("value") or another metric ("metric_target"),
    e.g. p95 latency <= the agreed latency target. Returns a problem or None."""
    name = check["metric"]
    if name not in metrics:
        return f"metric {name!r} not reported"
    if "metric_target" in check:
        if check["metric_target"] not in metrics:
            return f"target {check['metric_target']!r} not reported"
        target = metrics[check["metric_target"]]
    else:
        target = check["value"]
    actual = metrics[name]
    if not OPS[check["op"]](actual, target):
        return f"{name} = {actual} fails {check['op']} {target}"
    return None


def item_problems(item: dict, metrics: dict) -> list[str]:
    """Why an item is not satisfied (empty list = satisfied)."""
    problems = []
    if item.get("status") != "done":
        problems.append(f"status is {item.get('status', 'missing')!r}")
    if not item.get("evidence"):
        problems.append("no evidence link")
    if item.get("check"):
        failure = run_check(item["check"], metrics)
        if failure:
            problems.append(failure)
    return problems


def evaluate(checklist: dict) -> GateResult:
    errors = validate_checklist(checklist)
    if errors:
        return GateResult(NO_GO, blocking=["invalid checklist: " + e for e in errors])

    metrics = checklist.get("metrics", {})
    assessed = date.fromisoformat(checklist["assessed_on"]) if checklist.get("assessed_on") else date.today()
    result = GateResult(GO)
    for item in checklist["items"]:
        problems = item_problems(item, metrics)
        label = f"{item['id']} {item['title']}"
        if not problems:
            result.passed.append(item["id"])
        elif item["severity"] == "blocker":
            result.blocking.append(f"{label}: " + "; ".join(problems))
        elif item["severity"] == "major":
            owner, due = item.get("owner"), item.get("due")
            if not owner or not due:
                result.blocking.append(f"{label}: major item not met and has no "
                                       + ("owner" if not owner else "due date"))
            elif date.fromisoformat(due) < assessed:
                result.blocking.append(f"{label}: condition already overdue (due {due})")
            else:
                result.conditions.append(Condition(item["id"], item["title"], owner, due, problems))
        else:
            result.notes.append(f"{label}: " + "; ".join(problems))

    if result.blocking:
        result.verdict = NO_GO
    elif result.conditions:
        result.verdict = GO_WITH_CONDITIONS
    return result


def format_result(checklist: dict, r: GateResult) -> str:
    lines = [f"{checklist.get('project', 'Deployment')}: {r.verdict}",
             f"assessed {checklist.get('assessed_on')}, go-live {checklist.get('go_live')}",
             f"{len(r.passed)} of {len(checklist.get('items', []))} items satisfied", ""]
    if r.blocking:
        lines.append("Blocking:")
        lines += [f"  x {b}" for b in r.blocking]
    if r.conditions:
        lines.append("Conditions (must be closed by the due date):")
        for c in sorted(r.conditions, key=lambda c: c.due):
            lines.append(f"  - {c.item_id} {c.title}\n      owner: {c.owner}; due {c.due}; now: {'; '.join(c.problems)}")
    if r.notes:
        lines.append("Minor items open:")
        lines += [f"  . {n}" for n in r.notes]
    return "\n".join(lines)


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "checklist.json"
    with open(path, encoding="utf-8") as f:
        checklist = json.load(f)
    result = evaluate(checklist)
    print(format_result(checklist, result))
    return 1 if result.verdict == NO_GO else 0


if __name__ == "__main__":
    sys.exit(main())
