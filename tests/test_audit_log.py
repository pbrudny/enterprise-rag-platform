"""AuditLogger must be append-only JSONL, separate from application logs,
and never lose prior entries across multiple writes."""

from rag_platform.security.audit_log import AuditLogger


def test_log_appends_structured_jsonl_entries(tmp_path):
    logger = AuditLogger(audit_log_file=tmp_path / "audit.jsonl")

    logger.log("query_injection_detected", user_id="u1", tenant_id="t1", matched_patterns=["x"])
    logger.log("retrieval_authorized", user_id="u1", tenant_id="t1", retrieved_chunk_ids=["c1"])

    entries = logger.tail(n=10)
    assert len(entries) == 2
    assert entries[0]["event_type"] == "query_injection_detected"
    assert entries[1]["event_type"] == "retrieval_authorized"
    assert all("timestamp" in e for e in entries)


def test_tail_respects_n(tmp_path):
    logger = AuditLogger(audit_log_file=tmp_path / "audit.jsonl")
    for i in range(5):
        logger.log("event", seq=i)

    entries = logger.tail(n=2)
    assert [e["seq"] for e in entries] == [3, 4]


def test_tail_on_missing_file_returns_empty(tmp_path):
    logger = AuditLogger(audit_log_file=tmp_path / "does-not-exist.jsonl")
    assert logger.tail() == []
