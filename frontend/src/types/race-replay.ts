/**
 * Race replay and analysis types.
 * Tipos de replay e analise de corrida.
 */

export type RaceEventType =
  | "safety_car"
  | "virtual_safety_car"
  | "red_flag"
  | "incident"
  | "penalty"
  | "overtake"
  | "mechanical_failure"
  | "race_start"
  | "race_end";

export interface LapPosition {
  id: string;
  race_id: string;
  driver_id: string;
  team_id: string;
  lap_number: number;
  position: number;
  gap_to_leader_ms: number | null;
  interval_ms: number | null;
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

export interface LapPositionDetail extends LapPosition {
  driver: DriverInfo;
  team: TeamInfo;
}

export interface RaceEvent {
  id: string;
  race_id: string;
  lap_number: number;
  event_type: RaceEventType;
  description: string | null;
  driver_id: string | null;
  created_at: string;
}

export interface RaceEventDetail extends RaceEvent {
  driver: DriverInfo | null;
}

// --- Analysis types / Tipos de analise ---

export interface ReplayPositionData {
  driver_id: string;
  driver_name: string;
  team_id: string;
  position: number;
  gap_to_leader_ms: number | null;
  interval_ms: number | null;
}

export interface ReplayEventData {
  event_type: RaceEventType;
  description: string | null;
  driver_id: string | null;
  driver_name: string | null;
}

export interface ReplayPitStopData {
  driver_id: string;
  driver_name: string;
  duration_ms: number;
  tire_from: string | null;
  tire_to: string | null;
}

export interface ReplayLapData {
  lap_number: number;
  positions: ReplayPositionData[];
  events: ReplayEventData[];
  pit_stops: ReplayPitStopData[];
}

export interface FullReplayResponse {
  race_id: string;
  total_laps: number;
  laps: ReplayLapData[];
}

export interface StintData {
  driver_id: string;
  driver_name: string;
  stint_number: number;
  compound: string | null;
  start_lap: number;
  end_lap: number;
  total_laps: number;
  avg_pace_ms: number | null;
  best_lap_ms: number | null;
  degradation_ms: number | null;
}

export interface DriverStintData {
  driver_id: string;
  driver_name: string;
  stints: StintData[];
}

export interface StintAnalysisResponse {
  race_id: string;
  drivers: DriverStintData[];
}

export interface OvertakeData {
  lap_number: number;
  driver_id: string;
  driver_name: string;
  from_position: number;
  to_position: number;
  positions_gained: number;
}

export interface OvertakesResponse {
  race_id: string;
  total_overtakes: number;
  overtakes: OvertakeData[];
}

export interface FastestLapData {
  driver_id: string;
  driver_name: string;
  lap_number: number;
  lap_time_ms: number;
}

export interface RaceSummaryResponse {
  race_id: string;
  total_laps: number;
  total_overtakes: number;
  leader_changes: number;
  safety_car_laps: number;
  dnf_count: number;
  fastest_lap: FastestLapData | null;
}
