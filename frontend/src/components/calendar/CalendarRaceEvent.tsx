/**
 * Race event pill/badge for the calendar grid.
 * Pilula/badge de evento de corrida para o grid do calendario.
 */
import Link from "next/link";
import type { CalendarRace } from "@/types/calendar";
import type { RaceStatus } from "@/types/race";

const STATUS_COLORS: Record<RaceStatus, string> = {
  scheduled: "bg-gray-200 text-gray-800 hover:bg-gray-300",
  qualifying: "bg-yellow-200 text-yellow-800 hover:bg-yellow-300",
  active: "bg-green-200 text-green-800 hover:bg-green-300",
  finished: "bg-blue-200 text-blue-800 hover:bg-blue-300",
  cancelled: "bg-red-200 text-red-800 hover:bg-red-300",
};

interface CalendarRaceEventProps {
  race: CalendarRace;
}

export default function CalendarRaceEvent({ race }: CalendarRaceEventProps) {
  const time = new Date(race.scheduled_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <Link
      href={`/races/${race.id}`}
      className={`block truncate rounded px-1.5 py-0.5 text-xs font-medium transition-colors ${STATUS_COLORS[race.status]}`}
      title={`${race.display_name} — ${race.championship_display_name} (${time})${race.track_name ? ` @ ${race.track_name}` : ""}`}
    >
      {race.display_name}
    </Link>
  );
}
