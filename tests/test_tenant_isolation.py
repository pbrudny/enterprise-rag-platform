"""The marquee test: tenant isolation must hold even when a cross-tenant
document is genuinely semantically closer than same-tenant content.
"""

import pytest

from rag_platform.retrieval.authz import AccessContext

CROSS_TENANT_QUERY = "What is our VPN password rotation policy?"

ALL_USER_IDS = [
    "acme-employee",
    "acme-manager",
    "acme-exec",
    "globex-employee",
    "globex-manager",
    "globex-exec",
    "initech-employee",
    "initech-manager",
]


def test_unfiltered_query_actually_leaks_cross_tenant(seeded_store, fake_embeddings):
    """Proves the fixture is real: an unfiltered similarity search must
    surface both tenants' VPN docs. If this assertion ever fails, the
    parametrized test below would be passing for the wrong reason (topic
    divergence, not enforcement) rather than proving anything."""
    query_embedding = fake_embeddings.embed_query(CROSS_TENANT_QUERY)
    hits = seeded_store.query(query_embedding, where=None, k=10)

    tenant_ids = {h.tenant_id for h in hits}
    assert {"acme-corp", "initech"} <= tenant_ids, (
        "expected the unfiltered baseline to include both tenants' VPN docs; "
        f"got tenants={tenant_ids}"
    )


@pytest.mark.parametrize("user_id", ALL_USER_IDS)
@pytest.mark.parametrize("k", [1, 3, 5, 11])
def test_retrieve_never_returns_cross_tenant_chunks(seeded_retriever, tenant_registry, user_id, k):
    user = tenant_registry.get_user(user_id)
    ctx = AccessContext.from_user(user)

    hits = seeded_retriever.retrieve(CROSS_TENANT_QUERY, ctx=ctx, k=k)

    assert hits, "expected at least one hit (every user can see at least their PUBLIC docs)"
    leaked = [h.tenant_id for h in hits if h.tenant_id != user.tenant_id]
    assert not leaked, (
        f"cross-tenant leak: user {user_id} (tenant={user.tenant_id}) retrieved chunks "
        f"from tenants {leaked}"
    )
