/**
 * Canonical backend roles (UserRole enum + DB user_role).
 * Legacy `administrator` is normalized to platform_administrator (matches backend permissions.py).
 */
export const CANONICAL_API_ROLES = [
  'citizen',
  'officer',
  'department_administrator',
  'platform_administrator',
  'administrator',
  'community_moderator',
] as const;

export type CanonicalApiRole = (typeof CANONICAL_API_ROLES)[number];

export type WorkspaceKind = 'citizen' | 'officer' | 'dept_admin' | 'platform_admin' | 'moderator';

export function normalizeApiRole(role: string | null | undefined): CanonicalApiRole | null {
  if (!role || typeof role !== 'string') return null;
  const r = role.trim().toLowerCase();
  if (r === 'administrator') return 'platform_administrator';
  if ((CANONICAL_API_ROLES as readonly string[]).includes(r)) return r as CanonicalApiRole;
  return null;
}

export function mapApiRoleToWorkspace(role: string | null | undefined): WorkspaceKind {
  const normalized = normalizeApiRole(role);
  switch (normalized) {
    case 'officer':
      return 'officer';
    case 'department_administrator':
      return 'dept_admin';
    case 'platform_administrator':
    case 'administrator':
      return 'platform_admin';
    case 'community_moderator':
      return 'moderator';
    case 'citizen':
      return 'citizen';
    default:
      return 'citizen';
  }
}

export function workspaceHome(workspace: WorkspaceKind): string {
  switch (workspace) {
    case 'officer':
      return '/officer';
    case 'dept_admin':
    case 'platform_admin':
      return '/admin';
    case 'moderator':
      return '/community';
    default:
      return '/dashboard';
  }
}

/** Route prefixes allowed per workspace (UX only — backend enforces data). */
export function canAccessPath(workspace: WorkspaceKind, pathname: string): boolean {
  const p = pathname.split('?')[0];
  const citizen = ['/', '/dashboard', '/submit', '/grievances', '/track', '/notifications', '/help', '/community'];
  const officer = ['/officer', '/review-queue', '/grievances', '/track', '/notifications'];
  const deptAdmin = [...officer, '/admin', '/analytics', '/sla'];
  const platform = [...deptAdmin];
  const moderator = ['/community', '/help', '/notifications'];

  const allowed =
    workspace === 'citizen'
      ? citizen
      : workspace === 'officer'
        ? officer
        : workspace === 'dept_admin'
          ? deptAdmin
          : workspace === 'platform_admin'
            ? platform
            : moderator;

  return allowed.some((prefix) => p === prefix || p.startsWith(`${prefix}/`));
}

export function workspaceFromPermissions(permissions: string[]): WorkspaceKind | null {
  if (permissions.includes('analytics:all') || permissions.includes('department:manage')) {
    return 'platform_admin';
  }
  if (permissions.includes('analytics:dept')) return 'dept_admin';
  if (permissions.includes('grievance:read_assigned')) return 'officer';
  if (permissions.includes('community:moderate') && !permissions.includes('grievance:read_own')) {
    return 'moderator';
  }
  if (permissions.includes('grievance:create')) return 'citizen';
  return null;
}
