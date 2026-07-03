"""Tenant and user identity. A mock stand-in for a real SSO/IdP-issued identity
(Google Identity / Entra ID / Okta / SAML per PRD FR-001) — see
tenancy/registry.py for how this gets resolved from a `--user` CLI flag
instead of a validated auth token.
"""

from pydantic import BaseModel

from rag_platform.models.enums import Classification


class Tenant(BaseModel):
    tenant_id: str
    name: str
    region: str


class User(BaseModel):
    user_id: str
    tenant_id: str
    display_name: str
    role: str
    clearance: Classification
    acl_groups: list[str]
