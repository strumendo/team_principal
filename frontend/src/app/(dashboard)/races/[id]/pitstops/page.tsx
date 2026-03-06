"use client";

/**
 * Race pit stops page: list, create, and view pit stop summary.
 * Pagina de pit stops da corrida: listar, criar e ver resumo de pit stops.
 */

import { useCallback, useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { PitStop as PitStopType, PitStopSummary, TireCompound } from "@/types/pitstops";
import type { DriverListItem } from "@/types/driver";
import { pitstopsApi, driversApi } from "@/lib/api-client";
import PitStopTable from "@/components/pitstops/PitStopTable";
import PitStopForm from "@/components/pitstops/PitStopForm";

export default function RacePitStopsPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [pitStops, setPitStops] = useState<PitStopType[]>([]);
  const [summary, setSummary] = useState<PitStopSummary | null>(null);
  const [drivers, setDrivers] = useState<DriverListItem[]>([]);
  const [selectedDriver, setSelectedDriver] = useState<string>("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  const fetchData = useCallback(async () => {
    setLoading(true);
    const [pitsResult, summaryResult, driversResult] = await Promise.all([
      pitstopsApi.list(token, id),
      pitstopsApi.getSummary(token, id),
      driversApi.list(token),
    ]);

    if (pitsResult.error) {
      setError(pitsResult.error);
    } else {
      setPitStops(pitsResult.data || []);
      setSummary(summaryResult.data || null);
      setDrivers(driversResult.data || []);
      setError(null);
    }
    setLoading(false);
  }, [token, id]);

  useEffect(() => {
    if (!session || !id) return;
    fetchData();
  }, [session, id, fetchData]);

  const handleCreate = async (data: {
    driver_id: string;
    team_id: string;
    lap_number: number;
    duration_ms: number;
    tire_from?: TireCompound;
    tire_to?: TireCompound;
    notes?: string;
  }) => {
    setSaving(true);
    const { error: err } = await pitstopsApi.create(token, id, data);
    setSaving(false);
    if (err) {
      setError(err);
    } else {
      setShowForm(false);
      await fetchData();
    }
  };

  const handleDelete = async (pitStopId: string) => {
    if (!confirm("Delete this pit stop? / Excluir este pit stop?")) return;
    const { error: err } = await pitstopsApi.delete(token, pitStopId);
    if (err) {
      setError(err);
    } else {
      await fetchData();
    }
  };

  const filteredPitStops = selectedDriver
    ? pitStops.filter((ps) => ps.driver_id === selectedDriver)
    : pitStops;

  if (loading) return <p className="text-gray-500">Loading... / Carregando...</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <div>
      {/* Header / Cabecalho */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pit Stops</h1>
          <p className="text-sm text-gray-500">Race ID: {id}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded bg-orange-600 px-4 py-2 text-white hover:bg-orange-700"
          >
            {showForm ? "Cancel / Cancelar" : "Add Pit Stop / Adicionar Pit Stop"}
          </button>
          <Link
            href={`/races/${id}/strategies`}
            className="rounded bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700"
          >
            Strategies / Estrategias
          </Link>
          <Link href={`/races/${id}`} className="rounded border px-4 py-2 text-gray-700 hover:bg-gray-50">
            &larr; Back / Voltar
          </Link>
        </div>
      </div>

      {/* Form / Formulario */}
      {showForm && (
        <div className="mb-6">
          <PitStopForm
            drivers={drivers.map((d) => ({ id: d.id, display_name: d.display_name, team_id: d.team_id || "" }))}
            onSubmit={handleCreate}
            onCancel={() => setShowForm(false)}
            saving={saving}
          />
        </div>
      )}

      {/* Summary / Resumo */}
      {summary && summary.drivers.length > 0 && (
        <div className="mb-6 rounded-lg border bg-white p-4">
          <h2 className="mb-3 text-lg font-semibold text-gray-900">Summary / Resumo</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Driver / Piloto</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Total Stops / Paradas</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Avg Duration / Media</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Fastest / Mais Rapida</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {summary.drivers.map((d) => (
                  <tr key={d.driver_id}>
                    <td className="whitespace-nowrap px-4 py-2 text-sm font-medium text-gray-900">
                      {d.driver_display_name}
                    </td>
                    <td className="whitespace-nowrap px-4 py-2 text-sm text-gray-700">
                      {d.total_stops}
                    </td>
                    <td className="whitespace-nowrap px-4 py-2 text-sm font-mono text-gray-700">
                      {(d.avg_duration_ms / 1000).toFixed(3)}s
                    </td>
                    <td className="whitespace-nowrap px-4 py-2 text-sm font-mono text-gray-700">
                      {(d.fastest_pit_ms / 1000).toFixed(3)}s
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Driver filter / Filtro por piloto */}
      {summary && summary.drivers.length > 0 && (
        <div className="mb-4">
          <label className="mr-2 text-sm font-medium text-gray-700">
            Filter by Driver / Filtrar por Piloto:
          </label>
          <select
            value={selectedDriver}
            onChange={(e) => setSelectedDriver(e.target.value)}
            className="rounded border px-3 py-1.5 text-sm"
          >
            <option value="">All Drivers / Todos os Pilotos</option>
            {summary.drivers.map((d) => (
              <option key={d.driver_id} value={d.driver_id}>
                {d.driver_display_name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Table / Tabela */}
      <div className="mb-6">
        <h2 className="mb-3 text-lg font-semibold text-gray-900">
          Pit Stops ({filteredPitStops.length})
        </h2>
        <PitStopTable pitStops={filteredPitStops} onDelete={handleDelete} />
      </div>
    </div>
  );
}
