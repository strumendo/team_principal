/**
 * Admin user detail page with edit form and role management.
 * Pagina admin de detalhe de usuario com formulario de edicao e gerenciamento de papeis.
 */
"use client";

import { useEffect, useState, useCallback } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { AdminUser, AdminRole } from "@/types/admin";
import { adminUsersApi, adminRolesApi } from "@/lib/api-client";
import ImageUpload from "@/components/ImageUpload";

export default function AdminUserDetailPage() {
  const { data: session } = useSession();
  const params = useParams();
  const userId = params.id as string;

  const [user, setUser] = useState<AdminUser | null>(null);
  const [userRoles, setUserRoles] = useState<AdminRole[]>([]);
  const [allRoles, setAllRoles] = useState<AdminRole[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  // Form state / Estado do formulario
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [isActive, setIsActive] = useState(true);

  // Role assignment / Atribuicao de papel
  const [selectedRoleId, setSelectedRoleId] = useState("");

  const getToken = useCallback(() => {
    return (session as unknown as { accessToken: string }).accessToken;
  }, [session]);

  useEffect(() => {
    if (!session) return;

    const fetchData = async () => {
      setLoading(true);
      const token = getToken();

      const [userRes, rolesRes, allRolesRes] = await Promise.all([
        adminUsersApi.get(token, userId),
        adminUsersApi.getRoles(token, userId),
        adminRolesApi.list(token),
      ]);

      if (userRes.error) {
        setError(userRes.error);
      } else if (userRes.data) {
        setUser(userRes.data);
        setFullName(userRes.data.full_name);
        setEmail(userRes.data.email);
        setIsActive(userRes.data.is_active);
        setError(null);
      }

      if (rolesRes.data) setUserRoles(rolesRes.data);
      if (allRolesRes.data) setAllRoles(allRolesRes.data);

      setLoading(false);
    };

    fetchData();
  }, [session, userId, getToken]);

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    const token = getToken();
    const { data, error: err } = await adminUsersApi.update(token, userId, {
      full_name: fullName,
      email,
      is_active: isActive,
    });
    if (err) {
      setMessage(err);
    } else if (data) {
      setUser(data);
      setMessage("User updated successfully / Usuario atualizado com sucesso");
    }
    setSaving(false);
  };

  const handleAssignRole = async () => {
    if (!selectedRoleId) return;
    const token = getToken();
    const { data, error: err } = await adminUsersApi.assignRole(token, userId, selectedRoleId);
    if (err) {
      setMessage(err);
    } else if (data) {
      setUserRoles(data);
      setSelectedRoleId("");
      setMessage("Role assigned / Papel atribuido");
    }
  };

  const handleRevokeRole = async (roleId: string) => {
    const token = getToken();
    const { data, error: err } = await adminUsersApi.revokeRole(token, userId, roleId);
    if (err) {
      setMessage(err);
    } else if (data) {
      setUserRoles(data);
      setMessage("Role revoked / Papel revogado");
    }
  };

  const availableRoles = allRoles.filter(
    (r) => !userRoles.some((ur) => ur.id === r.id)
  );

  if (loading) return <p className="text-gray-500">Loading... / Carregando...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!user) return <p className="text-gray-500">User not found / Usuario nao encontrado</p>;

  return (
    <div>
      <div className="mb-6">
        <Link href="/admin/users" className="text-blue-600 hover:underline">
          &larr; Back to Users / Voltar para Usuarios
        </Link>
      </div>

      <h1 className="mb-6 text-3xl font-bold text-gray-900">
        Edit User / Editar Usuario
      </h1>

      {message && (
        <p className={`mb-4 ${message.includes("success") || message.includes("sucesso") || message.includes("assigned") || message.includes("revoked") ? "text-green-600" : "text-red-600"}`}>
          {message}
        </p>
      )}

      {/* Avatar upload / Upload de avatar */}
      <div className="mb-8 max-w-lg rounded border p-6">
        <h2 className="mb-4 text-xl font-semibold">Avatar</h2>
        <ImageUpload
          currentImageUrl={user.avatar_url}
          uploadUrl={`/uploads/users/${userId}/avatar`}
          token={getToken()}
          onUploadSuccess={(url) => setUser({ ...user, avatar_url: url })}
          label="User Avatar / Avatar do Usuario"
        />
      </div>

      {/* Edit form / Formulario de edicao */}
      <div className="mb-8 max-w-lg rounded border p-6">
        <h2 className="mb-4 text-xl font-semibold">Profile / Perfil</h2>
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Full Name / Nome Completo
          </label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full rounded border px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded border px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
            />
            <span className="text-sm font-medium text-gray-700">
              Active / Ativo
            </span>
          </label>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Saving... / Salvando..." : "Save / Salvar"}
        </button>
      </div>

      {/* Roles section / Secao de papeis */}
      <div className="max-w-lg rounded border p-6">
        <h2 className="mb-4 text-xl font-semibold">Roles / Papeis</h2>

        {userRoles.length === 0 ? (
          <p className="mb-4 text-gray-500">No roles assigned / Nenhum papel atribuido</p>
        ) : (
          <table className="mb-4 min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">
                  Role / Papel
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">
                  Actions / Acoes
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {userRoles.map((role) => (
                <tr key={role.id}>
                  <td className="px-4 py-2 text-sm">
                    {role.display_name}
                    {role.is_system && (
                      <span className="ml-2 inline-flex rounded-full bg-gray-100 px-2 text-xs text-gray-600">
                        system
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2">
                    <button
                      onClick={() => handleRevokeRole(role.id)}
                      className="text-sm text-red-600 hover:underline"
                    >
                      Revoke / Revogar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {availableRoles.length > 0 && (
          <div className="flex gap-2">
            <select
              value={selectedRoleId}
              onChange={(e) => setSelectedRoleId(e.target.value)}
              className="flex-1 rounded border px-3 py-2"
            >
              <option value="">Select role / Selecionar papel</option>
              {availableRoles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.display_name}
                </option>
              ))}
            </select>
            <button
              onClick={handleAssignRole}
              disabled={!selectedRoleId}
              className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Assign / Atribuir
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
