/**
 * Shared theme constants: status colors, compound colors, labels.
 * Constantes de tema compartilhadas: cores de status, cores de compostos, rotulos.
 */

import type { TireCompound } from "@/types/pitstops";

// ---- Championship status / Status de campeonato ----

export type ChampionshipStatusKey = "planned" | "active" | "completed" | "cancelled";

export const CHAMPIONSHIP_STATUS_COLORS: Record<ChampionshipStatusKey, string> = {
  planned: "bg-gray-100 text-gray-800",
  active: "bg-green-100 text-green-800",
  completed: "bg-blue-100 text-blue-800",
  cancelled: "bg-red-100 text-red-800",
};

export const CHAMPIONSHIP_STATUS_LABELS: Record<ChampionshipStatusKey, string> = {
  planned: "Planned / Planejado",
  active: "Active / Ativo",
  completed: "Completed / Concluido",
  cancelled: "Cancelled / Cancelado",
};

// ---- Race status / Status de corrida ----

export type RaceStatusKey = "scheduled" | "qualifying" | "active" | "finished" | "cancelled";

export const RACE_STATUS_COLORS: Record<RaceStatusKey, string> = {
  scheduled: "bg-gray-100 text-gray-800",
  qualifying: "bg-yellow-100 text-yellow-800",
  active: "bg-green-100 text-green-800",
  finished: "bg-blue-100 text-blue-800",
  cancelled: "bg-red-100 text-red-800",
};

export const RACE_STATUS_LABELS: Record<RaceStatusKey, string> = {
  scheduled: "Scheduled / Agendado",
  qualifying: "Qualifying / Classificacao",
  active: "Active / Ativo",
  finished: "Finished / Encerrado",
  cancelled: "Cancelled / Cancelado",
};

// ---- Tire compound / Composto de pneu ----

export const COMPOUND_COLORS: Record<TireCompound | string, string> = {
  soft: "bg-red-100 text-red-800",
  medium: "bg-yellow-100 text-yellow-800",
  hard: "bg-gray-100 text-gray-800",
  intermediate: "bg-green-100 text-green-800",
  wet: "bg-blue-100 text-blue-800",
};

// ---- Active/inactive / Ativo/inativo ----

export const ACTIVE_COLORS = {
  active: "bg-green-100 text-green-800",
  inactive: "bg-red-100 text-red-800",
} as const;
