"""Document ingestion over HTTP, scoped to managers/admins for their own
tenant. This is the one place in the API a user *writes* into the
tenant-isolated index rather than just reading from it, so the tenant-
isolation and least-privilege invariants that govern the query path (see
retrieval/authz.py) apply here too, enforced server-side:

- role gate: only manager/security_admin may ingest at all.
- tenant_id is never client-supplied — always the resolved user's own
  tenant, so there is no field a caller could set to write into another
  tenant's index.
- classification/acl_group ceiling: a user can only assign a classification
  at or below their own clearance, and an acl_group they actually belong to
  (or "all") — mirrors this project's least-privilege principle, extended
  from reads to writes.
"""

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from rag_platform.api.deps import get_audit_logger, get_ingestion_pipeline, get_tenant_registry
from rag_platform.api.schemas import AuditEvent, DocumentIngestResponse
from rag_platform.ingestion.pipeline import DocumentQuarantinedError, IngestionPipeline
from rag_platform.models.enums import Classification
from rag_platform.security.audit_log import AuditLogger
from rag_platform.tenancy.registry import TenantRegistry

router = APIRouter()

_INGEST_ROLES = {"manager", "security_admin"}
_ACTIVITY_EVENT_TYPES = {"document_ingested", "document_quarantined"}


@router.post("", response_model=DocumentIngestResponse)
def upload_document(
    user_id: str = Form(...),
    acl_group: str = Form("all"),
    classification: str = Form("INTERNAL"),
    file: UploadFile = File(...),
    registry: TenantRegistry = Depends(get_tenant_registry),
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline),
) -> DocumentIngestResponse:
    try:
        user = registry.get_user(user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Unknown user_id: {user_id}") from None

    if user.role not in _INGEST_ROLES:
        raise HTTPException(status_code=403, detail=f"role '{user.role}' may not ingest documents")

    try:
        level = Classification[classification.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400, detail=f"Unknown classification: {classification}"
        ) from None

    if level > user.clearance:
        raise HTTPException(
            status_code=403,
            detail=f"clearance {user.clearance.name} cannot assign classification {level.name}",
        )
    if acl_group != "all" and acl_group not in user.acl_groups:
        raise HTTPException(status_code=403, detail=f"not a member of acl_group '{acl_group}'")

    original_name = Path(file.filename or "upload").name
    stem = Path(original_name).stem

    with tempfile.NamedTemporaryFile(suffix=Path(original_name).suffix, delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = Path(tmp.name)

    try:
        doc = pipeline.ingest_document(
            path=tmp_path,
            tenant_id=user.tenant_id,
            acl_group=acl_group,
            classification=level,
            doc_id=f"{user.tenant_id}:{stem}",
            title=stem.replace("-", " ").replace("_", " ").title(),
        )
    except DocumentQuarantinedError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Document quarantined: matched prompt-injection patterns",
                "matched_patterns": list(exc.matched_patterns),
            },
        ) from None
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    finally:
        tmp_path.unlink(missing_ok=True)

    return DocumentIngestResponse(
        doc_id=doc.doc_id,
        title=doc.title,
        tenant_id=doc.tenant_id,
        acl_group=doc.acl_group,
        classification=doc.classification.name,
    )


@router.get("/activity", response_model=list[AuditEvent])
def document_activity(
    user_id: str,
    registry: TenantRegistry = Depends(get_tenant_registry),
    audit: AuditLogger = Depends(get_audit_logger),
) -> list[AuditEvent]:
    try:
        user = registry.get_user(user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Unknown user_id: {user_id}") from None

    entries = audit.tail(n=200)
    return [
        AuditEvent(
            timestamp=e["timestamp"],
            event_type=e["event_type"],
            details={k: v for k, v in e.items() if k not in {"timestamp", "event_type"}},
        )
        for e in entries
        if e.get("event_type") in _ACTIVITY_EVENT_TYPES and e.get("tenant_id") == user.tenant_id
    ]
