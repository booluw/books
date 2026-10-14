"""Guardrails for AI-assisted personalisation (Chapters 10 and 13).

The model (not included; any LLM API) is asked for ONE relevance line plus the
evidence it used, as JSON:

    {"line": "...", "evidence_url": "https://...", "evidence_quote": "...", "confidence": "high"}

This module validates that output and renders the email from a human-written
template. If validation fails, it falls back to a segment-level line. It also
selects a deterministic QA sample for human review.
"""
from __future__ import annotations

import hashlib
import json
import re
import string
from dataclasses import dataclass, field
from urllib.parse import urlparse

BANNED_PHRASES = [
    "i hope this email finds you well", "game-changer", "game changer", "revolutionize",
    "revolutionise", "synergy", "i noticed you visited our website", "visited our pricing page",
    "as an ai", "i came across your profile", "touch base",
]
TRUSTED_EVIDENCE_HOSTS = {"news.example.org", "jobs.example.net"}   # e.g. your news or jobs feed
MAX_LINE_CHARS = 220

TEMPLATE = string.Template(
    "Hi $first_name,\n\n$relevance_line\n\n$value_prop\n\nWorth a quick look?\n\n$sender\n"
)


@dataclass
class Contact:
    first_name: str
    company: str
    domain: str
    segment: str
    tier: int


@dataclass
class Rendered:
    body: str
    used_ai_line: bool
    problems: list[str] = field(default_factory=list)
    needs_human_review: bool = False


SEGMENT_LINES = {
    "3pl": "Teams running multi-client warehouses usually tell us dispatch planning eats most of the morning.",
    "default": "Operations teams we talk to are trying to do more with the same headcount this year.",
}


def _host_matches(url: str, domain: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host == domain or host.endswith("." + domain) or host in TRUSTED_EVIDENCE_HOSTS


def validate_ai_output(raw: str, contact: Contact) -> tuple[str | None, list[str]]:
    """Return (line, problems). line is None when the output must not be used."""
    problems: list[str] = []
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None, ["output is not valid JSON"]
    line = str(data.get("line", "")).strip()
    evidence_url = str(data.get("evidence_url", "")).strip()
    quote = str(data.get("evidence_quote", "")).strip()
    confidence = str(data.get("confidence", "")).lower()

    if not line:
        problems.append("empty line")
    if len(line) > MAX_LINE_CHARS:
        problems.append(f"line longer than {MAX_LINE_CHARS} characters")
    lowered = line.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            problems.append(f"banned phrase: '{phrase}'")
    if re.search(r"\{\{.*?\}\}|\$[A-Za-z_]\w*|\[[A-Z_ ]+\]|<[a-z_]+>", line):
        problems.append("unfilled placeholder")
    if confidence not in {"high", "medium"}:
        problems.append(f"confidence '{confidence or 'missing'}' too low")
    if not evidence_url or not _host_matches(evidence_url, contact.domain):
        problems.append("missing or untrusted evidence URL")
    # Any number in the line must appear in the quoted evidence (no invented figures).
    for number in re.findall(r"\d[\d,.]*", line):
        if number.rstrip(".,") not in quote:
            problems.append(f"number '{number}' not supported by evidence")
    if contact.company.lower() not in lowered and "you" not in lowered:
        problems.append("line is not about the recipient")
    return (None if problems else line), problems


def render(contact: Contact, ai_raw: str | None, value_prop: str, sender: str) -> Rendered:
    problems: list[str] = []
    line = None
    if ai_raw is not None:
        line, problems = validate_ai_output(ai_raw, contact)
    used_ai = line is not None
    if not used_ai:
        line = SEGMENT_LINES.get(contact.segment, SEGMENT_LINES["default"])
    body = TEMPLATE.substitute(first_name=contact.first_name.strip().title() or "there",
                               relevance_line=line, value_prop=value_prop, sender=sender)
    leftover = re.findall(r"\$[A-Za-z_]\w*|\{\{.*?\}\}", body)
    if leftover:   # template bug: never send
        raise ValueError(f"unrendered placeholders: {leftover}")
    return Rendered(body, used_ai, problems, needs_human_review=contact.tier == 1)


def in_qa_sample(contact_key: str, batch_id: str, rate: float) -> bool:
    """Deterministic sampling: the same contact/batch always gets the same answer."""
    digest = hashlib.sha256(f"{batch_id}:{contact_key}".encode()).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF < rate


if __name__ == "__main__":
    c = Contact("jane", "Acme Logistics", "acme-logistics.com", "3pl", tier=2)
    good = json.dumps({"line": "Saw Acme Logistics is hiring 3 dispatch analysts for the Dallas hub.",
                       "evidence_url": "https://acme-logistics.com/careers",
                       "evidence_quote": "We are hiring 3 dispatch analysts in Dallas", "confidence": "high"})
    bad = json.dumps({"line": "Congrats on Acme Logistics raising $40M! Truly a game-changer.",
                      "evidence_url": "https://randomblog.example.com/post", "confidence": "high"})
    for raw in (good, bad):
        r = render(c, raw, "We help 3PLs cut planning time with automated load building.", "Sam")
        print("AI line used:" if r.used_ai_line else "Fallback used:", r.problems or "no problems")
        print(r.body)
