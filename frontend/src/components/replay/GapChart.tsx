"use client";

/**
 * Gap chart: line chart showing gap to leader per lap for each driver.
 * Grafico de gap: grafico de linhas mostrando gap para o lider por volta para cada piloto.
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
import type { ReplayLapData } from "@/types/race-replay";

const DRIVER_COLORS = [
  "#2563eb", "#dc2626", "#16a34a", "#9333ea",
  "#ea580c", "#0891b2", "#be185d", "#65a30d",
];

function formatGap(ms: number): string {
  const seconds = (ms / 1000).toFixed(1);
  return `+${seconds}s`;
}

interface GapChartProps {
  laps: ReplayLapData[];
  filterDriverId?: string;
}

export default function GapChart({ laps, filterDriverId }: GapChartProps) {
  if (laps.length === 0) {
    return (
      <p className="text-sm text-gray-500">
        No gap data available. / Nenhum dado de gap disponivel.
      </p>
    );
  }

  const driverNames = new Map<string, string>();
  laps.forEach((lap) =>
    lap.positions.forEach((p) => {
      if ((!filterDriverId || p.driver_id === filterDriverId) && p.gap_to_leader_ms !== null) {
        driverNames.set(p.driver_id, p.driver_name);
      }
    }),
  );

  const chartData = laps.map((lap) => {
    const entry: Record<string, number | string> = { lap: lap.lap_number };
    lap.positions.forEach((p) => {
      if ((!filterDriverId || p.driver_id === filterDriverId) && p.gap_to_leader_ms !== null) {
        entry[p.driver_name] = p.gap_to_leader_ms;
      }
    });
    return entry;
  });

  const drivers = Array.from(driverNames.entries());

  if (drivers.length === 0) {
    return (
      <p className="text-sm text-gray-500">
        No gap data available. / Nenhum dado de gap disponivel.
      </p>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Gap to Leader / Gap para o Lider
      </h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 20 }}>
          <XAxis
            dataKey="lap"
            tick={{ fontSize: 12 }}
            label={{ value: "Lap / Volta", position: "insideBottom", offset: -2, fontSize: 12 }}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            tickFormatter={(v: number) => formatGap(v)}
            width={70}
          />
          <Tooltip
            formatter={(value) => formatGap(Number(value))}
            labelFormatter={(label) => `Lap / Volta ${label}`}
          />
          <Legend />
          {drivers.map(([, name], i) => (
            <Line
              key={name}
              type="monotone"
              dataKey={name}
              stroke={DRIVER_COLORS[i % DRIVER_COLORS.length]}
              strokeWidth={2}
              dot={{ r: 2 }}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
