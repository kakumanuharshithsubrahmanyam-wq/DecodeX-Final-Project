import { describe, expect, it } from 'vitest';
import en from './en';
import te from './te';
import { allTranslationKeys } from './index';

describe('i18n dictionaries', () => {
  it('has matching keys in English and Telugu', () => {
    const enKeys = allTranslationKeys(en as unknown as Record<string, unknown>).sort();
    const teKeys = allTranslationKeys(te as unknown as Record<string, unknown>).sort();
    expect(teKeys).toEqual(enKeys);
  });

  it('includes critical navigation and auth keys', () => {
    const keys = allTranslationKeys(en as unknown as Record<string, unknown>);
    for (const key of ['nav.fileComplaint', 'nav.signIn', 'auth.registerTitle', 'help.faq.q1']) {
      expect(keys).toContain(key);
    }
  });

  it('includes portal workflow keys in both languages', () => {
    const keys = allTranslationKeys(en as unknown as Record<string, unknown>);
    for (const key of [
      'portal.landing.fileBtn',
      'portal.submit.title',
      'portal.track.title',
      'portal.dataSource.community',
      'chat.botDefault',
    ]) {
      expect(keys).toContain(key);
    }
    expect(en.portal.landing.fileBtn).toBeTruthy();
    expect(te.portal.landing.fileBtn).toBeTruthy();
    expect(en.portal.landing.fileBtn).not.toEqual(te.portal.landing.fileBtn);
  });
});
