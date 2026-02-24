/**
 * Admin role detail page with edit form and permission management.
 * Pagina admin de detalhe de papel com formulario de edicao e gerenciamento de permissoes.
 */
"use client";

import { useEffect, useState, useCallback } from "react";
import { useSession } from "next-auth/react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import type { AdminRoleDetail, AdminPermission } from "@/types/admin";
import { adminRolesApi, adminPermissionsApi } from "@/lib/api-client";

export default function AdminRoleDetailPage() {
  const { data: session } = useSession();
  const params = useParams();
  const router = useRouter();
  const roleId = params.id as string;

  const [role, setRole] = useState<AdminRoleDetail | null>(null);
  const [allPermissions, setAllPermissions] = useState<AdminPermission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  // Form state / Estado do formulario
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");

  // Permission assignment / Atribuicao de permissao
  const [selectedPermissionId, setSelectedPermissionId] = useState("");
  const [moduleFilter, setModuleFilter] = useState("");

  const getToken = useCallback(() => {
    return (session as unknown as { accessToken: string }).accessToken;
  }, [session]);

  useEffect(() => {
    if (!session) return;

    const fetchData = async () => {
      setLoading(true);
      const token = getToken();

      const [roleRes, permsRes] = await Promise.all([
        adminRolesApi.get(token, roleId),
        adminPermissionsApi.list(token),
      ]);

      if (roleRes.error) {
        setError(roleRes.error);
      } else if (roleRes.data) {
        setRole(roleRes.data);
        setDisplayName(roleRes.data.display_name);
        setDescription(roleRes.data.description || "");
        setError(null);
      }

      if (permsRes.data) setAllPermissions(permsRes.data);

      setLoading(false);
    };

    fetchData();
  }, [session, roleId, getToken]);

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    const token = getToken();
    const { data, error: err } = await adminRolesApi.update(token, roleId, {
      display_name: displayName,
      description: description || undefined,
    });
    if (err) {
      setMessage(err);
    } else if (data) {
      setRole(data);
      setMessage("Role updated successfully / Papel atualizado com sucesso");
    }
    setSaving(false);
  };

  const handleDelete = async () => {
    if (!confirm("Delete this role? / Excluir este papel?")) return;
    const token = getToken();
    const { error: err } = await adminRolesApi.delete(token, roleId);
    if (err) {
      setMessage(err);
    } else {
      router.push("/admin/roles");
    }
  };

  const handleAssignPermission = async () => {
    if (!selectedPermissionId) return;
    const token = getToken();
    const { data, error: err } = await adminRolesApi.assignPermission(token, roleId, selectedPermissionId);
    if (err) {
      setMessage(err);
    } else if (data) {
      setRole(data);
      setSelectedPermissionId("");
      setMessage("Permission assigned / Permissao atribuida");
    }
  };

  const handleRevokePermission = async (permissionId: string) => {
    const token = getToken();
    const { data, error: err } = await adminRolesApi.revokePermission(token, roleId, permissionId);
    if (err) {
      setMessage(err);
    } else if (data) {
      setRole(data);
      setMessage("Permission revoked / Permissao revogada");
    }
  };

  const modules = Array.from(new Set(allPermissions.map((p) => p.module))).sort();
  const filteredPermissions = moduleFilter
    ? allPermissions.filter((p) => p.module === moduleFilter)
    : allPermissions;
  const availablePermissions = filteredPermissions.filter(
    (p) => !role?.permissions.some((rp) => rp.id === p.id)
  );

  if (loading) return <p className="text-gray-500">Loading... / Carregando...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!role) return <p className="text-gray-500">Role not found / Papel nao encontrado</p>;

  return (
    <div>
      <div className="mb-6">
        <Link href="/admin/roles" className="text-blue-600 hover:underline">
          &larr; Back to Roles / Voltar para Papeis
        </Link>
      </div>

      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Role: {role.name}
        </h1>
        {!role.is_system && (
          <button
            onClick={handleDelete}
            className="rounded bg-red-600 px-4 py-2 text-white hover:bg-red-700"
          >
            Delete / Excluir
          </button>
        )}
      </div>

      {message && (
        <p className={`mb-4 ${message.includes("success") || message.includes("sucesso") || message.includes("assigned") || message.includes("revoked") ? "text-green-600" : "text-red-600"}`}>
          {message}
        </p>
      )}

      {/* Edit form / Formulario de edicao */}
      {!role.is_system && (
        <div className="mb-8 max-w-lg rounded border p-6">
          <h2 className="mb-4 text-xl font-semibold">Edit / Editar</h2>
          <div className="mb-4">
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Display Name / Nome de Exibicao
            </label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="w-full rounded border px-3 py-2"
            />
          </div>
          <div className="mb-4">
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Description / Descricao
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full rounded border px-3 py-2"
            />
          </div>
          <button
            onClick={handleSave}
            disabled={saving}
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving... / Salvando..." : "Save / Salvar"}
          </button>
        </div>
      )}

      {role.is_system && (
        <div className="mb-8 rounded border border-yellow-200 bg-yellow-50 p-4">
          <p className="text-sm text-yellow-800">
            System roles cannot be edited or deleted. / Papeis do sistema nao podem ser editados ou excluidos.
          </p>
        </div>
      )}

      {/* Permissions section / Secao de permissoes */}
      <div className="max-w-2xl rounded border p-6">
        <h2 className="mb-4 text-xl font-semibold">Permissions / Permissoes</h2>

        {role.permissions.length === 0 ? (
          <p className="mb-4 text-gray-500">No permissions assigned / Nenhuma permissao atribuida</p>
        ) : (
          <table className="mb-4 min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">
                  Codename
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">
                  Module / Modulo
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">
                  Actions / Acoes
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {role.permissions.map((perm) => (
                <tr key={perm.id}>
                  <td className="px-4 py-2 text-sm">{perm.codename}</td>
                  <td className="px-4 py-2 text-sm text-gray-500">{perm.module}</td>
                  <td className="px-4 py-2">
                    <button
                      onClick={() => handleRevokePermission(perm.id)}
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

        <div className="flex gap-2">
          <select
            value={moduleFilter}
            onChange={(e) => {
              setModuleFilter(e.target.value);
              setSelectedPermissionId("");
            }}
            className="rounded border px-3 py-2"
          >
            <option value="">All Modules / Todos Modulos</option>
            {modules.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
          <select
            value={selectedPermissionId}
            onChange={(e) => setSelectedPermissionId(e.target.value)}
            className="flex-1 rounded border px-3 py-2"
          >
            <option value="">Select permission / Selecionar permissao</option>
            {availablePermissions.map((perm) => (
              <option key={perm.id} value={perm.id}>
                {perm.codename}
              </option>
            ))}
          </select>
          <button
            onClick={handleAssignPermission}
            disabled={!selectedPermissionId}
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Assign / Atribuir
          </button>
        </div>
      </div>
    </div>
  );
}
