/**
 * Race detail page with enrolled teams.
 * Pagina de detalhe da corrida com equipes inscritas.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import type { RaceDetail, RaceEntry, RaceStatus } from "@/types/race";
import { racesApi } from "@/lib/api-client";

const STATUS_COLORS: Record<RaceStatus, string> = {
  scheduled: "bg-gray-100 text-gray-800",
  qualifying: "bg-yellow-100 text-yellow-800",
  active: "bg-green-100 text-green-800",
  finished: "bg-blue-100 text-blue-800",
  cancelled: "bg-red-100 text-red-800",
};

export default function RaceDetailPage() {
  const { data: session } = useSession();
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [race, setRace] = useState<RaceDetail | null>(null);
  const [entries, setEntries] = useState<RaceEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !id) return;

    const fetchData = async () => {
      setLoading(true);
      const [raceResult, entriesResult] = await Promise.all([
        racesApi.get(token, id),
        racesApi.listEntries(token, id),
      ]);

      if (raceResult.error) {
        setError(raceResult.error);
      } else {
        setRace(raceResult.data || null);
        setEntries(entriesResult.data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [session, id, token]);

  const handleDelete = async () => {
    if (!confirm("Delete this race? / Excluir esta corrida?")) return;

    const { error: err } = await racesApi.delete(token, id);
    if (err) {
      setError(err);
    } else if (race) {
      router.push(`/championships/${race.championship_id}/races`);
    }
  };

  const handleRemoveEntry = async (teamId: string) => {
    const { data, error: err } = await racesApi.removeEntry(token, id, teamId);
    if (err) {
      setError(err);
    } else {
      setEntries(data || []);
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
          <h1 className="text-3xl font-bold text-gray-900">{race.display_name}</h1>
          <p className="text-sm text-gray-500">{race.name}</p>
        </div>
        <div className="flex gap-2">
          <Link
            href={`/races/${id}/results`}
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            Results / Resultados
          </Link>
          <Link
            href={`/races/${id}/edit`}
            className="rounded bg-yellow-500 px-4 py-2 text-white hover:bg-yellow-600"
          >
            Edit / Editar
          </Link>
          <button
            onClick={handleDelete}
            className="rounded bg-red-600 px-4 py-2 text-white hover:bg-red-700"
          >
            Delete / Excluir
          </button>
        </div>
      </div>

      {/* Race details / Detalhes da corrida */}
      <div className="mb-8 rounded-lg border bg-white p-6">
        <dl className="grid grid-cols-2 gap-4">
          <div>
            <dt className="text-sm font-medium text-gray-500">Round Number / Numero da Rodada</dt>
            <dd className="text-lg text-gray-900">{race.round_number}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Status</dt>
            <dd>
              <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${STATUS_COLORS[race.status]}`}>
                {race.status}
              </span>
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Track / Pista</dt>
            <dd className="text-gray-900">
              {race.track_name || "—"}
              {race.track_country && ` (${race.track_country})`}
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Scheduled At / Agendado para</dt>
            <dd className="text-gray-900">
              {race.scheduled_at
                ? new Date(race.scheduled_at).toLocaleString()
                : "—"}
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Laps / Voltas</dt>
            <dd className="text-gray-900">{race.laps_total ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Active / Ativo</dt>
            <dd>
              <span
                className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                  race.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                }`}
              >
                {race.is_active ? "Yes / Sim" : "No / Nao"}
              </span>
            </dd>
          </div>
          <div className="col-span-2">
            <dt className="text-sm font-medium text-gray-500">Description / Descricao</dt>
            <dd className="text-gray-900">{race.description || "—"}</dd>
          </div>
        </dl>
      </div>

      {/* Enrolled teams / Equipes inscritas */}
      <h2 className="mb-4 text-xl font-bold text-gray-900">
        Enrolled Teams / Equipes Inscritas ({entries.length})
      </h2>

      {entries.length === 0 ? (
        <p className="text-gray-500">
          No teams enrolled. / Nenhuma equipe inscrita.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Team / Equipe
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Registered At / Inscrito em
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
              {entries.map((entry) => (
                <tr key={entry.team_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <p className="font-medium text-gray-900">{entry.team_display_name}</p>
                    <p className="text-sm text-gray-500">{entry.team_name}</p>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(entry.registered_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                        entry.team_is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                      }`}
                    >
                      {entry.team_is_active ? "Yes / Sim" : "No / Nao"}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleRemoveEntry(entry.team_id)}
                      className="text-sm text-red-600 hover:underline"
                    >
                      Remove / Remover
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-6">
        <Link href={`/championships/${race.championship_id}/races`} className="text-blue-600 hover:underline">
          &larr; Back to Races / Voltar as Corridas
        </Link>
      </div>
    </div>
  );
}
