"use client";

import { useEffect, useState } from "react";

interface ThemeToggleProps {
  toggleLabel: string;
}

export function ThemeToggle({ toggleLabel }: ThemeToggleProps) {
  const [isDark, setIsDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setIsDark(document.documentElement.classList.contains("dark"));
  }, []);

  function toggle() {
    const newIsDark = document.documentElement.classList.toggle("dark");
    localStorage.setItem("theme", newIsDark ? "dark" : "light");
    setIsDark(newIsDark);
  }

  return (
    <button
      type="button"
      role="switch"
      aria-checked={mounted ? isDark : false}
      aria-label={toggleLabel}
      onClick={toggle}
      suppressHydrationWarning
      className={
        "relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 " +
        (isDark ? "bg-primary" : "bg-zinc-200 dark:bg-zinc-700")
      }
    >
      <span
        aria-hidden="true"
        className={
          "pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition-transform " +
          (isDark ? "translate-x-6" : "translate-x-1")
        }
      />
    </button>
  );
}
