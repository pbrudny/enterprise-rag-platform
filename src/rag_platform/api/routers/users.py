from fastapi import APIRouter, Depends

from rag_platform.api.deps import get_tenant_registry
from rag_platform.api.schemas import UserSummary
from rag_platform.tenancy.registry import TenantRegistry

router = APIRouter()


@router.get("", response_model=list[UserSummary])
def list_users(registry: TenantRegistry = Depends(get_tenant_registry)) -> list[UserSummary]:
    return [
        UserSummary(
            user_id=u.user_id,
            tenant_id=u.tenant_id,
            display_name=u.display_name,
            role=u.role,
            clearance=u.clearance.name,
            acl_groups=u.acl_groups,
        )
        for u in registry.list_users()
    ]
