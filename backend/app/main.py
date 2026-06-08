from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from app.config import Settings
from app.rag import RAGService
from app.store import VectorStore


class IngestTextRequest(BaseModel):
    source_name: str
    text: str
    source_type: str = "text"


class IngestDirectoryRequest(BaseModel):
    directory: str


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)


class CitationResponse(BaseModel):
    source_type: str
    source_name: str
    chunk_index: int
    excerpt: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    grounded: bool
    citations: list[CitationResponse]


class IngestResponse(BaseModel):
    chunks_added: int


class HealthResponse(BaseModel):
    status: str
    documents_indexed: int


def build_service(settings: Settings | None = None) -> RAGService:
    resolved = settings or Settings()
    store = VectorStore(resolved)
    return RAGService(resolved, store)


def create_app(settings: Settings | None = None):
    from fastapi import FastAPI, HTTPException

    resolved = settings or Settings()
    service = build_service(resolved)

    app = FastAPI(title=resolved.app_name, version="0.1.0")

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", documents_indexed=service.store.collection.count())

    @app.post("/ingest/text", response_model=IngestResponse)
    def ingest_text(payload: IngestTextRequest) -> IngestResponse:
        added = service.ingest_text(payload.source_name, payload.text, payload.source_type)
        return IngestResponse(chunks_added=added)

    @app.post("/ingest/directory", response_model=dict[str, int])
    def ingest_directory(payload: IngestDirectoryRequest) -> dict[str, int]:
        directory = Path(payload.directory)
        if not directory.exists() or not directory.is_dir():
            raise HTTPException(status_code=400, detail="Directory not found")
        return service.ingest_directory(directory)

    @app.post("/query", response_model=QueryResponse)
    def query(payload: QueryRequest) -> QueryResponse:
        try:
            result = service.query(payload.question)
        except Exception as exc:
            if exc.__class__.__module__.startswith("chromadb"):
                raise HTTPException(
                    status_code=503,
                    detail="Search index is unavailable. Reset the index and re-ingest documents.",
                ) from exc
            raise
        return QueryResponse(
            answer=result.answer,
            grounded=result.grounded,
            citations=[
                CitationResponse(
                    source_type=citation.source_type,
                    source_name=citation.source_name,
                    chunk_index=citation.chunk_index,
                    excerpt=citation.excerpt,
                    score=citation.score,
                )
                for citation in result.citations
            ],
        )

    @app.post("/admin/reset")
    def reset_index() -> dict[str, str]:
        service.store.reset()
        return {"status": "reset"}

    return app
