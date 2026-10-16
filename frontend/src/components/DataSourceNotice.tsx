import { useI18n } from '@/i18n';
import type { DataMode } from '@/data/GrievanceContext';
import { AlertTriangle, Database, Wifi } from 'lucide-react';

type Variant = 'demo' | 'live' | 'localOnly' | 'unavailable' | 'illustrativeChart' | 'community' | 'chatbot' | 'sla';

const messageKey: Record<Variant, `portal.dataSource.${Variant}`> = {
  demo: 'portal.dataSource.demo',
  live: 'portal.dataSource.live',
  localOnly: 'portal.dataSource.localOnly',
  unavailable: 'portal.dataSource.unavailable',
  illustrativeChart: 'portal.dataSource.illustrativeChart',
  community: 'portal.dataSource.community',
  chatbot: 'portal.dataSource.chatbot',
  sla: 'portal.dataSource.sla',
};

export function DataSourceNotice({ variant }: { variant: Variant }) {
  const { t } = useI18n();
  const Icon = variant === 'live' ? Wifi : variant === 'unavailable' ? AlertTriangle : Database;
  return (
    <p className="data-source-notice" role="note">
      <Icon size={14} aria-hidden />
      {t(messageKey[variant])}
    </p>
  );
}

export function dataModeVariant(mode: DataMode): Variant {
  if (mode === 'live') return 'live';
  if (mode === 'demo') return 'demo';
  return 'unavailable';
}
