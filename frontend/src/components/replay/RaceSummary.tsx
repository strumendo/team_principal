"use client";

/**
 * Race summary: stats cards grid.
 * Resumo da corrida: grid de cards de estatisticas.
 */

import type { RaceSummaryResponse } from "@/types/race-replay";

function formatTime(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  const millis = ms % 1000;
  return `${minutes}:${String(seconds).padStart(2, "0")}.${String(millis).padStart(3, "0")}`;
}

interface RaceSummaryProps {
  data: RaceSummaryResponse;
}

export default function RaceSummary({ data }: RaceSummaryProps) {
  const stats = [
    { label: "Total Laps / Voltas Totais", value: data.total_laps },
    { label: "Overtakes / Ultrapassagens", value: data.total_overtakes },
    { label: "Leader Changes / Mudancas de Lider", value: data.leader_changes },
    { label: "Safety Car Laps / Voltas de SC", value: data.safety_car_laps },
    { label: "DNFs", value: data.dnf_count },
  ];

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Race Summary / Resumo da Corrida
      </h3>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-lg border border-gray-100 bg-gray-50 p-3 text-center">
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            <p className="text-xs text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>
      {data.fastest_lap && (
        <div className="mt-4 rounded-lg border border-purple-100 bg-purple-50 p-3">
          <p className="text-sm font-medium text-purple-800">
            Fastest Lap / Volta Mais Rapida
          </p>
          <p className="text-lg font-bold text-purple-900">
            {formatTime(data.fastest_lap.lap_time_ms)}
          </p>
          <p className="text-xs text-purple-700">
            {data.fastest_lap.driver_name} — Lap / Volta {data.fastest_lap.lap_number}
          </p>
        </div>
      )}
    </div>
  );
}
