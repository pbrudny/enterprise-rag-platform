# rag-platform (practice build)

A runnable, local practice implementation of the multi-tenant secure RAG platform described in `prd.md`. Built for hands-on interview prep, not production use — see `CLAUDE.md` for the architecture invariants this build preserves and `prd.md` for the full target design.

Providers are pluggable (`src/rag_platform/providers/`): local `sentence-transformers` / OpenAI / Anthropic / **real Vertex AI** for embeddings and generation, and a local embedded Chroma or a **remote Chroma server** for the vector store — selected via `~/agenty/secrets/.env` (`EMBEDDING_PROVIDER`, `LLM_PROVIDER`, `CHROMA_MODE`). Nothing is hardcoded to one backend.

## Install & run (CLI)

```bash
cd enterprise-rag-platform
uv sync
# add `--extra local-embeddings` only if you want EMBEDDING_PROVIDER=local
# (sentence-transformers, which pulls in torch — sizable, not needed for
# openai/anthropic/vertex, and left out of the default install/Docker image)

uv run rag version
uv run rag seed-demo              # ingest all mock tenants' documents
uv run rag demo                   # interactive: pick a mock user, ask questions
uv run rag demo --scenario cross-tenant
uv run rag demo --scenario injection
uv run rag audit tail -n 20
```

## Web UI

A FastAPI backend (`src/rag_platform/api/`) exposes the same core service layer over HTTP, and a React/TypeScript frontend (`frontend/`) provides a browser UI: pick a mock user, ask questions (access context/filter/retrieved chunks/injection scan/output validation/citations), ingest documents if you're a manager or security admin, view the architecture diagram, and view the audit log.

**v1 scope, deliberately**: mock user picker (no real auth, plus an HTTP Basic Auth gate in front of the deployed instance specifically — see `src/rag_platform/api/auth.py` — since it triggers real billed LLM calls). Document ingestion (`/documents` page, `POST /api/documents`) is scoped to `manager`/`security_admin` roles, always attributed to the caller's own tenant (never client-supplied), and capped at the caller's own clearance/ACL membership — see `src/rag_platform/api/routers/documents.py`. `rag ingest`/`seed-demo` remain available from the CLI too, sharing the same `IngestionPipeline`.

The backend also serves the built frontend as static files (same process, same-origin, no CORS) when `frontend/dist/` exists — see the `Dockerfile` at the repo root for the deployed build.

Run both sides (two terminals):

```bash
# Terminal 1 — backend, http://127.0.0.1:8000
uv run rag serve
# or, for hot-reload while actively developing the backend:
uv run uvicorn rag_platform.api.app:app --reload

# Terminal 2 — frontend, http://localhost:5173
cd frontend
npm install
cp .env.example .env.local   # first time only
npm run dev
```

Note: `.env.local` points the frontend at `http://127.0.0.1:8000`, not `http://localhost:8000` — on machines where something else (e.g. a Docker container) also listens on port 8000 via IPv6, "localhost" can resolve ambiguously and hit the wrong service. Using the explicit loopback IP sidesteps that.

## Tests

```bash
uv run pytest              # fast, offline, uses fake embedding/LLM providers
uv run pytest -m integration --run-integration   # opt-in, hits real OpenAI/Anthropic/Vertex AI

cd frontend && npm run test   # Vitest + Testing Library
```

Reads `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GCP_PROJECT_ID` / `CHROMA_*` from `~/agenty/secrets/.env`.
