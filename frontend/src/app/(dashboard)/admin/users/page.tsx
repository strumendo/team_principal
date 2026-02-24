/**
 * Admin users list page with search and filters.
 * Pagina admin de listagem de usuarios com busca e filtros.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import Link from "next/link";
import type { AdminUser } from "@/types/admin";
import { adminUsersApi } from "@/lib/api-client";

export default function AdminUsersPage() {
  const { data: session } = useSession();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters / Filtros
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState<string>("");

  useEffect(() => {
    if (!session) return;

    const fetchUsers = async () => {
      setLoading(true);
      const token = (session as unknown as { accessToken: string }).accessToken;
      const params: { is_active?: boolean; search?: string } = {};
      if (activeFilter) params.is_active = activeFilter === "true";
      if (search) params.search = search;

      const { data, error: err } = await adminUsersApi.list(token, params);
      if (err) {
        setError(err);
      } else {
        setUsers(data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchUsers();
  }, [session, activeFilter, search]);

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold text-gray-900">
        Users / Usuarios
      </h1>

      {/* Filters / Filtros */}
      <div className="mb-6 flex gap-4">
        <input
          type="text"
          placeholder="Search name or email / Buscar nome ou email"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-72 rounded border px-3 py-2"
        />
        <select
          value={activeFilter}
          onChange={(e) => setActiveFilter(e.target.value)}
          className="rounded border px-3 py-2"
        >
          <option value="">All / Todos</option>
          <option value="true">Active / Ativo</option>
          <option value="false">Inactive / Inativo</option>
        </select>
      </div>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      {loading ? (
        <p className="text-gray-500">Loading... / Carregando...</p>
      ) : users.length === 0 ? (
        <p className="text-gray-500">
          No users found. / Nenhum usuario encontrado.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Name / Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Active / Ativo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Superuser
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Created / Criado
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link
                      href={`/admin/users/${user.id}`}
                      className="font-medium text-blue-600 hover:underline"
                    >
                      {user.email}
                    </Link>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {user.full_name}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                        user.is_active
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {user.is_active ? "Yes / Sim" : "No / Nao"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {user.is_superuser && (
                      <span className="inline-flex rounded-full bg-purple-100 px-2 text-xs font-semibold leading-5 text-purple-800">
                        Superuser
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(user.created_at).toLocaleDateString()}
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
