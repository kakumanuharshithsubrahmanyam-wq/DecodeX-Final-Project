import { describe, expect, it } from 'vitest';
import { canAccessPath, mapApiRoleToWorkspace, normalizeApiRole } from './roles';

describe('role mapping', () => {
  it('normalizes legacy administrator', () => {
    expect(normalizeApiRole('administrator')).toBe('platform_administrator');
    expect(mapApiRoleToWorkspace('administrator')).toBe('platform_admin');
  });

  it('rejects unknown roles', () => {
    expect(normalizeApiRole('superuser')).toBeNull();
    expect(mapApiRoleToWorkspace('superuser')).toBe('citizen');
  });

  it('maps department_administrator to dept_admin workspace', () => {
    expect(mapApiRoleToWorkspace('department_administrator')).toBe('dept_admin');
  });

  it('restricts citizen from officer routes', () => {
    expect(canAccessPath('citizen', '/officer')).toBe(false);
    expect(canAccessPath('citizen', '/dashboard')).toBe(true);
  });

  it('restricts moderator from grievance register', () => {
    expect(canAccessPath('moderator', '/grievances')).toBe(false);
    expect(canAccessPath('moderator', '/community')).toBe(true);
  });
});
