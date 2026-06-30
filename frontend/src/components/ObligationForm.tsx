import { createObligationAction } from "@/app/obligations/new/actions";
import { updateObligationAction } from "@/app/obligations/[id]/edit/actions";
import { getRequestDictionary } from "@/lib/i18n-server";
import type { ObligationType } from "@/lib/types";

const TYPES: ObligationType[] = [
  "annual_report",
  "franchise_tax",
  "boi_report",
  "registered_agent_renewal",
];

interface InitialValues {
  type: ObligationType;
  title: string;
  description: string | null;
  due_date: string;
  owner: string;
  requires_document: boolean;
  company_tax_id: string;
}

export async function ObligationForm({
  mode,
  obligationId,
  initial,
}: {
  mode: "create" | "edit";
  obligationId?: string;
  initial?: InitialValues;
}) {
  const t = await getRequestDictionary();
  const action =
    mode === "create" ? createObligationAction : updateObligationAction;
  const cancelHref =
    mode === "edit" && obligationId
      ? `/obligations/${obligationId}`
      : "/";

  const inputClass =
    "rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-sm text-zinc-900 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50";

  return (
    <form action={action} className="flex flex-col gap-4">
      {obligationId && (
        <input type="hidden" name="obligation_id" value={obligationId} />
      )}

      {mode === "create" && (
        <Field label={t["obligation.type"]}>
          <select
            name="type"
            required
            defaultValue={initial?.type ?? "annual_report"}
            className={inputClass}
          >
            {TYPES.map((tp) => (
              <option key={tp} value={tp}>
                {t[`type.${tp}`]}
              </option>
            ))}
          </select>
        </Field>
      )}

      {mode === "edit" && (
        <Field label={t["obligation.type"]}>
          <p className="text-sm text-zinc-700 dark:text-zinc-200">
            {t[`type.${initial?.type ?? "annual_report"}`]}
          </p>
        </Field>
      )}

      <Field label={t["obligation.title"]}>
        <input
          type="text"
          name="title"
          required
          maxLength={255}
          defaultValue={initial?.title ?? ""}
          className={inputClass}
        />
      </Field>

      <Field label={t["obligation.description"]}>
        <textarea
          name="description"
          rows={3}
          defaultValue={initial?.description ?? ""}
          className={inputClass}
        />
      </Field>

      <Field label={t["obligation.due_date"]}>
        <input
          type="date"
          name="due_date"
          required
          defaultValue={initial?.due_date ?? ""}
          className={inputClass}
        />
      </Field>

      <Field label={t["obligation.owner"]}>
        <input
          type="text"
          name="owner"
          required
          maxLength={255}
          defaultValue={initial?.owner ?? ""}
          className={inputClass}
        />
      </Field>

      {mode === "create" && (
        <Field label={t["obligation.tax_id"]}>
          <input
            type="text"
            name="company_tax_id"
            required
            maxLength={50}
            defaultValue={initial?.company_tax_id ?? ""}
            className={`${inputClass} font-mono`}
          />
        </Field>
      )}

      <Field label={t["obligation.requires_document"]}>
        <label className="flex items-center gap-2 text-sm text-zinc-700 dark:text-zinc-200">
          <input
            type="checkbox"
            name="requires_document"
            defaultChecked={initial?.requires_document ?? false}
            className="h-4 w-4 rounded border-zinc-300 text-primary focus:ring-primary"
          />
          <span>✓</span>
        </label>
      </Field>

      <div className="flex gap-2">
        <button
          type="submit"
          className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-primary/90"
        >
          {t["form.submit"]}
        </button>
        <a
          href={cancelHref}
          className="rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-sm font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800"
        >
          {t["form.cancel"]}
        </a>
      </div>
    </form>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-zinc-700 dark:text-zinc-200">
        {label}
      </label>
      {children}
    </div>
  );
}
