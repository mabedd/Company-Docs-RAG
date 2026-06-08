# Company Docs RAG

Internal document Q&A with ingestion, retrieval, grounded answers, and citations.

```
company-docs-rag/
├── backend/    # FastAPI + RAG API
└── frontend/   # React UI
```

## Backend

**Quick start** (from repo root):

```bash
cd backend
./run.sh
```

First-time setup (sample docs + SQLite DB):

```bash
cd backend
source .venv/bin/activate
python data/sample/create_sample_db.py
python data/sample/ingest_samples.py
```

Sample docs live in `backend/data/sample/` — upload them via the frontend **Ingest** tab, or bulk-ingest with the script above.

Manual start:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

> Run commands from `backend/`, not the repo root. The API needs **Python 3.11+** and the project virtualenv (`backend/.venv`). macOS `python3` is often 3.9 and will fail.

### Test

```bash
cd backend
source .venv/bin/activate
pytest -q
```

### API endpoints

- `GET /health`
- `POST /ingest/text`
- `POST /ingest/directory`
- `POST /query`
- `POST /admin/reset`

Uses mock embeddings/LLM by default. Set `OPENAI_API_KEY` in `backend/.env` for real OpenAI calls.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — dev server proxies `/api` to the backend on port 8000.

Production build: `npm run build` (output in `frontend/dist/`).

## Docker

```bash
docker compose up --build -d
```

Open http://localhost:8080

Seed sample docs:

```bash
docker compose exec backend python data/sample/ingest_samples.py
```

Run backend tests in Docker:

```bash
docker compose --profile test run --rm backend-test
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every push/PR to `main`/`master`:

1. **Backend tests** — `pytest` inside the backend test image
2. **Frontend build** — validates the production Docker build
3. **Integration** — full compose stack, seed data, RAG smoke test via nginx
