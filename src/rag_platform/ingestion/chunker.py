"""Paragraph-aware chunking with sliding-window overlap (PRD section 6.3.4)."""

from rag_platform.models.chunk import Chunk
from rag_platform.models.document import DocumentMetadata


class Chunker:
    def __init__(self, max_chars: int = 800, overlap_chars: int = 150) -> None:
        self._max_chars = max_chars
        self._overlap_chars = overlap_chars

    def chunk(self, text: str, doc: DocumentMetadata) -> list[Chunk]:
        windows = self._pack_paragraphs(text)
        return [
            Chunk(
                chunk_id=Chunk.make_id(doc.doc_id, i),
                doc_id=doc.doc_id,
                tenant_id=doc.tenant_id,
                acl_group=doc.acl_group,
                classification=doc.classification,
                chunk_index=i,
                title=doc.title,
                text=window,
            )
            for i, window in enumerate(windows)
        ]

    def _pack_paragraphs(self, text: str) -> list[str]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            return []

        windows: list[str] = []
        current = ""
        for para in paragraphs:
            candidate = f"{current}\n\n{para}" if current else para
            if not current or len(candidate) <= self._max_chars:
                current = candidate
            else:
                windows.append(current)
                tail = current[-self._overlap_chars :]
                current = f"{tail}\n\n{para}"
        if current:
            windows.append(current)
        return windows
