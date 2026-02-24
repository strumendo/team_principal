/**
 * Penalty TypeScript interfaces.
 * Interfaces TypeScript de penalidade.
 */

export type PenaltyType =
  | "warning"
  | "time_penalty"
  | "points_deduction"
  | "disqualification"
  | "grid_penalty";

export interface Penalty {
  id: string;
  race_id: string;
  result_id: string | null;
  team_id: string;
  driver_id: string | null;
  penalty_type: PenaltyType;
  reason: string;
  points_deducted: number;
  time_penalty_seconds: number | null;
  lap_number: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PenaltyDetail extends Penalty {
  team: {
    id: string;
    name: string;
    display_name: string;
  } | null;
  driver: {
    id: string;
    name: string;
    display_name: string;
    abbreviation: string;
  } | null;
}
