# Multi-stage build: frontend (Vite) -> backend (FastAPI, serving the built
# frontend as static files, see src/rag_platform/api/app.py).

FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json frontend/.npmrc ./
RUN npm ci
COPY frontend/ ./
# Empty base URL -> same-origin relative /api/... calls (no CORS needed in
# production; CORS stays a local-dev-only concern with two separate servers).
ENV VITE_API_BASE_URL=""
RUN npm run build

FROM python:3.12-slim AS backend
WORKDIR /app
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
RUN uv sync --frozen --no-dev

COPY data/ ./data/
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE 8000
# Invoke the venv's uvicorn directly, not `uv run` — `uv run` performs an
# implicit sync check on every invocation, which tries to reach the network
# for dev dependencies (e.g. ruff) even with a fully-synced frozen venv
# already in the image. That's pure runtime risk/latency for zero benefit.
CMD [".venv/bin/uvicorn", "rag_platform.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
