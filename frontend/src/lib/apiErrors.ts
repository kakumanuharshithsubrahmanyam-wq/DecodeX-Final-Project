import type { TranslationKey } from '@/i18n';
import { ApiError } from '@/lib/api-client';

const codeToKey: Record<string, TranslationKey> = {
  UNAUTHORIZED: 'errors.api.UNAUTHORIZED',
  FORBIDDEN: 'errors.api.FORBIDDEN',
  NOT_FOUND: 'errors.api.NOT_FOUND',
  VALIDATION_ERROR: 'errors.api.VALIDATION_ERROR',
  INTERNAL_ERROR: 'errors.api.INTERNAL_ERROR',
};

export function localizedApiError(t: (key: TranslationKey) => string, err: unknown): string {
  if (err instanceof ApiError) {
    const key = codeToKey[err.code];
    if (key) {
      const msg = t(key);
      if (msg !== key) return msg;
    }
    if (err.message && import.meta.env.DEV) return err.message;
  }
  if (err instanceof Error && err.message && import.meta.env.DEV) return err.message;
  return t('errors.api.generic');
}
