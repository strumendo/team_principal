/**
 * Admin roles list page.
 * Pagina admin de listagem de papeis.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import Link from "next/link";
import type { AdminRole } from "@/types/admin";
import { adminRolesApi } from "@/lib/api-client";

export default function AdminRolesPage() {
  const { data: session } = useSession();
  const [roles, setRoles] = useState<AdminRole[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) return;

    const fetchRoles = async () => {
      setLoading(true);
      const token = (session as unknown as { accessToken: string }).accessToken;
      const { data, error: err } = await adminRolesApi.list(token);
      if (err) {
        setError(err);
      } else {
        setRoles(data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchRoles();
  }, [session]);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Roles / Papeis
        </h1>
        <Link
          href="/admin/roles/create"
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          + New Role / Novo Papel
        </Link>
      </div>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      {loading ? (
        <p className="text-gray-500">Loading... / Carregando...</p>
      ) : roles.length === 0 ? (
        <p className="text-gray-500">
          No roles found. / Nenhum papel encontrado.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Name / Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Display Name / Nome de Exibicao
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  System / Sistema
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Description / Descricao
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {roles.map((role) => (
                <tr key={role.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link
                      href={`/admin/roles/${role.id}`}
                      className="font-medium text-blue-600 hover:underline"
                    >
                      {role.name}
                    </Link>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {role.display_name}
                  </td>
                  <td className="px-6 py-4">
                    {role.is_system && (
                      <span className="inline-flex rounded-full bg-gray-100 px-2 text-xs font-semibold leading-5 text-gray-600">
                        System / Sistema
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {role.description || "—"}
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
