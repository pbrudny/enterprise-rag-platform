"""Output validation: the final guardrail before a response reaches the user
(PRD section 6.4.7). Checks are deterministic, not model-judged — a
successfully-injected or hallucinating model cannot talk its way past this
layer by producing plausible-looking but ungrounded output. In particular,
citation grounding is checked against the actual retrieved/authorized chunk
set, so even a compromised model can't smuggle a citation to something that
was never returned to it (PRD section 7.3, defense in depth).
"""

from dataclasses import dataclass

from rag_platform.models.query import AnswerPayload, RetrievedChunk

_INSUFFICIENT_CONTEXT_MESSAGE = (
    "I don't have enough authorized information to answer that question."
)
_NO_CITATIONS_MESSAGE = (
    "I can't provide a grounded answer to that question — no supporting sources were found."
)
_UNGROUNDED_CITATION_MESSAGE = (
    "I can't provide a verified answer to that question — the response referenced content "
    "that wasn't part of the authorized, retrieved context."
)


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    reason: str | None
    final_answer: str


class OutputValidator:
    def validate(self, payload: AnswerPayload, retrieved: list[RetrievedChunk]) -> ValidationResult:
        if not payload.sufficient_context:
            return ValidationResult(
                passed=False,
                reason="insufficient_context",
                final_answer=_INSUFFICIENT_CONTEXT_MESSAGE,
            )

        if not payload.citations:
            return ValidationResult(
                passed=False, reason="no_citations", final_answer=_NO_CITATIONS_MESSAGE
            )

        retrieved_ids = {chunk.chunk_id for chunk in retrieved}
        ungrounded = [c for c in payload.citations if c not in retrieved_ids]
        if ungrounded:
            return ValidationResult(
                passed=False,
                reason="ungrounded_citation",
                final_answer=_UNGROUNDED_CITATION_MESSAGE,
            )

        return ValidationResult(passed=True, reason=None, final_answer=payload.answer)
