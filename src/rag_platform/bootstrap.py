"""Wires concrete providers based on Settings. This is the only place that
decides which concrete class backs each provider interface — swapping to
real Vertex AI later means adding a branch here, nothing else changes.
"""

from rag_platform.config import Settings
from rag_platform.generation.answer_service import AnswerService
from rag_platform.ingestion.pipeline import IngestionPipeline
from rag_platform.ingestion.quarantine import QuarantineStore
from rag_platform.providers.embeddings import (
    EmbeddingProvider,
    LocalEmbeddingProvider,
    OpenAIEmbeddingProvider,
    VertexAIEmbeddingProvider,
)
from rag_platform.providers.llm import (
    AnthropicLLMProvider,
    LLMProvider,
    OpenAILLMProvider,
    VertexAIGeminiProvider,
)
from rag_platform.providers.vector_store import ChromaVectorStore, VectorStore
from rag_platform.retrieval.retriever import Retriever
from rag_platform.security.audit_log import AuditLogger


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "vertex":
        return VertexAIEmbeddingProvider(
            project=settings.gcp_project_id,
            location=settings.gcp_location,
            model_name=settings.vertex_embedding_model,
        )
    if settings.embedding_provider == "openai":
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key, model=settings.embedding_model
        )
    return LocalEmbeddingProvider(model_name=settings.local_embedding_model)


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "vertex":
        return VertexAIGeminiProvider(
            project=settings.gcp_project_id,
            location=settings.gcp_location,
            model_name=settings.vertex_gemini_model,
        )
    if settings.llm_provider == "anthropic":
        return AnthropicLLMProvider(
            api_key=settings.anthropic_api_key, model=settings.anthropic_model
        )
    return OpenAILLMProvider(api_key=settings.openai_api_key, model=settings.openai_model)


def build_vector_store(settings: Settings) -> VectorStore:
    if settings.chroma_mode == "remote":
        return ChromaVectorStore(
            mode="remote",
            host=settings.chroma_host,
            port=settings.chroma_port,
            ssl=settings.chroma_ssl,
            auth_token=settings.chroma_auth_token,
            collection_name=settings.chroma_collection_name,
        )
    return ChromaVectorStore(
        persist_dir=settings.chroma_dir, collection_name=settings.chroma_collection_name
    )


def build_audit_logger(settings: Settings) -> AuditLogger:
    return AuditLogger(audit_log_file=settings.audit_log_file)


def build_ingestion_pipeline(settings: Settings) -> IngestionPipeline:
    return IngestionPipeline(
        embedding_provider=build_embedding_provider(settings),
        vector_store=build_vector_store(settings),
        raw_store_dir=settings.raw_store_dir,
        quarantine_store=QuarantineStore(quarantine_dir=settings.quarantine_dir),
        audit_logger=build_audit_logger(settings),
    )


def build_answer_service(settings: Settings) -> AnswerService:
    audit_logger = build_audit_logger(settings)
    retriever = Retriever(
        embedding_provider=build_embedding_provider(settings),
        vector_store=build_vector_store(settings),
        audit_logger=audit_logger,
    )
    return AnswerService(
        retriever=retriever, llm=build_llm_provider(settings), audit_logger=audit_logger
    )
