import Link from "next/link";
import { notFound } from "next/navigation";
import { ApiError, api } from "@/lib/api-client";
import { DEFAULT_LOCALE, getDictionary } from "@/lib/i18n";
import type { Dictionary } from "@/lib/i18n";
import type { ObligationDetail } from "@/lib/types";
import { StatusBadge } from "@/components/StatusBadge";
import { TransitionButtons } from "@/components/TransitionButtons";
import { UploadDocument } from "@/components/UploadDocument";
import { HistoryList } from "@/components/HistoryList";
import { DocumentList } from "@/components/DocumentList";

export default async function DetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ error?: string }>;
}) {
  const { id } = await params;
  const { error: errorParam } = await searchParams;
  const t = getDictionary(DEFAULT_LOCALE);

  let obligation: ObligationDetail | null = null;
  try {
    obligation = await api.getObligation(id);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      notFound();
    }
    throw e;
  }

  if (!obligation) notFound();

  const errorKey = errorParam
    ? (`error.${errorParam.toLowerCase()}` as keyof Dictionary)
    : null;
  const errorMessage = errorKey ? (t[errorKey] ?? t["error.generic"]) : null;

  return (
    <main className="flex flex-1 flex-col items-center bg-white px-6 py-10 dark:bg-zinc-950">
      <div className="w-full max-w-4xl">
        <Link
          href="/"
          className="inline-block text-sm text-primary hover:underline"
        >
          ← {t["nav.back"]}
        </Link>

        {errorMessage && (
          <div
            role="alert"
            className="mt-4 rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200"
          >
            {errorMessage}
          </div>
        )}

        <div className="mt-4 flex flex-col gap-2">
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
            {obligation.title}
          </h1>
          {obligation.description && (
            <p className="text-zinc-600 dark:text-zinc-400">{obligation.description}</p>
          )}
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge
              status={obligation.status}
              label={t[`status.${obligation.status}`]}
            />
            {obligation.is_overdue && (
              <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-800 dark:bg-red-950 dark:text-red-200">
                {t["dashboard.overdue"]}
              </span>
            )}
          </div>
        </div>

        <div className="mt-6">
          <Link
            href={`/obligations/${obligation.id}/edit`}
            className="rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-sm font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800"
          >
            {t["form.edit.title"]}
          </Link>
        </div>

        <section className="mt-8">
          <h2 className="text-sm font-semibold text-zinc-600 dark:text-zinc-400">
            {t["obligation.title"]}
          </h2>
          <dl className="mt-2 grid grid-cols-1 gap-x-6 gap-y-3 sm:grid-cols-2">
            <DetailRow label={t["obligation.type"]} value={t[`type.${obligation.type}`]} />
            <DetailRow label={t["obligation.due_date"]} value={obligation.due_date} />
            <DetailRow label={t["obligation.status"]} value={t[`status.${obligation.status}`]} />
            <DetailRow label={t["obligation.owner"]} value={obligation.owner} />
            <DetailRow
              label={t["obligation.tax_id"]}
              value={obligation.tax_id_masked}
              mono
            />
            <DetailRow
              label={t["obligation.requires_document"]}
              value={obligation.requires_document ? "✓" : "—"}
            />
          </dl>
        </section>

        <section className="mt-8">
          <h2 className="text-sm font-semibold text-zinc-600 dark:text-zinc-400">
            {t["transition.button"]}
          </h2>
          <div className="mt-2">
            <TransitionButtons obligation={obligation} />
          </div>
        </section>

        <section className="mt-8">
          <h2 className="text-sm font-semibold text-zinc-600 dark:text-zinc-400">
            {t["documents.title"]}
          </h2>
          <div className="mt-2 flex flex-col gap-3">
            <DocumentList documents={obligation.documents} />
            <UploadDocument obligationId={obligation.id} />
          </div>
        </section>

        <section className="mt-8">
          <h2 className="text-sm font-semibold text-zinc-600 dark:text-zinc-400">
            {t["history.title"]}
          </h2>
          <div className="mt-2">
            <HistoryList history={obligation.history} />
          </div>
        </section>
      </div>
    </main>
  );
}

function DetailRow({
  label,
  value,
  mono,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <dt className="text-xs text-zinc-500 dark:text-zinc-400">{label}</dt>
      <dd
        className={`mt-0.5 text-sm text-zinc-900 dark:text-zinc-50 ${mono ? "font-mono" : ""}`}
      >
        {value}
      </dd>
    </div>
  );
}
