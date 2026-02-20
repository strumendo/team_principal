/**
 * Dashboard page with summary widgets.
 * Pagina do dashboard com widgets de resumo.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import Link from "next/link";
import type { DashboardSummary } from "@/types/dashboard";
import { dashboardApi } from "@/lib/api-client";

export default function DashboardPage() {
  const { data: session } = useSession();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) return;
    const token = (session as unknown as { accessToken: string }).accessToken;

    const fetchData = async () => {
      setLoading(true);
      const { data, error: err } = await dashboardApi.getSummary(token);
      if (err) {
        setError(err);
      } else {
        setSummary(data || null);
        setError(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [session]);

  if (loading) {
    return <p className="text-gray-500">Loading... / Carregando...</p>;
  }

  if (error) {
    return <p className="text-red-600">{error}</p>;
  }

  if (!summary) {
    return <p className="text-gray-500">No data available. / Nenhum dado disponivel.</p>;
  }

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold text-gray-900">Dashboard</h1>

      {/* Active Championships / Campeonatos Ativos */}
      <section className="mb-8">
        <h2 className="mb-4 text-xl font-semibold text-gray-800">
          Active Championships / Campeonatos Ativos
        </h2>
        {summary.active_championships.length === 0 ? (
          <p className="text-gray-500">
            No active championships. / Nenhum campeonato ativo.
          </p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {summary.active_championships.map((champ) => (
              <Link
                key={champ.id}
                href={`/championships/${champ.id}`}
                className="block rounded-lg border border-gray-200 bg-white p-4 shadow-sm hover:shadow-md"
              >
                <h3 className="text-lg font-semibold text-gray-900">
                  {champ.display_name}
                </h3>
                <p className="text-sm text-gray-500">
                  Season / Temporada: {champ.season_year}
                </p>
                <div className="mt-3 flex items-center gap-4 text-sm">
                  <span className="text-gray-600">
                    {champ.completed_races}/{champ.total_races} races / corridas
                  </span>
                  <span className="text-gray-600">
                    {champ.team_count} teams / equipes
                  </span>
                </div>
                {champ.total_races > 0 && (
                  <div className="mt-2">
                    <div className="h-2 w-full rounded-full bg-gray-200">
                      <div
                        className="h-2 rounded-full bg-blue-600"
                        style={{
                          width: `${(champ.completed_races / champ.total_races) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
              </Link>
            ))}
          </div>
        )}
      </section>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Next Races / Proximas Corridas */}
        <section className="lg:col-span-2">
          <h2 className="mb-4 text-xl font-semibold text-gray-800">
            Next Races / Proximas Corridas
          </h2>
          {summary.next_races.length === 0 ? (
            <p className="text-gray-500">
              No upcoming races. / Nenhuma corrida agendada.
            </p>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-gray-200">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Race / Corrida
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Championship / Campeonato
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Track / Pista
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Date / Data
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {summary.next_races.map((race) => (
                    <tr key={race.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <p className="font-medium text-gray-900">
                          {race.display_name}
                        </p>
                        <p className="text-xs text-gray-500">
                          Round {race.round_number}
                        </p>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        <Link
                          href={`/championships/${race.championship_id}`}
                          className="text-blue-600 hover:underline"
                        >
                          {race.championship_display_name}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {race.track_name || "-"}
                        {race.track_country && (
                          <span className="text-gray-400">
                            {" "}({race.track_country})
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {new Date(race.scheduled_at).toLocaleDateString(undefined, {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Standings / Classificacoes */}
        <section>
          <h2 className="mb-4 text-xl font-semibold text-gray-800">
            Standings / Classificacoes
          </h2>
          {summary.championship_standings.length === 0 ? (
            <p className="text-gray-500">
              No standings yet. / Nenhuma classificacao ainda.
            </p>
          ) : (
            <div className="space-y-4">
              {summary.championship_standings.map((cs) => (
                <div
                  key={cs.championship_id}
                  className="rounded-lg border border-gray-200 bg-white"
                >
                  <div className="border-b border-gray-200 px-4 py-2">
                    <Link
                      href={`/championships/${cs.championship_id}/standings`}
                      className="font-semibold text-blue-600 hover:underline"
                    >
                      {cs.championship_display_name}
                    </Link>
                  </div>
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">
                          Pos
                        </th>
                        <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">
                          Team / Equipe
                        </th>
                        <th className="px-3 py-2 text-right text-xs font-medium uppercase text-gray-500">
                          Pts
                        </th>
                        <th className="px-3 py-2 text-right text-xs font-medium uppercase text-gray-500">
                          W
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {cs.standings.map((s) => (
                        <tr
                          key={s.team_id}
                          className={s.position === 1 ? "bg-yellow-50" : "hover:bg-gray-50"}
                        >
                          <td className="px-3 py-2 text-sm font-medium text-gray-900">
                            {s.position}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {s.team_display_name}
                          </td>
                          <td className="px-3 py-2 text-right text-sm font-semibold text-gray-900">
                            {s.total_points}
                          </td>
                          <td className="px-3 py-2 text-right text-sm text-gray-500">
                            {s.wins}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
