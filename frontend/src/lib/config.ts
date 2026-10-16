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
  return import.meta.env.VITE_DEMO_MODE === 'true';
}

export function canUseLiveApi(sessionPresent: boolean): boolean {
  return isSupabaseConfigured() && isApiConfigured() && sessionPresent && !isExplicitDemoMode();
}
