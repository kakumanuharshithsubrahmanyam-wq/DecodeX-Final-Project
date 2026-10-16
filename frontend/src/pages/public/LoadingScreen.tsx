import { useI18n } from '@/i18n';

export function LoadingScreen() {
  const { t } = useI18n();
  return (
    <div className="auth-screen" role="status" aria-live="polite">
      <p>{t('auth.loading')}</p>
    </div>
  );
}
