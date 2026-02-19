/**
 * Race result and championship standing TypeScript interfaces.
 * Interfaces TypeScript de resultado de corrida e classificacao de campeonato.
 */

export interface RaceResult {
  id: string;
  race_id: string;
  team_id: string;
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

export interface RaceResultDetail extends RaceResult {
  team: RaceResultTeam;
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
