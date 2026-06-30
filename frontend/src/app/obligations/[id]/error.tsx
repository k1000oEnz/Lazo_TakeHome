"use client";

import { DEFAULT_LOCALE, getDictionary } from "@/lib/i18n";

export default function ErrorPage({ reset }: { error: Error; reset: () => void }) {
  const t = getDictionary(DEFAULT_LOCALE);
  return (
    <main className="flex flex-1 flex-col items-center justify-center bg-white px-6 py-10 dark:bg-zinc-950">
      <p className="text-red-600 dark:text-red-400">{t["error.generic"]}</p>
      <button
        type="button"
        onClick={reset}
        className="mt-3 rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-sm text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800"
      >
        {t["loading"]}
      </button>
    </main>
  );
}
