import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { useAuth } from '@/auth/AuthContext';
import { api } from '@/lib/api-client';
import { canUseLiveApi, isExplicitDemoMode } from '@/lib/config';
import { detailToUi, summaryToUi, type UiGrievance } from '@/lib/grievance-mapper';
import { seedData, seedNotices, type Notice } from '@/demo/seed';

export type DataMode = 'live' | 'demo' | 'empty';

type GrievanceContextValue = {
  mode: DataMode;
  loading: boolean;
  error: string | null;
  grievances: UiGrievance[];
  notices: Notice[];
  refresh: () => Promise<void>;
  update: (id: string, patch: Partial<UiGrievance>, message?: string) => Promise<void>;
  add: (g: UiGrievance) => Promise<void>;
  resetDemo: () => void;
  setNotices: React.Dispatch<React.SetStateAction<Notice[]>>;
};

const GrievanceContext = createContext<GrievanceContextValue | null>(null);

const GrievanceContextProvider = GrievanceContext.Provider;

export function GrievanceProvider({ children }: { children: ReactNode }) {
  const auth = useAuth();
  const live = canUseLiveApi(Boolean(auth.session));
  const demoOnly = isExplicitDemoMode() || !live;

  const [mode, setMode] = useState<DataMode>(demoOnly ? 'demo' : 'empty');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [grievances, setGrievances] = useState<UiGrievance[]>(() => (demoOnly ? seedData : []));
  const [notices, setNotices] = useState<Notice[]>(() => (demoOnly ? seedNotices : []));

  const citizenLabel = auth.profile?.full_name ?? auth.profile?.email ?? 'Citizen';

  const refresh = useCallback(async () => {
    if (demoOnly) {
      setMode('demo');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await api.listGrievances({ page: 1, page_size: 100 });
      setGrievances(res.data.map((g) => summaryToUi(g, citizenLabel)));
      setMode('live');
      const n = await api.notifications(1);
      setNotices(
        n.data.map((item, i) => ({
          id: i + 1,
          title: item.title,
          body: item.body,
          time: item.created_at,
          read: Boolean(item.read_at),
        })),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load complaints');
      setGrievances([]);
      setMode('empty');
    } finally {
      setLoading(false);
    }
  }, [demoOnly, citizenLabel]);

  useEffect(() => {
    if (auth.status === 'loading') return;
    if (live) void refresh();
    else if (demoOnly) {
      setGrievances(seedData);
      setNotices(seedNotices);
      setMode('demo');
    } else {
      setGrievances([]);
      setNotices([]);
      setMode('empty');
    }
  }, [auth.status, live, demoOnly, refresh]);

  const update = useCallback(
    async (id: string, patch: Partial<UiGrievance>, message?: string) => {
      if (mode === 'live') {
        const g = grievances.find((x) => x.id === id || x.uuid === id);
        if (g?.uuid && patch.status) {
          const { statusToApi } = await import('@/lib/grievance-mapper');
          await api.transition(g.uuid, statusToApi(patch.status), message);
          await refresh();
        }
        return;
      }
      setGrievances((old) =>
        old.map((g) =>
          g.id === id
            ? { ...g, ...patch, remarks: message ? [...g.remarks, message] : g.remarks }
            : g,
        ),
      );
      setNotices((old) => [
        {
          id: Date.now(),
          title: 'Complaint updated',
          body: `${id}: ${message ?? patch.status ?? 'Updated'}`,
          time: 'Just now',
          read: false,
        },
        ...old,
      ]);
    },
    [mode, grievances, refresh],
  );

  const add = useCallback(
    async (g: UiGrievance) => {
      if (mode === 'live') {
        await refresh();
        return;
      }
      setGrievances((old) => [g, ...old]);
      setNotices((old) => [
        {
          id: Date.now(),
          title: 'Complaint submitted',
          body: `${g.id} saved in demo mode.`,
          time: 'Just now',
          read: false,
        },
        ...old,
      ]);
    },
    [mode, refresh],
  );

  const resetDemo = useCallback(() => {
    if (mode !== 'demo') return;
    setGrievances(seedData);
    setNotices(seedNotices);
  }, [mode]);

  const value = useMemo(
    () => ({
      mode,
      loading,
      error,
      grievances,
      notices,
      refresh,
      update,
      add,
      resetDemo,
      setNotices,
    }),
    [mode, loading, error, grievances, notices, refresh, update, add, resetDemo],
  );

  return <GrievanceContextProvider value={value}>{children}</GrievanceContextProvider>;
}

export function useGrievanceData(): GrievanceContextValue {
  const ctx = useContext(GrievanceContext);
  if (!ctx) throw new Error('useGrievanceData must be used within GrievanceProvider');
  return ctx;
}

export async function createLiveGrievance(input: {
  title: string;
  description: string;
  location: string;
}): Promise<UiGrievance> {
  const res = await api.createGrievance({
    title: input.title,
    description: input.description,
    location_text: input.location,
  });
  return detailToUi(res.data, [], 'You');
}
