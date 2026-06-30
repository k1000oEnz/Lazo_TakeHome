interface KpiCardProps {
  label: string;
  value: number;
  variant?: "default" | "warning" | "success";
}

export function KpiCard({ label, value, variant = "default" }: KpiCardProps) {
  const valueClass =
    variant === "warning"
      ? "text-red-600 dark:text-red-400"
      : variant === "success"
        ? "text-primary"
        : "text-zinc-900 dark:text-zinc-50";

  return (
    <div className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
      <p className="text-sm text-zinc-600 dark:text-zinc-400">{label}</p>
      <p className={`mt-1 text-3xl font-semibold ${valueClass}`}>{value}</p>
    </div>
  );
}
