"""Lazy module-level singletons for FastAPI `Depends`.

AnswerService/Retriever/TenantRegistry hold no per-request state (just
wrapped provider clients and a file path), so building them once avoids
re-opening the Chroma connection or re-loading an embedding model on every
request. Lazy (built on first call, not at import time) so tests can install
`app.dependency_overrides` before anything touches Chroma/embeddings.
"""

from rag_platform.bootstrap import (
    build_answer_service,
    build_audit_logger,
    build_ingestion_pipeline,
)
from rag_platform.config import settings
from rag_platform.generation.answer_service import AnswerService
from rag_platform.ingestion.pipeline import IngestionPipeline
from rag_platform.security.audit_log import AuditLogger
from rag_platform.tenancy.registry import TenantRegistry

_answer_service: AnswerService | None = None
_audit_logger: AuditLogger | None = None
_tenant_registry: TenantRegistry | None = None
_ingestion_pipeline: IngestionPipeline | None = None


def get_answer_service() -> AnswerService:
    global _answer_service
    if _answer_service is None:
        _answer_service = build_answer_service(settings)
    return _answer_service


def get_audit_logger() -> AuditLogger:
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = build_audit_logger(settings)
    return _audit_logger


def get_tenant_registry() -> TenantRegistry:
    global _tenant_registry
    if _tenant_registry is None:
        _tenant_registry = TenantRegistry.load(settings.tenants_file)
    return _tenant_registry


def get_ingestion_pipeline() -> IngestionPipeline:
    global _ingestion_pipeline
    if _ingestion_pipeline is None:
        _ingestion_pipeline = build_ingestion_pipeline(settings)
    return _ingestion_pipeline
