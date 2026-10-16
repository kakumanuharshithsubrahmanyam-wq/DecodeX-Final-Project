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
import { getAccessToken, getSupabase, onAuthStateChange } from '@/lib/auth';
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
    setProfileStatus('loading');
    try {
      let token: string | null = null;
      for (let i = 0; i < 8 && reqId === profileReq.current; i += 1) {
        token = await getAccessToken();
        if (token) break;
        await new Promise((r) => setTimeout(r, 150));
      }
      if (!token) {
        if (reqId === profileReq.current) {
          setProfile(null);
          setProfileStatus(session ? 'error' : 'idle');
        }
        return;
      }
      const res = await api.me();
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
      setSession(data.session);
      setStatus(data.session ? 'authenticated' : 'guest');
    });
    const sub = onAuthStateChange((s) => {
      setSession(s);
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
  const liveApi = canUseLiveApi(Boolean(session));

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
