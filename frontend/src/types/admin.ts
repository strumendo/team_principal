/**
 * Admin panel TypeScript interfaces.
 * Interfaces TypeScript do painel admin.
 */

export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface AdminRole {
  id: string;
  name: string;
  display_name: string;
  description: string | null;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface AdminRoleDetail extends AdminRole {
  permissions: AdminPermission[];
}

export interface AdminPermission {
  id: string;
  codename: string;
  description: string | null;
  module: string;
  created_at: string;
  updated_at: string;
}
