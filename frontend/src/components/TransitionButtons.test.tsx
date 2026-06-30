import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import en from "@/lib/dictionaries/en.json";

vi.mock("@/lib/i18n-server", () => ({
  getRequestDictionary: vi.fn().mockResolvedValue(en),
}));

import { TransitionButtons } from "./TransitionButtons";
import type { ObligationDetail } from "@/lib/types";

const baseObligation: ObligationDetail = {
  id: "obl-1",
  type: "annual_report",
  title: "Annual Report 2024",
  description: null,
  due_date: "2024-12-31",
  owner: "alice@acme.com",
  requires_document: true,
  status: "in_progress",
  company_tax_id: "12-3456789",
  is_overdue: false,
  tax_id_masked: "****-6789",
  version: 1,
  documents: [],
  history: [],
  available_transitions: ["pending", "submitted"],
};

describe("TransitionButtons", () => {
  it("disables the submitted button when requires_document and no documents are attached", async () => {
    const element = await TransitionButtons({ obligation: baseObligation });
    render(element);

    const submitted = screen.getByRole("button", { name: /submitted/i });
    const pending = screen.getByRole("button", { name: /pending/i });

    expect(submitted).toBeDisabled();
    expect(submitted).toHaveAttribute("title", expect.stringContaining("document"));
    expect(pending).not.toBeDisabled();
  });

  it("enables the submitted button when a document is attached", async () => {
    const element = await TransitionButtons({
      obligation: {
        ...baseObligation,
        documents: [
          {
            id: "doc-1",
            filename: "report.pdf",
            size: 1024,
            uploaded_at: "2024-01-01T00:00:00Z",
          },
        ],
      },
    });
    render(element);

    expect(screen.getByRole("button", { name: /submitted/i })).not.toBeDisabled();
  });

  it("enables the submitted button when requires_document is false", async () => {
    const element = await TransitionButtons({
      obligation: { ...baseObligation, requires_document: false },
    });
    render(element);

    expect(screen.getByRole("button", { name: /submitted/i })).not.toBeDisabled();
  });

  it("renders one button per available transition", async () => {
    const element = await TransitionButtons({ obligation: baseObligation });
    render(element);

    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(baseObligation.available_transitions.length);
  });

  it("renders a placeholder when no transitions are available", async () => {
    const element = await TransitionButtons({
      obligation: { ...baseObligation, available_transitions: [] },
    });
    render(element);

    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(screen.getByText("—")).toBeInTheDocument();
  });
});
