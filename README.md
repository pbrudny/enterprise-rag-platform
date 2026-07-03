# rag-platform (practice build)

A runnable, local practice implementation of the multi-tenant secure RAG platform described in `prd.md`. 

No GCP account is required: OpenAI is used for embeddings/generation as a stand-in for Vertex AI Embeddings/Gemini, and a local ChromaDB index stands in for Vertex AI Vector Search. Both are behind provider interfaces (`src/rag_platform/providers/`) so a real Vertex AI swap-in is a matter of implementing one more class per interface.

## Install & run

```bash
cd enterprise-rag-platform
uv sync

uv run rag version
uv run rag seed-demo              # ingest all mock tenants' documents
uv run rag demo                   # interactive: pick a mock user, ask questions
uv run rag demo --scenario cross-tenant
uv run rag demo --scenario injection
uv run rag audit tail -n 20
```

## Tests

```bash
uv run pytest              # fast, offline, uses fake embedding/LLM providers
uv run pytest -m integration --run-integration   # opt-in, hits real OpenAI/Anthropic
```
