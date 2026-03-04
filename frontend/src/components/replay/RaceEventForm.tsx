"use client";

/**
 * Form for creating race events.
 * Formulario para criar eventos de corrida.
 */

import { useState } from "react";
import type { RaceEventType } from "@/types/race-replay";

const EVENT_TYPES: { value: RaceEventType; label: string }[] = [
  { value: "safety_car", label: "Safety Car" },
  { value: "virtual_safety_car", label: "Virtual Safety Car (VSC)" },
  { value: "red_flag", label: "Red Flag / Bandeira Vermelha" },
  { value: "incident", label: "Incident / Incidente" },
  { value: "penalty", label: "Penalty / Penalidade" },
  { value: "overtake", label: "Overtake / Ultrapassagem" },
  { value: "mechanical_failure", label: "Mechanical Failure / Falha Mecanica" },
  { value: "race_start", label: "Race Start / Inicio da Corrida" },
  { value: "race_end", label: "Race End / Fim da Corrida" },
];

interface DriverOption {
  id: string;
  display_name: string;
}

interface RaceEventFormProps {
  raceId: string;
  drivers: DriverOption[];
  token: string;
  onSubmit: (data: {
    lap_number: number;
    event_type: RaceEventType;
    description?: string;
    driver_id?: string;
  }) => Promise<void>;
  onCancel: () => void;
}

export default function RaceEventForm({
  drivers,
  onSubmit,
  onCancel,
}: RaceEventFormProps) {
  const [lapNumber, setLapNumber] = useState(1);
  const [eventType, setEventType] = useState<RaceEventType>("safety_car");
  const [description, setDescription] = useState("");
  const [driverId, setDriverId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      await onSubmit({
        lap_number: lapNumber,
        event_type: eventType,
        ...(description ? { description } : {}),
        ...(driverId ? { driver_id: driverId } : {}),
      });
    } catch {
      setError("Failed to create event. / Falha ao criar evento.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Add Event / Adicionar Evento
      </h3>

      {error && <p className="mb-2 text-sm text-red-600">{error}</p>}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Lap Number / Numero da Volta
          </label>
          <input
            type="number"
            min={1}
            value={lapNumber}
            onChange={(e) => setLapNumber(Number(e.target.value))}
            className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500 sm:text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Event Type / Tipo de Evento
          </label>
          <select
            value={eventType}
            onChange={(e) => setEventType(e.target.value as RaceEventType)}
            className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500 sm:text-sm"
          >
            {EVENT_TYPES.map((et) => (
              <option key={et.value} value={et.value}>{et.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Driver / Piloto (optional / opcional)
          </label>
          <select
            value={driverId}
            onChange={(e) => setDriverId(e.target.value)}
            className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500 sm:text-sm"
          >
            <option value="">— None / Nenhum —</option>
            {drivers.map((d) => (
              <option key={d.id} value={d.id}>{d.display_name}</option>
            ))}
          </select>
        </div>

        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-gray-700">
            Description / Descricao (optional / opcional)
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
            className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500 sm:text-sm"
          />
        </div>
      </div>

      <div className="mt-4 flex gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-pink-600 px-4 py-2 text-sm text-white hover:bg-pink-700 disabled:opacity-50"
        >
          {submitting ? "Saving..." : "Save / Salvar"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
        >
          Cancel / Cancelar
        </button>
      </div>
    </form>
  );
}
