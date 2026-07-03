"""Embedding provider abstraction.

LocalEmbeddingProvider (sentence-transformers) is the default: it needs no
API key or billing, which matters because both the OpenAI and Anthropic keys
available in this environment turned out to have no usable quota/credits.
OpenAIEmbeddingProvider is kept as a real, switchable alternative (and as the
closer stand-in for Vertex AI Embeddings) for whenever billing is sorted out.
Swapping to real Vertex AI later means implementing VertexAIEmbeddingProvider
below and adding a branch in bootstrap.py — nothing else in the codebase
depends on which provider is active.
"""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of chunk texts for indexing."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string for retrieval."""


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self._client.embeddings.create(model=self._model, input=texts)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class LocalEmbeddingProvider(EmbeddingProvider):
    """Sentence-transformers, downloaded and run locally. No API key, no
    quota, no network dependency at query time (only the first model
    download needs network access)."""

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class VertexAIEmbeddingProvider(EmbeddingProvider):
    """Not implemented — no GCP/Vertex AI credentials available in this environment.

    Real implementation: `vertexai.language_models.TextEmbeddingModel.from_pretrained(
    "text-embedding-005")`, called region-pinned via `vertexai.init(project=..., location=
    tenant.region)`, batching `.get_embeddings(texts)` for `embed_documents` and a
    single-item call for `embed_query`.
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("Vertex AI requires GCP credentials not available here")

    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError("Vertex AI requires GCP credentials not available here")
