/**
 * Individual day cell with race events for the calendar grid.
 * Celula de dia individual com eventos de corrida para o grid do calendario.
 */
import type { CalendarRace } from "@/types/calendar";
import CalendarRaceEvent from "./CalendarRaceEvent";

interface CalendarDayCellProps {
  day: number | null;
  races: CalendarRace[];
  isToday: boolean;
}

export default function CalendarDayCell({
  day,
  races,
  isToday,
}: CalendarDayCellProps) {
  if (day === null) {
    return <div className="min-h-[80px] bg-gray-50 p-1" />;
  }

  return (
    <div
      className={`min-h-[80px] border-t p-1 ${isToday ? "bg-blue-50" : "bg-white"}`}
    >
      <span
        className={`mb-1 inline-block text-sm font-medium ${
          isToday
            ? "rounded-full bg-blue-600 px-1.5 text-white"
            : "text-gray-700"
        }`}
      >
        {day}
      </span>
      <div className="space-y-0.5">
        {races.slice(0, 3).map((race) => (
          <CalendarRaceEvent key={race.id} race={race} />
        ))}
        {races.length > 3 && (
          <span className="block text-xs text-gray-500">
            +{races.length - 3} more / mais
          </span>
        )}
      </div>
    </div>
  );
}
