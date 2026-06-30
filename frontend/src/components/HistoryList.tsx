import { getRequestDictionary } from "@/lib/i18n-server";
import type { HistoryEntry } from "@/lib/types";

export async function HistoryList({ history }: { history: HistoryEntry[] }) {
  const t = await getRequestDictionary();
  if (history.length === 0) {
    return (
      <p className="text-sm text-zinc-500 dark:text-zinc-400">{t["history.empty"]}</p>
    );
  }
  return (
    <ol className="flex flex-col gap-2">
      {history.map((h) => (
        <li
          key={h.id}
          className="rounded-md border border-zinc-200 bg-white p-3 text-sm dark:border-zinc-800 dark:bg-zinc-900"
        >
          <div className="flex items-center justify-between">
            <span className="text-zinc-900 dark:text-zinc-50">
              {t[`status.${h.from_status}`]} → {t[`status.${h.to_status}`]}
            </span>
            <span className="text-xs text-zinc-500 dark:text-zinc-400">
              {new Date(h.at).toLocaleString()}
            </span>
          </div>
          {h.actor && (
            <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">{h.actor}</p>
          )}
        </li>
      ))}
    </ol>
  );
}
