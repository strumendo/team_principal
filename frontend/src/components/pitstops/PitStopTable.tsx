"use client";

/**
 * Pit stop table: displays pit stops with duration, tire changes, and notes.
 * Tabela de pit stops: exibe pit stops com duracao, troca de pneus e notas.
 */

import type { PitStop, TireCompound } from "@/types/pitstops";

const COMPOUND_COLORS: Record<TireCompound, string> = {
  soft: "bg-red-100 text-red-800",
  medium: "bg-yellow-100 text-yellow-800",
  hard: "bg-gray-100 text-gray-800",
  intermediate: "bg-green-100 text-green-800",
  wet: "bg-blue-100 text-blue-800",
};

/**
 * Format milliseconds to seconds with decimals (e.g. 2.450s).
 * Formata milissegundos para segundos com decimais.
 */
function formatDuration(ms: number): string {
  const seconds = ms / 1000;
  return `${seconds.toFixed(3)}s`;
}

function CompoundBadge({ compound }: { compound: TireCompound | null }) {
  if (!compound) return <span className="text-gray-400">-</span>;
  return (
    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${COMPOUND_COLORS[compound]}`}>
      {compound.charAt(0).toUpperCase() + compound.slice(1)}
    </span>
  );
}

interface PitStopTableProps {
  pitStops: PitStop[];
  onDelete?: (id: string) => void;
}

export default function PitStopTable({ pitStops, onDelete }: PitStopTableProps) {
  if (pitStops.length === 0) {
    return (
      <p className="text-sm text-gray-500">
        No pit stops recorded. / Nenhum pit stop registrado.
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
              Duration / Duracao
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Tire From / Pneu De
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Tire To / Pneu Para
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Notes / Notas
            </th>
            {onDelete && (
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                Actions / Acoes
              </th>
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {pitStops.map((ps) => (
            <tr key={ps.id} className="hover:bg-gray-50">
              <td className="whitespace-nowrap px-4 py-2 text-sm font-medium text-gray-900">
                {ps.lap_number}
              </td>
              <td className="whitespace-nowrap px-4 py-2 text-sm font-mono text-gray-900">
                {formatDuration(ps.duration_ms)}
              </td>
              <td className="whitespace-nowrap px-4 py-2 text-sm">
                <CompoundBadge compound={ps.tire_from} />
              </td>
              <td className="whitespace-nowrap px-4 py-2 text-sm">
                <CompoundBadge compound={ps.tire_to} />
              </td>
              <td className="px-4 py-2 text-sm text-gray-600">
                {ps.notes || "-"}
              </td>
              {onDelete && (
                <td className="whitespace-nowrap px-4 py-2 text-right text-sm">
                  <button
                    onClick={() => onDelete(ps.id)}
                    className="text-red-600 hover:underline"
                  >
                    Delete / Excluir
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
