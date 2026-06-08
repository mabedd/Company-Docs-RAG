"""Ingest all sample files via the running API (preferred) or directly."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

SAMPLE_DIR = Path(__file__).resolve().parent
API_URL = "http://127.0.0.1:8000"


def ingest_via_api() -> bool:
    try:
        health = httpx.get(f"{API_URL}/health", timeout=2.0)
        health.raise_for_status()
    except httpx.HTTPError:
        return False

    response = httpx.post(
        f"{API_URL}/ingest/directory",
        json={"directory": str(SAMPLE_DIR)},
        timeout=60.0,
    )
    response.raise_for_status()
    counts = response.json()
    total = sum(counts.values())
    print(f"Ingested {total} chunks from {len(counts)} files via API:")
    for name, chunks in sorted(counts.items()):
        print(f"  {name}: {chunks} chunks")
    return True


def ingest_direct() -> None:
    backend_root = SAMPLE_DIR.parents[1]
    sys.path.insert(0, str(backend_root))

    from app.config import Settings
    from app.rag import RAGService
    from app.store import VectorStore

    service = RAGService(Settings(), VectorStore(Settings()))
    counts = service.ingest_directory(SAMPLE_DIR)
    total = sum(counts.values())
    print(f"Ingested {total} chunks from {len(counts)} files:")
    for name, chunks in sorted(counts.items()):
        print(f"  {name}: {chunks} chunks")
    print("Note: stop the API server before direct ingest to avoid index corruption.")


def main() -> None:
    if not ingest_via_api():
        ingest_direct()


if __name__ == "__main__":
    main()
