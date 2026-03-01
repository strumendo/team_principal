/**
 * Bar chart showing races distribution per month.
 * Grafico de barras mostrando distribuicao de corridas por mes.
 */
"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { DashboardNextRace } from "@/types/dashboard";

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

interface RaceDistributionChartProps {
  races: DashboardNextRace[];
}

export default function RaceDistributionChart({ races }: RaceDistributionChartProps) {
  if (races.length === 0) return null;

  // Group races by month / Agrupar corridas por mes
  const monthCounts: Record<string, number> = {};
  for (const race of races) {
    const date = new Date(race.scheduled_at);
    const key = MONTH_NAMES[date.getMonth()];
    monthCounts[key] = (monthCounts[key] || 0) + 1;
  }

  const chartData = Object.entries(monthCounts).map(([month, count]) => ({
    month,
    count,
  }));

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Races per Month / Corridas por Mes
      </h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={chartData} margin={{ top: 0, right: 20, bottom: 0, left: 0 }}>
          <XAxis dataKey="month" tick={{ fontSize: 12 }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="count" fill="#16a34a" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
