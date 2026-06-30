import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { StatusBadge } from "./StatusBadge";

describe("StatusBadge", () => {
  it.each([
    ["pending", "Pending"],
    ["in_progress", "In progress"],
    ["submitted", "Submitted"],
    ["done", "Done"],
  ])("renders the label for status %s", (status, label) => {
    render(<StatusBadge status={status as never} label={label} />);
    expect(screen.getByText(label)).toBeInTheDocument();
  });

  it("applies the solid primary background to submitted", () => {
    const { container } = render(<StatusBadge status="submitted" label="Submitted" />);
    const span = container.querySelector("span");
    expect(span?.className).toContain("bg-primary");
    expect(span?.className).toContain("text-white");
  });
});
