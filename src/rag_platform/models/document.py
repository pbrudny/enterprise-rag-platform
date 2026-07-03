"""Source document metadata. Every chunk derived from a document inherits this metadata."""

from pathlib import Path

from pydantic import BaseModel

from rag_platform.models.enums import Classification


class DocumentMetadata(BaseModel):
    doc_id: str
    tenant_id: str
    acl_group: str
    classification: Classification
    title: str
    source_path: Path
    source_system: str = "upload"
