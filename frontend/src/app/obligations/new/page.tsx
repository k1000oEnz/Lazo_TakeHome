import Link from "next/link";
import { DEFAULT_LOCALE, getDictionary } from "@/lib/i18n";
import { ObligationForm } from "@/components/ObligationForm";

export default async function NewObligationPage() {
  const t = getDictionary(DEFAULT_LOCALE);
  return (
    <main className="flex flex-1 flex-col items-center bg-white px-6 py-10 dark:bg-zinc-950">
      <div className="w-full max-w-2xl">
        <Link
          href="/"
          className="inline-block text-sm text-primary hover:underline"
        >
          ← {t["nav.back"]}
        </Link>
        <h1 className="mt-4 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          {t["form.create.title"]}
        </h1>
        <div className="mt-6">
          <ObligationForm mode="create" />
        </div>
      </div>
    </main>
  );
}
