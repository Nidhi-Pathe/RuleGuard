from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.retriever import Retriever, SIMILARITY_THRESHOLD
from backend.vector_store import index_exists
from backend.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    if not index_exists():
        pytest.skip("Build the index first: python scripts/generate_pdf.py && python scripts/build_index.py")
    return TestClient(app)


def test_api_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_answerable_question(client: TestClient) -> None:
    response = client.post(
        "/ask",
        json={"question": "How many print volumes may an undergraduate student borrow from the Central Library?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "answered"
    assert body["sources"]
    assert "library" in body["answer"].lower() or "four" in body["answer"].lower()
    assert "similarity" in body["sources"][0]


def test_not_covered_question(client: TestClient) -> None:
    response = client.post(
        "/ask",
        json={"question": "Can I pay my fees using cryptocurrency?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "not_covered"
    assert "does not specify" in body["answer"].lower()


def test_not_covered_wedding(client: TestClient) -> None:
    response = client.post(
        "/ask",
        json={"question": "What happens if I miss an examination because of a family wedding?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "not_covered"
    assert "does not specify" in body["answer"].lower()


def test_attendance_conflict(client: TestClient) -> None:
    response = client.post(
        "/ask",
        json={"question": "What attendance is required to appear for the semester examination?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "conflict"
    assert body["conflicts"]
    blob = json.dumps(body).lower()
    assert "75" in blob and "60" in blob


def test_fee_conflict(client: TestClient) -> None:
    response = client.post(
        "/ask",
        json={"question": "When is the Odd Semester undergraduate tuition deadline for 2026-2027?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "conflict"
    blob = json.dumps(body).lower()
    assert "15 august" in blob and "20 august" in blob


def test_hostel_conflict(client: TestClient) -> None:
    response = client.post(
        "/ask",
        json={"question": "What is the weekday hostel curfew or return time for resident students?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "conflict"
    blob = json.dumps(body).lower()
    assert "10:00" in blob and "11:00" in blob


def test_retrieval() -> None:
    if not index_exists():
        pytest.skip("Index missing")
    retriever = Retriever()
    hits = retriever.retrieve("library borrowing limit undergraduate print volumes")
    assert hits
    assert "similarity" in hits[0]
    assert hits[0]["similarity"] >= SIMILARITY_THRESHOLD or hits[0]["similarity"] > 0.2
    sources = {hit["source"] for hit in hits}
    assert any("academic" in name or "01_" in name for name in sources)
