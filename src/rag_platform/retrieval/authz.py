"""Access-control resolution — the core security boundary (PRD section 6.4.4).

AccessContext is the only thing Retriever.retrieve accepts. There is no
constructor for it that doesn't come from a real User record, and no
retrieval code path that accepts a raw/unfiltered query — this is the
concrete enforcement of PRD section 7.5 ("ACL Bypass via Application Logic
Bugs"): the filter is built here, once, and passed straight into the vector
store's query call, never applied afterward in application code.
"""

from dataclasses import dataclass

from rag_platform.models.enums import Classification
from rag_platform.models.tenant import User


@dataclass(frozen=True)
class AccessContext:
    user_id: str
    tenant_id: str
    clearance: Classification
    acl_groups: tuple[str, ...]

    @classmethod
    def from_user(cls, user: User) -> "AccessContext":
        groups = tuple({*user.acl_groups, "all"})
        return cls(
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            clearance=user.clearance,
            acl_groups=groups,
        )


def build_metadata_filter(ctx: AccessContext) -> dict:
    """Chroma `where` clause: tenant match AND acl_group membership AND
    classification <= clearance (PRD section 6.4.4), evaluated inside the
    vector query itself.
    """
    return {
        "$and": [
            {"tenant_id": ctx.tenant_id},
            {"acl_group": {"$in": list(ctx.acl_groups)}},
            {"classification": {"$lte": int(ctx.clearance)}},
        ]
    }
