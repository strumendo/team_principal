/**
 * Race result and championship standing TypeScript interfaces.
 * Interfaces TypeScript de resultado de corrida e classificacao de campeonato.
 */

export interface RaceResult {
  id: string;
  race_id: string;
  team_id: string;
  driver_id: string | null;
  position: number;
  points: number;
  laps_completed: number | null;
  fastest_lap: boolean;
  dnf: boolean;
  dsq: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface RaceResultTeam {
  id: string;
  name: string;
  display_name: string;
  is_active: boolean;
}

export interface RaceResultDriver {
  id: string;
  name: string;
  display_name: string;
  abbreviation: string;
  number: number;
}

export interface RaceResultDetail extends RaceResult {
  team: RaceResultTeam;
  driver: RaceResultDriver | null;
}

export interface ChampionshipStanding {
  position: number;
  team_id: string;
  team_name: string;
  team_display_name: string;
  total_points: number;
  races_scored: number;
  wins: number;
}

// Standings breakdown interfaces / Interfaces de detalhamento de classificacao

export interface BreakdownRace {
  race_id: string;
  race_name: string;
  race_display_name: string;
  round_number: number;
}

export interface RacePoints {
  race_id: string;
  points: number;
  position: number;
  dsq: boolean;
}

export interface TeamBreakdown {
  position: number;
  team_id: string;
  team_name: string;
  team_display_name: string;
  total_points: number;
  wins: number;
  race_points: RacePoints[];
}

export interface DriverBreakdown {
  position: number;
  driver_id: string;
  driver_name: string;
  driver_display_name: string;
  driver_abbreviation: string;
  team_id: string;
  team_name: string;
  team_display_name: string;
  total_points: number;
  wins: number;
  race_points: RacePoints[];
}

export interface StandingsBreakdown {
  races: BreakdownRace[];
  team_standings: TeamBreakdown[];
  driver_standings: DriverBreakdown[];
}
