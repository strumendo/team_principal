/**
 * Telemetry types: lap times, car setups, driver comparison.
 * Tipos de telemetria: tempos de volta, setups de carro, comparacao de pilotos.
 */

export interface LapTime {
  id: string;
  race_id: string;
  driver_id: string;
  team_id: string;
  lap_number: number;
  lap_time_ms: number;
  sector_1_ms: number | null;
  sector_2_ms: number | null;
  sector_3_ms: number | null;
  is_valid: boolean;
  is_personal_best: boolean;
  created_at: string;
}

export interface LapTimeSummaryDriver {
  driver_id: string;
  driver_display_name: string;
  fastest_lap_ms: number;
  avg_lap_ms: number;
  total_laps: number;
  personal_best_lap: number | null;
}

export interface LapTimeSummary {
  drivers: LapTimeSummaryDriver[];
  overall_fastest: LapTime | null;
}

export interface CarSetup {
  id: string;
  race_id: string;
  driver_id: string;
  team_id: string;
  name: string;
  notes: string | null;
  front_wing: number | null;
  rear_wing: number | null;
  differential: number | null;
  brake_bias: number | null;
  tire_pressure_fl: number | null;
  tire_pressure_fr: number | null;
  tire_pressure_rl: number | null;
  tire_pressure_rr: number | null;
  suspension_stiffness: number | null;
  anti_roll_bar: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
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

export interface CarSetupDetail extends CarSetup {
  driver: DriverInfo;
  team: TeamInfo;
}

export interface DriverComparison {
  driver_id: string;
  driver_display_name: string;
  laps: LapTime[];
}
