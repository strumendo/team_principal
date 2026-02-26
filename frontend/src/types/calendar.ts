/**
 * Calendar TypeScript interfaces.
 * Interfaces TypeScript do calendario.
 */

import type { RaceStatus } from "./race";

export interface CalendarRace {
  id: string;
  display_name: string;
  round_number: number;
  status: RaceStatus;
  scheduled_at: string;
  track_name: string | null;
  track_country: string | null;
  championship_id: string;
  championship_display_name: string;
  championship_status: string;
}
