"""Retrieval layer — the sole place where tenant/ACL/classification filtering
is enforced. `retrieve` takes an AccessContext, not a raw filter dict, so a
caller cannot accidentally query unfiltered (PRD section 7.5).
"""

from rag_platform.models.query import RetrievedChunk
from rag_platform.providers.embeddings import EmbeddingProvider
from rag_platform.providers.vector_store import VectorStore
from rag_platform.retrieval.authz import AccessContext, build_metadata_filter
from rag_platform.security.audit_log import AuditLogger


class Retriever:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self._embeddings = embedding_provider
        self._store = vector_store
        self._audit = audit_logger

    def retrieve(self, query_text: str, ctx: AccessContext, k: int = 5) -> list[RetrievedChunk]:
        query_embedding = self._embeddings.embed_query(query_text)
        where = build_metadata_filter(ctx)
        hits = self._store.query(query_embedding, where=where, k=k)

        if self._audit is not None:
            self._audit.log(
                "retrieval_authorized",
                user_id=ctx.user_id,
                tenant_id=ctx.tenant_id,
                clearance=ctx.clearance.name,
                acl_groups=list(ctx.acl_groups),
                filter_applied=where,
                retrieved_chunk_ids=[h.chunk_id for h in hits],
            )

        return hits
