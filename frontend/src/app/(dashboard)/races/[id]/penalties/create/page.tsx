/**
 * Create penalty page.
 * Pagina de criacao de penalidade.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import type { RaceDetail } from "@/types/race";
import type { RaceResult } from "@/types/result";
import { racesApi, resultsApi, penaltiesApi, driversApi } from "@/lib/api-client";
import type { DriverListItem } from "@/types/driver";

export default function CreatePenaltyPage() {
  const { data: session } = useSession();
  const params = useParams();
  const router = useRouter();
  const raceId = params.id as string;

  const [race, setRace] = useState<RaceDetail | null>(null);
  const [results, setResults] = useState<RaceResult[]>([]);
  const [drivers, setDrivers] = useState<DriverListItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Form state / Estado do formulario
  const [teamId, setTeamId] = useState("");
  const [driverId, setDriverId] = useState("");
  const [resultId, setResultId] = useState("");
  const [penaltyType, setPenaltyType] = useState("");
  const [reason, setReason] = useState("");
  const [pointsDeducted, setPointsDeducted] = useState("");
  const [timePenaltySeconds, setTimePenaltySeconds] = useState("");
  const [lapNumber, setLapNumber] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !raceId) return;

    const fetchData = async () => {
      setLoading(true);
      const [raceResult, resultsResult, driversResult] = await Promise.all([
        racesApi.get(token, raceId),
        resultsApi.listByRace(token, raceId),
        driversApi.list(token),
      ]);

      if (raceResult.error) {
        setError(raceResult.error);
      } else {
        setRace(raceResult.data || null);
        setResults(resultsResult.data || []);
        setDrivers(driversResult.data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [session, raceId, token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!session) return;

    setSubmitting(true);
    setError(null);

    const payload: {
      team_id: string;
      penalty_type: string;
      reason: string;
      driver_id?: string;
      result_id?: string;
      points_deducted?: number;
      time_penalty_seconds?: number;
      lap_number?: number;
    } = {
      team_id: teamId,
      penalty_type: penaltyType,
      reason,
    };

    if (driverId) payload.driver_id = driverId;
    if (resultId) payload.result_id = resultId;
    if (pointsDeducted) payload.points_deducted = parseFloat(pointsDeducted);
    if (timePenaltySeconds) payload.time_penalty_seconds = parseInt(timePenaltySeconds);
    if (lapNumber) payload.lap_number = parseInt(lapNumber);

    const { error: err } = await penaltiesApi.create(token, raceId, payload);

    if (err) {
      setError(err);
      setSubmitting(false);
    } else {
      router.push(`/races/${raceId}/penalties`);
    }
  };

  if (loading) {
    return <p className="text-gray-500">Loading... / Carregando...</p>;
  }

  if (!race) {
    return <p className="text-gray-500">Race not found. / Corrida nao encontrada.</p>;
  }

  // Filter drivers by selected team / Filtra pilotos pela equipe selecionada
  const filteredDrivers = teamId
    ? drivers.filter((d) => d.team_id === teamId)
    : drivers;

  // Filter results by selected team / Filtra resultados pela equipe selecionada
  const filteredResults = teamId
    ? results.filter((r) => r.team_id === teamId)
    : results;

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-3xl font-bold text-gray-900">
        New Penalty / Nova Penalidade — {race.display_name}
      </h1>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Team / Equipe */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Team / Equipe *
          </label>
          <select
            value={teamId}
            onChange={(e) => {
              setTeamId(e.target.value);
              setDriverId("");
              setResultId("");
            }}
            required
            className="mt-1 w-full rounded border px-3 py-2"
          >
            <option value="">Select team / Selecione a equipe</option>
            {race.teams.map((team) => (
              <option key={team.id} value={team.id}>
                {team.display_name}
              </option>
            ))}
          </select>
        </div>

        {/* Driver / Piloto */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Driver / Piloto
          </label>
          <select
            value={driverId}
            onChange={(e) => setDriverId(e.target.value)}
            className="mt-1 w-full rounded border px-3 py-2"
          >
            <option value="">None / Nenhum</option>
            {filteredDrivers.map((driver) => (
              <option key={driver.id} value={driver.id}>
                {driver.display_name} ({driver.abbreviation})
              </option>
            ))}
          </select>
        </div>

        {/* Result / Resultado */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Race Result / Resultado da Corrida
          </label>
          <select
            value={resultId}
            onChange={(e) => setResultId(e.target.value)}
            className="mt-1 w-full rounded border px-3 py-2"
          >
            <option value="">None / Nenhum</option>
            {filteredResults.map((result) => (
              <option key={result.id} value={result.id}>
                P{result.position} — {result.points} pts
              </option>
            ))}
          </select>
        </div>

        {/* Penalty Type / Tipo de Penalidade */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Penalty Type / Tipo de Penalidade *
          </label>
          <select
            value={penaltyType}
            onChange={(e) => setPenaltyType(e.target.value)}
            required
            className="mt-1 w-full rounded border px-3 py-2"
          >
            <option value="">Select type / Selecione o tipo</option>
            <option value="warning">Warning / Advertencia</option>
            <option value="time_penalty">Time Penalty / Penalidade de Tempo</option>
            <option value="points_deduction">Points Deduction / Deducao de Pontos</option>
            <option value="disqualification">Disqualification / Desclassificacao</option>
            <option value="grid_penalty">Grid Penalty / Penalidade de Grid</option>
          </select>
        </div>

        {/* Reason / Razao */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Reason / Razao *
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            required
            rows={3}
            className="mt-1 w-full rounded border px-3 py-2"
            placeholder="Describe the incident / Descreva o incidente"
          />
        </div>

        {/* Points Deducted / Pontos Deduzidos (conditional) */}
        {(penaltyType === "points_deduction" || penaltyType === "disqualification") && (
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Points Deducted / Pontos Deduzidos
            </label>
            <input
              type="number"
              step="0.5"
              min="0"
              value={pointsDeducted}
              onChange={(e) => setPointsDeducted(e.target.value)}
              className="mt-1 w-full rounded border px-3 py-2"
              placeholder="0.0"
            />
          </div>
        )}

        {/* Time Penalty Seconds / Segundos de Penalidade (conditional) */}
        {penaltyType === "time_penalty" && (
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Time Penalty (seconds) / Penalidade de Tempo (segundos)
            </label>
            <input
              type="number"
              min="1"
              value={timePenaltySeconds}
              onChange={(e) => setTimePenaltySeconds(e.target.value)}
              className="mt-1 w-full rounded border px-3 py-2"
              placeholder="5"
            />
          </div>
        )}

        {/* Lap Number / Numero da Volta */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Lap Number / Numero da Volta
          </label>
          <input
            type="number"
            min="1"
            value={lapNumber}
            onChange={(e) => setLapNumber(e.target.value)}
            className="mt-1 w-full rounded border px-3 py-2"
            placeholder="Optional / Opcional"
          />
        </div>

        {/* Buttons / Botoes */}
        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={submitting}
            className="rounded bg-orange-600 px-6 py-2 text-white hover:bg-orange-700 disabled:opacity-50"
          >
            {submitting ? "Creating... / Criando..." : "Create Penalty / Criar Penalidade"}
          </button>
          <Link
            href={`/races/${raceId}/penalties`}
            className="rounded border px-6 py-2 text-gray-700 hover:bg-gray-50"
          >
            Cancel / Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
}
