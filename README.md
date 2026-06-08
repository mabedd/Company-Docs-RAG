# Company Docs RAG

![CI](https://github.com/mabedd/Company-Docs-RAG/actions/workflows/ci.yml/badge.svg)

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

## Publish (GHCR)

On every push to `main`/`master`, `.github/workflows/publish.yml` builds and pushes:

- `ghcr.io/mabedd/company-docs-rag-backend:latest` (+ commit SHA tag)
- `ghcr.io/mabedd/company-docs-rag-frontend:latest` (+ commit SHA tag)

After the first publish, open **GitHub → Packages** and set each package to **Public** (or use `docker login ghcr.io` on the VM with a PAT that has `read:packages`).

## Deploy to a Linux VM

### 1. Merge to `main` and wait for Publish workflow

Images must exist in GHCR before the VM can pull them.

### 2. Prepare the VM (Ubuntu)

```bash
# SSH into your VM, then:
git clone https://github.com/mabedd/Company-Docs-RAG.git
cd Company-Docs-RAG
sudo ./deploy/setup-vm.sh
```

Log out and back in so Docker group membership applies.

### 3. Configure and deploy

```bash
cp deploy/.env.example .env
# edit .env if needed (HTTP_PORT, OPENAI_API_KEY)

# If packages are private:
echo <GITHUB_PAT> | docker login ghcr.io -u mabedd --password-stdin

./deploy/deploy.sh
```

Open `http://<vm-ip>` (or `:8080` if you set `HTTP_PORT=8080`).

### 4. Seed documents on the server

```bash
docker compose -f docker-compose.prod.yml exec backend python data/sample/ingest_samples.py
```

### 5. Update to a new release

```bash
git pull
./deploy/deploy.sh
```

Or pin a specific build: `IMAGE_TAG=<commit-sha>` in `.env`, then `./deploy/deploy.sh`.
