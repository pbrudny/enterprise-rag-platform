import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { UserProvider } from "../src/context/UserContext";
import { UserPickerPage } from "../src/pages/UserPickerPage";
import * as usersApi from "../src/services/usersApi";
import type { UserSummary } from "../src/types/user";

const mockUsers: UserSummary[] = [
  {
    user_id: "acme-employee",
    tenant_id: "acme-corp",
    display_name: "Alice Employee",
    role: "employee",
    clearance: "INTERNAL",
    acl_groups: ["engineering"],
  },
  {
    user_id: "acme-manager",
    tenant_id: "acme-corp",
    display_name: "Morgan Manager",
    role: "manager",
    clearance: "CONFIDENTIAL",
    acl_groups: ["engineering", "finance"],
  },
];

function renderPage() {
  return render(
    <MemoryRouter>
      <UserProvider>
        <UserPickerPage />
      </UserProvider>
    </MemoryRouter>,
  );
}

describe("UserPickerPage", () => {
  it("renders users returned by the API", async () => {
    vi.spyOn(usersApi, "getUsers").mockResolvedValue(mockUsers);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Alice Employee")).toBeInTheDocument();
    });
    expect(screen.getByText("Morgan Manager")).toBeInTheDocument();
    expect(screen.getAllByText(/acme-corp/)).toHaveLength(2);
  });

  it("shows an error message when the API call fails", async () => {
    vi.spyOn(usersApi, "getUsers").mockRejectedValue(new Error("network error"));

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/Failed to load users/)).toBeInTheDocument();
    });
  });
});
