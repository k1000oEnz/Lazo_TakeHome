import { getRequestDictionary } from "@/lib/i18n-server";
import type { DocumentSummary } from "@/lib/types";

export async function DocumentList({ documents }: { documents: DocumentSummary[] }) {
  const t = await getRequestDictionary();
  if (documents.length === 0) {
    return (
      <p className="text-sm text-zinc-500 dark:text-zinc-400">{t["documents.empty"]}</p>
    );
  }
  return (
    <ul className="flex flex-col gap-1">
      {documents.map((d) => (
        <li
          key={d.id}
          className="flex items-center justify-between rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm dark:border-zinc-800 dark:bg-zinc-900"
        >
          <span className="text-zinc-900 dark:text-zinc-50">{d.filename}</span>
          <span className="text-xs text-zinc-500 dark:text-zinc-400">{d.size} B</span>
        </li>
      ))}
    </ul>
  );
}
