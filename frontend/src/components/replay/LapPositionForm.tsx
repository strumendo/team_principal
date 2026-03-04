"use client";

/**
 * Form for creating lap positions (bulk entry).
 * Formulario para criar posicoes por volta (entrada em massa).
 */

import { useState } from "react";

interface DriverOption {
  id: string;
  display_name: string;
  team_id: string;
}

interface LapPositionFormProps {
  raceId: string;
  drivers: DriverOption[];
  token: string;
  onSubmit: (positions: Array<{
    driver_id: string;
    team_id: string;
    lap_number: number;
    position: number;
    gap_to_leader_ms?: number;
    interval_ms?: number;
  }>) => Promise<void>;
  onCancel: () => void;
}

export default function LapPositionForm({
  drivers,
  onSubmit,
  onCancel,
}: LapPositionFormProps) {
  const [lapNumber, setLapNumber] = useState(1);
  const [positionEntries, setPositionEntries] = useState<
    Array<{ driverId: string; position: number; gap: string; interval: string }>
  >(drivers.map((d) => ({ driverId: d.id, position: 0, gap: "", interval: "" })));
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePositionChange = (index: number, field: string, value: string) => {
    setPositionEntries((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: field === "position" ? Number(value) : value };
      return updated;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const positions = positionEntries
        .filter((entry) => entry.position > 0)
        .map((entry) => {
          const driver = drivers.find((d) => d.id === entry.driverId);
          return {
            driver_id: entry.driverId,
            team_id: driver?.team_id || "",
            lap_number: lapNumber,
            position: entry.position,
            ...(entry.gap ? { gap_to_leader_ms: Number(entry.gap) } : {}),
            ...(entry.interval ? { interval_ms: Number(entry.interval) } : {}),
          };
        });

      await onSubmit(positions);
    } catch {
      setError("Failed to create positions. / Falha ao criar posicoes.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">
        Add Positions / Adicionar Posicoes
      </h3>

      {error && <p className="mb-2 text-sm text-red-600">{error}</p>}

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700">Lap Number / Numero da Volta</label>
        <input
          type="number"
          min={1}
          value={lapNumber}
          onChange={(e) => setLapNumber(Number(e.target.value))}
          className="mt-1 block w-32 rounded border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500 sm:text-sm"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr>
              <th className="px-2 py-1 text-left text-xs text-gray-500">Driver / Piloto</th>
              <th className="px-2 py-1 text-left text-xs text-gray-500">Position / Posicao</th>
              <th className="px-2 py-1 text-left text-xs text-gray-500">Gap (ms)</th>
              <th className="px-2 py-1 text-left text-xs text-gray-500">Interval (ms)</th>
            </tr>
          </thead>
          <tbody>
            {positionEntries.map((entry, i) => {
              const driver = drivers.find((d) => d.id === entry.driverId);
              return (
                <tr key={entry.driverId}>
                  <td className="px-2 py-1">{driver?.display_name}</td>
                  <td className="px-2 py-1">
                    <input
                      type="number"
                      min={0}
                      value={entry.position}
                      onChange={(e) => handlePositionChange(i, "position", e.target.value)}
                      className="w-20 rounded border-gray-300 text-sm"
                    />
                  </td>
                  <td className="px-2 py-1">
                    <input
                      type="text"
                      value={entry.gap}
                      onChange={(e) => handlePositionChange(i, "gap", e.target.value)}
                      className="w-24 rounded border-gray-300 text-sm"
                      placeholder="0"
                    />
                  </td>
                  <td className="px-2 py-1">
                    <input
                      type="text"
                      value={entry.interval}
                      onChange={(e) => handlePositionChange(i, "interval", e.target.value)}
                      className="w-24 rounded border-gray-300 text-sm"
                      placeholder="0"
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
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
