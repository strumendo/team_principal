/**
 * Race replay and analysis page.
 * Pagina de replay e analise de corrida.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { replayApi, racesApi, driversApi } from "@/lib/api-client";
import type { RaceDetail } from "@/types/race";
import type {
  FullReplayResponse,
  StintAnalysisResponse,
  OvertakesResponse,
  RaceSummaryResponse,
  RaceEventType,
} from "@/types/race-replay";
import PositionChart from "@/components/replay/PositionChart";
import GapChart from "@/components/replay/GapChart";
import RaceTimeline from "@/components/replay/RaceTimeline";
import StintTable from "@/components/replay/StintTable";
import RaceSummary from "@/components/replay/RaceSummary";
import LapPositionForm from "@/components/replay/LapPositionForm";
import RaceEventForm from "@/components/replay/RaceEventForm";

type TabType = "replay" | "analysis" | "summary";

interface DriverOption {
  id: string;
  display_name: string;
  team_id: string;
}

export default function RaceReplayPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [race, setRace] = useState<RaceDetail | null>(null);
  const [replay, setReplay] = useState<FullReplayResponse | null>(null);
  const [stints, setStints] = useState<StintAnalysisResponse | null>(null);
  const [overtakes, setOvertakes] = useState<OvertakesResponse | null>(null);
  const [summary, setSummary] = useState<RaceSummaryResponse | null>(null);
  const [drivers, setDrivers] = useState<DriverOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>("replay");
  const [filterDriverId, setFilterDriverId] = useState<string>("");
  const [showPositionForm, setShowPositionForm] = useState(false);
  const [showEventForm, setShowEventForm] = useState(false);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !id) return;

    const fetchData = async () => {
      setLoading(true);
      const [raceResult, replayResult, stintsResult, overtakesResult, summaryResult, driversResult] = await Promise.all([
        racesApi.get(token, id),
        replayApi.getReplay(token, id),
        replayApi.getStintAnalysis(token, id),
        replayApi.getOvertakes(token, id),
        replayApi.getRaceSummary(token, id),
        driversApi.list(token),
      ]);

      if (raceResult.error) {
        setError(raceResult.error);
      } else {
        setRace(raceResult.data || null);
        setReplay(replayResult.data || null);
        setStints(stintsResult.data || null);
        setOvertakes(overtakesResult.data || null);
        setSummary(summaryResult.data || null);
        setDrivers(
          (driversResult.data || []).map((d) => ({
            id: d.id,
            display_name: d.display_name,
            team_id: d.team_id || "",
          })),
        );
        setError(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [session, id, token]);

  const refreshData = async () => {
    const [replayResult, stintsResult, overtakesResult, summaryResult] = await Promise.all([
      replayApi.getReplay(token, id),
      replayApi.getStintAnalysis(token, id),
      replayApi.getOvertakes(token, id),
      replayApi.getRaceSummary(token, id),
    ]);
    setReplay(replayResult.data || null);
    setStints(stintsResult.data || null);
    setOvertakes(overtakesResult.data || null);
    setSummary(summaryResult.data || null);
  };

  const handlePositionSubmit = async (positions: Array<{
    driver_id: string;
    team_id: string;
    lap_number: number;
    position: number;
    gap_to_leader_ms?: number;
    interval_ms?: number;
  }>) => {
    await replayApi.bulkCreatePositions(token, id, positions);
    setShowPositionForm(false);
    await refreshData();
  };

  const handleEventSubmit = async (data: {
    lap_number: number;
    event_type: RaceEventType;
    description?: string;
    driver_id?: string;
  }) => {
    await replayApi.createEvent(token, id, data);
    setShowEventForm(false);
    await refreshData();
  };

  if (loading) {
    return <p className="text-gray-500">Loading... / Carregando...</p>;
  }

  if (error) {
    return <p className="text-red-600">{error}</p>;
  }

  if (!race) {
    return <p className="text-gray-500">Race not found. / Corrida nao encontrada.</p>;
  }

  const TABS: { key: TabType; label: string }[] = [
    { key: "replay", label: "Replay" },
    { key: "analysis", label: "Analysis / Analise" },
    { key: "summary", label: "Summary / Resumo" },
  ];

  // Collect unique drivers from replay data for filter
  const replayDrivers: { id: string; name: string }[] = [];
  const seen = new Set<string>();
  replay?.laps.forEach((lap) =>
    lap.positions.forEach((p) => {
      if (!seen.has(p.driver_id)) {
        seen.add(p.driver_id);
        replayDrivers.push({ id: p.driver_id, name: p.driver_name });
      }
    }),
  );

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Replay — {race.display_name}
          </h1>
          <p className="text-sm text-gray-500">{race.name}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowPositionForm(!showPositionForm)}
            className="rounded bg-pink-600 px-4 py-2 text-sm text-white hover:bg-pink-700"
          >
            {showPositionForm ? "Hide / Esconder" : "Add Positions / Adicionar Posicoes"}
          </button>
          <button
            onClick={() => setShowEventForm(!showEventForm)}
            className="rounded bg-purple-600 px-4 py-2 text-sm text-white hover:bg-purple-700"
          >
            {showEventForm ? "Hide / Esconder" : "Add Event / Adicionar Evento"}
          </button>
        </div>
      </div>

      {/* Forms / Formularios */}
      {showPositionForm && (
        <div className="mb-6">
          <LapPositionForm
            raceId={id}
            drivers={drivers}
            token={token}
            onSubmit={handlePositionSubmit}
            onCancel={() => setShowPositionForm(false)}
          />
        </div>
      )}

      {showEventForm && (
        <div className="mb-6">
          <RaceEventForm
            raceId={id}
            drivers={drivers}
            token={token}
            onSubmit={handleEventSubmit}
            onCancel={() => setShowEventForm(false)}
          />
        </div>
      )}

      {/* Tab bar / Barra de abas */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex gap-4">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`border-b-2 px-1 pb-3 text-sm font-medium ${
                activeTab === tab.key
                  ? "border-pink-500 text-pink-600"
                  : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Driver filter / Filtro de piloto */}
      {activeTab === "replay" && replayDrivers.length > 0 && (
        <div className="mb-4">
          <label className="mr-2 text-sm font-medium text-gray-700">
            Filter Driver / Filtrar Piloto:
          </label>
          <select
            value={filterDriverId}
            onChange={(e) => setFilterDriverId(e.target.value)}
            className="rounded border-gray-300 text-sm"
          >
            <option value="">All Drivers / Todos os Pilotos</option>
            {replayDrivers.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
        </div>
      )}

      {/* Tab content / Conteudo das abas */}
      {activeTab === "replay" && replay && (
        <div className="space-y-6">
          <PositionChart laps={replay.laps} filterDriverId={filterDriverId || undefined} />
          <GapChart laps={replay.laps} filterDriverId={filterDriverId || undefined} />
          <RaceTimeline laps={replay.laps} totalLaps={replay.total_laps} />

          {/* Overtakes list / Lista de ultrapassagens */}
          {overtakes && overtakes.overtakes.length > 0 && (
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <h3 className="mb-3 text-sm font-semibold text-gray-700">
                Overtakes ({overtakes.total_overtakes}) / Ultrapassagens
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Lap / Volta</th>
                      <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Driver / Piloto</th>
                      <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">From / De</th>
                      <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">To / Para</th>
                      <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">Gained / Ganhou</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {overtakes.overtakes.map((ot, i) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="px-3 py-2">{ot.lap_number}</td>
                        <td className="px-3 py-2 font-medium">{ot.driver_name}</td>
                        <td className="px-3 py-2">P{ot.from_position}</td>
                        <td className="px-3 py-2 font-bold text-green-600">P{ot.to_position}</td>
                        <td className="px-3 py-2">+{ot.positions_gained}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "analysis" && stints && (
        <StintTable data={stints} />
      )}

      {activeTab === "summary" && summary && (
        <RaceSummary data={summary} />
      )}

      <div className="mt-6">
        <Link href={`/races/${id}`} className="text-blue-600 hover:underline">
          &larr; Back to Race / Voltar a Corrida
        </Link>
      </div>
    </div>
  );
}
