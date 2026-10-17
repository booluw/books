"""Match customer records across two systems (Chapter 10).

The same customer lives in the CRM as 'Fabrikam, Inc.' and in billing as
'FABRIKAM INC', with a postcode typed with or without a space and a phone
number with or without +44. Record linkage finds those pairs:

  1. normalise   - make equal things look equal (case, punctuation, suffixes)
  2. block       - only compare records that share a cheap key, so we do not
                   compare every record with every other (n x m comparisons)
  3. score       - compare fields with string similarity and weight them
  4. classify    - match / review / non-match by two thresholds
  5. evaluate    - precision and recall against pairs a human has labelled

Usage:
    python3 linkage.py          # links crm.csv to billing.csv, scores against labels.csv
"""
from __future__ import annotations

import csv
import pathlib
import re
import unicodedata
from dataclasses import dataclass, field
from itertools import product

# Legal-form words that differ between systems but don't distinguish companies.
COMPANY_SUFFIXES = {
    "ltd", "limited", "inc", "incorporated", "plc", "llc", "llp", "corp",
    "corporation", "co", "company", "gmbh", "sa", "ag", "bv", "group", "the",
}

# Field weights: how much each field's agreement counts towards the score.
# Names carry most weight; email and phone are strong but often missing.
DEFAULT_WEIGHTS = {"name": 0.45, "postcode": 0.2, "email": 0.2, "phone": 0.15}
MATCH_THRESHOLD = 0.88      # at or above: link automatically
REVIEW_THRESHOLD = 0.70     # between the two: a person decides


# --------------------------------------------------------------------------
# 1. Normalisation
# --------------------------------------------------------------------------

def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def normalise_name(name: str) -> str:
    """'Fabrikam, Inc.' -> 'fabrikam'; 'Northwind Traders Limited' -> 'northwind traders'."""
    s = strip_accents(name or "").lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)                 # punctuation -> space
    tokens = [t for t in s.split() if t not in COMPANY_SUFFIXES]
    return " ".join(tokens)


def normalise_postcode(postcode: str) -> str:
    return re.sub(r"\s+", "", (postcode or "").upper())


def normalise_email(email: str) -> str:
    return (email or "").strip().lower()


def normalise_phone(phone: str) -> str:
    """Digits only, with the UK +44 country code turned into a leading 0."""
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("44"):
        digits = "0" + digits[2:]
    return digits


@dataclass
class Record:
    id: str
    name: str
    postcode: str = ""
    email: str = ""
    phone: str = ""
    # Normalised copies, filled in by __post_init__.
    n_name: str = field(init=False)
    n_postcode: str = field(init=False)
    n_email: str = field(init=False)
    n_phone: str = field(init=False)

    def __post_init__(self):
        self.n_name = normalise_name(self.name)
        self.n_postcode = normalise_postcode(self.postcode)
        self.n_email = normalise_email(self.email)
        self.n_phone = normalise_phone(self.phone)


# --------------------------------------------------------------------------
# 2. Blocking
# --------------------------------------------------------------------------

def block_keys(r: Record) -> set[str]:
    """Cheap keys; two records are compared only if they share one.

    - postcode district: UK postcodes end with a 3-character inward code, so
      'SW1A1AA' -> 'SW1A'. Same district = plausibly the same site.
    - first four letters of the normalised name, which survives most typos
      later in the name.
    Blocking trades a little recall for a lot of speed: a pair with a typo in
    the first letters *and* a different postcode will never be compared.
    """
    keys = set()
    if len(r.n_postcode) > 3:
        keys.add("pc:" + r.n_postcode[:-3])
    if r.n_name:
        keys.add("nm:" + r.n_name.replace(" ", "")[:4])
    return keys


def candidate_pairs(left: list[Record], right: list[Record]) -> list[tuple[Record, Record]]:
    index: dict[str, list[Record]] = {}
    for r in right:
        for k in block_keys(r):
            index.setdefault(k, []).append(r)
    pairs, seen = [], set()
    for l in left:
        for k in block_keys(l):
            for r in index.get(k, []):
                if (l.id, r.id) not in seen:
                    seen.add((l.id, r.id))
                    pairs.append((l, r))
    return pairs


# --------------------------------------------------------------------------
# 3. Similarity and scoring
# --------------------------------------------------------------------------

def jaro(s1: str, s2: str) -> float:
    """Jaro similarity: 1.0 for identical strings, 0.0 for nothing in common.

    Counts characters that match within a window, then penalises those that
    appear in a different order (transpositions).
    """
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    window = max(max(len(s1), len(s2)) // 2 - 1, 0)
    used1, used2 = [False] * len(s1), [False] * len(s2)
    matches = 0
    for i, c in enumerate(s1):
        for j in range(max(0, i - window), min(i + window + 1, len(s2))):
            if not used2[j] and s2[j] == c:
                used1[i] = used2[j] = True
                matches += 1
                break
    if matches == 0:
        return 0.0
    # Count transpositions: matched characters that are out of order.
    a = [c for c, u in zip(s1, used1) if u]
    b = [c for c, u in zip(s2, used2) if u]
    transpositions = sum(x != y for x, y in zip(a, b)) / 2
    return (matches / len(s1) + matches / len(s2) + (matches - transpositions) / matches) / 3


def jaro_winkler(s1: str, s2: str, prefix_scale: float = 0.1) -> float:
    """Jaro, boosted when the strings share a prefix (up to 4 characters).
    Suits names, where typos tend to come later in the word."""
    j = jaro(s1, s2)
    prefix = 0
    for x, y in zip(s1[:4], s2[:4]):
        if x != y:
            break
        prefix += 1
    return j + prefix * prefix_scale * (1 - j)


def field_similarities(a: Record, b: Record) -> dict[str, float | None]:
    """Per-field similarity in [0, 1], or None when either side is missing."""
    def exact(x: str, y: str) -> float | None:
        return None if not x or not y else float(x == y)

    return {
        "name": jaro_winkler(a.n_name, b.n_name) if a.n_name and b.n_name else None,
        "postcode": exact(a.n_postcode, b.n_postcode),
        "email": exact(a.n_email, b.n_email),
        "phone": exact(a.n_phone, b.n_phone),
    }


def score_pair(a: Record, b: Record, weights: dict[str, float] = DEFAULT_WEIGHTS) -> tuple[float, dict]:
    """Weighted average of the fields both records have.

    A missing field neither helps nor hurts: its weight is dropped and the rest
    renormalised. Otherwise every record with no phone number would look like
    a weaker match than it is.
    """
    sims = field_similarities(a, b)
    present = {f: s for f, s in sims.items() if s is not None}
    total_weight = sum(weights[f] for f in present)
    if total_weight == 0:
        return 0.0, sims
    score = sum(weights[f] * s for f, s in present.items()) / total_weight
    return round(score, 4), sims


# --------------------------------------------------------------------------
# 4. Classification and linking
# --------------------------------------------------------------------------

@dataclass
class Candidate:
    left_id: str
    right_id: str
    score: float
    decision: str                   # "match" | "review" | "non-match"
    fields: dict


def classify(score: float, match: float = MATCH_THRESHOLD, review: float = REVIEW_THRESHOLD) -> str:
    if score >= match:
        return "match"
    if score >= review:
        return "review"
    return "non-match"


def link(left: list[Record], right: list[Record], match: float = MATCH_THRESHOLD,
         review: float = REVIEW_THRESHOLD, one_to_one: bool = True) -> list[Candidate]:
    """Score blocked pairs and classify them. Returns match and review candidates,
    best first.

    With one_to_one=True each record is used in at most one pair (greedy, best
    score first), which suits two systems that each hold one row per customer.
    """
    scored = []
    for a, b in candidate_pairs(left, right):
        s, sims = score_pair(a, b)
        decision = classify(s, match, review)
        if decision != "non-match":
            scored.append(Candidate(a.id, b.id, s, decision, sims))
    scored.sort(key=lambda c: (-c.score, c.left_id, c.right_id))
    if not one_to_one:
        return scored
    used_left, used_right, kept = set(), set(), []
    for c in scored:
        if c.left_id not in used_left and c.right_id not in used_right:
            kept.append(c)
            used_left.add(c.left_id)
            used_right.add(c.right_id)
    return kept


# --------------------------------------------------------------------------
# 5. Evaluation
# --------------------------------------------------------------------------

@dataclass
class Evaluation:
    true_positives: int
    false_positives: int
    false_negatives: int

    @property
    def precision(self) -> float:
        """Of the pairs we linked, the share that are right."""
        predicted = self.true_positives + self.false_positives
        return self.true_positives / predicted if predicted else 0.0

    @property
    def recall(self) -> float:
        """Of the true pairs, the share we found."""
        actual = self.true_positives + self.false_negatives
        return self.true_positives / actual if actual else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if p + r else 0.0


def evaluate(candidates: list[Candidate], true_pairs: set[tuple[str, str]],
             include_review: bool = False) -> Evaluation:
    """Compare predicted pairs with labelled true pairs.

    include_review=False measures what is linked automatically.
    include_review=True assumes reviewers accept every review-band pair, which
    shows the recall available if people do the review.
    """
    wanted = {"match", "review"} if include_review else {"match"}
    predicted = {(c.left_id, c.right_id) for c in candidates if c.decision in wanted}
    tp = len(predicted & true_pairs)
    return Evaluation(tp, len(predicted - true_pairs), len(true_pairs - predicted))


# --------------------------------------------------------------------------
# Files and CLI
# --------------------------------------------------------------------------

HERE = pathlib.Path(__file__).parent


def load_records(path: pathlib.Path) -> list[Record]:
    with open(path, newline="", encoding="utf-8") as f:
        return [Record(r["id"], r["name"], r["postcode"], r["email"], r["phone"]) for r in csv.DictReader(f)]


def load_labels(path: pathlib.Path) -> set[tuple[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return {(r["crm_id"], r["billing_id"]) for r in csv.DictReader(f)}


def main() -> None:
    crm, billing = load_records(HERE / "crm.csv"), load_records(HERE / "billing.csv")
    labels = load_labels(HERE / "labels.csv")
    pairs = candidate_pairs(crm, billing)
    print(f"{len(crm)} CRM x {len(billing)} billing = {len(crm) * len(billing)} possible pairs; "
          f"blocking leaves {len(pairs)} to score.\n")
    names = {r.id: r.name for r in crm + billing}
    candidates = link(crm, billing)
    for c in candidates:
        mark = "ok " if (c.left_id, c.right_id) in labels else "BAD"
        print(f"{mark} {c.decision:7} {c.score:.3f}  {names[c.left_id]!r:32} <-> {names[c.right_id]!r}")
    for label, inc in (("automatic matches", False), ("matches + review", True)):
        e = evaluate(candidates, labels, include_review=inc)
        print(f"\n{label}: precision {e.precision:.2f}, recall {e.recall:.2f}, F1 {e.f1:.2f}")


if __name__ == "__main__":
    main()
