"use client";

/**
 * Lap time chart: line chart showing lap times per driver.
 * Grafico de tempos de volta: grafico de linhas mostrando tempos por piloto.
 */

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { DriverComparison } from "@/types/telemetry";

const DRIVER_COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea"];

/**
 * Format milliseconds to mm:ss.mmm.
 * Formata milissegundos para mm:ss.mmm.
 */
function formatLapTime(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  const millis = ms % 1000;
  return `${minutes}:${String(seconds).padStart(2, "0")}.${String(millis).padStart(3, "0")}`;
}

interface LapTimeChartProps {
  comparisons: DriverComparison[];
}

export default function LapTimeChart({ comparisons }: LapTimeChartProps) {
  if (comparisons.length === 0) return null;

  // Build chart data: one entry per lap_number, with each driver's time as a key
  // Constroi dados do grafico: uma entrada por numero de volta, com tempo de cada piloto
  const allLapNumbers = new Set<number>();
  comparisons.forEach((c) => c.laps.forEach((l) => allLapNumbers.add(l.lap_number)));
  const sortedLaps = Array.from(allLapNumbers).sort((a, b) => a - b);

  const chartData = sortedLaps.map((lapNum) => {
    const entry: Record<string, number | string> = { lap: lapNum };
    comparisons.forEach((c) => {
      const lap = c.laps.find((l) => l.lap_number === lapNum);
      if (lap) {
        entry[c.driver_display_name] = lap.lap_time_ms;
      }
    });
    return entry;
  });

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Lap Times / Tempos de Volta
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 20 }}>
          <XAxis dataKey="lap" tick={{ fontSize: 12 }} label={{ value: "Lap / Volta", position: "insideBottom", offset: -2, fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} tickFormatter={(v: number) => formatLapTime(v)} width={80} />
          <Tooltip
            formatter={(value) => formatLapTime(Number(value))}
            labelFormatter={(label) => `Lap / Volta ${label}`}
          />
          <Legend />
          {comparisons.map((c, i) => (
            <Line
              key={c.driver_id}
              type="monotone"
              dataKey={c.driver_display_name}
              stroke={DRIVER_COLORS[i % DRIVER_COLORS.length]}
              strokeWidth={2}
              dot={{ r: 3 }}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
