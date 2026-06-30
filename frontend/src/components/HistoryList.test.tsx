import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import en from "@/lib/dictionaries/en.json";

vi.mock("@/lib/i18n-server", () => ({
  getRequestDictionary: vi.fn().mockResolvedValue(en),
}));

import { HistoryList } from "./HistoryList";
import type { HistoryEntry } from "@/lib/types";

describe("HistoryList", () => {
  it("renders the empty state when there is no history", async () => {
    const element = await HistoryList({ history: [] });
    render(element);

    expect(screen.getByText(/no changes/i)).toBeInTheDocument();
  });

  it("renders each entry with from → to and timestamp", async () => {
    const history: HistoryEntry[] = [
      {
        id: "h-1",
        from_status: "pending",
        to_status: "in_progress",
        at: "2024-01-01T00:00:00Z",
        actor: "alice@acme.com",
      },
      {
        id: "h-2",
        from_status: "in_progress",
        to_status: "submitted",
        at: "2024-01-02T00:00:00Z",
        actor: null,
      },
    ];
    const element = await HistoryList({ history });
    render(element);

    expect(screen.getByText(/Pending → In progress/i)).toBeInTheDocument();
    expect(screen.getByText(/In progress → Submitted/i)).toBeInTheDocument();
    expect(screen.getByText(/alice@acme\.com/)).toBeInTheDocument();
    expect(screen.getByText(/1\/1\/2024/)).toBeInTheDocument();
  });

  it("hides the actor line when actor is null", async () => {
    const history: HistoryEntry[] = [
      {
        id: "h-1",
        from_status: "pending",
        to_status: "in_progress",
        at: "2024-01-01T00:00:00Z",
        actor: null,
      },
    ];
    const element = await HistoryList({ history });
    render(element);

    expect(screen.queryByText(/@/)).not.toBeInTheDocument();
  });
});
