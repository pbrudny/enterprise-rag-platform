"""Orchestrates scan -> retrieve -> build prompt -> generate -> validate.
Retrieval's own audit event (retrieval_authorized) is logged inside
Retriever.retrieve; this module logs the events specific to the query path.
"""

from dataclasses import dataclass

from rag_platform.generation.prompt_builder import (
    DEVELOPER_INSTRUCTIONS,
    SYSTEM_PROMPT,
    build_context_block,
)
from rag_platform.models.query import AnswerPayload, RetrievedChunk
from rag_platform.providers.llm import LLMProvider
from rag_platform.retrieval.authz import AccessContext
from rag_platform.retrieval.retriever import Retriever
from rag_platform.security.audit_log import AuditLogger
from rag_platform.security.output_validation import OutputValidator
from rag_platform.security.prompt_injection import PromptInjectionDetector

_INJECTION_REFUSAL = (
    "I can't process this request: it appears to contain an attempt to override "
    "system instructions, which I'm not able to act on."
)


@dataclass(frozen=True)
class QueryOutcome:
    """Everything the security layers decided along the way, not just the
    final answer — so a caller (CLI demo, tests, audit review) can show or
    assert on *why* an answer looks the way it does."""

    payload: AnswerPayload
    chunks: list[RetrievedChunk]
    injection_detected: bool
    injection_matched_patterns: tuple[str, ...]
    validation_passed: bool
    validation_reason: str | None


class AnswerService:
    def __init__(
        self,
        retriever: Retriever,
        llm: LLMProvider,
        injection_detector: PromptInjectionDetector | None = None,
        output_validator: OutputValidator | None = None,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self._retriever = retriever
        self._llm = llm
        self._injection_detector = injection_detector or PromptInjectionDetector()
        self._output_validator = output_validator or OutputValidator()
        self._audit = audit_logger

    def answer(self, query_text: str, ctx: AccessContext, k: int = 5) -> QueryOutcome:
        scan = self._injection_detector.scan(query_text)
        if scan.is_suspicious:
            if self._audit is not None:
                self._audit.log(
                    "query_injection_detected",
                    user_id=ctx.user_id,
                    tenant_id=ctx.tenant_id,
                    matched_patterns=list(scan.matched_patterns),
                )
            refusal = AnswerPayload(
                answer=_INJECTION_REFUSAL, citations=[], sufficient_context=False
            )
            return QueryOutcome(
                payload=refusal,
                chunks=[],
                injection_detected=True,
                injection_matched_patterns=scan.matched_patterns,
                validation_passed=False,
                validation_reason="query_injection_detected",
            )

        chunks = self._retriever.retrieve(query_text, ctx=ctx, k=k)
        context_block = build_context_block(chunks)
        try:
            payload = self._llm.generate(
                system_prompt=SYSTEM_PROMPT,
                developer_instructions=DEVELOPER_INSTRUCTIONS,
                context_block=context_block,
                user_query=query_text,
            )
        except Exception as exc:  # noqa: BLE001 - third-party LLM API call; degrade, don't crash
            if self._audit is not None:
                self._audit.log(
                    "llm_generation_failed",
                    user_id=ctx.user_id,
                    tenant_id=ctx.tenant_id,
                    error=type(exc).__name__,
                )
            degraded = AnswerPayload(
                answer=(
                    f"LLM generation is unavailable right now ({type(exc).__name__}). "
                    "Showing retrieved, authorized context only — see chunks above."
                ),
                citations=[c.chunk_id for c in chunks],
                sufficient_context=False,
            )
            return QueryOutcome(
                payload=degraded,
                chunks=chunks,
                injection_detected=False,
                injection_matched_patterns=(),
                validation_passed=False,
                validation_reason="llm_generation_failed",
            )

        validation = self._output_validator.validate(payload, chunks)
        if not validation.passed:
            if self._audit is not None:
                self._audit.log(
                    "output_validation_violation",
                    user_id=ctx.user_id,
                    tenant_id=ctx.tenant_id,
                    reason=validation.reason,
                    citations_attempted=payload.citations,
                )
            payload = AnswerPayload(
                answer=validation.final_answer, citations=[], sufficient_context=False
            )
        elif self._audit is not None:
            self._audit.log(
                "query_answered",
                user_id=ctx.user_id,
                tenant_id=ctx.tenant_id,
                citation_count=len(payload.citations),
            )

        return QueryOutcome(
            payload=payload,
            chunks=chunks,
            injection_detected=False,
            injection_matched_patterns=(),
            validation_passed=validation.passed,
            validation_reason=validation.reason,
        )
