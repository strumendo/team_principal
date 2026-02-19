/**
 * Race edit form page.
 * Pagina de formulario de edicao de corrida.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { racesApi } from "@/lib/api-client";

export default function EditRacePage() {
  const { data: session } = useSession();
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [roundNumber, setRoundNumber] = useState(1);
  const [status, setStatus] = useState("scheduled");
  const [scheduledAt, setScheduledAt] = useState("");
  const [trackName, setTrackName] = useState("");
  const [trackCountry, setTrackCountry] = useState("");
  const [lapsTotal, setLapsTotal] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !id) return;

    const fetchRace = async () => {
      const { data, error: err } = await racesApi.get(token, id);
      if (err) {
        setError(err);
      } else if (data) {
        setDisplayName(data.display_name);
        setDescription(data.description || "");
        setRoundNumber(data.round_number);
        setStatus(data.status);
        setScheduledAt(
          data.scheduled_at
            ? new Date(data.scheduled_at).toISOString().slice(0, 16)
            : ""
        );
        setTrackName(data.track_name || "");
        setTrackCountry(data.track_country || "");
        setLapsTotal(data.laps_total ? String(data.laps_total) : "");
        setIsActive(data.is_active);
      }
      setLoading(false);
    };

    fetchRace();
  }, [session, id, token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!session) return;

    setSubmitting(true);
    setError(null);

    const payload: Record<string, unknown> = {
      display_name: displayName,
      round_number: roundNumber,
      status,
      is_active: isActive,
    };
    if (description) payload.description = description;
    if (scheduledAt) payload.scheduled_at = new Date(scheduledAt).toISOString();
    if (trackName) payload.track_name = trackName;
    if (trackCountry) payload.track_country = trackCountry;
    if (lapsTotal) payload.laps_total = parseInt(lapsTotal);

    const { error: err } = await racesApi.update(
      token,
      id,
      payload as Parameters<typeof racesApi.update>[2],
    );

    if (err) {
      setError(err);
      setSubmitting(false);
    } else {
      router.push(`/races/${id}`);
    }
  };

  if (loading) {
    return <p className="text-gray-500">Loading... / Carregando...</p>;
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-3xl font-bold text-gray-900">
        Edit Race / Editar Corrida
      </h1>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      <form onSubmit={handleSubmit} className="space-y-4">
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

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="isActive"
            checked={isActive}
            onChange={(e) => setIsActive(e.target.checked)}
            className="h-4 w-4"
          />
          <label htmlFor="isActive" className="text-sm font-medium text-gray-700">
            Active / Ativo
          </label>
        </div>

        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={submitting}
            className="rounded bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? "Saving... / Salvando..." : "Save / Salvar"}
          </button>
          <Link
            href={`/races/${id}`}
            className="rounded border px-6 py-2 text-gray-700 hover:bg-gray-50"
          >
            Cancel / Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
}
