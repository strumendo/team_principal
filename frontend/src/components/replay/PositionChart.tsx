"use client";

/**
 * Position chart: line chart showing position per lap for each driver.
 * Grafico de posicao: grafico de linhas mostrando posicao por volta para cada piloto.
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

interface PositionChartProps {
  laps: ReplayLapData[];
  filterDriverId?: string;
}

export default function PositionChart({ laps, filterDriverId }: PositionChartProps) {
  if (laps.length === 0) {
    return (
      <p className="text-sm text-gray-500">
        No position data available. / Nenhum dado de posicao disponivel.
      </p>
    );
  }

  // Collect all driver names / Coleta todos os nomes de pilotos
  const driverNames = new Map<string, string>();
  laps.forEach((lap) =>
    lap.positions.forEach((p) => {
      if (!filterDriverId || p.driver_id === filterDriverId) {
        driverNames.set(p.driver_id, p.driver_name);
      }
    }),
  );

  const chartData = laps.map((lap) => {
    const entry: Record<string, number | string> = { lap: lap.lap_number };
    lap.positions.forEach((p) => {
      if (!filterDriverId || p.driver_id === filterDriverId) {
        entry[p.driver_name] = p.position;
      }
    });
    return entry;
  });

  const drivers = Array.from(driverNames.entries());

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Position Chart / Grafico de Posicao
      </h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 20 }}>
          <XAxis
            dataKey="lap"
            tick={{ fontSize: 12 }}
            label={{ value: "Lap / Volta", position: "insideBottom", offset: -2, fontSize: 12 }}
          />
          <YAxis
            reversed
            tick={{ fontSize: 12 }}
            label={{ value: "Position / Posicao", angle: -90, position: "insideLeft", fontSize: 12 }}
            domain={[1, "dataMax"]}
            allowDecimals={false}
          />
          <Tooltip labelFormatter={(label) => `Lap / Volta ${label}`} />
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
