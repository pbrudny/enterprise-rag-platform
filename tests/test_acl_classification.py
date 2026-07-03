"""Parametrized over (user, chunk) pairs within a single tenant: ACL group and
classification-clearance boundaries must hold in both directions — under-
privileged users never see chunks above their clearance or outside their ACL
groups, and correctly-entitled users do see what they should (catches
over-strict filters too, not just leaks).
"""

import pytest

from rag_platform.retrieval.authz import AccessContext

# (user_id, chunk_id, should_be_visible)
CASES = [
    # acme-employee: INTERNAL clearance, acl_groups={engineering, all}
    ("acme-employee", "acme-corp:employee-handbook::0", True),
    ("acme-employee", "acme-corp:vpn-password-policy::0", True),
    # wrong acl_group + over clearance
    ("acme-employee", "acme-corp:q3-financial-results-draft::0", False),
    ("acme-employee", "acme-corp:2026-reorg-plan::0", False),
    # acme-manager: CONFIDENTIAL clearance, acl_groups={engineering, finance, all}
    ("acme-manager", "acme-corp:q3-financial-results-draft::0", True),
    ("acme-manager", "acme-corp:2026-reorg-plan::0", False),  # wrong acl_group + over clearance
    # acme-exec: RESTRICTED clearance, acl_groups={exec, all}
    ("acme-exec", "acme-corp:2026-reorg-plan::0", True),
    # clearance ok, wrong acl_group
    ("acme-exec", "acme-corp:q3-financial-results-draft::0", False),
    # globex-employee: INTERNAL clearance, acl_groups={clinical, all}
    ("globex-employee", "globex-inc:patient-data-handling-policy::0", True),
    # acl ok, over clearance
    ("globex-employee", "globex-inc:clinical-trial-results-confidential::0", False),
    # globex-manager: CONFIDENTIAL clearance, acl_groups={clinical, hr, all}
    ("globex-manager", "globex-inc:clinical-trial-results-confidential::0", True),
    # wrong acl_group + over clearance
    ("globex-manager", "globex-inc:executive-merger-plan::0", False),
    # globex-exec: RESTRICTED clearance, acl_groups={exec, all}
    ("globex-exec", "globex-inc:executive-merger-plan::0", True),
    # initech-employee: INTERNAL clearance, acl_groups={engineering, all}
    ("initech-employee", "initech:org-restructuring-plan-confidential::0", False),
    # initech-manager: RESTRICTED clearance, acl_groups={engineering, exec, all}
    ("initech-manager", "initech:org-restructuring-plan-confidential::0", True),
]


@pytest.mark.parametrize("user_id,chunk_id,should_be_visible", CASES)
def test_acl_and_classification_boundaries(
    seeded_retriever, tenant_registry, user_id, chunk_id, should_be_visible
):
    user = tenant_registry.get_user(user_id)
    ctx = AccessContext.from_user(user)

    # Broad query, k covering the whole tenant's corpus: presence/absence of a
    # specific chunk_id is then purely a function of the authz filter, not of
    # similarity ranking.
    hits = seeded_retriever.retrieve("company policy information", ctx=ctx, k=20)
    visible_ids = {h.chunk_id for h in hits}

    assert (chunk_id in visible_ids) == should_be_visible
