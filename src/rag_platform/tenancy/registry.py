"""Loads the mock tenant/user directory from tenants.yaml — a stand-in for a
real IdP/SSO integration (PRD FR-001). Token validation is out of scope for
this practice build; a `--user` CLI flag stands in for "authenticated
identity" (see enterprise-rag-platform/CLAUDE.md scope cuts).
"""

from pathlib import Path

import yaml

from rag_platform.models.enums import Classification
from rag_platform.models.tenant import Tenant, User


class TenantRegistry:
    def __init__(self, tenants: dict[str, Tenant], users: dict[str, User]) -> None:
        self._tenants = tenants
        self._users = users

    @classmethod
    def load(cls, path: Path) -> "TenantRegistry":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        tenants = {t["tenant_id"]: Tenant(**t) for t in data["tenants"]}
        users = {}
        for u in data["users"]:
            user = User(
                user_id=u["user_id"],
                tenant_id=u["tenant_id"],
                display_name=u["display_name"],
                role=u["role"],
                clearance=Classification[u["clearance"]],
                acl_groups=u.get("acl_groups", []),
            )
            users[user.user_id] = user
        return cls(tenants=tenants, users=users)

    def get_user(self, user_id: str) -> User:
        try:
            return self._users[user_id]
        except KeyError:
            raise ValueError(f"Unknown user_id: {user_id}") from None

    def get_tenant(self, tenant_id: str) -> Tenant:
        try:
            return self._tenants[tenant_id]
        except KeyError:
            raise ValueError(f"Unknown tenant_id: {tenant_id}") from None

    def list_users(self) -> list[User]:
        return list(self._users.values())
