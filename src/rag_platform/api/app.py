"""FastAPI app exposing the same AnswerService/IngestionPipeline core the
CLI uses, over HTTP. No new business logic lives here — routers only adapt
between HTTP and the existing service layer (see rag_platform.bootstrap).
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rag_platform.api.routers.router import api_router
from rag_platform.logging_config import configure_logging

configure_logging()

app = FastAPI(title="RAG Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("RAG_PLATFORM_CORS_ORIGIN", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
