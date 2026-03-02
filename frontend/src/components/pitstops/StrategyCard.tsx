"use client";

/**
 * Strategy card: displays a race strategy with actions.
 * Card de estrategia: exibe uma estrategia de corrida com acoes.
 */

import type { RaceStrategy, TireCompound } from "@/types/pitstops";

const COMPOUND_COLORS: Record<TireCompound, string> = {
  soft: "bg-red-100 text-red-800",
  medium: "bg-yellow-100 text-yellow-800",
  hard: "bg-gray-100 text-gray-800",
  intermediate: "bg-green-100 text-green-800",
  wet: "bg-blue-100 text-blue-800",
};

interface StrategyCardProps {
  strategy: RaceStrategy;
  onEdit?: (strategy: RaceStrategy) => void;
  onDelete?: (id: string) => void;
}

export default function StrategyCard({ strategy, onEdit, onDelete }: StrategyCardProps) {
  return (
    <div className={`rounded-lg border p-4 ${strategy.is_active ? "bg-white" : "bg-gray-50 opacity-75"}`}>
      <div className="mb-3 flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{strategy.name}</h3>
          {strategy.description && (
            <p className="mt-1 text-sm text-gray-600">{strategy.description}</p>
          )}
        </div>
        <span
          className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${
            strategy.is_active
              ? "bg-green-100 text-green-800"
              : "bg-red-100 text-red-800"
          }`}
        >
          {strategy.is_active ? "Active / Ativo" : "Inactive / Inativo"}
        </span>
      </div>

      <dl className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <dt className="font-medium text-gray-500">Target Stops / Paradas Planejadas</dt>
          <dd className="text-gray-900">{strategy.target_stops}</dd>
        </div>
        <div>
          <dt className="font-medium text-gray-500">Planned Laps / Voltas Planejadas</dt>
          <dd className="text-gray-900">{strategy.planned_laps || "-"}</dd>
        </div>
        <div className="col-span-2">
          <dt className="font-medium text-gray-500">Starting Compound / Composto Inicial</dt>
          <dd className="mt-1">
            {strategy.starting_compound ? (
              <span
                className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${COMPOUND_COLORS[strategy.starting_compound]}`}
              >
                {strategy.starting_compound.charAt(0).toUpperCase() + strategy.starting_compound.slice(1)}
              </span>
            ) : (
              <span className="text-gray-400">-</span>
            )}
          </dd>
        </div>
      </dl>

      {(onEdit || onDelete) && (
        <div className="mt-4 flex gap-2 border-t pt-3">
          {onEdit && (
            <button
              onClick={() => onEdit(strategy)}
              className="text-sm text-blue-600 hover:underline"
            >
              Edit / Editar
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(strategy.id)}
              className="text-sm text-red-600 hover:underline"
            >
              Delete / Excluir
            </button>
          )}
        </div>
      )}
    </div>
  );
}
