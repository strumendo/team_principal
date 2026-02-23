/**
 * Dashboard TypeScript interfaces.
 * Interfaces TypeScript do dashboard.
 */

export interface DashboardChampionship {
  id: string;
  name: string;
  display_name: string;
  season_year: number;
  status: string;
  start_date: string | null;
  end_date: string | null;
  total_races: number;
  completed_races: number;
  team_count: number;
}

export interface DashboardNextRace {
  id: string;
  name: string;
  display_name: string;
  championship_id: string;
  championship_display_name: string;
  round_number: number;
  scheduled_at: string;
  track_name: string | null;
  track_country: string | null;
}

export interface DashboardStandingEntry {
  position: number;
  team_id: string;
  team_name: string;
  team_display_name: string;
  total_points: number;
  races_scored: number;
  wins: number;
}

export interface DashboardChampionshipStandings {
  championship_id: string;
  championship_display_name: string;
  standings: DashboardStandingEntry[];
}

export interface DashboardSummary {
  active_championships: DashboardChampionship[];
  next_races: DashboardNextRace[];
  championship_standings: DashboardChampionshipStandings[];
}
