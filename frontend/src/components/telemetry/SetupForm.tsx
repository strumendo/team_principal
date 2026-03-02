"use client";

/**
 * Car setup form: create or edit a car setup configuration.
 * Formulario de setup: cria ou edita uma configuracao de setup de carro.
 */

import { useState } from "react";

interface SetupFormData {
  name: string;
  notes: string;
  front_wing: string;
  rear_wing: string;
  differential: string;
  brake_bias: string;
  tire_pressure_fl: string;
  tire_pressure_fr: string;
  tire_pressure_rl: string;
  tire_pressure_rr: string;
  suspension_stiffness: string;
  anti_roll_bar: string;
}

interface SetupFormProps {
  initialData?: Partial<SetupFormData>;
  onSubmit: (data: Record<string, string | number | undefined>) => Promise<void>;
  onCancel: () => void;
  saving?: boolean;
}

const EMPTY_FORM: SetupFormData = {
  name: "",
  notes: "",
  front_wing: "",
  rear_wing: "",
  differential: "",
  brake_bias: "",
  tire_pressure_fl: "",
  tire_pressure_fr: "",
  tire_pressure_rl: "",
  tire_pressure_rr: "",
  suspension_stiffness: "",
  anti_roll_bar: "",
};

function FloatInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-gray-700">{label}</label>
      <input
        type="number"
        step="0.1"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded border px-3 py-2 text-sm"
        placeholder="0.0"
      />
    </div>
  );
}

export default function SetupForm({ initialData, onSubmit, onCancel, saving = false }: SetupFormProps) {
  const [form, setForm] = useState<SetupFormData>({ ...EMPTY_FORM, ...initialData });
  const [error, setError] = useState<string | null>(null);

  const set = (field: keyof SetupFormData) => (value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError("Name is required. / Nome e obrigatorio.");
      return;
    }
    setError(null);

    const data: Record<string, string | number | undefined> = { name: form.name };
    if (form.notes) data.notes = form.notes;

    const floatFields: (keyof SetupFormData)[] = [
      "front_wing", "rear_wing", "differential", "brake_bias",
      "tire_pressure_fl", "tire_pressure_fr", "tire_pressure_rl", "tire_pressure_rr",
      "suspension_stiffness", "anti_roll_bar",
    ];
    for (const field of floatFields) {
      if (form[field] !== "") {
        data[field] = parseFloat(form[field]);
      }
    }

    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded border p-4">
      {error && <p className="text-sm text-red-600">{error}</p>}

      {/* Name and Notes / Nome e Notas */}
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Name / Nome *
        </label>
        <input
          type="text"
          value={form.name}
          onChange={(e) => set("name")(e.target.value)}
          required
          className="w-full rounded border px-3 py-2"
          placeholder="e.g. Monza Low Downforce"
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Notes / Notas
        </label>
        <textarea
          value={form.notes}
          onChange={(e) => set("notes")(e.target.value)}
          className="w-full rounded border px-3 py-2"
          rows={2}
          placeholder="Optional setup notes / Notas opcionais"
        />
      </div>

      {/* Aero / Aerodinamica */}
      <fieldset className="rounded border p-3">
        <legend className="px-2 text-sm font-semibold text-gray-700">
          Aero / Aerodinamica
        </legend>
        <div className="grid grid-cols-2 gap-3">
          <FloatInput label="Front Wing / Asa Dianteira" value={form.front_wing} onChange={set("front_wing")} />
          <FloatInput label="Rear Wing / Asa Traseira" value={form.rear_wing} onChange={set("rear_wing")} />
        </div>
      </fieldset>

      {/* Mechanical / Mecanica */}
      <fieldset className="rounded border p-3">
        <legend className="px-2 text-sm font-semibold text-gray-700">
          Mechanical / Mecanica
        </legend>
        <div className="grid grid-cols-2 gap-3">
          <FloatInput label="Differential / Diferencial" value={form.differential} onChange={set("differential")} />
          <FloatInput label="Brake Bias / Balanco de Freio" value={form.brake_bias} onChange={set("brake_bias")} />
          <FloatInput label="Suspension / Suspensao" value={form.suspension_stiffness} onChange={set("suspension_stiffness")} />
          <FloatInput label="Anti-Roll Bar / Barra Anti-Rolagem" value={form.anti_roll_bar} onChange={set("anti_roll_bar")} />
        </div>
      </fieldset>

      {/* Tires / Pneus */}
      <fieldset className="rounded border p-3">
        <legend className="px-2 text-sm font-semibold text-gray-700">
          Tire Pressure / Pressao dos Pneus
        </legend>
        <div className="grid grid-cols-2 gap-3">
          <FloatInput label="FL (Front Left / Dianteiro Esq.)" value={form.tire_pressure_fl} onChange={set("tire_pressure_fl")} />
          <FloatInput label="FR (Front Right / Dianteiro Dir.)" value={form.tire_pressure_fr} onChange={set("tire_pressure_fr")} />
          <FloatInput label="RL (Rear Left / Traseiro Esq.)" value={form.tire_pressure_rl} onChange={set("tire_pressure_rl")} />
          <FloatInput label="RR (Rear Right / Traseiro Dir.)" value={form.tire_pressure_rr} onChange={set("tire_pressure_rr")} />
        </div>
      </fieldset>

      {/* Actions / Acoes */}
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={saving}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Saving... / Salvando..." : "Save / Salvar"}
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
