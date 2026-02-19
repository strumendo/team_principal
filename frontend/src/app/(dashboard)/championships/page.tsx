/**
 * Championships list page with filters.
 * Pagina de listagem de campeonatos com filtros.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import Link from "next/link";
import type { ChampionshipListItem, ChampionshipStatus } from "@/types/championship";
import { championshipsApi } from "@/lib/api-client";

const STATUS_COLORS: Record<ChampionshipStatus, string> = {
  planned: "bg-gray-100 text-gray-800",
  active: "bg-green-100 text-green-800",
  completed: "bg-blue-100 text-blue-800",
  cancelled: "bg-red-100 text-red-800",
};

const STATUS_LABELS: Record<ChampionshipStatus, string> = {
  planned: "Planned / Planejado",
  active: "Active / Ativo",
  completed: "Completed / Concluido",
  cancelled: "Cancelled / Cancelado",
};

export default function ChampionshipsPage() {
  const { data: session } = useSession();
  const [championships, setChampionships] = useState<ChampionshipListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters / Filtros
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [seasonFilter, setSeasonFilter] = useState<string>("");
  const [activeFilter, setActiveFilter] = useState<string>("");

  useEffect(() => {
    if (!session) return;

    const fetchChampionships = async () => {
      setLoading(true);
      const token = (session as unknown as { accessToken: string }).accessToken;
      const params: { status?: string; season_year?: number; is_active?: boolean } = {};
      if (statusFilter) params.status = statusFilter;
      if (seasonFilter) params.season_year = parseInt(seasonFilter);
      if (activeFilter) params.is_active = activeFilter === "true";

      const { data, error: err } = await championshipsApi.list(token, params);
      if (err) {
        setError(err);
      } else {
        setChampionships(data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchChampionships();
  }, [session, statusFilter, seasonFilter, activeFilter]);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Championships / Campeonatos
        </h1>
        <Link
          href="/championships/create"
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          + New Championship / Novo Campeonato
        </Link>
      </div>

      {/* Filters / Filtros */}
      <div className="mb-6 flex gap-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded border px-3 py-2"
        >
          <option value="">All Statuses / Todos os Status</option>
          <option value="planned">Planned / Planejado</option>
          <option value="active">Active / Ativo</option>
          <option value="completed">Completed / Concluido</option>
          <option value="cancelled">Cancelled / Cancelado</option>
        </select>

        <input
          type="number"
          placeholder="Season Year / Ano"
          value={seasonFilter}
          onChange={(e) => setSeasonFilter(e.target.value)}
          className="w-32 rounded border px-3 py-2"
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

      {error && (
        <p className="mb-4 text-red-600">{error}</p>
      )}

      {loading ? (
        <p className="text-gray-500">Loading... / Carregando...</p>
      ) : championships.length === 0 ? (
        <p className="text-gray-500">
          No championships found. / Nenhum campeonato encontrado.
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
                  Season / Temporada
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Dates / Datas
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Active / Ativo
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {championships.map((champ) => (
                <tr key={champ.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link
                      href={`/championships/${champ.id}`}
                      className="font-medium text-blue-600 hover:underline"
                    >
                      {champ.display_name}
                    </Link>
                    <p className="text-sm text-gray-500">{champ.name}</p>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {champ.season_year}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${STATUS_COLORS[champ.status]}`}
                    >
                      {STATUS_LABELS[champ.status]}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {champ.start_date || "—"} / {champ.end_date || "—"}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                        champ.is_active
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {champ.is_active ? "Yes / Sim" : "No / Nao"}
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
