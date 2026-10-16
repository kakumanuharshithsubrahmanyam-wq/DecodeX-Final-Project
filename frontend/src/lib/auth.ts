/**
 * Supabase Auth session helper for browser use (anon/publishable key only).
 * Requires @supabase/supabase-js once Claude's app adds package.json.
 */
import { createClient, SupabaseClient, Session } from '@supabase/supabase-js';

let client: SupabaseClient | null = null;

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

export async function getAccessToken(): Promise<string | null> {
  const supabase = getSupabase();
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? null;
}

export function onAuthStateChange(cb: (session: Session | null) => void) {
  return getSupabase().auth.onAuthStateChange((_event, session) => cb(session));
}
