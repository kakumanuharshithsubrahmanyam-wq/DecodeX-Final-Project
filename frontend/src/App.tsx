import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { useAuth } from '@/auth/AuthContext';
import { GrievanceProvider } from '@/data/GrievanceContext';
import { useI18n } from '@/i18n';
import RtgsPortal from '@/RtgsPortal';
import { ForgotPasswordPage } from '@/pages/public/ForgotPasswordPage';
import { LoginPage } from '@/pages/public/LoginPage';
import { RegisterPage } from '@/pages/public/RegisterPage';
import { UnauthorizedPage } from '@/pages/public/UnauthorizedPage';

function LoadingScreen() {
  const { t } = useI18n();
  return (
    <div className="auth-screen" role="status" aria-live="polite">
      <p>{t('auth.loading')}</p>
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
    return <Navigate to="/login" replace state={{ reason: 'profile' }} />;
  }
  return <GrievanceProvider>{children}</GrievanceProvider>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      <Route
        path="/*"
        element={
          <RequireAuth>
            <RtgsPortal />
          </RequireAuth>
        }
      />
    </Routes>
  );
}
