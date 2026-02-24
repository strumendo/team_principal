/**
 * Penalties list page for a race.
 * Pagina de listagem de penalidades de uma corrida.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { Penalty, PenaltyType } from "@/types/penalty";
import type { RaceDetail } from "@/types/race";
import { racesApi, penaltiesApi } from "@/lib/api-client";

const PENALTY_TYPE_LABELS: Record<PenaltyType, string> = {
  warning: "Warning / Advertencia",
  time_penalty: "Time Penalty / Penalidade de Tempo",
  points_deduction: "Points Deduction / Deducao de Pontos",
  disqualification: "DSQ / Desclassificacao",
  grid_penalty: "Grid Penalty / Penalidade de Grid",
};

const PENALTY_TYPE_COLORS: Record<PenaltyType, string> = {
  warning: "bg-yellow-100 text-yellow-800",
  time_penalty: "bg-orange-100 text-orange-800",
  points_deduction: "bg-blue-100 text-blue-800",
  disqualification: "bg-red-100 text-red-800",
  grid_penalty: "bg-purple-100 text-purple-800",
};

export default function RacePenaltiesPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [race, setRace] = useState<RaceDetail | null>(null);
  const [penalties, setPenalties] = useState<Penalty[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !id) return;

    const fetchData = async () => {
      setLoading(true);
      const [raceResult, penaltiesResult] = await Promise.all([
        racesApi.get(token, id),
        penaltiesApi.listByRace(token, id),
      ]);

      if (raceResult.error) {
        setError(raceResult.error);
      } else {
        setRace(raceResult.data || null);
        setPenalties(penaltiesResult.data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [session, id, token]);

  const handleDelete = async (penaltyId: string) => {
    if (!confirm("Delete this penalty? / Excluir esta penalidade?")) return;

    const { error: err } = await penaltiesApi.delete(token, penaltyId);
    if (err) {
      setError(err);
    } else {
      setPenalties((prev) => prev.filter((p) => p.id !== penaltyId));
    }
  };

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
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Penalties / Penalidades — {race.display_name}
          </h1>
          <p className="text-sm text-gray-500">{race.name}</p>
        </div>
        <Link
          href={`/races/${id}/penalties/create`}
          className="rounded bg-orange-600 px-4 py-2 text-white hover:bg-orange-700"
        >
          New Penalty / Nova Penalidade
        </Link>
      </div>

      {penalties.length === 0 ? (
        <p className="text-gray-500">
          No penalties recorded. / Nenhuma penalidade registrada.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Type / Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Team / Equipe
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Reason / Razao
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Points / Pontos
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Lap / Volta
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Active / Ativo
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                  Actions / Acoes
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {penalties.map((penalty) => {
                const team = race.teams.find((t) => t.id === penalty.team_id);
                return (
                  <tr key={penalty.id} className={penalty.is_active ? "hover:bg-gray-50" : "bg-gray-100 opacity-60"}>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                          PENALTY_TYPE_COLORS[penalty.penalty_type as PenaltyType] || "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {PENALTY_TYPE_LABELS[penalty.penalty_type as PenaltyType] || penalty.penalty_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {team?.display_name || penalty.team_id}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                      {penalty.reason}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {penalty.points_deducted > 0 ? `-${penalty.points_deducted}` : "—"}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {penalty.lap_number ?? "—"}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                          penalty.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                        }`}
                      >
                        {penalty.is_active ? "Yes / Sim" : "No / Nao"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleDelete(penalty.id)}
                        className="text-sm text-red-600 hover:underline"
                      >
                        Delete / Excluir
                      </button>
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
