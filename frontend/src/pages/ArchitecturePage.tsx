import { MermaidDiagram } from "../components/MermaidDiagram";

const DIAGRAM = `flowchart TB
    subgraph Clients
        CLI["CLI (Typer)<br/>ingest / ask / demo / serve"]
        Browser["Browser<br/>React + TS + Vite + Tailwind"]
    end

    subgraph API["FastAPI Application (single process)"]
        BasicAuth["Basic Auth Middleware<br/>no-op locally, gates the deployed instance"]
        StaticFiles["Static frontend (SPA)<br/>same-origin, no CORS in prod"]
        Routers["Routers<br/>/api/users  /api/query  /api/audit"]
    end

    subgraph Core["Core Service Layer"]
        Registry["TenantRegistry<br/>mock users / tenants / ACLs"]
        Ingestion["IngestionPipeline"]
        AnswerSvc["AnswerService<br/>scan to retrieve to generate to validate"]
        AuditLog["AuditLogger<br/>append-only JSONL"]
    end

    subgraph Security["Security Layers"]
        ACL["ACL / tenant / classification filter<br/>enforced inside the vector query"]
        Injection["Prompt injection detector<br/>ingest time and query time"]
        Validation["Output validator<br/>citations must be grounded"]
    end

    subgraph Providers["Pluggable Providers"]
        Embeddings["EmbeddingProvider<br/>local / OpenAI / Vertex AI"]
        LLM["LLMProvider<br/>OpenAI / Anthropic / Vertex AI Gemini"]
    end

    subgraph VectorDB["Vector Store"]
        ChromaLocal["Chroma, embedded<br/>local dev default"]
        ChromaRemote["Chroma, remote HTTP<br/>behind an Envoy bearer-token gate"]
    end

    subgraph Deployment["Mikrus VPS, via Coolify"]
        AppContainer["rag-app container"]
        ChromaContainer["rag-chroma container"]
    end

    CLI --> Core
    Browser -->|HTTP| BasicAuth
    BasicAuth --> Routers
    BasicAuth --> StaticFiles
    Routers --> Core
    Core --> Security
    Security --> VectorDB
    AnswerSvc --> Providers
    Ingestion --> Providers

    AppContainer -.runs.-> API
    AppContainer -.runs.-> Core
    ChromaContainer -.runs.-> ChromaRemote
    AppContainer -->|private LAN IP<br/>public IP hairpins on this host| ChromaContainer
`;

export function ArchitecturePage() {
  return (
    <div className="mx-auto max-w-5xl p-6">
      <h1 className="text-xl font-semibold text-slate-900">Architecture</h1>
      <p className="mt-1 text-sm text-slate-500">
        The as-built practice system this app runs — a scoped-down implementation of the target
        enterprise design in <code>prd.md</code> (no real SSO, CLI-only ingestion, no Vertex AI
        Vector Search). Non-negotiable invariants preserved from that design: ACL/tenant/
        classification filtering happens <em>inside</em> the vector query, never as a post-hoc
        filter; the LLM is treated as untrusted, retrieved context is data, never instructions.
      </p>
      <div className="mt-6 rounded-lg border border-slate-200 bg-white p-4">
        <MermaidDiagram chart={DIAGRAM} />
      </div>
    </div>
  );
}
