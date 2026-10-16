export function isSupabaseConfigured(): boolean {
  const url = import.meta.env.VITE_SUPABASE_URL as string | undefined;
  const key = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;
  return Boolean(url && key && !url.includes('YOUR_PROJECT'));
}

export function isApiConfigured(): boolean {
  const base = import.meta.env.VITE_API_BASE_URL as string | undefined;
  return Boolean(base && base.startsWith('http'));
}

/** Explicit demo dataset — never mixed with live API grievances */
export function isExplicitDemoMode(): boolean {
  if (import.meta.env.VITE_DEMO_MODE !== 'true') return false;
  const appEnv = (import.meta.env.VITE_APP_ENV as string | undefined)?.toLowerCase();
  if (appEnv === 'production') {
    console.error('VITE_DEMO_MODE must not be enabled when VITE_APP_ENV=production.');
    return false;
  }
  return true;
}

/** True when the signed-in user should load grievances from the FastAPI backend (not demo seed). */
export function canUseLiveApi(authenticatedWithProfile: boolean): boolean {
  return isSupabaseConfigured() && isApiConfigured() && authenticatedWithProfile && !isExplicitDemoMode();
}
