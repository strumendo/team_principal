/**
 * Race create form page (scoped to championship).
 * Pagina de formulario de criacao de corrida (vinculada ao campeonato).
 */
"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { racesApi } from "@/lib/api-client";

export default function CreateRacePage() {
  const { data: session } = useSession();
  const params = useParams();
  const router = useRouter();
  const championshipId = params.id as string;

  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [roundNumber, setRoundNumber] = useState(1);
  const [status, setStatus] = useState("scheduled");
  const [scheduledAt, setScheduledAt] = useState("");
  const [trackName, setTrackName] = useState("");
  const [trackCountry, setTrackCountry] = useState("");
  const [lapsTotal, setLapsTotal] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!session) return;

    setSubmitting(true);
    setError(null);

    const token = (session as unknown as { accessToken: string }).accessToken;
    const payload: Record<string, unknown> = {
      name,
      display_name: displayName,
      round_number: roundNumber,
      status,
    };
    if (description) payload.description = description;
    if (scheduledAt) payload.scheduled_at = new Date(scheduledAt).toISOString();
    if (trackName) payload.track_name = trackName;
    if (trackCountry) payload.track_country = trackCountry;
    if (lapsTotal) payload.laps_total = parseInt(lapsTotal);

    const { error: err } = await racesApi.create(
      token,
      championshipId,
      payload as Parameters<typeof racesApi.create>[2],
    );

    if (err) {
      setError(err);
      setSubmitting(false);
    } else {
      router.push(`/championships/${championshipId}/races`);
    }
  };

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-3xl font-bold text-gray-900">
        New Race / Nova Corrida
      </h1>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Name (slug) / Nome (slug)
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="mt-1 w-full rounded border px-3 py-2"
            placeholder="e.g. round_01_monza"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Display Name / Nome de Exibicao
          </label>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            required
            className="mt-1 w-full rounded border px-3 py-2"
            placeholder="e.g. Round 1 - Monza"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Description / Descricao
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="mt-1 w-full rounded border px-3 py-2"
            rows={3}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Round Number / Numero da Rodada
          </label>
          <input
            type="number"
            value={roundNumber}
            onChange={(e) => setRoundNumber(parseInt(e.target.value))}
            required
            min={1}
            className="mt-1 w-32 rounded border px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Status
          </label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="mt-1 rounded border px-3 py-2"
          >
            <option value="scheduled">Scheduled / Agendada</option>
            <option value="qualifying">Qualifying / Classificacao</option>
            <option value="active">Active / Ativa</option>
            <option value="finished">Finished / Finalizada</option>
            <option value="cancelled">Cancelled / Cancelada</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Scheduled At / Agendado para
          </label>
          <input
            type="datetime-local"
            value={scheduledAt}
            onChange={(e) => setScheduledAt(e.target.value)}
            className="mt-1 w-full rounded border px-3 py-2"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Track Name / Nome da Pista
            </label>
            <input
              type="text"
              value={trackName}
              onChange={(e) => setTrackName(e.target.value)}
              className="mt-1 w-full rounded border px-3 py-2"
              placeholder="e.g. Autodromo di Monza"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Track Country / Pais da Pista
            </label>
            <input
              type="text"
              value={trackCountry}
              onChange={(e) => setTrackCountry(e.target.value)}
              className="mt-1 w-full rounded border px-3 py-2"
              placeholder="e.g. Italy"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Total Laps / Total de Voltas
          </label>
          <input
            type="number"
            value={lapsTotal}
            onChange={(e) => setLapsTotal(e.target.value)}
            min={1}
            className="mt-1 w-32 rounded border px-3 py-2"
          />
        </div>

        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={submitting}
            className="rounded bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? "Creating... / Criando..." : "Create / Criar"}
          </button>
          <Link
            href={`/championships/${championshipId}/races`}
            className="rounded border px-6 py-2 text-gray-700 hover:bg-gray-50"
          >
            Cancel / Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
}
