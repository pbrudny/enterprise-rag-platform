from fastapi import APIRouter, Depends, HTTPException

from rag_platform.api.deps import get_answer_service, get_tenant_registry
from rag_platform.api.schemas import (
    AccessContextView,
    QueryRequest,
    QueryResponse,
    RetrievedChunkView,
)
from rag_platform.config import settings
from rag_platform.generation.answer_service import AnswerService
from rag_platform.retrieval.authz import AccessContext, build_metadata_filter
from rag_platform.tenancy.registry import TenantRegistry

router = APIRouter()


@router.post("", response_model=QueryResponse)
def ask(
    body: QueryRequest,
    registry: TenantRegistry = Depends(get_tenant_registry),
    service: AnswerService = Depends(get_answer_service),
) -> QueryResponse:
    try:
        user = registry.get_user(body.user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Unknown user_id: {body.user_id}") from None

    ctx = AccessContext.from_user(user)
    k = body.k or settings.retrieval_top_k
    outcome = service.answer(body.question, ctx=ctx, k=k)

    return QueryResponse(
        access_context=AccessContextView(
            user_id=ctx.user_id,
            tenant_id=ctx.tenant_id,
            clearance=ctx.clearance.name,
            acl_groups=list(ctx.acl_groups),
        ),
        filter_applied=build_metadata_filter(ctx),
        injection_detected=outcome.injection_detected,
        injection_matched_patterns=list(outcome.injection_matched_patterns),
        chunks=[
            RetrievedChunkView(
                chunk_id=c.chunk_id,
                doc_id=c.doc_id,
                tenant_id=c.tenant_id,
                acl_group=c.acl_group,
                classification=c.classification.name,
                title=c.title,
                text=c.text,
                score=c.score,
            )
            for c in outcome.chunks
        ],
        answer=outcome.payload.answer,
        citations=outcome.payload.citations,
        sufficient_context=outcome.payload.sufficient_context,
        validation_passed=outcome.validation_passed,
        validation_reason=outcome.validation_reason,
    )
