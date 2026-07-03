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

    embedding_provider: str = "local"  # "local" or "openai"
    embedding_model: str = "text-embedding-3-small"
    local_embedding_model: str = "all-MiniLM-L6-v2"
    llm_provider: str = "openai"  # "openai" or "anthropic"
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-haiku-4-5-20251001"

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


settings = Settings()
