"use client";

/**
 * Race strategies page: create, edit, and delete race strategies.
 * Pagina de estrategias: criar, editar e excluir estrategias de corrida.
 */

import { useCallback, useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { RaceStrategy, TireCompound } from "@/types/pitstops";
import type { DriverListItem } from "@/types/driver";
import { strategiesApi, driversApi } from "@/lib/api-client";
import StrategyCard from "@/components/pitstops/StrategyCard";

const TIRE_COMPOUNDS: TireCompound[] = ["soft", "medium", "hard", "intermediate", "wet"];

export default function RaceStrategiesPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [strategies, setStrategies] = useState<RaceStrategy[]>([]);
  const [drivers, setDrivers] = useState<DriverListItem[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<RaceStrategy | null>(null);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state / Estado do formulario
  const [formDriverId, setFormDriverId] = useState("");
  const [formName, setFormName] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [formTargetStops, setFormTargetStops] = useState("1");
  const [formPlannedLaps, setFormPlannedLaps] = useState("");
  const [formStartingCompound, setFormStartingCompound] = useState("");

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  const fetchData = useCallback(async () => {
    setLoading(true);
    const [strategiesResult, driversResult] = await Promise.all([
      strategiesApi.list(token, id),
      driversApi.list(token),
    ]);

    if (strategiesResult.error) {
      setError(strategiesResult.error);
    } else {
      setStrategies(strategiesResult.data || []);
      setDrivers(driversResult.data || []);
      setError(null);
    }
    setLoading(false);
  }, [token, id]);

  useEffect(() => {
    if (!session || !id) return;
    fetchData();
  }, [session, id, fetchData]);

  const resetForm = () => {
    setFormDriverId("");
    setFormName("");
    setFormDescription("");
    setFormTargetStops("1");
    setFormPlannedLaps("");
    setFormStartingCompound("");
    setEditingStrategy(null);
    setShowForm(false);
  };

  const handleEdit = (strategy: RaceStrategy) => {
    setEditingStrategy(strategy);
    setFormDriverId(strategy.driver_id);
    setFormName(strategy.name);
    setFormDescription(strategy.description || "");
    setFormTargetStops(String(strategy.target_stops));
    setFormPlannedLaps(strategy.planned_laps || "");
    setFormStartingCompound(strategy.starting_compound || "");
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formName.trim()) {
      setError("Name is required. / Nome e obrigatorio.");
      return;
    }
    setSaving(true);
    setError(null);

    if (editingStrategy) {
      // Update / Atualizar
      const data: Record<string, string | number | boolean | undefined> = {};
      if (formName !== editingStrategy.name) data.name = formName;
      if (formDescription !== (editingStrategy.description || "")) data.description = formDescription;
      if (parseInt(formTargetStops) !== editingStrategy.target_stops) data.target_stops = parseInt(formTargetStops);
      if (formPlannedLaps !== (editingStrategy.planned_laps || "")) data.planned_laps = formPlannedLaps;
      if (formStartingCompound !== (editingStrategy.starting_compound || "")) {
        data.starting_compound = formStartingCompound || undefined;
      }

      const { error: err } = await strategiesApi.update(token, editingStrategy.id, data as Parameters<typeof strategiesApi.update>[2]);
      setSaving(false);
      if (err) {
        setError(err);
      } else {
        resetForm();
        await fetchData();
      }
    } else {
      // Create / Criar
      const selectedDriver = drivers.find((d) => d.id === formDriverId);
      const data: {
        driver_id: string;
        team_id: string;
        name: string;
        description?: string;
        target_stops: number;
        planned_laps?: string;
        starting_compound?: TireCompound;
      } = {
        driver_id: formDriverId,
        team_id: selectedDriver?.team_id || "",
        name: formName,
        target_stops: parseInt(formTargetStops),
      };
      if (formDescription.trim()) data.description = formDescription.trim();
      if (formPlannedLaps.trim()) data.planned_laps = formPlannedLaps.trim();
      if (formStartingCompound) data.starting_compound = formStartingCompound as TireCompound;

      const { error: err } = await strategiesApi.create(token, id, data);
      setSaving(false);
      if (err) {
        setError(err);
      } else {
        resetForm();
        await fetchData();
      }
    }
  };

  const handleDelete = async (strategyId: string) => {
    if (!confirm("Delete this strategy? / Excluir esta estrategia?")) return;
    const { error: err } = await strategiesApi.delete(token, strategyId);
    if (err) {
      setError(err);
    } else {
      await fetchData();
    }
  };

  if (loading) return <p className="text-gray-500">Loading... / Carregando...</p>;

  return (
    <div>
      {/* Header / Cabecalho */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Strategies / Estrategias</h1>
          <p className="text-sm text-gray-500">Race ID: {id}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => {
              if (showForm) { resetForm(); } else { setShowForm(true); }
            }}
            className="rounded bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700"
          >
            {showForm ? "Cancel / Cancelar" : "New Strategy / Nova Estrategia"}
          </button>
          <Link
            href={`/races/${id}/pitstops`}
            className="rounded bg-orange-600 px-4 py-2 text-white hover:bg-orange-700"
          >
            Pit Stops
          </Link>
          <Link href={`/races/${id}`} className="rounded border px-4 py-2 text-gray-700 hover:bg-gray-50">
            &larr; Back / Voltar
          </Link>
        </div>
      </div>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      {/* Form / Formulario */}
      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 space-y-4 rounded border p-4">
          <div className="grid grid-cols-2 gap-4">
            {!editingStrategy && (
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Driver / Piloto *
                </label>
                <select
                  value={formDriverId}
                  onChange={(e) => setFormDriverId(e.target.value)}
                  required
                  className="w-full rounded border px-3 py-2"
                >
                  <option value="">Select driver / Selecionar piloto</option>
                  {drivers.map((d) => (
                    <option key={d.id} value={d.id}>{d.display_name}</option>
                  ))}
                </select>
              </div>
            )}
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Name / Nome *
              </label>
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                required
                className="w-full rounded border px-3 py-2"
                placeholder="e.g. Two Stop Medium-Hard"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Description / Descricao
            </label>
            <textarea
              value={formDescription}
              onChange={(e) => setFormDescription(e.target.value)}
              className="w-full rounded border px-3 py-2"
              rows={2}
              placeholder="Strategy description / Descricao da estrategia"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Target Stops / Paradas *
              </label>
              <input
                type="number"
                min="0"
                value={formTargetStops}
                onChange={(e) => setFormTargetStops(e.target.value)}
                required
                className="w-full rounded border px-3 py-2"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Planned Laps / Voltas
              </label>
              <input
                type="text"
                value={formPlannedLaps}
                onChange={(e) => setFormPlannedLaps(e.target.value)}
                className="w-full rounded border px-3 py-2"
                placeholder="e.g. 15,35"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Starting Compound / Composto
              </label>
              <select
                value={formStartingCompound}
                onChange={(e) => setFormStartingCompound(e.target.value)}
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

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={saving}
              className="rounded bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {saving
                ? "Saving... / Salvando..."
                : editingStrategy
                  ? "Update / Atualizar"
                  : "Create / Criar"}
            </button>
            <button
              type="button"
              onClick={resetForm}
              className="rounded border px-4 py-2 text-gray-700 hover:bg-gray-50"
            >
              Cancel / Cancelar
            </button>
          </div>
        </form>
      )}

      {/* Strategy cards / Cards de estrategia */}
      {strategies.length === 0 ? (
        <p className="text-gray-500">
          No strategies defined. / Nenhuma estrategia definida.
        </p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {strategies.map((strategy) => (
            <StrategyCard
              key={strategy.id}
              strategy={strategy}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
