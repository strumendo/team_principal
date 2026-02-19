/**
 * Championship TypeScript interfaces.
 * Interfaces TypeScript de campeonato.
 */

export type ChampionshipStatus = "planned" | "active" | "completed" | "cancelled";

export interface ChampionshipListItem {
  id: string;
  name: string;
  display_name: string;
  description: string | null;
  season_year: number;
  status: ChampionshipStatus;
  start_date: string | null;
  end_date: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChampionshipTeam {
  id: string;
  name: string;
  display_name: string;
  is_active: boolean;
}

export interface ChampionshipDetail extends ChampionshipListItem {
  teams: ChampionshipTeam[];
}

export interface ChampionshipEntry {
  team_id: string;
  team_name: string;
  team_display_name: string;
  team_is_active: boolean;
  registered_at: string;
}
