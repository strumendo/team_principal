/**
 * Standings hub page — lists all championships with links to standings.
 * Pagina hub de classificacao — lista todos os campeonatos com links para standings.
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

export default function StandingsHubPage() {
  const { data: session } = useSession();
  const [championships, setChampionships] = useState<ChampionshipListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session) return;

    const fetchChampionships = async () => {
      setLoading(true);
      const { data, error: err } = await championshipsApi.list(token);
      if (err) {
        setError(err);
      } else {
        setChampionships(data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchChampionships();
  }, [session, token]);

  if (loading) {
    return <p className="text-gray-500">Loading... / Carregando...</p>;
  }

  if (error) {
    return <p className="text-red-600">{error}</p>;
  }

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold text-gray-900">
        Standings / Classificacao
      </h1>

      {championships.length === 0 ? (
        <p className="text-gray-500">
          No championships found. / Nenhum campeonato encontrado.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {championships.map((champ) => (
            <div
              key={champ.id}
              className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
            >
              <div className="mb-3 flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    {champ.display_name}
                  </h2>
                  <p className="text-sm text-gray-500">{champ.name}</p>
                </div>
                <span
                  className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${STATUS_COLORS[champ.status]}`}
                >
                  {STATUS_LABELS[champ.status]}
                </span>
              </div>

              <p className="mb-4 text-sm text-gray-600">
                Season / Temporada: {champ.season_year}
              </p>

              <div className="flex gap-3">
                <Link
                  href={`/championships/${champ.id}/standings`}
                  className="rounded bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-700"
                >
                  View Standings / Ver Classificacao
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
