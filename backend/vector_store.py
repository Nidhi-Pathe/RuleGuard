"""File-based vector store with manual cosine similarity (NumPy only)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.npy"
CHUNKS_PATH = DATA_DIR / "chunks.json"


def cosine_similarity_matrix(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    query = np.asarray(query, dtype=np.float32).reshape(-1)
    matrix = np.asarray(matrix, dtype=np.float32)
    if matrix.size == 0:
        return np.array([], dtype=np.float32)
    query_norm = float(np.linalg.norm(query))
    row_norms = np.linalg.norm(matrix, axis=1)
    denom = row_norms * query_norm
    denom = np.where(denom == 0, 1e-12, denom)
    return (matrix @ query) / denom


def save_index(chunks: list[dict[str, Any]], embeddings: np.ndarray) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    np.save(EMBEDDINGS_PATH, embeddings)
    CHUNKS_PATH.write_text(json.dumps(chunks, ensure_ascii=True, indent=2), encoding="utf-8")


def index_exists() -> bool:
    return EMBEDDINGS_PATH.exists() and CHUNKS_PATH.exists()


def load_index() -> tuple[list[dict[str, Any]], np.ndarray]:
    if not index_exists():
        raise FileNotFoundError(
            "Vector index not found. From the project root run:\n"
            "  python scripts/generate_pdf.py\n"
            "  python scripts/build_index.py"
        )
    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    embeddings = np.load(EMBEDDINGS_PATH)
    if len(chunks) != embeddings.shape[0]:
        raise ValueError("Index is corrupted: chunk count does not match embedding rows.")
    return chunks, embeddings


def search(
    query_vector: np.ndarray,
    chunks: list[dict[str, Any]],
    embeddings: np.ndarray,
    top_k: int = 8,
) -> list[dict[str, Any]]:
    scores = cosine_similarity_matrix(query_vector, embeddings)
    if scores.size == 0:
        return []
    order = np.argsort(scores)[::-1][:top_k]
    results: list[dict[str, Any]] = []
    for idx in order:
        item = dict(chunks[int(idx)])
        item["similarity"] = float(scores[int(idx)])
        results.append(item)
    return results
