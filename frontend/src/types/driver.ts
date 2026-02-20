/**
 * Driver TypeScript interfaces.
 * Interfaces TypeScript de piloto.
 */

export interface DriverTeam {
  id: string;
  name: string;
  display_name: string;
  is_active: boolean;
}

export interface DriverListItem {
  id: string;
  name: string;
  display_name: string;
  abbreviation: string;
  number: number;
  nationality: string | null;
  team_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DriverDetail extends DriverListItem {
  date_of_birth: string | null;
  photo_url: string | null;
  team: DriverTeam;
}

export interface DriverStanding {
  position: number;
  driver_id: string;
  driver_name: string;
  driver_display_name: string;
  driver_abbreviation: string;
  team_id: string;
  team_name: string;
  team_display_name: string;
  total_points: number;
  races_scored: number;
  wins: number;
}
