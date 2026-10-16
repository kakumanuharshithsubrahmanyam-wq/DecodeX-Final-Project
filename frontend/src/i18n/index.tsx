import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import en, { type TranslationDict } from './en';
import te from './te';

export type Locale = 'en' | 'te';

const STORAGE_KEY = 'rtgs-locale';

type NestedKeyOf<T, Prefix extends string = ''> = T extends object
  ? {
      [K in keyof T & string]: T[K] extends object
        ? NestedKeyOf<T[K], `${Prefix}${K}.`>
        : `${Prefix}${K}`;
    }[keyof T & string]
  : never;

export type TranslationKey = NestedKeyOf<TranslationDict>;

function getNested(obj: Record<string, unknown>, path: string): string {
  const parts = path.split('.');
  let cur: unknown = obj;
  for (const p of parts) {
    if (cur && typeof cur === 'object' && p in (cur as object)) {
      cur = (cur as Record<string, unknown>)[p];
    } else {
      if (import.meta.env.DEV) {
        console.warn(`Missing translation key: ${path}`);
      }
      return path;
    }
  }
  return typeof cur === 'string' ? cur : path;
}

type I18nContextValue = {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: TranslationKey) => string;
  formatDate: (iso: string) => string;
  formatNumber: (n: number) => string;
};

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'te' ? 'te' : 'en';
  });

  const dict = locale === 'te' ? te : en;

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    localStorage.setItem(STORAGE_KEY, l);
  }, []);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const t = useCallback((key: TranslationKey) => getNested(dict as unknown as Record<string, unknown>, key), [dict]);

  const formatDate = useCallback(
    (iso: string) => {
      try {
        return new Intl.DateTimeFormat(locale === 'te' ? 'te-IN' : 'en-IN', {
          dateStyle: 'medium',
        }).format(new Date(iso));
      } catch {
        return iso.slice(0, 10);
      }
    },
    [locale],
  );

  const formatNumber = useCallback(
    (n: number) => new Intl.NumberFormat(locale === 'te' ? 'te-IN' : 'en-IN').format(n),
    [locale],
  );

  const value = useMemo(
    () => ({ locale, setLocale, t, formatDate, formatNumber }),
    [locale, setLocale, t, formatDate, formatNumber],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
}

/** Collect all string leaf keys for tests */
export function allTranslationKeys(obj: Record<string, unknown>, prefix = ''): string[] {
  const keys: string[] = [];
  for (const [k, v] of Object.entries(obj)) {
    const p = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      keys.push(...allTranslationKeys(v as Record<string, unknown>, p));
    } else if (typeof v === 'string') {
      keys.push(p);
    }
  }
  return keys;
}

export { en, te };
