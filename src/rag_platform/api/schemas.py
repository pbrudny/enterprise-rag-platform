"""HTTP request/response models for the API layer.

Classification/clearance fields are typed `str` (the enum's `.name`, e.g.
"INTERNAL") rather than the raw `Classification` IntEnum — pydantic would
otherwise serialize an IntEnum as a bare int, losing the readability the CLI
already gets from `.name`. Routers populate `.name` explicitly when mapping
domain objects into these schemas.
"""

from pydantic import BaseModel, Field


class UserSummary(BaseModel):
    user_id: str
    tenant_id: str
    display_name: str
    role: str
    clearance: str
    acl_groups: list[str]


class AccessContextView(BaseModel):
    user_id: str
    tenant_id: str
    clearance: str
    acl_groups: list[str]


class RetrievedChunkView(BaseModel):
    chunk_id: str
    doc_id: str
    tenant_id: str
    acl_group: str
    classification: str
    title: str
    text: str
    score: float


class QueryRequest(BaseModel):
    user_id: str
    question: str
    k: int | None = None


class QueryResponse(BaseModel):
    access_context: AccessContextView
    filter_applied: dict
    injection_detected: bool
    injection_matched_patterns: list[str]
    chunks: list[RetrievedChunkView]
    answer: str
    citations: list[str]
    sufficient_context: bool
    validation_passed: bool
    validation_reason: str | None


class AuditEvent(BaseModel):
    timestamp: str
    event_type: str
    details: dict = Field(default_factory=dict)


class DocumentIngestResponse(BaseModel):
    doc_id: str
    title: str
    tenant_id: str
    acl_group: str
    classification: str
