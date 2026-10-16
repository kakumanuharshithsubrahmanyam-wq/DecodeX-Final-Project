import type { TranslationKey } from './index';

const uiStatusKeys: Record<string, TranslationKey> = {
  Submitted: 'status.submitted',
  'Under Review': 'status.under_review',
  'Needs information': 'status.needs_information',
  Assigned: 'status.assigned',
  'In Progress': 'status.in_progress',
  Resolved: 'status.resolved',
  Reopened: 'status.reopened',
  Breached: 'portal.sla.watchTitle',
  'On track': 'status.assigned',
  'Approaching deadline': 'status.under_review',
};

const uiPriorityKeys: Record<string, TranslationKey> = {
  Critical: 'priority.critical',
  High: 'priority.high',
  Medium: 'priority.medium',
  Low: 'priority.low',
};

export function labelUiStatus(t: (k: TranslationKey) => string, status: string): string {
  const key = uiStatusKeys[status];
  return key ? t(key) : status;
}

export function labelUiPriority(t: (k: TranslationKey) => string, priority: string): string {
  const key = uiPriorityKeys[priority];
  return key ? t(key) : priority;
}

const categoryKeys: Record<string, TranslationKey> = {
  'Water Supply': 'portal.categories.Water Supply',
  'Roads & Potholes': 'portal.categories.Roads & Potholes',
  Sanitation: 'portal.categories.Sanitation',
  Electricity: 'portal.categories.Electricity',
  Streetlights: 'portal.categories.Streetlights',
  Drainage: 'portal.categories.Drainage',
  'Public Health': 'portal.categories.Public Health',
  'Public Safety': 'portal.categories.Public Safety',
  Environment: 'portal.categories.Environment',
  Transport: 'portal.categories.Transport',
  Other: 'portal.categories.Other',
};

export function labelCategory(t: (k: TranslationKey) => string, category: string): string {
  const key = categoryKeys[category];
  if (!key) return category;
  try {
    return t(key);
  } catch {
    return category;
  }
}
