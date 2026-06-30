import type { Status } from "@/lib/types";

export function statusBadgeClass(status: Status): string {
  const base = "rounded-full px-2 py-0.5 text-xs font-medium";
  if (status === "submitted") {
    return `${base} bg-primary text-white`;
  }
  if (status === "done") {
    return `${base} bg-primary/30 text-primary dark:bg-primary/20`;
  }
  if (status === "in_progress") {
    return `${base} bg-primary/15 text-primary border border-primary/30 dark:bg-primary/10`;
  }
  return `${base} bg-primary/10 text-primary dark:bg-primary/10`;
}

export function StatusBadge({ status, label }: { status: Status; label: string }) {
  return <span className={statusBadgeClass(status)}>{label}</span>;
}
