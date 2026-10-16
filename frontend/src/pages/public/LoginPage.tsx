import { useState, type FormEvent } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import { useAuth } from '@/auth/AuthContext';
import { useI18n } from '@/i18n';
import { isSupabaseConfigured } from '@/lib/config';
import { signInWithPassword } from '@/lib/auth';

export function LoginPage() {
  const { t } = useI18n();
  const auth = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from ?? '/dashboard';
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (auth.status === 'authenticated') {
    return <Navigate to={from} replace />;
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (!isSupabaseConfigured()) {
      setError(t('mode.offline'));
      return;
    }
    setBusy(true);
    const { error: err } = await signInWithPassword(email.trim(), password);
    setBusy(false);
    if (err) {
      setError(t('auth.errors.invalidCredentials'));
      return;
    }
    navigate(from, { replace: true });
  };

  return (
    <div className="auth-screen">
      <div className="auth-card panel">
        <div className="auth-brand">
          <ShieldCheck size={28} aria-hidden />
          <div>
            <b>{t('brand.title')}</b>
            <small>{t('brand.tagline')}</small>
          </div>
        </div>
        <h1>{t('auth.signInTitle')}</h1>
        <p>{t('auth.signInDesc')}</p>
        <form onSubmit={onSubmit} noValidate>
          <label className="field-label">
            {t('auth.email')}
            <input
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
          <label className="field-label">
            {t('auth.password')}
            <input
              type="password"
              autoComplete="current-password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          {error && (
            <div className="error-banner" role="alert">
              {error}
            </div>
          )}
          <button type="submit" className="btn btn-primary full-width" disabled={busy}>
            {t('auth.signInButton')}
          </button>
        </form>
        <p className="auth-links">
          <Link to="/forgot-password">{t('auth.forgotTitle')}</Link>
          <Link to="/register">{t('nav.signUp')}</Link>
        </p>
      </div>
    </div>
  );
}
