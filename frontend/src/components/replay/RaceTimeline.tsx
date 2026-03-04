"use client";

/**
 * Race timeline: horizontal event markers for race events.
 * Linha do tempo da corrida: marcadores horizontais para eventos da corrida.
 */

import type { ReplayLapData, RaceEventType } from "@/types/race-replay";

const EVENT_COLORS: Record<RaceEventType, string> = {
  safety_car: "bg-yellow-400",
  virtual_safety_car: "bg-yellow-300",
  red_flag: "bg-red-500",
  incident: "bg-orange-400",
  penalty: "bg-red-400",
  overtake: "bg-green-400",
  mechanical_failure: "bg-gray-500",
  race_start: "bg-blue-500",
  race_end: "bg-blue-800",
};

const EVENT_LABELS: Record<RaceEventType, string> = {
  safety_car: "SC",
  virtual_safety_car: "VSC",
  red_flag: "RED",
  incident: "INC",
  penalty: "PEN",
  overtake: "OVT",
  mechanical_failure: "MF",
  race_start: "START",
  race_end: "END",
};

interface RaceTimelineProps {
  laps: ReplayLapData[];
  totalLaps: number;
}

export default function RaceTimeline({ laps, totalLaps }: RaceTimelineProps) {
  const events = laps.flatMap((lap) =>
    lap.events.map((evt) => ({
      lap_number: lap.lap_number,
      ...evt,
    })),
  );

  if (events.length === 0) {
    return (
      <p className="text-sm text-gray-500">
        No events recorded. / Nenhum evento registrado.
      </p>
    );
  }

  const maxLap = totalLaps || Math.max(...events.map((e) => e.lap_number), 1);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Race Timeline / Linha do Tempo
      </h3>
      <div className="relative h-12 rounded bg-gray-100">
        {events.map((evt, i) => {
          const left = `${(evt.lap_number / maxLap) * 100}%`;
          const colorClass = EVENT_COLORS[evt.event_type] || "bg-gray-400";
          return (
            <div
              key={`${evt.lap_number}-${evt.event_type}-${i}`}
              className={`absolute top-1 h-10 w-8 rounded text-center text-xs font-bold text-white ${colorClass}`}
              style={{ left }}
              title={`Lap ${evt.lap_number}: ${evt.event_type}${evt.description ? ` - ${evt.description}` : ""}`}
            >
              <span className="leading-10">{EVENT_LABELS[evt.event_type]}</span>
            </div>
          );
        })}
      </div>
      {/* Legend / Legenda */}
      <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-600">
        {Object.entries(EVENT_LABELS).map(([type, label]) => (
          <div key={type} className="flex items-center gap-1">
            <span className={`inline-block h-3 w-3 rounded ${EVENT_COLORS[type as RaceEventType]}`} />
            {label}
          </div>
        ))}
      </div>
    </div>
  );
}
