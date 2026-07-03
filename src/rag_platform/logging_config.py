"""Structured JSON application logging.

Redacted by design: log calls in this codebase must only pass structured
kwargs/IDs (request_id, tenant_id, chunk_id, latency_ms, ...), never chunk
text, prompts, or model output. That content belongs in the separate,
access-controlled audit log (see security/audit_log.py) or nowhere at all.
"""

import json
import logging
import sys
from datetime import UTC, datetime

from rag_platform.config import settings

_RESERVED = frozenset(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extras = {k: v for k, v in record.__dict__.items() if k not in _RESERVED}
        payload.update(extras)
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    settings.app_log_file.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("rag_platform")
    root.setLevel(logging.INFO)
    root.handlers.clear()

    file_handler = logging.FileHandler(settings.app_log_file)
    file_handler.setFormatter(JsonFormatter())
    root.addHandler(file_handler)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(JsonFormatter())
    stderr_handler.setLevel(logging.WARNING)
    root.addHandler(stderr_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"rag_platform.{name}")
