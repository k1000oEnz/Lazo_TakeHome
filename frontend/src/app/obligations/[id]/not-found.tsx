import Link from "next/link";
import { DEFAULT_LOCALE, getDictionary } from "@/lib/i18n";

export default function NotFound() {
  const t = getDictionary(DEFAULT_LOCALE);
  return (
    <main className="flex flex-1 flex-col items-center justify-center bg-white px-6 py-10 dark:bg-zinc-950">
      <p className="text-zinc-600 dark:text-zinc-400">{t["error.not_found"]}</p>
      <Link
        href="/"
        className="mt-2 text-sm text-primary hover:underline"
      >
        {t["nav.back"]}
      </Link>
    </main>
  );
}
