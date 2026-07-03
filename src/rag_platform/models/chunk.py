"""A single indexed chunk. Carries the full security metadata of its source document."""

from pydantic import BaseModel

from rag_platform.models.enums import Classification


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    tenant_id: str
    acl_group: str
    classification: Classification
    chunk_index: int
    title: str
    text: str

    @staticmethod
    def make_id(doc_id: str, chunk_index: int) -> str:
        """Deterministic ID so re-ingesting a document upserts rather than duplicates."""
        return f"{doc_id}::{chunk_index}"
