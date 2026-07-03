"""Data shapes exchanged between retrieval and generation."""

from pydantic import BaseModel, Field

from rag_platform.models.enums import Classification


class RetrievedChunk(BaseModel):
    chunk_id: str
    doc_id: str
    tenant_id: str
    acl_group: str
    classification: Classification
    title: str
    text: str
    score: float


class AnswerPayload(BaseModel):
    """Structured LLM output. `citations` must reference chunk_ids that were
    actually retrieved and authorized — enforced by OutputValidator, not the model.
    """

    answer: str
    citations: list[str] = Field(default_factory=list)
    sufficient_context: bool
