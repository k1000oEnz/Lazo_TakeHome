import { ApiError, api } from "@/lib/api-client";
import { DEFAULT_LOCALE, getDictionary } from "@/lib/i18n";

export default async function HomePage() {
  const t = getDictionary(DEFAULT_LOCALE);

  let obligations: Awaited<ReturnType<typeof api.listObligations>> = [];
  let errorMessage: string | null = null;

  try {
    obligations = await api.listObligations();
  } catch (error) {
    errorMessage =
      error instanceof ApiError
        ? error.message
        : t["error.generic"];
  }

  return (
    <main className="flex flex-1 flex-col items-center px-6 py-16">
      <div className="w-full max-w-3xl flex flex-col gap-2">
        <h1 className="text-3xl font-semibold tracking-tight">{t["app.title"]}</h1>
        <p className="text-zinc-600 dark:text-zinc-400">{t["app.subtitle"]}</p>
      </div>

      <section className="w-full max-w-3xl mt-10">
        {errorMessage ? (
          <div
            role="alert"
            className="rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200"
          >
            {t["error.generic"]}: {errorMessage}
          </div>
        ) : obligations.length === 0 ? (
          <p className="text-zinc-500 dark:text-zinc-400">{t["empty.no_obligations"]}</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {obligations.map((o) => (
              <li
                key={o.id}
                className="rounded-md border border-zinc-200 bg-white px-4 py-3 dark:border-zinc-800 dark:bg-zinc-900"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{o.title}</span>
                  <span
                    className={
                      o.is_overdue
                        ? "rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-800 dark:bg-red-950 dark:text-red-200"
                        : "rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200"
                    }
                  >
                    {t[`status.${o.status}`]}
                  </span>
                </div>
                <div className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                  {o.due_date} · {o.owner} · {o.tax_id_masked}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
