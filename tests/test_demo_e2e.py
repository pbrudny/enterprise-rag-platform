"""Full pipeline smoke test: seeded corpus -> retriever -> answer service ->
validated payload, using fakes (fast/offline) by default. One gated test
exercises the real OpenAI/Anthropic provider end to end.
"""

import pytest

from rag_platform.generation.answer_service import AnswerService
from rag_platform.retrieval.authz import AccessContext
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
