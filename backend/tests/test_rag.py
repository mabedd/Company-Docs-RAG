from pathlib import Path

import pytest

from app.chunking import chunk_text
from app.config import Settings
from app.loaders import load_sql_schema, load_text_file
from app.main import create_app
from app.rag import RAGService
from app.store import VectorStore


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        chroma_path=str(tmp_path / "chroma"),
        collection_name="test_docs",
        chunk_size=120,
        chunk_overlap=20,
        min_relevance_score=0.18,
    )


@pytest.fixture
def service(settings: Settings) -> RAGService:
    store = VectorStore(settings)
    return RAGService(settings, store)


def test_chunk_text_overlap():
    text = "word " * 80
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_ingest_and_query_with_citations(service: RAGService):
    service.ingest_text(
        "policy.txt",
        "Employees receive 20 paid vacation days each year.",
        source_type="text",
    )

    result = service.query("How many vacation days do employees receive?")

    assert result.grounded is True
    assert "20" in result.answer
    assert len(result.citations) >= 1
    assert result.citations[0].source_name == "policy.txt"


def test_low_confidence_returns_fallback(service: RAGService):
    service.ingest_text("notes.txt", "The cafeteria serves lunch from 12 to 2.", source_type="text")

    result = service.query("What is the company's stock ticker symbol?")

    assert result.grounded is False
    assert "don't have enough information" in result.answer.lower()


def test_sql_schema_loader(tmp_path: Path):
    db_path = tmp_path / "sample.db"
    import sqlite3

    connection = sqlite3.connect(db_path)
    connection.execute("CREATE TABLE employees (id INTEGER, name TEXT)")
    connection.commit()
    connection.close()

    schema = load_sql_schema(db_path)
    assert "Table employees" in schema
    assert "name (TEXT)" in schema


def test_ingest_directory(service: RAGService, tmp_path: Path):
    sample = tmp_path / "handbook.txt"
    sample.write_text("Remote work is allowed up to 3 days per week.", encoding="utf-8")

    counts = service.ingest_directory(tmp_path)
    assert counts["handbook.txt"] == 1

    result = service.query("How many remote days are allowed?")
    assert "3" in result.answer


def test_api_health_and_query(settings: Settings, tmp_path: Path):
    sample_dir = tmp_path / "docs"
    sample_dir.mkdir()
    (sample_dir / "policy.txt").write_text(
        "MFA is required on all production systems.",
        encoding="utf-8",
    )

    app = create_app(settings)
    from fastapi.testclient import TestClient

    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    ingest = client.post("/ingest/directory", json={"directory": str(sample_dir)})
    assert ingest.status_code == 200
    assert ingest.json()["policy.txt"] == 1

    query = client.post("/query", json={"question": "Is MFA required?"})
    assert query.status_code == 200
    body = query.json()
    assert body["grounded"] is True
    assert len(body["citations"]) >= 1
    assert "MFA" in body["answer"] or "mfa" in body["answer"].lower()


def test_sample_hr_file_exists():
    path = Path("data/sample/hr-policy.txt")
    assert path.exists()
    content = load_text_file(path)
    assert "20 paid days" in content
