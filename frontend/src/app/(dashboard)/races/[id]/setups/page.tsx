"use client";

/**
 * Race car setups page: list, create, edit, and delete car setups.
 * Pagina de setups de carro: listar, criar, editar e excluir setups.
 */

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { CarSetup } from "@/types/telemetry";
import type { DriverListItem } from "@/types/driver";
import { telemetryApi, driversApi } from "@/lib/api-client";
import SetupForm from "@/components/telemetry/SetupForm";

export default function RaceSetupsPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [setups, setSetups] = useState<CarSetup[]>([]);
  const [drivers, setDrivers] = useState<DriverListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingSetup, setEditingSetup] = useState<CarSetup | null>(null);
  const [saving, setSaving] = useState(false);
  const [selectedDriver, setSelectedDriver] = useState("");

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  const fetchSetups = async () => {
    const { data, error: err } = await telemetryApi.listSetups(token, id);
    if (err) {
      setError(err);
    } else {
      setSetups(data || []);
      setError(null);
    }
  };

  useEffect(() => {
    if (!session || !id) return;

    const fetchData = async () => {
      setLoading(true);
      const [setupsResult, driversResult] = await Promise.all([
        telemetryApi.listSetups(token, id),
        driversApi.list(token, { is_active: true }),
      ]);

      if (setupsResult.error) {
        setError(setupsResult.error);
      } else {
        setSetups(setupsResult.data || []);
        setDrivers(driversResult.data || []);
        setError(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [session, id, token]);

  const handleCreate = async (data: Record<string, string | number | undefined>) => {
    if (!selectedDriver) {
      setError("Please select a driver. / Selecione um piloto.");
      return;
    }
    const driver = drivers.find((d) => d.id === selectedDriver);
    if (!driver) return;

    setSaving(true);
    const { error: err } = await telemetryApi.createSetup(token, id, {
      driver_id: driver.id,
      team_id: driver.team_id,
      name: data.name as string,
      notes: data.notes as string | undefined,
      front_wing: data.front_wing as number | undefined,
      rear_wing: data.rear_wing as number | undefined,
      differential: data.differential as number | undefined,
      brake_bias: data.brake_bias as number | undefined,
      tire_pressure_fl: data.tire_pressure_fl as number | undefined,
      tire_pressure_fr: data.tire_pressure_fr as number | undefined,
      tire_pressure_rl: data.tire_pressure_rl as number | undefined,
      tire_pressure_rr: data.tire_pressure_rr as number | undefined,
      suspension_stiffness: data.suspension_stiffness as number | undefined,
      anti_roll_bar: data.anti_roll_bar as number | undefined,
    });
    setSaving(false);

    if (err) {
      setError(err);
    } else {
      setShowForm(false);
      setSelectedDriver("");
      await fetchSetups();
    }
  };

  const handleUpdate = async (data: Record<string, string | number | undefined>) => {
    if (!editingSetup) return;
    setSaving(true);
    const { error: err } = await telemetryApi.updateSetup(token, editingSetup.id, {
      name: data.name as string | undefined,
      notes: data.notes as string | undefined,
      front_wing: data.front_wing as number | undefined,
      rear_wing: data.rear_wing as number | undefined,
      differential: data.differential as number | undefined,
      brake_bias: data.brake_bias as number | undefined,
      tire_pressure_fl: data.tire_pressure_fl as number | undefined,
      tire_pressure_fr: data.tire_pressure_fr as number | undefined,
      tire_pressure_rl: data.tire_pressure_rl as number | undefined,
      tire_pressure_rr: data.tire_pressure_rr as number | undefined,
      suspension_stiffness: data.suspension_stiffness as number | undefined,
      anti_roll_bar: data.anti_roll_bar as number | undefined,
    });
    setSaving(false);

    if (err) {
      setError(err);
    } else {
      setEditingSetup(null);
      await fetchSetups();
    }
  };

  const handleDelete = async (setupId: string) => {
    if (!confirm("Delete this setup? / Excluir este setup?")) return;
    const { error: err } = await telemetryApi.deleteSetup(token, setupId);
    if (err) {
      setError(err);
    } else {
      await fetchSetups();
    }
  };

  if (loading) return <p className="text-gray-500">Loading... / Carregando...</p>;
  if (error && !setups.length) return <p className="text-red-600">{error}</p>;

  // Group setups by driver / Agrupa setups por piloto
  const setupsByDriver = new Map<string, CarSetup[]>();
  setups.forEach((s) => {
    if (!setupsByDriver.has(s.driver_id)) {
      setupsByDriver.set(s.driver_id, []);
    }
    setupsByDriver.get(s.driver_id)!.push(s);
  });

  return (
    <div>
      {/* Header / Cabecalho */}
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Car Setups / Setups de Carro</h1>
        <div className="flex gap-2">
          {!showForm && !editingSetup && (
            <button
              onClick={() => setShowForm(true)}
              className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              Create Setup / Criar Setup
            </button>
          )}
          <Link href={`/races/${id}/telemetry`} className="rounded border px-4 py-2 text-gray-700 hover:bg-gray-50">
            Telemetry / Telemetria
          </Link>
          <Link href={`/races/${id}`} className="rounded border px-4 py-2 text-gray-700 hover:bg-gray-50">
            &larr; Back / Voltar
          </Link>
        </div>
      </div>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      {/* Create form / Formulario de criacao */}
      {showForm && (
        <div className="mb-6">
          <h2 className="mb-3 text-lg font-semibold text-gray-900">
            New Setup / Novo Setup
          </h2>
          <div className="mb-3">
            <label className="mr-2 text-sm font-medium text-gray-700">
              Driver / Piloto: *
            </label>
            <select
              value={selectedDriver}
              onChange={(e) => setSelectedDriver(e.target.value)}
              className="rounded border px-3 py-1.5 text-sm"
            >
              <option value="">Select... / Selecione...</option>
              {drivers.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.display_name} ({d.abbreviation})
                </option>
              ))}
            </select>
          </div>
          <SetupForm onSubmit={handleCreate} onCancel={() => setShowForm(false)} saving={saving} />
        </div>
      )}

      {/* Edit form / Formulario de edicao */}
      {editingSetup && (
        <div className="mb-6">
          <h2 className="mb-3 text-lg font-semibold text-gray-900">
            Edit Setup / Editar Setup: {editingSetup.name}
          </h2>
          <SetupForm
            initialData={{
              name: editingSetup.name,
              notes: editingSetup.notes || "",
              front_wing: editingSetup.front_wing?.toString() || "",
              rear_wing: editingSetup.rear_wing?.toString() || "",
              differential: editingSetup.differential?.toString() || "",
              brake_bias: editingSetup.brake_bias?.toString() || "",
              tire_pressure_fl: editingSetup.tire_pressure_fl?.toString() || "",
              tire_pressure_fr: editingSetup.tire_pressure_fr?.toString() || "",
              tire_pressure_rl: editingSetup.tire_pressure_rl?.toString() || "",
              tire_pressure_rr: editingSetup.tire_pressure_rr?.toString() || "",
              suspension_stiffness: editingSetup.suspension_stiffness?.toString() || "",
              anti_roll_bar: editingSetup.anti_roll_bar?.toString() || "",
            }}
            onSubmit={handleUpdate}
            onCancel={() => setEditingSetup(null)}
            saving={saving}
          />
        </div>
      )}

      {/* Setups list grouped by driver / Lista de setups agrupada por piloto */}
      {setups.length === 0 ? (
        <p className="text-gray-500">
          No setups configured. / Nenhum setup configurado.
        </p>
      ) : (
        Array.from(setupsByDriver.entries()).map(([driverId, driverSetups]) => {
          const driverName = drivers.find((d) => d.id === driverId)?.display_name || driverId;
          return (
            <div key={driverId} className="mb-6">
              <h2 className="mb-3 text-lg font-semibold text-gray-900">{driverName}</h2>
              <div className="space-y-3">
                {driverSetups.map((setup) => (
                  <div key={setup.id} className="rounded-lg border bg-white p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-gray-900">{setup.name}</h3>
                        {setup.notes && <p className="text-sm text-gray-500">{setup.notes}</p>}
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setEditingSetup(setup)}
                          className="rounded bg-yellow-500 px-3 py-1 text-sm text-white hover:bg-yellow-600"
                        >
                          Edit / Editar
                        </button>
                        <button
                          onClick={() => handleDelete(setup.id)}
                          className="rounded bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700"
                        >
                          Delete / Excluir
                        </button>
                      </div>
                    </div>
                    {/* Setup values grid / Grade de valores do setup */}
                    <div className="mt-3 grid grid-cols-2 gap-2 text-sm sm:grid-cols-4">
                      {setup.front_wing !== null && (
                        <div><span className="text-gray-500">Front Wing:</span> {setup.front_wing}</div>
                      )}
                      {setup.rear_wing !== null && (
                        <div><span className="text-gray-500">Rear Wing:</span> {setup.rear_wing}</div>
                      )}
                      {setup.differential !== null && (
                        <div><span className="text-gray-500">Differential:</span> {setup.differential}</div>
                      )}
                      {setup.brake_bias !== null && (
                        <div><span className="text-gray-500">Brake Bias:</span> {setup.brake_bias}%</div>
                      )}
                      {setup.tire_pressure_fl !== null && (
                        <div><span className="text-gray-500">FL:</span> {setup.tire_pressure_fl}</div>
                      )}
                      {setup.tire_pressure_fr !== null && (
                        <div><span className="text-gray-500">FR:</span> {setup.tire_pressure_fr}</div>
                      )}
                      {setup.tire_pressure_rl !== null && (
                        <div><span className="text-gray-500">RL:</span> {setup.tire_pressure_rl}</div>
                      )}
                      {setup.tire_pressure_rr !== null && (
                        <div><span className="text-gray-500">RR:</span> {setup.tire_pressure_rr}</div>
                      )}
                      {setup.suspension_stiffness !== null && (
                        <div><span className="text-gray-500">Suspension:</span> {setup.suspension_stiffness}</div>
                      )}
                      {setup.anti_roll_bar !== null && (
                        <div><span className="text-gray-500">Anti-Roll:</span> {setup.anti_roll_bar}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}
