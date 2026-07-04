"""FastAPI app exposing the same AnswerService/IngestionPipeline core the
CLI uses, over HTTP. No new business logic lives here — routers only adapt
between HTTP and the existing service layer (see rag_platform.bootstrap).

Also serves the built frontend (frontend/dist/) as static files when
present, so the deployed instance is a single process/port with no CORS
needed (same-origin). Locally, frontend/dist/ typically doesn't exist (the
Vite dev server is used instead) — the mount is skipped in that case, not
an error.
"""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import Scope

from rag_platform.api.auth import BasicAuthMiddleware
from rag_platform.api.routers.router import api_router
from rag_platform.config import settings
from rag_platform.logging_config import configure_logging

configure_logging()

_FRONTEND_DIST = Path(__file__).resolve().parents[3] / "frontend" / "dist"


class SPAStaticFiles(StaticFiles):
    """Falls back to index.html for any path that isn't a real static file,
    so React Router's client-side routes (e.g. /ask, /audit) work on a full
    page load/refresh, not just via in-app navigation.
    """

    async def get_response(self, path: str, scope: Scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


app = FastAPI(title="RAG Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("RAG_PLATFORM_CORS_ORIGIN", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Added last so it's outermost (runs first) — nothing below it is reachable
# without valid credentials whenever it's enabled (see auth.py: a no-op
# locally, active only when basic_auth_user/password are set).
app.add_middleware(BasicAuthMiddleware, settings=settings)

app.include_router(api_router, prefix="/api")

if _FRONTEND_DIST.is_dir():
    app.mount("/", SPAStaticFiles(directory=str(_FRONTEND_DIST), html=True), name="frontend")
