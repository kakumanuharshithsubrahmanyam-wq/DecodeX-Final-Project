import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useI18n } from '@/i18n';
import { isSupabaseConfigured } from '@/lib/config';
import { sendPasswordReset } from '@/lib/auth';

export function ForgotPasswordPage() {
  const { t } = useI18n();
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (!isSupabaseConfigured()) {
      setError(t('mode.offline'));
      return;
    }
    setBusy(true);
    const { error: err } = await sendPasswordReset(email.trim());
    setBusy(false);
    if (err) {
      setError(t('auth.errors.generic'));
      return;
    }
    setSent(true);
  };

  return (
    <div className="auth-screen">
      <div className="auth-card panel">
        <h1>{t('auth.forgotTitle')}</h1>
        <p>{t('auth.forgotDesc')}</p>
        {sent ? (
          <div className="success-banner" role="status">
            {t('auth.forgotDesc')}
          </div>
        ) : (
          <form onSubmit={onSubmit}>
            <label className="field-label">
              {t('auth.email')}
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
            {error && <div className="error-banner">{error}</div>}
            <button type="submit" className="btn btn-primary full-width" disabled={busy}>
              {t('auth.forgotButton')}
            </button>
          </form>
        )}
        <p className="auth-links">
          <Link to="/login">{t('auth.backToSignIn')}</Link>
        </p>
      </div>
    </div>
  );
}
