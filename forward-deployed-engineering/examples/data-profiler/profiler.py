"""Profile a CSV file before you build on it (Chapter 10).

The first thing an FDE does with a customer extract is *look at it properly*:
how many values are missing, what type each column really holds, what shapes
the identifiers take, which values are placeholders pretending to be data, and
whether the "unique" key is actually unique. This module answers those
questions for any CSV, using only the standard library.

Usage:
    python3 profiler.py sample.csv                 # key column = first column
    python3 profiler.py sample.csv --key claim_id
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime

# Values people type when they have no real value. They are not empty, so a
# naive null check misses them, and they quietly poison counts and joins.
PLACEHOLDERS = {
    "n/a", "na", "null", "none", "nil", "unknown", "unk", "-", "--", "?", ".",
    "tbc", "tbd", "test", "xxx", "missing", "not known", "0000-00-00",
    "1900-01-01", "9999-12-31", "01/01/1900", "31/12/9999", "999999", "000000",
}

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")  # ISO first; then UK day/month/year
BOOLEAN_VALUES = {"true", "false", "yes", "no", "y", "n"}
# Numbers like 99999999 or 0000 are often "magic" values meaning "not set".
SENTINEL_RE = re.compile(r"^(9{4,}|0{4,})(\.0+)?$")
INTEGER_RE = re.compile(r"^[+-]?\d+$")
DECIMAL_RE = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)$")


# --------------------------------------------------------------------------
# Value-level helpers
# --------------------------------------------------------------------------

def is_null(value: str | None) -> bool:
    """Truly empty: missing, empty string or only whitespace."""
    return value is None or value.strip() == ""


def is_placeholder(value: str) -> bool:
    """A non-empty value that stands in for 'we don't know'."""
    return value.strip().lower() in PLACEHOLDERS


def shape(value: str, collapse: bool = False) -> str:
    """Reduce a value to its pattern: upper-case letter -> A, lower-case -> a,
    digit -> 9, everything else kept. 'CLM-0042' -> 'AAA-9999'.

    With collapse=True, runs of the same class shrink to one character
    ('AAA-9999' -> 'A-9'), which groups identifiers of different lengths.
    """
    out = []
    for ch in value:
        if ch.isdigit():
            out.append("9")
        elif ch.isalpha():
            out.append("A" if ch.isupper() else "a")
        else:
            out.append(ch)
    s = "".join(out)
    if collapse:
        s = re.sub(r"(.)\1+", r"\1", s)
    return s


def parse_date(value: str) -> date | None:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def value_type(value: str) -> str:
    """Classify a single (non-null, non-placeholder) value."""
    v = value.strip()
    if INTEGER_RE.match(v):
        return "integer"
    if DECIMAL_RE.match(v):
        return "decimal"
    if parse_date(v):
        return "date"
    if v.lower() in BOOLEAN_VALUES:
        return "boolean"
    return "text"


def _sort_key(value: str, kind: str):
    """Turn a value into something comparable for min/max, by column type."""
    v = value.strip()
    if kind in ("integer", "decimal"):
        return float(v)
    if kind == "date":
        return parse_date(v)
    return v


# --------------------------------------------------------------------------
# Column and table profiles
# --------------------------------------------------------------------------

@dataclass
class ColumnProfile:
    name: str
    count: int                                  # rows in the file
    null_count: int                             # empty / whitespace
    placeholder_count: int                      # "N/A", "unknown", ...
    distinct_count: int                         # distinct real values
    inferred_type: str                          # dominant type of real values
    type_share: float                           # share of real values of that type
    min: str | None
    max: str | None
    top_values: list[tuple[str, int]]
    shapes: list[tuple[str, int]]
    suspicious: list[tuple[str, str, int]] = field(default_factory=list)  # (value, reason, count)

    @property
    def null_rate(self) -> float:
        return self.null_count / self.count if self.count else 0.0

    @property
    def missing_rate(self) -> float:
        """Nulls plus placeholders: the share of rows with no usable value."""
        return (self.null_count + self.placeholder_count) / self.count if self.count else 0.0


@dataclass
class TableProfile:
    row_count: int
    columns: list[ColumnProfile]
    key: str | None
    duplicate_keys: dict[str, int]              # key value -> number of rows
    ragged_rows: list[int] = field(default_factory=list)  # file line numbers

    def column(self, name: str) -> ColumnProfile:
        return next(c for c in self.columns if c.name == name)


def profile_column(name: str, values: list[str | None], top_n: int = 5,
                   type_threshold: float = 0.9) -> ColumnProfile:
    """Profile one column. `type_threshold` is the share of real values that
    must agree before we call a column (say) 'date' rather than 'text'."""
    nulls = sum(1 for v in values if is_null(v))
    present = [v for v in values if not is_null(v)]
    placeholders = [v for v in present if is_placeholder(v)]
    real = [v for v in present if not is_placeholder(v)]

    # Type inference: the most common value type, if it is dominant enough.
    # Integers also count as decimals, so a column of 12, 15.5, 20 is decimal.
    types = Counter(value_type(v) for v in real)
    if types.get("decimal") and types.get("integer"):
        types["decimal"] += types.pop("integer")
    kind, kind_count = types.most_common(1)[0] if types else ("empty", 0)
    share = kind_count / len(real) if real else 0.0
    if share < type_threshold:
        kind_used_for_minmax = "text"
    else:
        kind_used_for_minmax = kind

    # Suspicious values: placeholders, padding, and values that don't fit the type.
    suspicious: Counter = Counter()
    for v in placeholders:
        suspicious[(v, "placeholder")] += 1
    for v in real:
        if SENTINEL_RE.match(v.strip()):
            suspicious[(v, "sentinel number")] += 1
    for v in present:
        if v != v.strip():
            suspicious[(v, "leading/trailing whitespace")] += 1
    if kind != "text" and share >= 0.5:
        for v in real:
            t = value_type(v)
            fits = t == kind or (kind == "decimal" and t == "integer")
            if not fits:
                suspicious[(v, f"not a {kind}")] += 1

    # Min / max over values that match the column type.
    comparable = [v for v in real
                  if kind_used_for_minmax == "text"
                  or value_type(v) == kind_used_for_minmax
                  or (kind_used_for_minmax == "decimal" and value_type(v) == "integer")]
    lo = hi = None
    if comparable:
        lo = min(comparable, key=lambda v: _sort_key(v, kind_used_for_minmax)).strip()
        hi = max(comparable, key=lambda v: _sort_key(v, kind_used_for_minmax)).strip()

    return ColumnProfile(
        name=name,
        count=len(values),
        null_count=nulls,
        placeholder_count=len(placeholders),
        distinct_count=len({v.strip() for v in real}),
        inferred_type=kind if share >= type_threshold else f"mixed ({kind} {share:.0%})",
        type_share=round(share, 3),
        min=lo,
        max=hi,
        top_values=Counter(v.strip() for v in present).most_common(top_n),
        shapes=Counter(shape(v.strip()) for v in real).most_common(top_n),
        suspicious=[(v, reason, n) for (v, reason), n in suspicious.most_common()],
    )


def find_duplicate_keys(rows: list[dict], key: str) -> dict[str, int]:
    """Key values that appear on more than one row. Keys are compared after
    trimming and upper-casing, because 'clm-1' and 'CLM-1 ' are usually the
    same record entered twice."""
    counts = Counter((r.get(key) or "").strip().upper() for r in rows
                     if not is_null(r.get(key)))
    return {k: n for k, n in counts.items() if n > 1}


def profile_rows(headers: list[str], rows: list[dict], key: str | None = None) -> TableProfile:
    columns = [profile_column(h, [r.get(h) for r in rows]) for h in headers]
    dupes = find_duplicate_keys(rows, key) if key else {}
    return TableProfile(row_count=len(rows), columns=columns, key=key,
                        duplicate_keys=dupes, ragged_rows=find_ragged_rows(rows))


def find_ragged_rows(rows: list[dict]) -> list[int]:
    """Rows with too many or too few fields, as file line numbers (header = 1).

    csv.DictReader puts surplus fields under the key None and fills missing
    ones with None. The usual cause is an unquoted comma inside a value, such
    as an amount written '1,200.00', which shifts every later column along.
    """
    return [i + 2 for i, r in enumerate(rows)
            if None in r or any(v is None for v in r.values())]


def read_csv(path: str) -> tuple[list[str], list[dict]]:
    # utf-8-sig strips the byte-order mark Excel adds to "CSV UTF-8" exports.
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def profile_csv(path: str, key: str | None = None) -> TableProfile:
    headers, rows = read_csv(path)
    return profile_rows(headers, rows, key or (headers[0] if headers else None))


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def format_report(p: TableProfile) -> str:
    lines = [f"Rows: {p.row_count}   Columns: {len(p.columns)}   Key: {p.key}", ""]
    for c in p.columns:
        lines.append(f"== {c.name}")
        lines.append(f"   type: {c.inferred_type}   null rate: {c.null_rate:.0%}   "
                     f"missing incl. placeholders: {c.missing_rate:.0%}   distinct: {c.distinct_count}")
        lines.append(f"   min: {c.min}   max: {c.max}")
        lines.append("   top values: " + ", ".join(f"{v!r}×{n}" for v, n in c.top_values))
        lines.append("   shapes: " + ", ".join(f"{s}×{n}" for s, n in c.shapes))
        for v, reason, n in c.suspicious:
            lines.append(f"   ! {reason}: {v!r} ×{n}")
        lines.append("")
    if p.ragged_rows:
        lines.append("Rows with the wrong number of fields (line numbers): " +
                     ", ".join(map(str, p.ragged_rows)))
    if p.duplicate_keys:
        lines.append(f"Duplicate keys in {p.key!r}: " +
                     ", ".join(f"{k}×{n}" for k, n in sorted(p.duplicate_keys.items())))
    elif p.key:
        lines.append(f"No duplicate keys in {p.key!r}.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile a CSV file.")
    parser.add_argument("path")
    parser.add_argument("--key", help="column expected to be unique (default: first column)")
    args = parser.parse_args()
    print(format_report(profile_csv(args.path, args.key)))


if __name__ == "__main__":
    main()
