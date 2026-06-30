"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";
import type { Locale } from "@/lib/i18n";

export function LocaleSwitch({ current }: { current: Locale }) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  function switchTo(locale: Locale) {
    if (locale === current) return;
    document.cookie = `locale=${locale}; path=/; max-age=31536000; samesite=lax`;
    startTransition(() => {
      router.refresh();
    });
  }

  return (
    <div
      className="flex overflow-hidden rounded-md border border-zinc-200 bg-white text-xs dark:border-zinc-700 dark:bg-zinc-900"
      role="group"
      aria-label="Language"
    >
      <button
        type="button"
        onClick={() => switchTo("es")}
        aria-pressed={current === "es"}
        disabled={isPending}
        className={
          "px-2 py-1 font-medium transition-colors " +
          (current === "es"
            ? "bg-primary text-white"
            : "text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800")
        }
      >
        ES
      </button>
      <button
        type="button"
        onClick={() => switchTo("en")}
        aria-pressed={current === "en"}
        disabled={isPending}
        className={
          "border-l border-zinc-200 px-2 py-1 font-medium transition-colors dark:border-zinc-700 " +
          (current === "en"
            ? "bg-primary text-white"
            : "text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800")
        }
      >
        EN
      </button>
    </div>
  );
}
