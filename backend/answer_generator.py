"""Deterministic extractive answers. Never invents corpus facts."""

from __future__ import annotations

import re
from typing import Any

NOT_COVERED_TEXT = "The rulebook does not specify this."


def _sentences(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in pieces if p.strip()]


def _keywords(question: str) -> list[str]:
    stop = {
        "what",
        "when",
        "where",
        "which",
        "who",
        "whom",
        "how",
        "does",
        "do",
        "the",
        "a",
        "an",
        "is",
        "are",
        "for",
        "to",
        "of",
        "in",
        "on",
        "and",
        "or",
        "my",
        "i",
        "can",
        "if",
        "with",
        "from",
        "at",
        "be",
        "required",
        "requirement",
    }
    tokens = re.findall(r"[a-z0-9%]+", question.lower())
    return [t for t in tokens if t not in stop and len(t) > 2]


def _score_sentence(sentence: str, keys: list[str]) -> int:
    lowered = sentence.lower()
    return sum(1 for key in keys if key in lowered)


GENERIC_TERMS = {
    "student",
    "students",
    "university",
    "nexus",
    "semester",
    "course",
    "campus",
    "rule",
    "policy",
    "examination",
    "exam",
    "attendance",
    "hostel",
    "tuition",
    "fees",
    "fee",
    "library",
    "identity",
    "academic",
    "department",
    "undergraduate",
    "postgraduate",
}


def evidence_is_sufficient(question: str, hits: list[dict[str, Any]]) -> bool:
    """Refuse when distinctive question terms never appear in retrieved text."""
    keys = _keywords(question)
    blob = " ".join(hit["text"].lower() for hit in hits)
    matched = sum(1 for key in keys if key in blob)
    if keys and matched == 0:
        return False
    specific = [key for key in keys if key not in GENERIC_TERMS and len(key) >= 6]
    if specific and not any(key in blob for key in specific):
        return False
    return True

def generate_answered(question: str, hits: list[dict[str, Any]]) -> str:
    keys = _keywords(question)
    ranked: list[tuple[int, str, dict[str, Any]]] = []
    for hit in hits[:5]:
        for sentence in _sentences(hit["text"]):
            if len(sentence) < 25:
                continue
            ranked.append((_score_sentence(sentence, keys), sentence, hit))
    ranked.sort(key=lambda item: item[0], reverse=True)
    chosen: list[tuple[str, dict[str, Any]]] = []
    used = set()
    for score, sentence, hit in ranked:
        if score <= 0:
            continue
        if sentence in used:
            continue
        used.add(sentence)
        chosen.append((sentence, hit))
        if len(chosen) >= 3:
            break
    if not chosen:
        top = hits[0]
        snippet = top["text"][:320].strip()
        return (
            f"According to Section {top['section']} ({top['title']}) in {top['source']}: {snippet}"
        )

    lines = []
    citations = []
    for sentence, hit in chosen:
        lines.append(sentence.rstrip("."))
        cite = f"Section {hit['section']} ({hit['title']}, {hit['source']})"
        if cite not in citations:
            citations.append(cite)
    body = ". ".join(lines) + "."
    return f"{body} Sources: " + "; ".join(citations) + "."


def generate_conflict(conflicts: list[dict[str, Any]], hits: list[dict[str, Any]]) -> str:
    first = conflicts[0]
    return (
        "The rulebook contains conflicting provisions and RuleGuard cannot choose a winning rule. "
        f"{first['explanation']} "
        f"Section {first['section_a']} ({first['title_a']}, {first['source_a']}) states: {first['rule_a']} "
        f"Section {first['section_b']} ({first['title_b']}, {first['source_b']}) states: {first['rule_b']} "
        "Consult the Registrar for an official interpretation."
    )


def generate_not_covered(hits: list[dict[str, Any]]) -> str:
    if not hits:
        return NOT_COVERED_TEXT
    names = ", ".join(f"Section {h['section']} ({h['source']})" for h in hits[:3])
    return (
        f"{NOT_COVERED_TEXT} Nearby passages ({names}) do not contain an applicable rule "
        "for the requested situation."
    )
