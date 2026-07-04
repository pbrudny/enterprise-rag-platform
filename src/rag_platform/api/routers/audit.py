from fastapi import APIRouter, Depends

from rag_platform.api.deps import get_audit_logger
from rag_platform.api.schemas import AuditEvent
from rag_platform.security.audit_log import AuditLogger

router = APIRouter()


@router.get("", response_model=list[AuditEvent])
def tail_audit(n: int = 50, audit: AuditLogger = Depends(get_audit_logger)) -> list[AuditEvent]:
    entries = audit.tail(n=n)
    return [
        AuditEvent(
            timestamp=e["timestamp"],
            event_type=e["event_type"],
            details={k: v for k, v in e.items() if k not in {"timestamp", "event_type"}},
        )
        for e in entries
    ]
