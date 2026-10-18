"""Permission-aware retrieval with citations (Chapters 12 and 14).

Retrieval-augmented generation (RAG) finds documents relevant to a question
and gives them to a model as context. Inside an organisation, documents have
access controls: the restructuring plan is for HR leadership only. If retrieval
ignores them, the assistant becomes a way to read anything.

This module:
  1. ranks documents with BM25, a classic keyword-relevance formula;
  2. applies *security trimming*: only documents the user may read are ever
     scored, so a restricted document cannot appear in results, context or
     citations, and cannot even influence the ranking statistics;
  3. builds a context block where each document is labelled [doc:ID];
  4. checks an answer's citations: every cited ID must be one that was
     retrieved for, and permitted to, this user.

Usage:
    python3 retrieval.py
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from",
    "how", "i", "in", "is", "it", "my", "of", "on", "or", "our", "the", "to", "we", "what",
    "when", "which", "who", "will", "with", "you",
}
CITATION_RE = re.compile(r"\[doc:([A-Za-z0-9_.-]+)\]")


def tokenise(text: str) -> list[str]:
    """Lower-case words and numbers, minus very common words. A crude plural
    strip lets 'claims' match 'claim'."""
    tokens = []
    for t in re.findall(r"[a-z0-9]+", text.lower()):
        if t in STOPWORDS:
            continue
        if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        tokens.append(t)
    return tokens


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    allowed_groups: frozenset[str]      # empty = nobody (deny by default)


@dataclass(frozen=True)
class User:
    id: str
    groups: frozenset[str]


def can_read(user: User, doc: Document) -> bool:
    """Access control list (ACL) check: the user must share a group with the
    document. A document with no groups is readable by nobody, so a missing
    ACL fails closed rather than open."""
    return bool(user.groups & doc.allowed_groups)


@dataclass
class Hit:
    doc: Document
    score: float


class BM25Index:
    """BM25 ('best match 25') scores a document for a query by summing, over
    query terms:

        idf(term) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_len / avg_len))

    - tf: how often the term appears in the document (with diminishing returns,
      controlled by k1);
    - idf: inverse document frequency, so rare terms count more than common ones;
    - b: how much to penalise long documents.
    """

    def __init__(self, docs: list[Document], k1: float = 1.5, b: float = 0.75):
        self.docs = {d.id: d for d in docs}
        self.k1, self.b = k1, b
        # Title words are added to the body so a title match counts.
        self.terms = {d.id: Counter(tokenise(d.title + " " + d.text)) for d in docs}
        self.lengths = {i: sum(c.values()) for i, c in self.terms.items()}

    def search(self, query: str, user: User, k: int = 3) -> list[Hit]:
        # Security trimming happens FIRST. Corpus statistics (document
        # frequency, average length) are computed over the permitted set only:
        # if they included restricted documents, a user could infer that a
        # hidden document mentions 'redundancy' from how results shift.
        permitted = [i for i, d in self.docs.items() if can_read(user, d)]
        if not permitted:
            return []
        n = len(permitted)
        avg_len = sum(self.lengths[i] for i in permitted) / n
        q_terms = tokenise(query)
        df = {t: sum(1 for i in permitted if t in self.terms[i]) for t in set(q_terms)}

        hits = []
        for i in permitted:
            score = 0.0
            for t in q_terms:
                tf = self.terms[i].get(t, 0)
                if not tf:
                    continue
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                norm = tf + self.k1 * (1 - self.b + self.b * self.lengths[i] / avg_len)
                score += idf * tf * (self.k1 + 1) / norm
            if score > 0:
                hits.append(Hit(self.docs[i], round(score, 4)))
        hits.sort(key=lambda h: (-h.score, h.doc.id))
        return hits[:k]


@dataclass
class Context:
    text: str
    doc_ids: list[str]                  # what the model was shown, in order


def build_context(hits: list[Hit], max_chars: int = 2000) -> Context:
    """Label each document so the model can cite it as [doc:ID]. Stop adding
    documents when the character budget is used (a stand-in for a token budget)."""
    parts, ids, used = [], [], 0
    for h in hits:
        block = f"[doc:{h.doc.id}] {h.doc.title}\n{h.doc.text}\n"
        if used + len(block) > max_chars and parts:
            break
        parts.append(block)
        ids.append(h.doc.id)
        used += len(block)
    return Context("\n".join(parts), ids)


@dataclass
class CitationCheck:
    cited: list[str]
    unknown: list[str] = field(default_factory=list)     # cited but not in the context

    @property
    def ok(self) -> bool:
        return bool(self.cited) and not self.unknown


def check_citations(answer: str, context: Context) -> CitationCheck:
    """Every cited ID must be one the user was shown. A citation outside the
    context is either invented by the model or, worse, a document the user may
    not read; both are blocked. An answer with no citations also fails."""
    cited = list(dict.fromkeys(CITATION_RE.findall(answer)))   # unique, in order
    allowed = set(context.doc_ids)
    return CitationCheck(cited, [c for c in cited if c not in allowed])


# --------------------------------------------------------------------------
# Sample corpus: Woodgrove Bank's internal documents (fictional)
# --------------------------------------------------------------------------

CORPUS = [
    Document("POL-EXP", "Expenses policy",
             "Staff may claim travel, meals and accommodation expenses within 30 days. "
             "Receipts are required for any claim above £25. Managers approve claims.",
             frozenset({"all-staff"})),
    Document("POL-TRV", "Travel policy",
             "Book rail travel in standard class. Flights within the UK need director approval. "
             "Hotel limits are £150 per night in London and £110 elsewhere.",
             frozenset({"all-staff"})),
    Document("HR-RESTRUCT", "Leeds office restructuring plan",
             "Confidential. Proposed redundancy of 40 roles in the Leeds office in Q1. "
             "Consultation starts after the board meeting. Do not share.",
             frozenset({"hr-leadership"})),
    Document("HR-PAY", "Salary bands 2026",
             "Salary bands for 2026 by grade, including the Leeds office location allowance.",
             frozenset({"hr", "hr-leadership"})),
    Document("OPS-LEEDS", "Leeds office guide",
             "The Leeds office is open 8am to 6pm. Visitors sign in at reception. "
             "Desk booking uses the workplace app.",
             frozenset({"all-staff"})),
    Document("SEC-INC-42", "Incident report 42",
             "Phishing campaign targeting the payments team. Credentials for two accounts were reset.",
             frozenset({"security"})),
    Document("DRAFT-NOACL", "Untitled draft",
             "Leeds office redundancy notes, draft.",
             frozenset()),                                      # no ACL: nobody can read it
]

USERS = {
    "analyst": User("analyst", frozenset({"all-staff"})),
    "hr_director": User("hr_director", frozenset({"all-staff", "hr", "hr-leadership"})),
}


def fake_answer(question: str, context: Context) -> str:
    """Stands in for the model: summarises the top document and cites it."""
    if not context.doc_ids:
        return "I couldn't find anything you have access to on that."
    return f"See the relevant guidance [doc:{context.doc_ids[0]}]."


def main() -> None:
    index = BM25Index(CORPUS)
    question = "Leeds office redundancy plans"
    for user in USERS.values():
        hits = index.search(question, user)
        ctx = build_context(hits)
        answer = fake_answer(question, ctx)
        print(f"{user.id} ({', '.join(sorted(user.groups))}) asks: {question!r}")
        for h in hits:
            print(f"   {h.score:6.3f}  {h.doc.id:12} {h.doc.title}")
        print(f"   answer: {answer}   citations ok: {check_citations(answer, ctx).ok}\n")
    # An answer that cites a restricted document is caught.
    ctx = build_context(index.search(question, USERS["analyst"]))
    bad = "Forty roles are at risk [doc:HR-RESTRUCT]."
    print(f"analyst answer citing HR-RESTRUCT -> {check_citations(bad, ctx)}")


if __name__ == "__main__":
    main()
