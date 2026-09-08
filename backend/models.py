from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    text: str
    source: str
    section: str
    title: str


class SourceHit(BaseModel):
    source: str
    section: str
    title: str
    text: str
    similarity: float


class ConflictPair(BaseModel):
    section_a: str
    title_a: str
    source_a: str
    rule_a: str
    section_b: str
    title_b: str
    source_b: str
    rule_b: str
    category: str
    explanation: str


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)


class AskResponse(BaseModel):
    status: str
    answer: str
    sources: list[SourceHit] = Field(default_factory=list)
    conflicts: Optional[list[ConflictPair]] = None
    extra: Optional[dict[str, Any]] = None
