from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb

from app.chunking import chunk_text
from app.config import Settings
from app.providers import EmbeddingProvider, MockEmbeddingProvider, OpenAIEmbeddingProvider


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]
    score: float | None = None


class VectorStore:
    def __init__(self, settings: Settings, embedder: EmbeddingProvider | None = None) -> None:
        self.settings = settings
        self.embedder = embedder or self._default_embedder(settings)
        Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection(name=settings.collection_name)

    @staticmethod
    def _default_embedder(settings: Settings) -> EmbeddingProvider:
        if settings.openai_api_key:
            return OpenAIEmbeddingProvider(settings.openai_api_key, settings.embedding_model)
        return MockEmbeddingProvider()

    def reset(self) -> None:
        self.client.delete_collection(self.settings.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.settings.collection_name)

    def add_documents(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0
        embeddings = self.embedder.embed([chunk.text for chunk in chunks])
        self.collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk.metadata for chunk in chunks],
        )
        return len(chunks)

    def query(self, question: str, top_k: int | None = None) -> list[DocumentChunk]:
        k = top_k or self.settings.top_k
        if self.collection.count() == 0:
            return []

        query_embedding = self.embedder.embed([question])[0]
        result = self.collection.query(query_embeddings=[query_embedding], n_results=k)
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        chunks: list[DocumentChunk] = []
        for idx, text in enumerate(docs):
            distance = distances[idx] if idx < len(distances) else 2.0
            # Chroma returns L2 distance; for normalized embeddings use cosine similarity.
            score = max(0.0, 1.0 - (distance * distance) / 2.0)
            chunks.append(
                DocumentChunk(
                    chunk_id=ids[idx],
                    text=text,
                    metadata=metas[idx] or {},
                    score=score,
                )
            )
        return chunks

    def build_chunks(
        self,
        *,
        source_type: str,
        source_name: str,
        text: str,
        extra_metadata: dict[str, Any] | None = None,
    ) -> list[DocumentChunk]:
        pieces = chunk_text(text, self.settings.chunk_size, self.settings.chunk_overlap)
        chunks: list[DocumentChunk] = []
        for index, piece in enumerate(pieces):
            metadata = {
                "source_type": source_type,
                "source_name": source_name,
                "chunk_index": index,
            }
            if extra_metadata:
                metadata.update(extra_metadata)
            chunk_id = f"{source_type}:{source_name}:{index}"
            chunks.append(DocumentChunk(chunk_id=chunk_id, text=piece, metadata=metadata))
        return chunks
