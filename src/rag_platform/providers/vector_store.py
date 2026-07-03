"""Vector store abstraction. ChromaVectorStore stands in for Vertex AI Vector Search.

Metadata filtering (`where=`) is a mandatory argument of `collection.query`
itself, not something applied after an unfiltered search — this is a
deliberate choice (see enterprise-rag-platform/CLAUDE.md) to make the
ACL-bypass-via-application-logic anti-pattern (PRD section 7.5) structurally
awkward to write by accident: there is no `.query()` call without a `where`
decision.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from rag_platform.models.chunk import Chunk
from rag_platform.models.enums import Classification
from rag_platform.models.query import RetrievedChunk


class VectorStore(ABC):
    @abstractmethod
    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None: ...

    @abstractmethod
    def query(self, embedding: list[float], where: dict | None, k: int) -> list[RetrievedChunk]: ...

    @abstractmethod
    def delete_document(self, doc_id: str) -> None: ...

    @abstractmethod
    def count(self) -> int: ...


class ChromaVectorStore(VectorStore):
    def __init__(self, persist_dir: Path, collection_name: str = "chunks") -> None:
        import chromadb

        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._collection = self._client.get_or_create_collection(collection_name)

    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        self._collection.upsert(
            ids=[c.chunk_id for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[
                {
                    "doc_id": c.doc_id,
                    "tenant_id": c.tenant_id,
                    "acl_group": c.acl_group,
                    "classification": int(c.classification),
                    "chunk_index": c.chunk_index,
                    "title": c.title,
                }
                for c in chunks
            ],
        )

    def query(self, embedding: list[float], where: dict | None, k: int) -> list[RetrievedChunk]:
        n_results = min(k, max(self.count(), 1))
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where=where,
        )
        hits: list[RetrievedChunk] = []
        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        for chunk_id, text, meta, distance in zip(
            ids, documents, metadatas, distances, strict=True
        ):
            hits.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    doc_id=meta["doc_id"],
                    tenant_id=meta["tenant_id"],
                    acl_group=meta["acl_group"],
                    classification=Classification(meta["classification"]),
                    title=meta["title"],
                    text=text,
                    score=1.0 - distance,
                )
            )
        return hits

    def delete_document(self, doc_id: str) -> None:
        self._collection.delete(where={"doc_id": doc_id})

    def count(self) -> int:
        return self._collection.count()
