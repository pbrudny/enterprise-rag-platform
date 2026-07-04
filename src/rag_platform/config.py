"""Configuration via pydantic-settings, loaded from .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_SECRETS_ENV = Path.home() / "agenty" / "secrets" / ".env"
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", str(_SECRETS_ENV)),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    anthropic_api_key: str = ""

    embedding_provider: str = "local"  # "local", "openai", or "vertex"
    embedding_model: str = "text-embedding-3-small"
    local_embedding_model: str = "all-MiniLM-L6-v2"
    llm_provider: str = "openai"  # "openai", "anthropic", or "vertex"
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-haiku-4-5-20251001"

    # Vertex AI, via the unified google-genai SDK (genai.Client(vertexai=True, ...)).
    # Auth is Application Default Credentials (`gcloud auth application-default
    # login`) — no key file, nothing read from these settings for credentials.
    gcp_project_id: str = ""
    gcp_location: str = "europe-west4"
    vertex_embedding_model: str = "text-embedding-005"
    vertex_gemini_model: str = "gemini-2.5-flash"

    # Chroma: "local" (embedded PersistentClient) or "remote" (HttpClient
    # against a server, e.g. the one deployed to the Mikrus VPS via Coolify).
    chroma_mode: str = "local"
    chroma_host: str = ""
    chroma_port: int = 443
    chroma_ssl: bool = True
    chroma_auth_token: str = ""

    data_dir: Path = _PROJECT_ROOT / "data"
    chroma_dir: Path = _PROJECT_ROOT / "data" / "chroma"
    quarantine_dir: Path = _PROJECT_ROOT / "data" / "quarantine"
    raw_store_dir: Path = _PROJECT_ROOT / "data" / "raw_store"
    tenants_file: Path = _PROJECT_ROOT / "data" / "tenants.yaml"
    documents_dir: Path = _PROJECT_ROOT / "data" / "documents"
    documents_manifest: Path = _PROJECT_ROOT / "data" / "documents" / "manifest.yaml"
    audit_log_file: Path = _PROJECT_ROOT / "data" / "audit.jsonl"
    app_log_file: Path = _PROJECT_ROOT / "data" / "app.jsonl"

    retrieval_top_k: int = 5

    # HTTP Basic Auth gate for the API/frontend (src/rag_platform/api/auth.py).
    # Empty (the default, i.e. local dev) disables the gate entirely.
    basic_auth_user: str = ""
    basic_auth_password: str = ""


settings = Settings()
