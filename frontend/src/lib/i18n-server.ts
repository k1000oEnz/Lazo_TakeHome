import { cache } from "react";
import { cookies } from "next/headers";
import {
  DEFAULT_LOCALE,
  getDictionary,
  isLocale,
  type Dictionary,
  type Locale,
} from "./i18n";

export const getRequestLocale = cache(async (): Promise<Locale> => {
  const store = await cookies();
  const value = store.get("locale")?.value;
  return isLocale(value) ? value : DEFAULT_LOCALE;
});

export const getRequestDictionary = cache(async (): Promise<Dictionary> => {
  const locale = await getRequestLocale();
  return getDictionary(locale);
});
