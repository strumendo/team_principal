"use client";

/**
 * Driver comparison page: compare lap times for up to 3 drivers.
 * Pagina de comparacao: compara tempos de volta de ate 3 pilotos.
 */

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { LapTimeSummary, DriverComparison } from "@/types/telemetry";
import type { DriverListItem } from "@/types/driver";
import { telemetryApi, driversApi } from "@/lib/api-client";
import LapTimeChart from "@/components/telemetry/LapTimeChart";

function formatMs(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  const millis = ms % 1000;
  return `${minutes}:${String(seconds).padStart(2, "0")}.${String(millis).padStart(3, "0")}`;
}

export default function CompareDriversPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [drivers, setDrivers] = useState<DriverListItem[]>([]);
  const [summary, setSummary] = useState<LapTimeSummary | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [comparisons, setComparisons] = useState<DriverComparison[]>([]);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !id) return;

    const fetchData = async () => {
      setLoading(true);
      const [driversResult, summaryResult] = await Promise.all([
        driversApi.list(token, { is_active: true }),
        telemetryApi.getLapSummary(token, id),
      ]);

      if (driversResult.error) {
        setError(driversResult.error);
      } else {
        setDrivers(driversResult.data || []);
        setSummary(summaryResult.data || null);
        setError(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [session, id, token]);

  const handleToggleDriver = (driverId: string) => {
    setSelectedIds((prev) => {
      if (prev.includes(driverId)) {
        return prev.filter((id) => id !== driverId);
      }
      if (prev.length >= 3) return prev;
      return [...prev, driverId];
    });
  };

  const handleCompare = async () => {
    if (selectedIds.length === 0) return;
    setComparing(true);
    setError(null);

    const { data, error: err } = await telemetryApi.compareDrivers(token, id, selectedIds);
    if (err) {
      setError(err);
    } else {
      setComparisons(data || []);
    }
    setComparing(false);
  };

  // Filter drivers to only show those with laps in this race
  // Filtra pilotos que tem voltas nesta corrida
  const driversWithLaps = summary
    ? drivers.filter((d) => summary.drivers.some((sd) => sd.driver_id === d.id))
    : drivers;

  if (loading) return <p className="text-gray-500">Loading... / Carregando...</p>;

  return (
    <div>
      {/* Header / Cabecalho */}
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Compare Drivers / Comparar Pilotos
        </h1>
        <Link href={`/races/${id}/telemetry`} className="rounded border px-4 py-2 text-gray-700 hover:bg-gray-50">
          &larr; Back to Telemetry / Voltar para Telemetria
        </Link>
      </div>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      {/* Driver selection / Selecao de pilotos */}
      <div className="mb-6 rounded-lg border bg-white p-4">
        <h2 className="mb-3 text-lg font-semibold text-gray-900">
          Select Drivers (max 3) / Selecione Pilotos (max 3)
        </h2>
        <div className="mb-3 flex flex-wrap gap-2">
          {driversWithLaps.map((d) => {
            const isSelected = selectedIds.includes(d.id);
            return (
              <button
                key={d.id}
                onClick={() => handleToggleDriver(d.id)}
                className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                  isSelected
                    ? "border-blue-600 bg-blue-600 text-white"
                    : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
                } ${!isSelected && selectedIds.length >= 3 ? "cursor-not-allowed opacity-50" : ""}`}
                disabled={!isSelected && selectedIds.length >= 3}
              >
                {d.display_name} ({d.abbreviation})
              </button>
            );
          })}
          {driversWithLaps.length === 0 && (
            <p className="text-sm text-gray-500">
              No drivers with lap data. / Nenhum piloto com dados de volta.
            </p>
          )}
        </div>
        <button
          onClick={handleCompare}
          disabled={selectedIds.length === 0 || comparing}
          className="rounded bg-purple-600 px-4 py-2 text-white hover:bg-purple-700 disabled:opacity-50"
        >
          {comparing ? "Comparing... / Comparando..." : "Compare / Comparar"}
        </button>
      </div>

      {/* Chart / Grafico */}
      {comparisons.length > 0 && (
        <div className="mb-6">
          <LapTimeChart comparisons={comparisons} />
        </div>
      )}

      {/* Summary stats table / Tabela de estatisticas */}
      {comparisons.length > 0 && (
        <div className="rounded-lg border bg-white p-4">
          <h2 className="mb-3 text-lg font-semibold text-gray-900">
            Comparison Stats / Estatisticas de Comparacao
          </h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">
                    Driver / Piloto
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">
                    Fastest / Mais Rapida
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">
                    Avg / Media
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">
                    Total Laps / Total de Voltas
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {comparisons.map((c) => {
                  const times = c.laps.map((l) => l.lap_time_ms);
                  const fastest = times.length > 0 ? Math.min(...times) : 0;
                  const avg = times.length > 0 ? Math.round(times.reduce((a, b) => a + b, 0) / times.length) : 0;
                  return (
                    <tr key={c.driver_id}>
                      <td className="whitespace-nowrap px-4 py-2 text-sm font-medium text-gray-900">
                        {c.driver_display_name}
                      </td>
                      <td className="whitespace-nowrap px-4 py-2 text-sm font-mono text-gray-700">
                        {times.length > 0 ? formatMs(fastest) : "-"}
                      </td>
                      <td className="whitespace-nowrap px-4 py-2 text-sm font-mono text-gray-700">
                        {times.length > 0 ? formatMs(avg) : "-"}
                      </td>
                      <td className="whitespace-nowrap px-4 py-2 text-sm text-gray-700">
                        {c.laps.length}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
