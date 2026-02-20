/**
 * Drivers list page with filters.
 * Pagina de listagem de pilotos com filtros.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import type { DriverListItem } from "@/types/driver";
import { driversApi } from "@/lib/api-client";

export default function DriversPage() {
  const { data: session } = useSession();
  const [drivers, setDrivers] = useState<DriverListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters / Filtros
  const [activeFilter, setActiveFilter] = useState<string>("");
  const [teamFilter, setTeamFilter] = useState<string>("");

  useEffect(() => {
    if (!session) return;

    const fetchDrivers = async () => {
      setLoading(true);
      const token = (session as unknown as { accessToken: string }).accessToken;
      const params: { is_active?: boolean; team_id?: string } = {};
      if (activeFilter) params.is_active = activeFilter === "true";
      if (teamFilter) params.team_id = teamFilter;

      const { data, error: err } = await driversApi.list(token, params);
      if (err) {
        setError(err);
      } else {
        setDrivers(data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchDrivers();
  }, [session, activeFilter, teamFilter]);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Drivers / Pilotos
        </h1>
      </div>

      {/* Filters / Filtros */}
      <div className="mb-6 flex gap-4">
        <select
          value={activeFilter}
          onChange={(e) => setActiveFilter(e.target.value)}
          className="rounded border px-3 py-2"
        >
          <option value="">All / Todos</option>
          <option value="true">Active / Ativo</option>
          <option value="false">Inactive / Inativo</option>
        </select>

        <input
          type="text"
          placeholder="Team ID / ID da Equipe"
          value={teamFilter}
          onChange={(e) => setTeamFilter(e.target.value)}
          className="w-80 rounded border px-3 py-2"
        />
      </div>

      {error && (
        <p className="mb-4 text-red-600">{error}</p>
      )}

      {loading ? (
        <p className="text-gray-500">Loading... / Carregando...</p>
      ) : drivers.length === 0 ? (
        <p className="text-gray-500">
          No drivers found. / Nenhum piloto encontrado.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  #
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Abbr.
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Name / Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Nationality / Nacionalidade
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Active / Ativo
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {drivers.map((driver) => (
                <tr key={driver.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-bold text-gray-900">
                    {driver.number}
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex rounded bg-gray-200 px-2 py-1 text-xs font-bold text-gray-800">
                      {driver.abbreviation}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-medium text-gray-900">
                      {driver.display_name}
                    </span>
                    <p className="text-sm text-gray-500">{driver.name}</p>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {driver.nationality || "—"}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                        driver.is_active
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {driver.is_active ? "Yes / Sim" : "No / Nao"}
                    </span>
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
