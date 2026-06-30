import Link from "next/link";
import { ApiError, api } from "@/lib/api-client";
import { isLocale } from "@/lib/i18n";
import { getRequestDictionary } from "@/lib/i18n-server";
import type { Obligation, Status } from "@/lib/types";
import { KpiCard } from "@/components/KpiCard";
import { StatusBadge } from "@/components/StatusBadge";

type Filter = { status?: Status; overdue?: boolean };

function isStatus(value: string | undefined): value is Status {
  return value === "pending" || value === "in_progress" || value === "submitted" || value === "done";
}

function parseFilter(params: { status?: string; overdue?: string }): Filter {
  const filter: Filter = {};
  if (params.overdue === "true") filter.overdue = true;
  else if (isStatus(params.status)) filter.status = params.status;
  return filter;
}

function applyFilter(obligations: Obligation[], filter: Filter): Obligation[] {
  if (filter.overdue) return obligations.filter((o) => o.is_overdue);
  if (filter.status) return obligations.filter((o) => o.status === filter.status);
  return obligations;
}

function filterHref(target: Filter): string {
  if (target.overdue) return "/?overdue=true";
  if (target.status) return `/?status=${target.status}`;
  return "/";
}

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string; overdue?: string }>;
}) {
  const params = await searchParams;
  const t = await getRequestDictionary();
  const filter = parseFilter(params);

  let allObligations: Obligation[] = [];
  let errorMessage: string | null = null;

  try {
    allObligations = await api.listObligations();
  } catch (error) {
    errorMessage =
      error instanceof ApiError
        ? error.message
        : error instanceof Error
          ? error.message
          : t["error.generic"];
  }

  const now = new Date();
  const sevenDaysFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
  const isDueSoon = (o: Obligation) => {
    if (o.status === "submitted" || o.status === "done") return false;
    const due = new Date(o.due_date);
    return due >= now && due <= sevenDaysFromNow;
  };

  const kpis = {
    total: allObligations.length,
    overdue: allObligations.filter((o) => o.is_overdue).length,
    dueSoon: allObligations.filter(isDueSoon).length,
    submitted: allObligations.filter((o) => o.status === "submitted").length,
  };

  const filteredObligations = applyFilter(allObligations, filter);

  const activeKey = filter.overdue
    ? "overdue"
    : (filter.status ?? "all");

  return (
    <main className="flex flex-1 flex-col items-center bg-white px-6 py-10 dark:bg-zinc-950">
      <div className="w-full max-w-6xl flex flex-col gap-1">
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
          {t["dashboard.total"]}
        </h2>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          {t["app.subtitle"]}
        </p>
      </div>

      <section className="w-full max-w-6xl mt-6">
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <KpiCard label={t["dashboard.total"]} value={kpis.total} />
          <KpiCard
            label={t["dashboard.overdue"]}
            value={kpis.overdue}
            variant={kpis.overdue > 0 ? "warning" : "default"}
          />
          <KpiCard label={t["dashboard.due_soon"]} value={kpis.dueSoon} />
          <KpiCard label={t["status.submitted"]} value={kpis.submitted} variant="success" />
        </div>
      </section>

      <section className="w-full max-w-6xl mt-8 flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap gap-2" role="tablist" aria-label={t["filter.status"]}>
            <FilterChip
              href={filterHref({})}
              active={activeKey === "all"}
              label={t["filter.all"]}
            />
            <FilterChip
              href={filterHref({ status: "pending" })}
              active={activeKey === "pending"}
              label={t["status.pending"]}
            />
            <FilterChip
              href={filterHref({ status: "in_progress" })}
              active={activeKey === "in_progress"}
              label={t["status.in_progress"]}
            />
            <FilterChip
              href={filterHref({ status: "submitted" })}
              active={activeKey === "submitted"}
              label={t["status.submitted"]}
            />
            <FilterChip
              href={filterHref({ status: "done" })}
              active={activeKey === "done"}
              label={t["status.done"]}
            />
            <FilterChip
              href={filterHref({ overdue: true })}
              active={activeKey === "overdue"}
              label={t["filter.overdue"]}
            />
          </div>
          <Link
            href="/obligations/new"
            className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-primary/90"
          >
            {t["nav.new_obligation"]}
          </Link>
        </div>

        {errorMessage ? (
          <div
            role="alert"
            className="rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200"
          >
            {errorMessage}
          </div>
        ) : filteredObligations.length === 0 ? (
          <p className="text-zinc-500 dark:text-zinc-400">
            {t["empty.no_obligations"]}
          </p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b-2 border-primary">
                  <th scope="col" className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                    {t["obligation.title"]}
                  </th>
                  <th scope="col" className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                    {t["obligation.type"]}
                  </th>
                  <th scope="col" className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                    {t["obligation.due_date"]}
                  </th>
                  <th scope="col" className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                    {t["obligation.status"]}
                  </th>
                  <th scope="col" className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                    {t["obligation.owner"]}
                  </th>
                  <th scope="col" className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                    {t["obligation.tax_id"]}
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredObligations.map((o) => (
                  <tr
                    key={o.id}
                    className={`border-t border-zinc-100 transition-colors hover:bg-primary/5 dark:border-zinc-800 dark:hover:bg-primary/10 ${
                      o.is_overdue ? "bg-red-50/60 dark:bg-red-950/20" : ""
                    }`}
                  >
                    <td className="px-4 py-3 font-medium text-zinc-900 dark:text-zinc-50">
                      <Link
                        href={`/obligations/${o.id}`}
                        className="hover:text-primary"
                      >
                        {o.title}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">
                      {t[`type.${o.type}`]}
                    </td>
                    <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">
                      {o.due_date}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge
                        status={o.status}
                        label={t[`status.${o.status}`]}
                      />
                    </td>
                    <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">{o.owner}</td>
                    <td className="px-4 py-3 font-mono text-zinc-600 dark:text-zinc-400">
                      {o.tax_id_masked}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

function FilterChip({ href, active, label }: { href: string; active: boolean; label: string }) {
  return (
    <Link
      href={href}
      role="tab"
      aria-selected={active}
      className={
        "rounded-full px-3 py-1 text-sm transition-colors " +
        (active
          ? "bg-primary text-white"
          : "border border-zinc-200 bg-white text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800")
      }
    >
      {label}
    </Link>
  );
}
