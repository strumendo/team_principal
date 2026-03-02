"use client";

/**
 * Lap time table: displays lap times with sectors, validity, and personal best.
 * Tabela de tempos de volta: exibe tempos com setores, validade e melhor volta pessoal.
 */

import type { LapTime } from "@/types/telemetry";

/**
 * Format milliseconds to mm:ss.mmm.
 * Formata milissegundos para mm:ss.mmm.
 */
function formatMs(ms: number | null): string {
  if (ms === null) return "-";
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  const millis = ms % 1000;
  return `${minutes}:${String(seconds).padStart(2, "0")}.${String(millis).padStart(3, "0")}`;
}

interface LapTimeTableProps {
  laps: LapTime[];
  fastestLapMs?: number | null;
}

export default function LapTimeTable({ laps, fastestLapMs }: LapTimeTableProps) {
  if (laps.length === 0) {
    return (
      <p className="text-sm text-gray-500">
        No lap times recorded. / Nenhum tempo de volta registrado.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Lap / Volta
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Time / Tempo
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              S1
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              S2
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              S3
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Valid / Valida
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              PB
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {laps.map((lap) => {
            const isFastest = fastestLapMs !== null && fastestLapMs !== undefined && lap.lap_time_ms === fastestLapMs;
            return (
              <tr
                key={lap.id}
                className={
                  !lap.is_valid
                    ? "bg-red-50"
                    : isFastest || lap.is_personal_best
                      ? "bg-green-50"
                      : ""
                }
              >
                <td className="whitespace-nowrap px-4 py-2 text-sm font-medium text-gray-900">
                  {lap.lap_number}
                </td>
                <td className={`whitespace-nowrap px-4 py-2 text-sm font-mono ${isFastest ? "font-bold text-green-700" : "text-gray-900"}`}>
                  {formatMs(lap.lap_time_ms)}
                </td>
                <td className="whitespace-nowrap px-4 py-2 text-sm font-mono text-gray-600">
                  {formatMs(lap.sector_1_ms)}
                </td>
                <td className="whitespace-nowrap px-4 py-2 text-sm font-mono text-gray-600">
                  {formatMs(lap.sector_2_ms)}
                </td>
                <td className="whitespace-nowrap px-4 py-2 text-sm font-mono text-gray-600">
                  {formatMs(lap.sector_3_ms)}
                </td>
                <td className="whitespace-nowrap px-4 py-2 text-sm">
                  {lap.is_valid ? (
                    <span className="text-green-600">Yes / Sim</span>
                  ) : (
                    <span className="text-red-600">No / Nao</span>
                  )}
                </td>
                <td className="whitespace-nowrap px-4 py-2 text-sm">
                  {lap.is_personal_best && (
                    <span className="rounded bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-800">
                      PB
                    </span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
