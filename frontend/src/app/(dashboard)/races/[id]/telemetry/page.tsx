"use client";

/**
 * Race telemetry page: lap times chart, table, and summary.
 * Pagina de telemetria da corrida: grafico de tempos, tabela e resumo.
 */

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { LapTime, LapTimeSummary, DriverComparison } from "@/types/telemetry";
import { telemetryApi } from "@/lib/api-client";
import LapTimeChart from "@/components/telemetry/LapTimeChart";
import LapTimeTable from "@/components/telemetry/LapTimeTable";

export default function RaceTelemetryPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [summary, setSummary] = useState<LapTimeSummary | null>(null);
  const [laps, setLaps] = useState<LapTime[]>([]);
  const [selectedDriver, setSelectedDriver] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !id) return;

    const fetchData = async () => {
      setLoading(true);
      const [summaryResult, lapsResult] = await Promise.all([
        telemetryApi.getLapSummary(token, id),
        telemetryApi.listLaps(token, id),
      ]);

      if (summaryResult.error) {
        setError(summaryResult.error);
      } else {
        setSummary(summaryResult.data || null);
        setLaps(lapsResult.data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [session, id, token]);

  // Filter laps by selected driver / Filtra voltas pelo piloto selecionado
  const filteredLaps = selectedDriver
    ? laps.filter((l) => l.driver_id === selectedDriver)
    : laps;

  // Build chart data from all laps grouped by driver / Constroi dados do grafico
  const driverMap = new Map<string, { driver_id: string; driver_display_name: string; laps: LapTime[] }>();
  const displayLaps = selectedDriver ? laps.filter((l) => l.driver_id === selectedDriver) : laps;
  displayLaps.forEach((l) => {
    if (!driverMap.has(l.driver_id)) {
      const driverInfo = summary?.drivers.find((d) => d.driver_id === l.driver_id);
      driverMap.set(l.driver_id, {
        driver_id: l.driver_id,
        driver_display_name: driverInfo?.driver_display_name || l.driver_id,
        laps: [],
      });
    }
    driverMap.get(l.driver_id)!.laps.push(l);
  });
  const chartComparisons: DriverComparison[] = Array.from(driverMap.values());

  if (loading) return <p className="text-gray-500">Loading... / Carregando...</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <div>
      {/* Header / Cabecalho */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Telemetry / Telemetria</h1>
          <p className="text-sm text-gray-500">Race ID: {id}</p>
        </div>
        <div className="flex gap-2">
          <Link
            href={`/races/${id}/telemetry/compare`}
            className="rounded bg-purple-600 px-4 py-2 text-white hover:bg-purple-700"
          >
            Compare Drivers / Comparar Pilotos
          </Link>
          <Link
            href={`/races/${id}/setups`}
            className="rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700"
          >
            Setups
          </Link>
          <Link href={`/races/${id}`} className="rounded border px-4 py-2 text-gray-700 hover:bg-gray-50">
            &larr; Back / Voltar
          </Link>
        </div>
      </div>

      {/* Summary / Resumo */}
      {summary && summary.drivers.length > 0 && (
        <div className="mb-6 rounded-lg border bg-white p-4">
          <h2 className="mb-3 text-lg font-semibold text-gray-900">Summary / Resumo</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Driver / Piloto</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Fastest / Mais Rapida</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Avg / Media</th>
                  <th className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Laps / Voltas</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {summary.drivers.map((d) => (
                  <tr key={d.driver_id}>
                    <td className="whitespace-nowrap px-4 py-2 text-sm font-medium text-gray-900">
                      {d.driver_display_name}
                    </td>
                    <td className="whitespace-nowrap px-4 py-2 text-sm font-mono text-gray-700">
                      {formatMs(d.fastest_lap_ms)}
                    </td>
                    <td className="whitespace-nowrap px-4 py-2 text-sm font-mono text-gray-700">
                      {formatMs(d.avg_lap_ms)}
                    </td>
                    <td className="whitespace-nowrap px-4 py-2 text-sm text-gray-700">
                      {d.total_laps}
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

      {/* Chart / Grafico */}
      {chartComparisons.length > 0 && (
        <div className="mb-6">
          <LapTimeChart comparisons={chartComparisons} />
        </div>
      )}

      {/* Table / Tabela */}
      <div className="mb-6">
        <h2 className="mb-3 text-lg font-semibold text-gray-900">
          Lap Times / Tempos de Volta
        </h2>
        <LapTimeTable
          laps={filteredLaps}
          fastestLapMs={summary?.overall_fastest?.lap_time_ms}
        />
      </div>
    </div>
  );
}

function formatMs(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  const millis = ms % 1000;
  return `${minutes}:${String(seconds).padStart(2, "0")}.${String(millis).padStart(3, "0")}`;
}
