"""Section-aware chunking that keeps source metadata."""

from __future__ import annotations

from typing import Any

MAX_CHARS = 1200
OVERLAP = 150


def _split_long(text: str, max_chars: int = MAX_CHARS, overlap: int = OVERLAP) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    parts: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            break_at = text.rfind("\n", start + max_chars // 2, end)
            if break_at == -1:
                break_at = text.rfind(". ", start + max_chars // 2, end)
            if break_at != -1:
                end = break_at + 1
        chunk = text[start:end].strip()
        if chunk:
            parts.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return parts


def chunk_documents(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for doc in documents:
        pieces = _split_long(doc["text"])
        for index, piece in enumerate(pieces, start=1):
            section = doc.get("section") or "unknown"
            title = doc.get("title") or "Untitled"
            if len(pieces) > 1:
                title = f"{title} (part {index})"
            chunks.append(
                {
                    "text": piece,
                    "source": doc.get("source", "unknown"),
                    "section": section,
                    "title": title,
                }
            )
    return chunks
