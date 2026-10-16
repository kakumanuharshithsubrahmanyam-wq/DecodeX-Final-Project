/**
 * Supabase Auth session helper for browser use (anon/publishable key only).
 * Requires @supabase/supabase-js once Claude's app adds package.json.
 */
import { createClient, type Session, type SupabaseClient } from '@supabase/supabase-js';

let client: SupabaseClient | null = null;
let memoryToken: string | null = null;

export function getSupabase(): SupabaseClient {
  if (client) return client;
  const url = import.meta.env.VITE_SUPABASE_URL as string;
  const anon = import.meta.env.VITE_SUPABASE_ANON_KEY as string;
  if (!url || !anon) {
    throw new Error('VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must be set');
  }
  client = createClient(url, anon);
  return client;
}

export function rememberSession(session: Session | null) {
  memoryToken = session?.access_token ?? null;
}

export async function getAccessToken(): Promise<string | null> {
  if (memoryToken) return memoryToken;
  const supabase = getSupabase();
  const { data } = await supabase.auth.getSession();
  rememberSession(data.session);
  return memoryToken;
}

export function onAuthStateChange(cb: (session: Session | null) => void) {
  return getSupabase().auth.onAuthStateChange((_event, session) => {
    rememberSession(session);
    cb(session);
  });
}

export async function signInWithPassword(email: string, password: string) {
  return getSupabase().auth.signInWithPassword({ email, password });
}

export async function signUpCitizen(email: string, password: string, fullName?: string) {
  return getSupabase().auth.signUp({
    email,
    password,
    options: {
      data: fullName ? { full_name: fullName } : undefined,
    },
  });
}

export async function sendPasswordReset(email: string) {
  const redirectTo = `${window.location.origin}/login`;
  return getSupabase().auth.resetPasswordForEmail(email, { redirectTo });
}

export async function signOut() {
  return getSupabase().auth.signOut();
}
