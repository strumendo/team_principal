/**
 * Championship edit form page.
 * Pagina de formulario de edicao de campeonato.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { championshipsApi } from "@/lib/api-client";

export default function EditChampionshipPage() {
  const { data: session } = useSession();
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [seasonYear, setSeasonYear] = useState(2026);
  const [status, setStatus] = useState("planned");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !id) return;

    const fetchChampionship = async () => {
      const { data, error: err } = await championshipsApi.get(token, id);
      if (err) {
        setError(err);
      } else if (data) {
        setDisplayName(data.display_name);
        setDescription(data.description || "");
        setSeasonYear(data.season_year);
        setStatus(data.status);
        setStartDate(data.start_date || "");
        setEndDate(data.end_date || "");
        setIsActive(data.is_active);
      }
      setLoading(false);
    };

    fetchChampionship();
  }, [session, id, token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!session) return;

    setSubmitting(true);
    setError(null);

    const payload: Record<string, unknown> = {
      display_name: displayName,
      season_year: seasonYear,
      status,
      is_active: isActive,
    };
    if (description) payload.description = description;
    if (startDate) payload.start_date = startDate;
    if (endDate) payload.end_date = endDate;

    const { error: err } = await championshipsApi.update(
      token,
      id,
      payload as Parameters<typeof championshipsApi.update>[2],
    );

    if (err) {
      setError(err);
      setSubmitting(false);
    } else {
      router.push(`/championships/${id}`);
    }
  };

  if (loading) {
    return <p className="text-gray-500">Loading... / Carregando...</p>;
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-3xl font-bold text-gray-900">
        Edit Championship / Editar Campeonato
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
            Season Year / Ano da Temporada
          </label>
          <input
            type="number"
            value={seasonYear}
            onChange={(e) => setSeasonYear(parseInt(e.target.value))}
            required
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
            <option value="planned">Planned / Planejado</option>
            <option value="active">Active / Ativo</option>
            <option value="completed">Completed / Concluido</option>
            <option value="cancelled">Cancelled / Cancelado</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Start Date / Data Inicio
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="mt-1 w-full rounded border px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              End Date / Data Fim
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="mt-1 w-full rounded border px-3 py-2"
            />
          </div>
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
            href={`/championships/${id}`}
            className="rounded border px-6 py-2 text-gray-700 hover:bg-gray-50"
          >
            Cancel / Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
}
