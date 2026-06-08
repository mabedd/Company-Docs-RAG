from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config import Settings
from app.loaders import load_pdf_file, load_sql_schema, load_text_file
from app.providers import LLMProvider, MockLLMProvider, OpenAILLMProvider
from app.store import DocumentChunk, VectorStore


@dataclass
class Citation:
    source_type: str
    source_name: str
    chunk_index: int
    excerpt: str
    score: float


@dataclass
class QueryResult:
    answer: str
    citations: list[Citation]
    grounded: bool


class RAGService:
    def __init__(self, settings: Settings, store: VectorStore, llm: LLMProvider | None = None) -> None:
        self.settings = settings
        self.store = store
        self.llm = llm or self._default_llm(settings)

    @staticmethod
    def _default_llm(settings: Settings) -> LLMProvider:
        if settings.openai_api_key:
            return OpenAILLMProvider(settings.openai_api_key, settings.openai_model)
        return MockLLMProvider()

    def ingest_text(self, source_name: str, text: str, source_type: str = "text") -> int:
        chunks = self.store.build_chunks(
            source_type=source_type,
            source_name=source_name,
            text=text,
        )
        return self.store.add_documents(chunks)

    def ingest_file(self, path: Path) -> int:
        suffix = path.suffix.lower()
        if suffix == ".txt":
            text = load_text_file(path)
            return self.ingest_text(path.name, text, source_type="text")
        if suffix == ".pdf":
            text = load_pdf_file(path)
            return self.ingest_text(path.name, text, source_type="pdf")
        if suffix in {".db", ".sqlite", ".sqlite3"}:
            text = load_sql_schema(path)
            return self.ingest_text(path.name, text, source_type="sql")
        raise ValueError(f"Unsupported file type: {suffix}")

    def ingest_directory(self, directory: Path) -> dict[str, int]:
        counts: dict[str, int] = {}
        for path in sorted(directory.iterdir()):
            if path.is_file() and path.suffix.lower() in {".txt", ".pdf", ".db", ".sqlite", ".sqlite3"}:
                counts[path.name] = self.ingest_file(path)
        return counts

    def query(self, question: str) -> QueryResult:
        retrieved = self.store.query(question)
        relevant = [
            chunk
            for chunk in retrieved
            if chunk.score is not None and chunk.score >= self.settings.min_relevance_score
        ]

        if not relevant:
            return QueryResult(
                answer="I don't have enough information in the provided sources to answer that.",
                citations=[],
                grounded=False,
            )

        context = "\n\n".join(chunk.text for chunk in relevant)
        answer = self.llm.generate(question, context)
        citations = [
            Citation(
                source_type=chunk.metadata.get("source_type", "unknown"),
                source_name=chunk.metadata.get("source_name", "unknown"),
                chunk_index=int(chunk.metadata.get("chunk_index", 0)),
                excerpt=chunk.text[:240],
                score=float(chunk.score or 0.0),
            )
            for chunk in relevant
        ]
        grounded = "don't have enough information" not in answer.lower()
        return QueryResult(answer=answer, citations=citations, grounded=grounded)
