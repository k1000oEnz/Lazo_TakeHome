import { getRequestDictionary } from "@/lib/i18n-server";

export default async function Loading() {
  const t = await getRequestDictionary();
  return (
    <main className="flex flex-1 items-center justify-center bg-white px-6 py-10 dark:bg-zinc-950">
      <p className="text-zinc-500 dark:text-zinc-400">{t["loading"]}…</p>
    </main>
  );
}
