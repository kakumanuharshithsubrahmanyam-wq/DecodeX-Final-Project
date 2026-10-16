import { useState, type FormEvent } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import { LoadingScreen } from '@/pages/public/LoadingScreen';
import { useAuth } from '@/auth/AuthContext';
import { canAccessPath, workspaceHome } from '@/auth/roles';
import { useI18n } from '@/i18n';
import { isSupabaseConfigured } from '@/lib/config';
import { signInWithPassword } from '@/lib/auth';

export function LoginPage() {
  const { t } = useI18n();
  const auth = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const rawFrom = (location.state as { from?: string } | null)?.from;
  const home = workspaceHome(auth.workspace);
  const from =
    rawFrom && rawFrom !== '/login' && rawFrom !== '/register' && rawFrom !== '/forgot-password'
      ? rawFrom
      : home;
  const dest = auth.profileStatus === 'ready' && canAccessPath(auth.workspace, from) ? from : home;
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (auth.status === 'loading' || (auth.status === 'authenticated' && (auth.profileStatus === 'idle' || auth.profileStatus === 'loading'))) {
    return <LoadingScreen />;
  }
  if (auth.status === 'authenticated' && auth.profileStatus === 'ready') {
    return <Navigate to={dest} replace />;
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
    navigate(dest, { replace: true });
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
        {auth.profileStatus === 'error' && (
          <div className="error-banner" role="alert">
            {t('auth.profileError')}
          </div>
        )}
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
