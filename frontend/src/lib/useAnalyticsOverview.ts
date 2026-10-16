import { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { useAuth } from '@/auth/AuthContext';

export type AnalyticsOverview = {
  total_grievances: number;
  pending_grievances: number;
  in_progress_grievances: number;
  overdue_count: number;
  resolved_grievances: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  sla_compliance_rate: number | null;
  department_workload: { department_id: string; open_count: number; overdue_count: number }[];
};

export function useAnalyticsOverview(enabled: boolean) {
  const auth = useAuth();
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!enabled || !auth.liveApi) {
      setData(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .analyticsOverview()
      .then((res) => {
        if (!cancelled) setData(res.data as AnalyticsOverview);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load analytics');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [enabled, auth.liveApi]);

  return { data, error, loading, isLive: auth.liveApi };
}
