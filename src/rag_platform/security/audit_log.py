"""Immutable, append-only audit log — separate from application logs (PRD
section 8.3.3). Captures security-relevant *decisions* (what filter was
applied, what got blocked and why, what was retrieved by ID) as structured
events. Like logging_config.py, this must only ever receive IDs/counts/
pattern names as fields — never raw chunk text, prompts, or model output.
"""

import json
from datetime import UTC, datetime
from pathlib import Path


class AuditLogger:
    def __init__(self, audit_log_file: Path) -> None:
        self._path = audit_log_file
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event_type: str, **fields: object) -> None:
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": event_type,
            **fields,
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")

    def tail(self, n: int = 20) -> list[dict]:
        if not self._path.exists():
            return []
        lines = self._path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines[-n:]]
