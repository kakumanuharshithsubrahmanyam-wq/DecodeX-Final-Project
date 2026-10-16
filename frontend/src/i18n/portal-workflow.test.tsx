import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
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

function WorkflowProbe({ dialogOpen }: { dialogOpen: boolean }) {
  const { t, locale, setLocale } = useI18n();
  return (
    <div>
      <span data-testid="submit-title">{t('portal.submit.sectionTitle')}</span>
      <span data-testid="track-title">{t('portal.track.title')}</span>
      <span data-testid="officer-title">{t('portal.officer.reviewTitle')}</span>
      <span data-testid="locale">{locale}</span>
      {dialogOpen && (
        <div role="dialog" aria-label={t('portal.officer.reviewTitle')}>
          <span data-testid="dialog-body">{t('portal.officer.flaggedHint')}</span>
        </div>
      )}
      <button type="button" onClick={() => setLocale(locale === 'en' ? 'te' : 'en')}>
        toggle-lang
      </button>
    </div>
  );
}

describe('portal workflow localization', () => {
  it('renders English and Telugu strings for submit, track, and officer flows', () => {
    render(
      <I18nProvider>
        <WorkflowProbe dialogOpen={false} />
      </I18nProvider>,
    );
    expect(screen.getByTestId('submit-title').textContent).toMatch(/report|నమోదు/i);
    expect(screen.getByTestId('track-title').textContent).toMatch(/Complaint|ఫిర్యాదు/i);
    expect(screen.getByTestId('officer-title').textContent).toMatch(/review|సమీక్ష/i);

    fireEvent.click(screen.getByText('toggle-lang'));
    expect(screen.getByTestId('locale').textContent).toBe('te');
    expect(screen.getByTestId('submit-title').textContent).toContain('నమోదు');
    expect(screen.getByTestId('track-title').textContent).toContain('ఫిర్యాదు');
  });

  it('updates open dialog copy when language changes', () => {
    render(
      <I18nProvider>
        <WorkflowProbe dialogOpen />
      </I18nProvider>,
    );
    const dialogBody = screen.getByTestId('dialog-body');
    const enText = dialogBody.textContent ?? '';
    fireEvent.click(screen.getByText('toggle-lang'));
    expect(dialogBody.textContent).not.toBe(enText);
    expect(dialogBody.textContent?.length).toBeGreaterThan(5);
  });

  it('persists locale preference in localStorage', () => {
    render(
      <I18nProvider>
        <WorkflowProbe dialogOpen={false} />
      </I18nProvider>,
    );
    fireEvent.click(screen.getByText('toggle-lang'));
    expect(localStorage.getItem('rtgs-locale')).toBe('te');
  });
});
