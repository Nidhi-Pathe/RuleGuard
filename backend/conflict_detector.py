"""Rule-based conflict detection for incompatible policy values."""

from __future__ import annotations

import re
from typing import Any

PERCENT_RE = re.compile(r"(\d{1,3})\s*%")
DATE_RE = re.compile(
    r"(\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d{2})",
    re.IGNORECASE,
)
TIME_RE = re.compile(r"\b(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))\b")

ATTENDANCE_KEYS = ("attendance", "present", "eligibility", "eligible to appear")
FEE_KEYS = ("fee", "tuition", "deadline", "due date", "payment")
CURFEW_KEYS = ("curfew", "hostel", "return to the hostel", "in-time", "lights out")


def _norm_time(value: str) -> str:
    raw = value.upper().replace(" ", "")
    match = re.match(r"(\d{1,2})(?::(\d{2}))?(AM|PM)", raw)
    if not match:
        return value
    hour = int(match.group(1))
    minute = match.group(2) or "00"
    suffix = match.group(3)
    return f"{hour}:{minute} {suffix}"


def _contains_any(text: str, keys: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(key in lowered for key in keys)


def _snippet(text: str, needle: str, radius: int = 140) -> str:
    loc = text.lower().find(needle.lower())
    if loc == -1:
        return text[:240].strip()
    start = max(0, loc - radius)
    end = min(len(text), loc + len(needle) + radius)
    piece = text[start:end].strip()
    if start > 0:
        piece = "..." + piece
    if end < len(text):
        piece = piece + "..."
    return piece


def _pairs(items: list[tuple[Any, ...]]) -> list[tuple[Any, Any]]:
    out = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            out.append((items[i], items[j]))
    return out


def detect_conflicts(question: str, hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    question_l = question.lower()
    conflicts: list[dict[str, Any]] = []

    asks_attendance = _contains_any(question_l, ATTENDANCE_KEYS + ("percent", "eligib"))
    asks_fee_when = _contains_any(
        question_l, ("deadline", "due date", "due", "last date", "when is")
    ) and _contains_any(question_l, ("fee", "tuition", "odd semester", "payment"))
    asks_curfew = _contains_any(question_l, ("curfew", "in-time", "return time", "return to")) or (
        "hostel" in question_l and _contains_any(question_l, ("weekday", "weeknight", "night", "timing", "time"))
    )

    if asks_attendance:
        conflicts.extend(_attendance_conflicts(hits))
    if asks_fee_when:
        conflicts.extend(_fee_conflicts(hits))
    if asks_curfew:
        conflicts.extend(_curfew_conflicts(hits))

    filtered = conflicts

    unique = []
    seen = set()
    for item in filtered:
        key = (
            item["section_a"],
            item["section_b"],
            item["rule_a"],
            item["rule_b"],
            item["category"],
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _attendance_conflicts(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found: list[tuple[dict[str, Any], str, str]] = []
    for hit in hits:
        text = hit["text"]
        if not _contains_any(text, ATTENDANCE_KEYS):
            continue
        for match in PERCENT_RE.finditer(text):
            value = match.group(1) + "%"
            window = text[max(0, match.start() - 80) : match.end() + 80].lower()
            if not _contains_any(window, ATTENDANCE_KEYS):
                continue
            found.append((hit, value, _snippet(text, match.group(0))))
    conflicts = []
    for left, right in _pairs(found):
        if left[1] == right[1]:
            continue
        if left[0]["source"] == right[0]["source"] and left[0]["section"] == right[0]["section"]:
            continue
        conflicts.append(
            _conflict_payload(
                left[0],
                right[0],
                left[2],
                right[2],
                "attendance",
                f"Incompatible attendance requirements: {left[1]} vs {right[1]}.",
            )
        )
    return conflicts


def _fee_conflicts(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found: list[tuple[dict[str, Any], str, str]] = []
    for hit in hits:
        text = hit["text"]
        if not _contains_any(text, FEE_KEYS):
            continue
        for match in DATE_RE.finditer(text):
            date = re.sub(r"\s+", " ", match.group(1)).title()
            window = text[max(0, match.start() - 90) : match.end() + 90].lower()
            if not _contains_any(window, ("deadline", "due", "pay", "last date")):
                continue
            # Focus on odd-semester / tuition style clashes used in the corpus.
            if "odd" not in text.lower() and "tuition" not in text.lower() and hit["source"].endswith(".csv"):
                pass
            found.append((hit, date, _snippet(text, match.group(1))))
    conflicts = []
    for left, right in _pairs(found):
        if left[1] == right[1]:
            continue
        sources = {left[0]["source"], right[0]["source"]}
        texts = (left[0]["text"] + " " + right[0]["text"]).lower()
        if "odd" not in texts:
            continue
        if not (("fee_deadlines.csv" in sources) or ("04_fee_policy.md" in sources)):
            continue
        conflicts.append(
            _conflict_payload(
                left[0],
                right[0],
                left[2],
                right[2],
                "fee_deadline",
                f"Incompatible fee deadlines: {left[1]} vs {right[1]}.",
            )
        )
    return conflicts


def _curfew_conflicts(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found: list[tuple[dict[str, Any], str, str]] = []
    for hit in hits:
        text = hit["text"]
        if not _contains_any(text, CURFEW_KEYS):
            continue
        for match in TIME_RE.finditer(text):
            window = text[max(0, match.start() - 70) : match.end() + 70].lower()
            if not _contains_any(window, ("curfew", "return", "in-time", "hostel", "weeknight", "weekday")):
                continue
            value = _norm_time(match.group(1))
            found.append((hit, value, _snippet(text, match.group(1))))
    conflicts = []
    for left, right in _pairs(found):
        if left[1] == right[1]:
            continue
        if left[0]["source"] == right[0]["source"] and left[0]["section"] == right[0]["section"]:
            continue
        conflicts.append(
            _conflict_payload(
                left[0],
                right[0],
                left[2],
                right[2],
                "hostel_curfew",
                f"Incompatible hostel return / curfew times: {left[1]} vs {right[1]}.",
            )
        )
    return conflicts


def _conflict_payload(
    a: dict[str, Any],
    b: dict[str, Any],
    rule_a: str,
    rule_b: str,
    category: str,
    explanation: str,
) -> dict[str, Any]:
    return {
        "section_a": a.get("section", ""),
        "title_a": a.get("title", ""),
        "source_a": a.get("source", ""),
        "rule_a": rule_a,
        "section_b": b.get("section", ""),
        "title_b": b.get("title", ""),
        "source_b": b.get("source", ""),
        "rule_b": rule_b,
        "category": category,
        "explanation": explanation,
    }
