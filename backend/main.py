"""FastAPI application for RuleGuard."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.answer_generator import (
    evidence_is_sufficient,
    generate_answered,
    generate_conflict,
    generate_not_covered,
)
from backend.conflict_detector import detect_conflicts
from backend.models import AskRequest, AskResponse, ConflictPair, SourceHit
from backend.retriever import Retriever
from backend.vector_store import index_exists

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"

app = FastAPI(
    title="RuleGuard",
    description="Contradiction-aware university rulebook assistant",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        if not index_exists():
            raise HTTPException(
                status_code=503,
                detail=(
                    "Vector index not found. From the project root run: "
                    "python scripts/generate_pdf.py then python scripts/build_index.py"
                ),
            )
        _retriever = Retriever()
    return _retriever


def _to_sources(hits: list[dict]) -> list[SourceHit]:
    return [
        SourceHit(
            source=hit["source"],
            section=hit["section"],
            title=hit["title"],
            text=hit["text"],
            similarity=round(float(hit["similarity"]), 4),
        )
        for hit in hits
    ]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    retriever = get_retriever()
    hits = retriever.retrieve(payload.question)
    relevant = retriever.relevant(hits)

    if not relevant or not evidence_is_sufficient(payload.question, relevant):
        return AskResponse(
            status="not_covered",
            answer=generate_not_covered(hits[:3]),
            sources=_to_sources(hits[:5] if not relevant else relevant[:5]),
        )

    conflicts = detect_conflicts(payload.question, relevant)
    if conflicts:
        return AskResponse(
            status="conflict",
            answer=generate_conflict(conflicts, relevant),
            sources=_to_sources(relevant),
            conflicts=[ConflictPair(**item) for item in conflicts],
        )

    return AskResponse(
        status="answered",
        answer=generate_answered(payload.question, relevant),
        sources=_to_sources(relevant),
    )


@app.get("/")
def home() -> FileResponse:
    index = FRONTEND / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Frontend not found.")
    return FileResponse(index)


if FRONTEND.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND)), name="assets")
