# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

A working practice implementation exists, per README.md: a Python core library (`src/rag_platform/`) exposed both as a CLI (`rag ...`) and an HTTP API (`src/rag_platform/api/`, FastAPI), plus a React/TypeScript web frontend (`frontend/`). Providers are pluggable — local/OpenAI/Anthropic/**real Vertex AI** for embeddings+generation, local or **remote Chroma** for the vector store — selected via `~/agenty/secrets/.env`. This is still a practice/interview-prep build, not a production deployment of the PRD below; see README.md for how to run the CLI, API, and frontend, and the scope-cuts noted there (no real SSO, CLI-only ingestion, local-only deployment for the web UI).

`prd.md` remains the full target design (~1900 lines) this build is a scoped-down practice version of — read it in full before implementing new pieces, since it defines requirements at a level of detail (specific mitigations, latency budgets, IAM rules) that should not be re-derived or guessed at.

## What this project is

A design for a multi-tenant, enterprise-grade RAG (Retrieval-Augmented Generation) platform on Google Cloud, using Gemini via Vertex AI. It targets regulated industries (finance, healthcare, government) where tenant isolation, ACL-aware retrieval, and auditability are first-class requirements rather than afterthoughts.

## Non-negotiable design invariants (from the PRD)

These are the load-bearing decisions in `prd.md` — any implementation must preserve them, since they're what the whole threat model rests on:

- **Authorization happens before retrieval, not after generation.** ACL/tenant/classification filtering is enforced *inside* the vector search query (`WHERE tenant_id IN user.tenant_ids AND ACL intersects user.permissions AND classification <= user.clearance`), never as a post-hoc filter in application code.
- **The LLM is treated as untrusted.** It is not a security boundary. Retrieved context is untrusted data, never instructions. Prompt structure is strictly layered: System Prompt → Developer Instructions → Retrieved Context (untrusted) → User Query.
- **No cross-tenant vector search, ever.** Either per-tenant index namespaces (regulated/enterprise tier) or a shared index with mandatory `tenant_id` metadata filtering (standard tier) — never unfiltered.
- **Every chunk inherits tenant_id, ACL, and classification metadata** from its source document; this propagates into the vector index and is what retrieval-time filtering keys off of.
- **Ingestion and query pipelines are separate** (offline/batch vs online/latency-sensitive) and scale independently.
- **Region pinning**: storage, vector index, embeddings, and Gemini inference must all stay within the tenant's selected region (EU/US/APAC) — no component may cross region boundaries for a given tenant's data.
- **Logging is redacted by default** — no raw prompts, retrieved content, or LLM responses in application logs. Audit logs (auth events, authorization decisions, document IDs, policy violations) are a separate, immutable, append-only system from application/debug logs.
- **Defense in depth across 6 layers**: identity auth → tenant isolation → ACL-aware retrieval → prompt injection detection → instruction hierarchy → output validation. No single layer is assumed sufficient.

## Reference architecture (Section 6 of the PRD)

Two pipelines:
- **Ingestion (offline)**: Document Sources → Ingestion API (Cloud Run) → Validation/malware scan → Prompt injection scan → Chunking → Vertex AI Embeddings → Vertex AI Vector Search (+ raw docs to GCS).
- **Query (online)**: User → API Gateway → Auth (IAM/Identity Platform) → Query Preprocessor (injection + PII detection) → Retriever (ACL-filtered Vector Search) → Prompt Builder → Gemini (Vertex AI) → Response Validator → User.

Both pipelines emit to Cloud Logging, Cloud Monitoring, and Cloud Audit Logs; secrets go through Secret Manager.

## When implementing pieces of this system

- Check `prd.md` section 6 (System Architecture) for the component's expected responsibilities and section 7 (Threat Model) for what it must defend against before writing it.
- Section 9 (Trade-offs & Design Decisions) records *why* certain alternatives were rejected (e.g., shared vs. per-tenant indexing, structured vs. free-form output) — don't relitigate these without flagging the change to the user first.
- Section 4.2 (Functional Requirements, FR-001 through FR-012) is the closest thing to acceptance criteria.
