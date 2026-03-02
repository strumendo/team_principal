"use client";

/**
 * Pit stop form: create a new pit stop record.
 * Formulario de pit stop: cria um novo registro de pit stop.
 */

import { useState } from "react";
import type { TireCompound } from "@/types/pitstops";

const TIRE_COMPOUNDS: TireCompound[] = ["soft", "medium", "hard", "intermediate", "wet"];

interface PitStopFormProps {
  drivers: Array<{ id: string; display_name: string; team_id: string }>;
  onSubmit: (data: {
    driver_id: string;
    team_id: string;
    lap_number: number;
    duration_ms: number;
    tire_from?: TireCompound;
    tire_to?: TireCompound;
    notes?: string;
  }) => Promise<void>;
  onCancel: () => void;
  saving?: boolean;
}

export default function PitStopForm({ drivers, onSubmit, onCancel, saving = false }: PitStopFormProps) {
  const [driverId, setDriverId] = useState("");
  const [lapNumber, setLapNumber] = useState("");
  const [durationMs, setDurationMs] = useState("");
  const [tireFrom, setTireFrom] = useState("");
  const [tireTo, setTireTo] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  const selectedDriver = drivers.find((d) => d.id === driverId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!driverId) {
      setError("Driver is required. / Piloto e obrigatorio.");
      return;
    }
    if (!lapNumber || !durationMs) {
      setError("Lap number and duration are required. / Numero da volta e duracao sao obrigatorios.");
      return;
    }
    setError(null);

    const data: {
      driver_id: string;
      team_id: string;
      lap_number: number;
      duration_ms: number;
      tire_from?: TireCompound;
      tire_to?: TireCompound;
      notes?: string;
    } = {
      driver_id: driverId,
      team_id: selectedDriver?.team_id || "",
      lap_number: parseInt(lapNumber),
      duration_ms: parseInt(durationMs),
    };

    if (tireFrom) data.tire_from = tireFrom as TireCompound;
    if (tireTo) data.tire_to = tireTo as TireCompound;
    if (notes.trim()) data.notes = notes.trim();

    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded border p-4">
      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Driver / Piloto *
          </label>
          <select
            value={driverId}
            onChange={(e) => setDriverId(e.target.value)}
            required
            className="w-full rounded border px-3 py-2"
          >
            <option value="">Select driver / Selecionar piloto</option>
            {drivers.map((d) => (
              <option key={d.id} value={d.id}>
                {d.display_name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Lap Number / Volta *
          </label>
          <input
            type="number"
            min="1"
            value={lapNumber}
            onChange={(e) => setLapNumber(e.target.value)}
            required
            className="w-full rounded border px-3 py-2"
            placeholder="e.g. 15"
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Duration (ms) / Duracao (ms) *
          </label>
          <input
            type="number"
            min="1"
            value={durationMs}
            onChange={(e) => setDurationMs(e.target.value)}
            required
            className="w-full rounded border px-3 py-2"
            placeholder="e.g. 2450"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Tire From / Pneu De
          </label>
          <select
            value={tireFrom}
            onChange={(e) => setTireFrom(e.target.value)}
            className="w-full rounded border px-3 py-2"
          >
            <option value="">-</option>
            {TIRE_COMPOUNDS.map((c) => (
              <option key={c} value={c}>
                {c.charAt(0).toUpperCase() + c.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Tire To / Pneu Para
          </label>
          <select
            value={tireTo}
            onChange={(e) => setTireTo(e.target.value)}
            className="w-full rounded border px-3 py-2"
          >
            <option value="">-</option>
            {TIRE_COMPOUNDS.map((c) => (
              <option key={c} value={c}>
                {c.charAt(0).toUpperCase() + c.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Notes / Notas
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="w-full rounded border px-3 py-2"
          rows={2}
          placeholder="Optional notes / Notas opcionais"
        />
      </div>

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={saving}
          className="rounded bg-orange-600 px-4 py-2 text-white hover:bg-orange-700 disabled:opacity-50"
        >
          {saving ? "Saving... / Salvando..." : "Add Pit Stop / Adicionar Pit Stop"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded border px-4 py-2 text-gray-700 hover:bg-gray-50"
        >
          Cancel / Cancelar
        </button>
      </div>
    </form>
  );
}
