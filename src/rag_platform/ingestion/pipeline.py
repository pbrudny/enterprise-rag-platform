"""Document ingestion: load -> scan -> chunk -> embed -> index.

Ingestion and query are deliberately separate pipelines (PRD section 6.3 vs
6.4) — this module never participates in the query path.
"""

import shutil
from pathlib import Path

from rag_platform.ingestion.chunker import Chunker
from rag_platform.ingestion.loaders import load_text
from rag_platform.ingestion.quarantine import QuarantineStore
from rag_platform.models.document import DocumentMetadata
from rag_platform.models.enums import Classification
from rag_platform.providers.embeddings import EmbeddingProvider
from rag_platform.providers.vector_store import VectorStore
from rag_platform.security.audit_log import AuditLogger
from rag_platform.security.prompt_injection import PromptInjectionDetector


class DocumentQuarantinedError(Exception):
    def __init__(self, path: Path, matched_patterns: tuple[str, ...]) -> None:
        self.path = path
        self.matched_patterns = matched_patterns
        super().__init__(
            f"Document {path} quarantined: matched injection patterns {matched_patterns}"
        )


class IngestionPipeline:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        raw_store_dir: Path,
        injection_detector: PromptInjectionDetector | None = None,
        quarantine_store: QuarantineStore | None = None,
        chunker: Chunker | None = None,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self._embeddings = embedding_provider
        self._store = vector_store
        self._raw_store_dir = raw_store_dir
        self._chunker = chunker or Chunker()
        self._injection_detector = injection_detector or PromptInjectionDetector()
        self._quarantine = quarantine_store
        self._audit = audit_logger

    def ingest_document(
        self,
        path: Path,
        tenant_id: str,
        acl_group: str = "all",
        classification: Classification = Classification.INTERNAL,
        doc_id: str | None = None,
        title: str | None = None,
        force: bool = False,
    ) -> DocumentMetadata:
        doc_id = doc_id or f"{tenant_id}:{path.stem}"
        title = title or path.stem.replace("-", " ").replace("_", " ").title()

        text = load_text(path)

        scan = self._injection_detector.scan(text)
        if scan.is_suspicious and not force:
            if self._quarantine is not None:
                self._quarantine.add(path, tenant_id, scan.matched_patterns)
            if self._audit is not None:
                self._audit.log(
                    "document_quarantined",
                    tenant_id=tenant_id,
                    doc_id=doc_id,
                    matched_patterns=list(scan.matched_patterns),
                )
            raise DocumentQuarantinedError(path, scan.matched_patterns)

        doc_meta = DocumentMetadata(
            doc_id=doc_id,
            tenant_id=tenant_id,
            acl_group=acl_group,
            classification=classification,
            title=title,
            source_path=path,
        )

        chunks = self._chunker.chunk(text, doc_meta)
        embeddings = self._embeddings.embed_documents([c.text for c in chunks])
        self._store.add(chunks, embeddings)
        self._archive_raw(path, doc_meta)

        if self._audit is not None:
            self._audit.log(
                "document_ingested",
                tenant_id=tenant_id,
                doc_id=doc_id,
                acl_group=acl_group,
                classification=classification.name,
                chunk_count=len(chunks),
                forced=force and scan.is_suspicious,
            )

        return doc_meta

    def _archive_raw(self, path: Path, doc_meta: DocumentMetadata) -> None:
        dest_dir = self._raw_store_dir / doc_meta.tenant_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest_dir / path.name)
