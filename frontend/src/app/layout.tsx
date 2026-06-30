import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { getDictionary } from "@/lib/i18n";
import { getRequestLocale } from "@/lib/i18n-server";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LocaleSwitch } from "@/components/LocaleSwitch";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const themeInitScript = `(function() {
  try {
    var theme = localStorage.getItem('theme');
    if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    }
  } catch (e) {}
})();`;

export const metadata: Metadata = {
  title: "Compliance Obligations Tracker",
  description: "Track compliance obligations: state, due dates, documents, history.",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getRequestLocale();
  const t = getDictionary(locale);

  return (
    <html
      lang={locale}
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className="min-h-full flex flex-col bg-white text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50">
        <header className="flex items-center justify-between border-b border-zinc-200 bg-white px-6 py-3 dark:border-zinc-800 dark:bg-zinc-950">
          <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
            {t["app.title"]}
          </h1>
          <div className="flex items-center gap-3">
            <LocaleSwitch current={locale} />
            <ThemeToggle toggleLabel={t["theme.toggle"]} />
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
