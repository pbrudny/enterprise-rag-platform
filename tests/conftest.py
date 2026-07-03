"""Shared test fixtures.

Fake providers keep tests fast and offline. FakeEmbeddingProvider is a
deterministic hashed bag-of-words embedding, not a random stub: shared
vocabulary between documents (e.g. the cross-tenant VPN-policy pair) lands
close together in vector space, which is exactly the property the isolation
tests need in order to be meaningful rather than vacuously passing.
"""

import hashlib
import math
from pathlib import Path

import pytest
import yaml

from rag_platform.config import settings as real_settings
from rag_platform.ingestion.pipeline import IngestionPipeline
from rag_platform.models.enums import Classification
from rag_platform.models.query import AnswerPayload
from rag_platform.providers.embeddings import EmbeddingProvider
from rag_platform.providers.llm import LLMProvider
from rag_platform.providers.vector_store import ChromaVectorStore
from rag_platform.retrieval.retriever import Retriever
from rag_platform.tenancy.registry import TenantRegistry


class FakeEmbeddingProvider(EmbeddingProvider):
    DIM = 64

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.DIM
        for word in text.lower().split():
            idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % self.DIM
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed_one(text)


class FakeLLMProvider(LLMProvider):
    """Canned structured output, configurable per-test."""

    def __init__(
        self,
        answer: str = "fake answer",
        citations: list[str] | None = None,
        sufficient_context: bool = True,
    ) -> None:
        self._answer = answer
        self._citations = citations if citations is not None else []
        self._sufficient_context = sufficient_context

    def generate(
        self, system_prompt: str, developer_instructions: str, context_block: str, user_query: str
    ) -> AnswerPayload:
        return AnswerPayload(
            answer=self._answer,
            citations=self._citations,
            sufficient_context=self._sufficient_context,
        )


def _load_manifest() -> list[dict]:
    return yaml.safe_load(real_settings.documents_manifest.read_text(encoding="utf-8"))


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run tests marked @pytest.mark.integration (calls real OpenAI/Anthropic APIs)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-integration"):
        return
    skip_integration = pytest.mark.skip(reason="needs --run-integration (calls real, billed APIs)")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture
def tenant_registry() -> TenantRegistry:
    return TenantRegistry.load(real_settings.tenants_file)


@pytest.fixture
def fake_embeddings() -> FakeEmbeddingProvider:
    return FakeEmbeddingProvider()


@pytest.fixture
def seeded_store(tmp_path: Path) -> ChromaVectorStore:
    """A fresh Chroma store seeded with the full non-adversarial mock corpus
    via the real IngestionPipeline (fake embeddings for speed)."""
    store = ChromaVectorStore(persist_dir=tmp_path / "chroma")
    pipeline = IngestionPipeline(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=store,
        raw_store_dir=tmp_path / "raw_store",
    )
    for entry in _load_manifest():
        pipeline.ingest_document(
            path=real_settings.documents_dir / entry["tenant_id"] / entry["filename"],
            tenant_id=entry["tenant_id"],
            acl_group=entry["acl_group"],
            classification=Classification[entry["classification"]],
        )
    return store


@pytest.fixture
def seeded_retriever(seeded_store: ChromaVectorStore) -> Retriever:
    return Retriever(embedding_provider=FakeEmbeddingProvider(), vector_store=seeded_store)
