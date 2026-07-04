import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("mermaid", () => ({
  default: {
    initialize: vi.fn(),
    render: vi.fn().mockResolvedValue({ svg: "<svg data-testid='stub-diagram'></svg>" }),
  },
}));

import { ArchitecturePage } from "../src/pages/ArchitecturePage";

describe("ArchitecturePage", () => {
  it("renders the heading and the diagram container", async () => {
    render(<ArchitecturePage />);

    expect(screen.getByText("Architecture")).toBeInTheDocument();

    await waitFor(() => {
      expect(document.querySelector("[data-testid='stub-diagram']")).toBeInTheDocument();
    });
  });
});
