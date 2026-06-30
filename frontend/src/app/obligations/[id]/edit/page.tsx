import Link from "next/link";
import { notFound } from "next/navigation";
import { ApiError, api } from "@/lib/api-client";
import { DEFAULT_LOCALE, getDictionary } from "@/lib/i18n";
import { ObligationForm } from "@/components/ObligationForm";

export default async function EditObligationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const t = getDictionary(DEFAULT_LOCALE);

  let obligation;
  try {
    obligation = await api.getObligation(id);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) notFound();
    throw e;
  }
  if (!obligation) notFound();

  return (
    <main className="flex flex-1 flex-col items-center bg-white px-6 py-10 dark:bg-zinc-950">
      <div className="w-full max-w-2xl">
        <Link
          href={`/obligations/${id}`}
          className="inline-block text-sm text-primary hover:underline"
        >
          ← {t["nav.back"]}
        </Link>
        <h1 className="mt-4 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          {t["form.edit.title"]}
        </h1>
        <div className="mt-6">
          <ObligationForm
            mode="edit"
            obligationId={id}
            initial={{
              type: obligation.type,
              title: obligation.title,
              description: obligation.description,
              due_date: obligation.due_date,
              owner: obligation.owner,
              requires_document: obligation.requires_document,
              company_tax_id: obligation.company_tax_id,
            }}
          />
        </div>
      </div>
    </main>
  );
}
