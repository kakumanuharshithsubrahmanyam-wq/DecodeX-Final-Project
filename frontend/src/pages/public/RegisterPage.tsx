import { useState, type FormEvent } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import { useAuth } from '@/auth/AuthContext';
import { workspaceHome } from '@/auth/roles';
import { useI18n } from '@/i18n';
import { isSupabaseConfigured } from '@/lib/config';
import { signUpCitizen } from '@/lib/auth';

export function RegisterPage() {
  const { t } = useI18n();
  const auth = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (auth.status === 'authenticated') {
    return <Navigate to={workspaceHome(auth.workspace)} replace />;
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    if (password.length < 8) {
      setError(t('auth.errors.weakPassword'));
      return;
    }
    if (!isSupabaseConfigured()) {
      setError(t('mode.offline'));
      return;
    }
    setBusy(true);
    const { error: err } = await signUpCitizen(email.trim(), password, fullName.trim() || undefined);
    setBusy(false);
    if (err) {
      setError(err.message.includes('registered') ? t('auth.errors.emailInUse') : t('auth.errors.generic'));
      return;
    }
    setMessage(t('auth.signInDesc'));
  };

  return (
    <div className="auth-screen">
      <div className="auth-card panel">
        <div className="auth-brand">
          <ShieldCheck size={28} aria-hidden />
          <div>
            <b>{t('brand.title')}</b>
          </div>
        </div>
        <h1>{t('auth.registerTitle')}</h1>
        <p>{t('auth.registerDesc')}</p>
        <form onSubmit={onSubmit} noValidate>
          <label className="field-label">
            {t('auth.fullName')}
            <input type="text" autoComplete="name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </label>
          <label className="field-label">
            {t('auth.email')} <em>*</em>
            <input type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <label className="field-label">
            {t('auth.password')} <em>*</em>
            <input
              type="password"
              autoComplete="new-password"
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
          {message && (
            <div className="success-banner" role="status">
              {message}
            </div>
          )}
          <button type="submit" className="btn btn-primary full-width" disabled={busy}>
            {t('auth.registerButton')}
          </button>
        </form>
        <p className="auth-links">
          <Link to="/login">{t('auth.backToSignIn')}</Link>
        </p>
      </div>
    </div>
  );
}
