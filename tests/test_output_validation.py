"""Output validation must catch: insufficient-context refusals, missing
citations, and citations pointing at chunks that were never actually
retrieved/authorized (the last case is the one that matters most — it's
what stops a successfully-injected or hallucinating model from smuggling a
fake source past the user, PRD section 7.3)."""

from rag_platform.models.enums import Classification
from rag_platform.models.query import AnswerPayload, RetrievedChunk
from rag_platform.security.output_validation import OutputValidator

_RETRIEVED = [
    RetrievedChunk(
        chunk_id="acme-corp:vpn-password-policy::0",
        doc_id="acme-corp:vpn-password-policy",
        tenant_id="acme-corp",
        acl_group="all",
        classification=Classification.INTERNAL,
        title="Vpn Password Policy",
        text="...",
        score=0.9,
    )
]


def test_valid_answer_with_grounded_citation_passes():
    payload = AnswerPayload(
        answer="Rotate every 90 days.",
        citations=["acme-corp:vpn-password-policy::0"],
        sufficient_context=True,
    )
    result = OutputValidator().validate(payload, _RETRIEVED)
    assert result.passed
    assert result.final_answer == payload.answer


def test_insufficient_context_is_flagged():
    payload = AnswerPayload(answer="I'm not sure.", citations=[], sufficient_context=False)
    result = OutputValidator().validate(payload, _RETRIEVED)
    assert not result.passed
    assert result.reason == "insufficient_context"


def test_empty_citations_are_flagged():
    payload = AnswerPayload(answer="Rotate every 90 days.", citations=[], sufficient_context=True)
    result = OutputValidator().validate(payload, _RETRIEVED)
    assert not result.passed
    assert result.reason == "no_citations"


def test_citation_to_non_retrieved_chunk_is_flagged():
    """The chunk_id below was never in `_RETRIEVED` — this is exactly what a
    successfully-injected model smuggling a fabricated source would look
    like."""
    payload = AnswerPayload(
        answer="Rotate every 90 days.",
        citations=["acme-corp:2026-reorg-plan::0"],
        sufficient_context=True,
    )
    result = OutputValidator().validate(payload, _RETRIEVED)
    assert not result.passed
    assert result.reason == "ungrounded_citation"


def test_answer_service_replaces_ungrounded_payload_with_refusal(seeded_retriever, tenant_registry):
    from rag_platform.generation.answer_service import AnswerService
    from rag_platform.retrieval.authz import AccessContext
    from tests.conftest import FakeLLMProvider

    ctx = AccessContext.from_user(tenant_registry.get_user("acme-employee"))
    service = AnswerService(
        retriever=seeded_retriever,
        llm=FakeLLMProvider(answer="fabricated", citations=["does-not-exist::0"]),
    )

    outcome = service.answer("What is our VPN password rotation policy?", ctx=ctx, k=5)

    assert outcome.chunks  # retrieval did happen
    assert outcome.validation_reason == "ungrounded_citation"
    assert outcome.payload.citations == []
    assert not outcome.payload.sufficient_context
    assert outcome.payload.answer != "fabricated"
