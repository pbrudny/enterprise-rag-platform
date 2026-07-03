"""Documents that fail the ingestion-time prompt-injection scan land here
instead of being embedded/indexed (PRD section 6.3.3 / FR-005)."""

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path


class QuarantineStore:
    def __init__(self, quarantine_dir: Path) -> None:
        self._dir = quarantine_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def add(self, path: Path, tenant_id: str, matched_patterns: tuple[str, ...]) -> Path:
        dest = self._dir / f"{tenant_id}__{path.name}"
        shutil.copy2(path, dest)
        record = {
            "original_path": str(path),
            "tenant_id": tenant_id,
            "matched_patterns": list(matched_patterns),
            "quarantined_at": datetime.now(UTC).isoformat(),
        }
        dest.with_suffix(dest.suffix + ".json").write_text(json.dumps(record, indent=2))
        return dest

    def list(self) -> list[dict]:
        return [json.loads(meta_file.read_text()) for meta_file in sorted(self._dir.glob("*.json"))]
