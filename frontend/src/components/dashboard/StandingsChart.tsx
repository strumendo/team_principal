/**
 * Bar chart for top standings per championship.
 * Grafico de barras para classificacao dos principais por campeonato.
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
import type { DashboardChampionshipStandings } from "@/types/dashboard";

interface StandingsChartProps {
  standings: DashboardChampionshipStandings[];
}

export default function StandingsChart({ standings }: StandingsChartProps) {
  if (standings.length === 0) return null;

  return (
    <div className="space-y-6">
      {standings.map((cs) => {
        const chartData = cs.standings.slice(0, 5).map((s) => ({
          name: s.team_display_name,
          points: s.total_points,
        }));

        return (
          <div
            key={cs.championship_id}
            className="rounded-lg border border-gray-200 bg-white p-4"
          >
            <h3 className="mb-3 text-sm font-semibold text-gray-700">
              {cs.championship_display_name} — Top 5
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 0, right: 20, bottom: 0, left: 80 }}
              >
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis
                  type="category"
                  dataKey="name"
                  tick={{ fontSize: 12 }}
                  width={75}
                />
                <Tooltip />
                <Bar dataKey="points" fill="#2563eb" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        );
      })}
    </div>
  );
}
