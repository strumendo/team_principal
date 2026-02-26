/**
 * Season calendar page — visual calendar with all races.
 * Pagina do calendario da temporada — calendario visual com todas as corridas.
 */
import CalendarGrid from "@/components/calendar/CalendarGrid";

export default function CalendarPage() {
  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">
        Season Calendar / Calendario da Temporada
      </h1>
      <CalendarGrid />
    </div>
  );
}
