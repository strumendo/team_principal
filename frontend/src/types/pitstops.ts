/**
 * Pit stop and race strategy types.
 * Tipos de pit stop e estrategia de corrida.
 */

export type TireCompound = "soft" | "medium" | "hard" | "intermediate" | "wet";

export interface PitStop {
  id: string;
  race_id: string;
  driver_id: string;
  team_id: string;
  lap_number: number;
  duration_ms: number;
  tire_from: TireCompound | null;
  tire_to: TireCompound | null;
  notes: string | null;
  created_at: string;
}

export interface DriverInfo {
  id: string;
  name: string;
  display_name: string;
  abbreviation: string;
}

export interface TeamInfo {
  id: string;
  name: string;
  display_name: string;
}

export interface PitStopDetail extends PitStop {
  driver: DriverInfo;
  team: TeamInfo;
}

export interface PitStopSummaryDriver {
  driver_id: string;
  driver_display_name: string;
  total_stops: number;
  avg_duration_ms: number;
  fastest_pit_ms: number;
}

export interface PitStopSummary {
  drivers: PitStopSummaryDriver[];
}

export interface RaceStrategy {
  id: string;
  race_id: string;
  driver_id: string;
  team_id: string;
  name: string;
  description: string | null;
  target_stops: number;
  planned_laps: string | null;
  starting_compound: TireCompound | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RaceStrategyDetail extends RaceStrategy {
  driver: DriverInfo;
  team: TeamInfo;
}
