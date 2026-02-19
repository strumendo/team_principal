/**
 * Races list within a championship.
 * Lista de corridas dentro de um campeonato.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { RaceListItem, RaceStatus } from "@/types/race";
import type { ChampionshipDetail } from "@/types/championship";
import { racesApi, championshipsApi } from "@/lib/api-client";

const STATUS_COLORS: Record<RaceStatus, string> = {
  scheduled: "bg-gray-100 text-gray-800",
  qualifying: "bg-yellow-100 text-yellow-800",
  active: "bg-green-100 text-green-800",
  finished: "bg-blue-100 text-blue-800",
  cancelled: "bg-red-100 text-red-800",
};

const STATUS_LABELS: Record<RaceStatus, string> = {
  scheduled: "Scheduled / Agendada",
  qualifying: "Qualifying / Classificacao",
  active: "Active / Ativa",
  finished: "Finished / Finalizada",
  cancelled: "Cancelled / Cancelada",
};

export default function ChampionshipRacesPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [championship, setChampionship] = useState<ChampionshipDetail | null>(null);
  const [races, setRaces] = useState<RaceListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters / Filtros
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [activeFilter, setActiveFilter] = useState<string>("");

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !id) return;

    const fetchData = async () => {
      setLoading(true);
      const params: { status?: string; is_active?: boolean } = {};
      if (statusFilter) params.status = statusFilter;
      if (activeFilter) params.is_active = activeFilter === "true";

      const [champResult, racesResult] = await Promise.all([
        championshipsApi.get(token, id),
        racesApi.listByChampionship(token, id, params),
      ]);

      if (champResult.error) {
        setError(champResult.error);
      } else {
        setChampionship(champResult.data || null);
        setRaces(racesResult.data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [session, id, token, statusFilter, activeFilter]);

  if (loading) {
    return <p className="text-gray-500">Loading... / Carregando...</p>;
  }

  if (error) {
    return <p className="text-red-600">{error}</p>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Races / Corridas
          </h1>
          {championship && (
            <p className="text-sm text-gray-500">
              {championship.display_name}
            </p>
          )}
        </div>
        <Link
          href={`/championships/${id}/races/create`}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          + New Race / Nova Corrida
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
          <option value="scheduled">Scheduled / Agendada</option>
          <option value="qualifying">Qualifying / Classificacao</option>
          <option value="active">Active / Ativa</option>
          <option value="finished">Finished / Finalizada</option>
          <option value="cancelled">Cancelled / Cancelada</option>
        </select>

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

      {races.length === 0 ? (
        <p className="text-gray-500">
          No races found. / Nenhuma corrida encontrada.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Round
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Name / Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Track / Pista
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Date / Data
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Active / Ativo
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {races.map((race) => (
                <tr key={race.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {race.round_number}
                  </td>
                  <td className="px-6 py-4">
                    <Link
                      href={`/races/${race.id}`}
                      className="font-medium text-blue-600 hover:underline"
                    >
                      {race.display_name}
                    </Link>
                    <p className="text-sm text-gray-500">{race.name}</p>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {race.track_name || "—"}
                    {race.track_country && ` (${race.track_country})`}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {race.scheduled_at
                      ? new Date(race.scheduled_at).toLocaleDateString()
                      : "—"}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${STATUS_COLORS[race.status]}`}
                    >
                      {STATUS_LABELS[race.status]}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                        race.is_active
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {race.is_active ? "Yes / Sim" : "No / Nao"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-6">
        <Link href={`/championships/${id}`} className="text-blue-600 hover:underline">
          &larr; Back to Championship / Voltar ao Campeonato
        </Link>
      </div>
    </div>
  );
}
