"use client";

/**
 * Stint table: breakdown of stint performance per driver.
 * Tabela de stints: detalhamento de desempenho por stint de cada piloto.
 */

import type { StintAnalysisResponse } from "@/types/race-replay";

const COMPOUND_COLORS: Record<string, string> = {
  soft: "bg-red-100 text-red-800",
  medium: "bg-yellow-100 text-yellow-800",
  hard: "bg-gray-100 text-gray-800",
  intermediate: "bg-green-100 text-green-800",
  wet: "bg-blue-100 text-blue-800",
};

function formatTime(ms: number | null): string {
  if (ms === null) return "—";
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  const millis = ms % 1000;
  return `${minutes}:${String(seconds).padStart(2, "0")}.${String(millis).padStart(3, "0")}`;
}

function formatDeg(ms: number | null): string {
  if (ms === null) return "—";
  const sign = ms >= 0 ? "+" : "";
  return `${sign}${(ms / 1000).toFixed(1)}s`;
}

interface StintTableProps {
  data: StintAnalysisResponse;
}

export default function StintTable({ data }: StintTableProps) {
  if (data.drivers.length === 0) {
    return (
      <p className="text-sm text-gray-500">
        No stint data available. / Nenhum dado de stint disponivel.
      </p>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Stint Analysis / Analise de Stints
      </h3>
      {data.drivers.map((driver) => (
        <div key={driver.driver_id} className="mb-4">
          <h4 className="mb-2 text-sm font-medium text-gray-800">{driver.driver_name}</h4>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Stint</th>
                  <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Compound / Composto</th>
                  <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Laps / Voltas</th>
                  <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Avg Pace / Ritmo Medio</th>
                  <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Best / Melhor</th>
                  <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Degradation / Degradacao</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {driver.stints.map((stint) => (
                  <tr key={stint.stint_number} className="hover:bg-gray-50">
                    <td className="px-3 py-2">{stint.stint_number}</td>
                    <td className="px-3 py-2">
                      {stint.compound ? (
                        <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${COMPOUND_COLORS[stint.compound] || "bg-gray-100"}`}>
                          {stint.compound}
                        </span>
                      ) : "—"}
                    </td>
                    <td className="px-3 py-2">{stint.start_lap}–{stint.end_lap} ({stint.total_laps})</td>
                    <td className="px-3 py-2">{formatTime(stint.avg_pace_ms)}</td>
                    <td className="px-3 py-2">{formatTime(stint.best_lap_ms)}</td>
                    <td className="px-3 py-2">{formatDeg(stint.degradation_ms)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
