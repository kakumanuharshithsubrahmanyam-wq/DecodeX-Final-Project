import { Link } from 'react-router-dom';
import { useI18n } from '@/i18n';

export function UnauthorizedPage() {
  const { t } = useI18n();
  return (
    <div className="auth-screen">
      <div className="auth-card panel empty-state">
        <h1>{t('auth.unauthorized')}</h1>
        <Link className="btn btn-primary" to="/dashboard">
          {t('nav.overview')}
        </Link>
      </div>
    </div>
  );
}
