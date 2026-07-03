"""Paragraph-aware chunking with sliding-window overlap (PRD section 6.3.4)."""

from rag_platform.ingestion.chunker import Chunker
from rag_platform.models.chunk import Chunk
from rag_platform.models.document import DocumentMetadata
from rag_platform.models.enums import Classification

_DOC = DocumentMetadata(
    doc_id="acme-corp:test-doc",
    tenant_id="acme-corp",
    acl_group="all",
    classification=Classification.PUBLIC,
    title="Test Doc",
    source_path=__file__,
)


def test_empty_text_produces_no_chunks():
    assert Chunker().chunk("", _DOC) == []


def test_short_text_produces_single_chunk():
    text = "Paragraph one.\n\nParagraph two."
    chunks = Chunker(max_chars=800).chunk(text, _DOC)

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "acme-corp:test-doc::0"
    assert chunks[0].tenant_id == "acme-corp"
    assert chunks[0].classification == Classification.PUBLIC


def test_long_text_splits_into_multiple_chunks_with_overlap():
    paragraphs = [f"Paragraph {i} " + ("word " * 30) for i in range(10)]
    text = "\n\n".join(paragraphs)
    chunks = Chunker(max_chars=200, overlap_chars=50).chunk(text, _DOC)

    assert len(chunks) > 1
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))
    assert chunks[0].chunk_id == "acme-corp:test-doc::0"
    assert chunks[1].chunk_id == "acme-corp:test-doc::1"

    tail_of_first = chunks[0].text[-50:]
    assert tail_of_first in chunks[1].text


def test_make_id_is_deterministic():
    assert Chunk.make_id("doc-a", 0) == "doc-a::0"
    assert Chunk.make_id("doc-a", 0) == Chunk.make_id("doc-a", 0)
    assert Chunk.make_id("doc-a", 1) != Chunk.make_id("doc-a", 0)
