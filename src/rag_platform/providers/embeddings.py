"""Embedding provider abstraction.

LocalEmbeddingProvider (sentence-transformers) needs no API key or billing.
OpenAIEmbeddingProvider and VertexAIEmbeddingProvider are real, switchable
alternatives. Nothing else in the codebase depends on which provider is
active — only bootstrap.py's factory function branches on config.
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
    """Real Vertex AI Embeddings, via the unified google-genai SDK
    (`genai.Client(vertexai=True, ...)`). Auth is Application Default
    Credentials (`gcloud auth application-default login`) — picked up
    automatically, no key file or explicit credentials object needed.

    Uses distinct task_type per call (RETRIEVAL_DOCUMENT vs RETRIEVAL_QUERY)
    to bias the embedding space for asymmetric search — a real improvement
    over the local/OpenAI providers, which don't distinguish the two.
    """

    def __init__(self, project: str, location: str, model_name: str) -> None:
        from google import genai

        self._client = genai.Client(vertexai=True, project=project, location=location)
        self._model_name = model_name

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        from google.genai.types import EmbedContentConfig

        response = self._client.models.embed_content(
            model=self._model_name,
            contents=texts,
            config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        return [e.values for e in response.embeddings]

    def embed_query(self, text: str) -> list[float]:
        from google.genai.types import EmbedContentConfig

        response = self._client.models.embed_content(
            model=self._model_name,
            contents=[text],
            config=EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )
        return response.embeddings[0].values
