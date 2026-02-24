/**
 * Race results page.
 * Pagina de resultados da corrida.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { RaceResult } from "@/types/result";
import type { Penalty } from "@/types/penalty";
import type { RaceDetail } from "@/types/race";
import { racesApi, resultsApi, penaltiesApi } from "@/lib/api-client";

export default function RaceResultsPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [race, setRace] = useState<RaceDetail | null>(null);
  const [results, setResults] = useState<RaceResult[]>([]);
  const [penalties, setPenalties] = useState<Penalty[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !id) return;

    const fetchData = async () => {
      setLoading(true);
      const [raceResult, resultsResult, penaltiesResult] = await Promise.all([
        racesApi.get(token, id),
        resultsApi.listByRace(token, id),
        penaltiesApi.listByRace(token, id),
      ]);

      if (raceResult.error) {
        setError(raceResult.error);
      } else {
        setRace(raceResult.data || null);
        setResults(resultsResult.data || []);
        setPenalties(penaltiesResult.data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [session, id, token]);

  if (loading) {
    return <p className="text-gray-500">Loading... / Carregando...</p>;
  }

  if (error) {
    return <p className="text-red-600">{error}</p>;
  }

  if (!race) {
    return <p className="text-gray-500">Race not found. / Corrida nao encontrada.</p>;
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          Results / Resultados — {race.display_name}
        </h1>
        <p className="text-sm text-gray-500">{race.name}</p>
      </div>

      {results.length === 0 ? (
        <p className="text-gray-500">
          No results recorded. / Nenhum resultado registrado.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Pos
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Team / Equipe
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Points / Pontos
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Laps / Voltas
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Flags
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Penalties / Penalidades
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Notes / Notas
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {results.map((result) => {
                const team = race.teams.find((t) => t.id === result.team_id);
                const resultPenalties = penalties.filter((p) => p.result_id === result.id);
                return (
                  <tr
                    key={result.id}
                    className={result.dsq ? "bg-red-50" : "hover:bg-gray-50"}
                  >
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {result.position}
                    </td>
                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-900">
                        {team?.display_name || "—"}
                      </p>
                      <p className="text-sm text-gray-500">
                        {team?.name || result.team_id}
                      </p>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {result.points}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {result.laps_completed ?? "—"}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-1">
                        {result.fastest_lap && (
                          <span className="inline-flex rounded-full bg-purple-100 px-2 text-xs font-semibold leading-5 text-purple-800">
                            FL
                          </span>
                        )}
                        {result.dnf && (
                          <span className="inline-flex rounded-full bg-orange-100 px-2 text-xs font-semibold leading-5 text-orange-800">
                            DNF
                          </span>
                        )}
                        {result.dsq && (
                          <span className="inline-flex rounded-full bg-red-100 px-2 text-xs font-semibold leading-5 text-red-800">
                            DSQ
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {resultPenalties.length > 0 ? (
                        <span className="inline-flex rounded-full bg-orange-100 px-2 text-xs font-semibold leading-5 text-orange-800">
                          {resultPenalties.length}
                        </span>
                      ) : (
                        <span className="text-sm text-gray-400">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {result.notes || "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-6">
        <Link href={`/races/${id}`} className="text-blue-600 hover:underline">
          &larr; Back to Race / Voltar a Corrida
        </Link>
      </div>
    </div>
  );
}
