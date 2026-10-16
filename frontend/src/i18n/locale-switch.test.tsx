import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { I18nProvider, useI18n } from './index';

beforeEach(() => {
  const store: Record<string, string> = {};
  vi.stubGlobal('localStorage', {
    getItem: (k: string) => store[k] ?? null,
    setItem: (k: string, v: string) => {
      store[k] = v;
    },
    removeItem: (k: string) => {
      delete store[k];
    },
  });
});

function LocaleProbe() {
  const { t, locale, setLocale } = useI18n();
  return (
    <div>
      <span data-testid="submit-title">{t('portal.submit.title')}</span>
      <span data-testid="locale">{locale}</span>
      <button type="button" onClick={() => setLocale(locale === 'en' ? 'te' : 'en')}>
        toggle
      </button>
    </div>
  );
}

describe('locale switching', () => {
  it('updates visible portal strings without reload', () => {
    render(
      <I18nProvider>
        <LocaleProbe />
      </I18nProvider>,
    );
    const title = screen.getByTestId('submit-title');
    expect(title.textContent).toMatch(/complaint|ఫిర్యాదు/i);
    fireEvent.click(screen.getByText('toggle'));
    expect(screen.getByTestId('locale').textContent).toBe('te');
    expect(title.textContent).toContain('ఫిర్యాదు');
  });
});
