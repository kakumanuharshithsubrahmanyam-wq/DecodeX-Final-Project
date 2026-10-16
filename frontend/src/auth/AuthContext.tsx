import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import type { Session } from '@supabase/supabase-js';
import { api } from '@/lib/api-client';
import type { MeProfile } from '@/lib/types';
import { getAccessToken, getSupabase, onAuthStateChange, rememberSession } from '@/lib/auth';
import { canUseLiveApi, isExplicitDemoMode, isSupabaseConfigured } from '@/lib/config';
import { mapApiRoleToWorkspace, normalizeApiRole, type WorkspaceKind } from '@/auth/roles';

export type AuthStatus = 'loading' | 'guest' | 'authenticated';

export type ProfileStatus = 'idle' | 'loading' | 'ready' | 'error';

type AuthContextValue = {
  status: AuthStatus;
  profileStatus: ProfileStatus;
  session: Session | null;
  profile: MeProfile | null;
  workspace: WorkspaceKind;
  apiRole: string | null;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  supabaseReady: boolean;
  liveApi: boolean;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [profileStatus, setProfileStatus] = useState<ProfileStatus>('idle');
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<MeProfile | null>(null);
  const supabaseReady = isSupabaseConfigured();
  const profileReq = useRef(0);

  const refreshProfile = useCallback(async () => {
    if (!session && !isExplicitDemoMode()) {
      setProfile(null);
      setProfileStatus('idle');
      return;
    }
    if (isExplicitDemoMode() && !session) {
      setProfile({
        id: '00000000-0000-4000-8000-000000000001',
        email: 'demo@rtgs.local',
        full_name: 'Demo Citizen',
        phone: null,
        role: 'citizen',
        permissions: ['grievance:create', 'grievance:read_own'],
        department_ids: [],
        locale: 'en',
      });
      setProfileStatus('ready');
      return;
    }
    const reqId = ++profileReq.current;
    setProfileStatus((s) => (s === 'ready' ? s : 'loading'));
    try {
      rememberSession(session);
      const token = session?.access_token ?? (await getAccessToken());
      if (!token) {
        if (reqId === profileReq.current) {
          setProfile(null);
          setProfileStatus(session ? 'error' : 'idle');
        }
        return;
      }
      await api.health().catch(() => undefined);
      if (reqId !== profileReq.current) return;
      let res: Awaited<ReturnType<typeof api.me>> | null = null;
      let lastErr: unknown;
      for (let attempt = 0; attempt < 2; attempt += 1) {
        try {
          res = await api.me();
          lastErr = undefined;
          break;
        } catch (e) {
          lastErr = e;
        }
      }
      if (!res) throw lastErr;
      if (reqId !== profileReq.current) return;
      const role = normalizeApiRole(res.data.role);
      if (!role) {
        setProfile(null);
        setProfileStatus('error');
        return;
      }
      setProfile(res.data);
      setProfileStatus('ready');
    } catch {
      if (reqId !== profileReq.current) return;
      setProfile(null);
      setProfileStatus('error');
    }
  }, [session]);

  useEffect(() => {
    if (!supabaseReady) {
      if (isExplicitDemoMode()) {
        setStatus('authenticated');
        setSession(null);
        void refreshProfile();
      } else {
        setStatus('guest');
        setProfile(null);
        setProfileStatus('idle');
      }
      return;
    }
    const supabase = getSupabase();
    supabase.auth.getSession().then(({ data }) => {
      rememberSession(data.session);
      setSession((prev) => (prev?.access_token === data.session?.access_token ? prev : data.session));
      setStatus(data.session ? 'authenticated' : 'guest');
    });
    const sub = onAuthStateChange((s) => {
      rememberSession(s);
      setSession((prev) => (prev?.access_token === s?.access_token ? prev : s));
      setStatus(s ? 'authenticated' : 'guest');
    });
    return () => sub.data.subscription.unsubscribe();
  }, [supabaseReady]);

  useEffect(() => {
    if (status === 'authenticated') {
      void refreshProfile();
    } else if (status === 'guest') {
      setProfile(null);
      setProfileStatus('idle');
    }
  }, [status, session, refreshProfile]);

  const signOut = useCallback(async () => {
    if (supabaseReady) {
      await getSupabase().auth.signOut();
    }
    setSession(null);
    setProfile(null);
    setProfileStatus('idle');
    setStatus('guest');
  }, [supabaseReady]);

  const workspace = mapApiRoleToWorkspace(profile?.role);
  const liveApi = canUseLiveApi(status === 'authenticated' && profileStatus === 'ready');

  const value = useMemo(
    () => ({
      status,
      profileStatus,
      session,
      profile,
      workspace,
      apiRole: profile?.role ?? null,
      signOut,
      refreshProfile,
      supabaseReady,
      liveApi,
    }),
    [status, profileStatus, session, profile, workspace, signOut, refreshProfile, supabaseReady, liveApi],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

/** Re-export for legacy imports */
export { mapApiRoleToWorkspace } from '@/auth/roles';
