import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/auth/AuthContext';
import { GrievanceProvider } from '@/data/GrievanceContext';
import { useI18n } from '@/i18n';
import RtgsPortal from '@/RtgsPortal';
import { ForgotPasswordPage } from '@/pages/public/ForgotPasswordPage';
import { LoadingScreen } from '@/pages/public/LoadingScreen';
import { LoginPage } from '@/pages/public/LoginPage';
import { RegisterPage } from '@/pages/public/RegisterPage';
import { UnauthorizedPage } from '@/pages/public/UnauthorizedPage';

function ProfileErrorScreen() {
  const { t } = useI18n();
  const auth = useAuth();
  return (
    <div className="auth-screen">
      <div className="auth-card panel empty-state">
        <h1>{t('auth.profileError')}</h1>
        <button type="button" className="btn btn-primary" onClick={() => void auth.refreshProfile()}>
          {t('auth.retry')}
        </button>
        <button type="button" className="btn btn-outline" onClick={() => void auth.signOut()}>
          {t('nav.signOut')}
        </button>
      </div>
    </div>
  );
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  const location = useLocation();
  if (auth.status === 'loading') return <LoadingScreen />;
  if (auth.status === 'guest') {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  if (auth.profileStatus === 'loading' || auth.profileStatus === 'idle') {
    return <LoadingScreen />;
  }
  if (auth.profileStatus === 'error') {
    return <ProfileErrorScreen />;
  }
  return <GrievanceProvider>{children}</GrievanceProvider>;
}

export default function App() {
  const { pathname } = useLocation();
  if (pathname === '/login') return <LoginPage />;
  if (pathname === '/register') return <RegisterPage />;
  if (pathname === '/forgot-password') return <ForgotPasswordPage />;
  if (pathname === '/unauthorized') return <UnauthorizedPage />;
  return (
    <RequireAuth>
      <RtgsPortal />
    </RequireAuth>
  );
}
