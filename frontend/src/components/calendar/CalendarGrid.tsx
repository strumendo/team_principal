/**
 * Monthly calendar grid with race events and navigation.
 * Grid de calendario mensal com eventos de corrida e navegacao.
 */
"use client";

import { useCallback, useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import Link from "next/link";
import type { CalendarRace } from "@/types/calendar";
import type { RaceStatus } from "@/types/race";
import type { ChampionshipListItem } from "@/types/championship";
import { calendarApi, championshipsApi } from "@/lib/api-client";
import CalendarDayCell from "./CalendarDayCell";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const WEEKDAYS_PT = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"];

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];
const MONTH_NAMES_PT = [
  "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

const STATUS_LEGEND: { status: RaceStatus; label: string; color: string }[] = [
  { status: "scheduled", label: "Scheduled / Agendada", color: "bg-gray-200" },
  { status: "qualifying", label: "Qualifying / Classificacao", color: "bg-yellow-200" },
  { status: "active", label: "Active / Ativa", color: "bg-green-200" },
  { status: "finished", label: "Finished / Finalizada", color: "bg-blue-200" },
  { status: "cancelled", label: "Cancelled / Cancelada", color: "bg-red-200" },
];

function getDaysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate();
}

function getFirstDayOfWeek(year: number, month: number): number {
  return new Date(year, month - 1, 1).getDay();
}

export default function CalendarGrid() {
  const { data: session } = useSession();
  const token = (session as unknown as { accessToken: string })?.accessToken;

  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [races, setRaces] = useState<CalendarRace[]>([]);
  const [championships, setChampionships] = useState<ChampionshipListItem[]>([]);
  const [selectedChampionship, setSelectedChampionship] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRaces = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);

    const params: { year: number; month: number; championship_id?: string } = { year, month };
    if (selectedChampionship) {
      params.championship_id = selectedChampionship;
    }

    const result = await calendarApi.listRaces(token, params);
    if (result.error) {
      setError(result.error);
    } else {
      setRaces(result.data || []);
    }
    setLoading(false);
  }, [token, year, month, selectedChampionship]);

  useEffect(() => {
    fetchRaces();
  }, [fetchRaces]);

  useEffect(() => {
    if (!token) return;
    championshipsApi.list(token).then((result) => {
      if (result.data) setChampionships(result.data);
    });
  }, [token]);

  const goToPrevMonth = () => {
    if (month === 1) {
      setYear(year - 1);
      setMonth(12);
    } else {
      setMonth(month - 1);
    }
  };

  const goToNextMonth = () => {
    if (month === 12) {
      setYear(year + 1);
      setMonth(1);
    } else {
      setMonth(month + 1);
    }
  };

  const goToToday = () => {
    const today = new Date();
    setYear(today.getFullYear());
    setMonth(today.getMonth() + 1);
  };

  // Build calendar grid / Construir grid do calendario
  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfWeek(year, month);

  // Map races to days / Mapear corridas para dias
  const racesByDay: Record<number, CalendarRace[]> = {};
  for (const race of races) {
    const day = new Date(race.scheduled_at).getDate();
    if (!racesByDay[day]) racesByDay[day] = [];
    racesByDay[day].push(race);
  }

  // Build grid cells / Construir celulas do grid
  const cells: (number | null)[] = [];
  for (let i = 0; i < firstDay; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);

  const today = new Date();
  const isCurrentMonth = year === today.getFullYear() && month === today.getMonth() + 1;

  // Agenda view for mobile / Visualizacao agenda para mobile
  const sortedRaceDays = Object.keys(racesByDay)
    .map(Number)
    .sort((a, b) => a - b);

  return (
    <div>
      {/* Header: navigation + filter / Cabecalho: navegacao + filtro */}
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <button
            onClick={goToPrevMonth}
            className="rounded border px-3 py-1 text-sm hover:bg-gray-100"
          >
            &larr;
          </button>
          <h2 className="text-lg font-semibold">
            {MONTH_NAMES[month - 1]} / {MONTH_NAMES_PT[month - 1]} {year}
          </h2>
          <button
            onClick={goToNextMonth}
            className="rounded border px-3 py-1 text-sm hover:bg-gray-100"
          >
            &rarr;
          </button>
          <button
            onClick={goToToday}
            className="ml-2 rounded border px-3 py-1 text-sm hover:bg-gray-100"
          >
            Today / Hoje
          </button>
        </div>
        <div>
          <select
            value={selectedChampionship}
            onChange={(e) => setSelectedChampionship(e.target.value)}
            className="rounded border px-3 py-1 text-sm"
          >
            <option value="">All Championships / Todos Campeonatos</option>
            {championships.map((c) => (
              <option key={c.id} value={c.id}>
                {c.display_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="py-12 text-center text-gray-500">
          Loading calendar... / Carregando calendario...
        </div>
      ) : (
        <>
          {/* Desktop: grid view / Desktop: visualizacao em grid */}
          <div className="hidden md:block">
            <div className="grid grid-cols-7 border-b text-center text-xs font-medium text-gray-500">
              {WEEKDAYS.map((day, i) => (
                <div key={day} className="border-l p-2 first:border-l-0">
                  {day} / {WEEKDAYS_PT[i]}
                </div>
              ))}
            </div>
            <div className="grid grid-cols-7 border-l">
              {cells.map((day, i) => (
                <div key={i} className="border-b border-r">
                  <CalendarDayCell
                    day={day}
                    races={day ? racesByDay[day] || [] : []}
                    isToday={isCurrentMonth && day === today.getDate()}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Mobile: agenda view / Mobile: visualizacao agenda */}
          <div className="md:hidden">
            {sortedRaceDays.length === 0 ? (
              <p className="py-8 text-center text-gray-500">
                No races this month / Sem corridas neste mes
              </p>
            ) : (
              <div className="space-y-3">
                {sortedRaceDays.map((day) => (
                  <div key={day} className="rounded border p-3">
                    <p className="mb-2 text-sm font-semibold text-gray-700">
                      {MONTH_NAMES[month - 1]} {day}, {year}
                    </p>
                    <div className="space-y-2">
                      {racesByDay[day].map((race) => (
                        <Link
                          key={race.id}
                          href={`/races/${race.id}`}
                          className="block rounded border p-2 hover:bg-gray-50"
                        >
                          <p className="text-sm font-medium">
                            {race.display_name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {race.championship_display_name}
                            {race.track_name && ` — ${race.track_name}`}
                            {race.track_country && `, ${race.track_country}`}
                          </p>
                          <p className="text-xs text-gray-400">
                            {new Date(race.scheduled_at).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </p>
                        </Link>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Legend / Legenda */}
          <div className="mt-4 flex flex-wrap gap-3 text-xs text-gray-600">
            {STATUS_LEGEND.map(({ status, label, color }) => (
              <div key={status} className="flex items-center gap-1">
                <span className={`inline-block h-3 w-3 rounded ${color}`} />
                {label}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
