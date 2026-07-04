import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { AskPage } from "../src/pages/AskPage";
import * as queryApi from "../src/services/queryApi";
import type { QueryResponse } from "../src/types/query";

vi.mock("../src/context/UserContext", () => ({
  useUser: () => ({
    selectedUser: {
      user_id: "acme-employee",
      tenant_id: "acme-corp",
      display_name: "Alice Employee",
      role: "employee",
      clearance: "INTERNAL",
      acl_groups: ["engineering"],
    },
    setSelectedUser: vi.fn(),
  }),
}));

const mockResponse: QueryResponse = {
  access_context: {
    user_id: "acme-employee",
    tenant_id: "acme-corp",
    clearance: "INTERNAL",
    acl_groups: ["all", "engineering"],
  },
  filter_applied: { tenant_id: "acme-corp" },
  injection_detected: false,
  injection_matched_patterns: [],
  chunks: [
    {
      chunk_id: "acme-corp:vpn-password-policy::0",
      doc_id: "acme-corp:vpn-password-policy",
      tenant_id: "acme-corp",
      acl_group: "all",
      classification: "INTERNAL",
      title: "Vpn Password Policy",
      text: "Rotate every 90 days.",
      score: 0.42,
    },
  ],
  answer: "Rotate your VPN password every 90 days.",
  citations: ["acme-corp:vpn-password-policy::0"],
  sufficient_context: true,
  validation_passed: true,
  validation_reason: null,
};

describe("AskPage", () => {
  it("renders all result sections after a successful query", async () => {
    vi.spyOn(queryApi, "postQuery").mockResolvedValue(mockResponse);
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <AskPage />
      </MemoryRouter>,
    );

    await user.type(
      screen.getByPlaceholderText(/VPN password/),
      "What is our VPN password rotation policy?",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    await waitFor(() => {
      expect(screen.getByText("Access context")).toBeInTheDocument();
    });
    expect(screen.getByText("Injection scan: clean")).toBeInTheDocument();
    expect(screen.getByText("acme-corp:vpn-password-policy::0")).toBeInTheDocument();
    expect(screen.getByText(/Output validation: passed/)).toBeInTheDocument();
    expect(screen.getByText("Rotate your VPN password every 90 days.")).toBeInTheDocument();
  });
});
