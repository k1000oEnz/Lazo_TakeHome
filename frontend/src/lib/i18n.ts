import en from "./dictionaries/en.json";
import es from "./dictionaries/es.json";

export type Locale = "es" | "en";

export const DEFAULT_LOCALE: Locale = "es";
export const LOCALES: ReadonlyArray<Locale> = ["es", "en"];

const dictionaries: Record<Locale, Dictionary> = { es, en };

export type Dictionary = typeof es;

export function getDictionary(locale: Locale): Dictionary {
  return dictionaries[locale] ?? dictionaries[DEFAULT_LOCALE];
}

export function isLocale(value: string | undefined): value is Locale {
  return (LOCALES as ReadonlyArray<string>).includes(value ?? "");
}
