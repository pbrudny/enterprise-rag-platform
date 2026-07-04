from fastapi import APIRouter

from rag_platform.api.routers import audit, documents, query, users

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
