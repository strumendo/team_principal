/**
 * Championship create form page.
 * Pagina de formulario de criacao de campeonato.
 */
"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { championshipsApi } from "@/lib/api-client";

export default function CreateChampionshipPage() {
  const { data: session } = useSession();
  const router = useRouter();

  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [seasonYear, setSeasonYear] = useState(new Date().getFullYear());
  const [status, setStatus] = useState("planned");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
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
      season_year: seasonYear,
      status,
    };
    if (description) payload.description = description;
    if (startDate) payload.start_date = startDate;
    if (endDate) payload.end_date = endDate;

    const { error: err } = await championshipsApi.create(
      token,
      payload as Parameters<typeof championshipsApi.create>[1],
    );

    if (err) {
      setError(err);
      setSubmitting(false);
    } else {
      router.push("/championships");
    }
  };

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-3xl font-bold text-gray-900">
        New Championship / Novo Campeonato
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
            placeholder="e.g. formula_e_2026"
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
            placeholder="e.g. Formula E 2026"
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

        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={submitting}
            className="rounded bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? "Creating... / Criando..." : "Create / Criar"}
          </button>
          <Link
            href="/championships"
            className="rounded border px-6 py-2 text-gray-700 hover:bg-gray-50"
          >
            Cancel / Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
}
