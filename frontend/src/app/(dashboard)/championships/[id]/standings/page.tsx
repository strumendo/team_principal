/**
 * Championship standings page.
 * Pagina de classificacao do campeonato.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { ChampionshipStanding } from "@/types/result";
import type { ChampionshipDetail } from "@/types/championship";
import { championshipsApi } from "@/lib/api-client";

export default function ChampionshipStandingsPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [championship, setChampionship] = useState<ChampionshipDetail | null>(null);
  const [standings, setStandings] = useState<ChampionshipStanding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !id) return;

    const fetchData = async () => {
      setLoading(true);
      const [champResult, standingsResult] = await Promise.all([
        championshipsApi.get(token, id),
        championshipsApi.getStandings(token, id),
      ]);

      if (champResult.error) {
        setError(champResult.error);
      } else {
        setChampionship(champResult.data || null);
        setStandings(standingsResult.data || []);
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

  if (!championship) {
    return <p className="text-gray-500">Championship not found. / Campeonato nao encontrado.</p>;
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          Standings / Classificacao — {championship.display_name}
        </h1>
        <p className="text-sm text-gray-500">{championship.name}</p>
      </div>

      {standings.length === 0 ? (
        <p className="text-gray-500">
          No standings yet. / Nenhuma classificacao ainda.
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
                  Races / Corridas
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Wins / Vitorias
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {standings.map((standing) => (
                <tr
                  key={standing.team_id}
                  className={standing.position === 1 ? "bg-yellow-50" : "hover:bg-gray-50"}
                >
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {standing.position}
                  </td>
                  <td className="px-6 py-4">
                    <p className="font-medium text-gray-900">{standing.team_display_name}</p>
                    <p className="text-sm text-gray-500">{standing.team_name}</p>
                  </td>
                  <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                    {standing.total_points}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {standing.races_scored}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {standing.wins}
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
