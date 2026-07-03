"""Full pipeline smoke test: seeded corpus -> retriever -> answer service ->
validated payload, using fakes (fast/offline) by default. Gated tests
exercise the real OpenAI/Anthropic/Vertex AI providers end to end.
"""

import pytest

from rag_platform.generation.answer_service import AnswerService
from rag_platform.providers.embeddings import VertexAIEmbeddingProvider
from rag_platform.providers.llm import VertexAIGeminiProvider
from rag_platform.retrieval.authz import AccessContext
from rag_platform.retrieval.retriever import Retriever
from tests.conftest import FakeLLMProvider


def test_seed_ingest_ask_smoke(seeded_retriever, tenant_registry):
    """Exercises the full wiring: fixture-seeded corpus -> retriever ->
    answer service -> validated payload, for a representative user/question."""
    ctx = AccessContext.from_user(tenant_registry.get_user("acme-manager"))
    service = AnswerService(
        retriever=seeded_retriever,
        llm=FakeLLMProvider(
            answer="Q3 revenue was 142 million EUR.",
            citations=["acme-corp:q3-financial-results-draft::0"],
        ),
    )

    outcome = service.answer("What were the Q3 financial results?", ctx=ctx, k=5)

    assert not outcome.injection_detected
    assert outcome.validation_passed
    assert outcome.payload.answer == "Q3 revenue was 142 million EUR."
    assert "acme-corp:q3-financial-results-draft::0" in outcome.payload.citations


@pytest.mark.integration
def test_real_provider_end_to_end(seeded_retriever, tenant_registry):
    """Requires OPENAI_API_KEY or ANTHROPIC_API_KEY with usable quota. Run with:
    uv run pytest -m integration --run-integration
    """
    from rag_platform.bootstrap import build_llm_provider
    from rag_platform.config import settings

    ctx = AccessContext.from_user(tenant_registry.get_user("acme-employee"))
    service = AnswerService(retriever=seeded_retriever, llm=build_llm_provider(settings))

    outcome = service.answer("What is our VPN password rotation policy?", ctx=ctx, k=5)

    assert outcome.chunks
    assert outcome.payload.answer


@pytest.mark.integration
def test_vertex_ai_end_to_end(tmp_path, tenant_registry):
    """Requires GCP_PROJECT_ID set and `gcloud auth application-default login`
    already run. Run with: uv run pytest -m integration --run-integration

    Ingests into a fresh store using the *same* real Vertex embedding
    provider used for retrieval, rather than reusing the fake-embedded
    `seeded_store` fixture — mixing a 768-dim real query vector against a
    64-dim fake-embedded collection would be a dimension mismatch, not a
    meaningful test.
    """
    from rag_platform.config import settings
    from rag_platform.ingestion.pipeline import IngestionPipeline
    from rag_platform.models.enums import Classification
    from rag_platform.providers.vector_store import ChromaVectorStore

    if not settings.gcp_project_id:
        pytest.skip("GCP_PROJECT_ID not configured")

    embeddings = VertexAIEmbeddingProvider(
        project=settings.gcp_project_id,
        location=settings.gcp_location,
        model_name=settings.vertex_embedding_model,
    )
    store = ChromaVectorStore(persist_dir=tmp_path / "chroma")
    pipeline = IngestionPipeline(
        embedding_provider=embeddings, vector_store=store, raw_store_dir=tmp_path / "raw_store"
    )
    pipeline.ingest_document(
        path=settings.documents_dir / "acme-corp" / "vpn-password-policy.md",
        tenant_id="acme-corp",
        classification=Classification.INTERNAL,
    )

    retriever = Retriever(embedding_provider=embeddings, vector_store=store)
    llm = VertexAIGeminiProvider(
        project=settings.gcp_project_id,
        location=settings.gcp_location,
        model_name=settings.vertex_gemini_model,
    )
    ctx = AccessContext.from_user(tenant_registry.get_user("acme-employee"))
    service = AnswerService(retriever=retriever, llm=llm)

    outcome = service.answer("What is our VPN password rotation policy?", ctx=ctx, k=5)

    assert outcome.chunks
    assert outcome.payload.answer
    assert outcome.payload.citations
