import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AuditLogPage } from "../src/pages/AuditLogPage";
import * as auditApi from "../src/services/auditApi";
import type { AuditEvent } from "../src/types/audit";

const mockEvents: AuditEvent[] = [
  {
    timestamp: "2026-07-04T00:00:00+00:00",
    event_type: "retrieval_authorized",
    details: { user_id: "acme-employee", tenant_id: "acme-corp" },
  },
  {
    timestamp: "2026-07-04T00:00:01+00:00",
    event_type: "query_answered",
    details: { user_id: "acme-employee", citation_count: 1 },
  },
];

describe("AuditLogPage", () => {
  it("renders audit events returned by the API, newest first", async () => {
    vi.spyOn(auditApi, "getAudit").mockResolvedValue(mockEvents);

    render(<AuditLogPage />);

    await waitFor(() => {
      expect(screen.getByText("query_answered")).toBeInTheDocument();
    });
    expect(screen.getByText("retrieval_authorized")).toBeInTheDocument();
  });

  it("shows an error message when the API call fails", async () => {
    vi.spyOn(auditApi, "getAudit").mockRejectedValue(new Error("network error"));

    render(<AuditLogPage />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load audit log/)).toBeInTheDocument();
    });
  });
});
