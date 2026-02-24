/**
 * Admin permissions list page (read-only).
 * Pagina admin de listagem de permissoes (somente leitura).
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import type { AdminPermission } from "@/types/admin";
import { adminPermissionsApi } from "@/lib/api-client";

export default function AdminPermissionsPage() {
  const { data: session } = useSession();
  const [permissions, setPermissions] = useState<AdminPermission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter / Filtro
  const [moduleFilter, setModuleFilter] = useState("");

  useEffect(() => {
    if (!session) return;

    const fetchPermissions = async () => {
      setLoading(true);
      const token = (session as unknown as { accessToken: string }).accessToken;
      const params: { module?: string } = {};
      if (moduleFilter) params.module = moduleFilter;

      const { data, error: err } = await adminPermissionsApi.list(token, params);
      if (err) {
        setError(err);
      } else {
        setPermissions(data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchPermissions();
  }, [session, moduleFilter]);

  const modules = Array.from(new Set(permissions.map((p) => p.module))).sort();

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold text-gray-900">
        Permissions / Permissoes
      </h1>

      {/* Filter / Filtro */}
      <div className="mb-6">
        <select
          value={moduleFilter}
          onChange={(e) => setModuleFilter(e.target.value)}
          className="rounded border px-3 py-2"
        >
          <option value="">All Modules / Todos Modulos</option>
          {modules.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      {loading ? (
        <p className="text-gray-500">Loading... / Carregando...</p>
      ) : permissions.length === 0 ? (
        <p className="text-gray-500">
          No permissions found. / Nenhuma permissao encontrada.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Codename
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Module / Modulo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Description / Descricao
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {permissions.map((perm) => (
                <tr key={perm.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {perm.codename}
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex rounded-full bg-gray-100 px-2 text-xs font-semibold leading-5 text-gray-600">
                      {perm.module}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {perm.description || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
