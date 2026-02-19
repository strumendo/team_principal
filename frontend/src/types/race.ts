/**
 * Race TypeScript interfaces.
 * Interfaces TypeScript de corrida.
 */

export type RaceStatus = "scheduled" | "qualifying" | "active" | "finished" | "cancelled";

export interface RaceListItem {
  id: string;
  championship_id: string;
  name: string;
  display_name: string;
  description: string | null;
  round_number: number;
  status: RaceStatus;
  scheduled_at: string | null;
  track_name: string | null;
  track_country: string | null;
  laps_total: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RaceTeam {
  id: string;
  name: string;
  display_name: string;
  is_active: boolean;
}

export interface RaceDetail extends RaceListItem {
  teams: RaceTeam[];
}

export interface RaceEntry {
  team_id: string;
  team_name: string;
  team_display_name: string;
  team_is_active: boolean;
  registered_at: string;
}
