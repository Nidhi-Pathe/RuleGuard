"""Retrieve top passages with a single configurable similarity threshold."""

from __future__ import annotations

from typing import Any

from backend.embeddings import embed_query
from backend.vector_store import load_index, search

# Change retrieval behaviour here only.
TOP_K = 12
SIMILARITY_THRESHOLD = 0.36


class Retriever:
    def __init__(self) -> None:
        self.chunks, self.embeddings = load_index()

    def retrieve(self, question: str, top_k: int = TOP_K) -> list[dict[str, Any]]:
        query_vector = embed_query(question)
        return search(query_vector, self.chunks, self.embeddings, top_k=top_k)

    def relevant(self, hits: list[dict[str, Any]], threshold: float = SIMILARITY_THRESHOLD) -> list[dict[str, Any]]:
        return [hit for hit in hits if hit.get("similarity", 0.0) >= threshold]
