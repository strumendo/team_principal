/**
 * Enhanced championship standings page with tabs and race-by-race breakdown.
 * Pagina aprimorada de classificacao do campeonato com abas e detalhamento corrida-a-corrida.
 */
"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { ChampionshipStanding } from "@/types/result";
import type { StandingsBreakdown, TeamBreakdown, DriverBreakdown, RacePoints } from "@/types/result";
import type { DriverStanding } from "@/types/driver";
import type { ChampionshipDetail } from "@/types/championship";
import { championshipsApi } from "@/lib/api-client";

type Tab = "teams" | "drivers";

const PODIUM_BORDER: Record<number, string> = {
  1: "border-l-4 border-yellow-400 bg-yellow-50",
  2: "border-l-4 border-gray-400 bg-gray-50",
  3: "border-l-4 border-amber-600 bg-amber-50",
};

function getRacePointsForRace(racePoints: RacePoints[], raceId: string): RacePoints | null {
  return racePoints.find((rp) => rp.race_id === raceId) || null;
}

export default function ChampionshipStandingsPage() {
  const { data: session } = useSession();
  const params = useParams();
  const id = params.id as string;

  const [championship, setChampionship] = useState<ChampionshipDetail | null>(null);
  const [teamStandings, setTeamStandings] = useState<ChampionshipStanding[]>([]);
  const [driverStandings, setDriverStandings] = useState<DriverStanding[]>([]);
  const [breakdown, setBreakdown] = useState<StandingsBreakdown | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("teams");
  const [showBreakdown, setShowBreakdown] = useState(false);

  const token = session ? (session as unknown as { accessToken: string }).accessToken : "";

  useEffect(() => {
    if (!session || !id) return;

    const fetchData = async () => {
      setLoading(true);
      const [champResult, standingsResult, driverResult, breakdownResult] = await Promise.all([
        championshipsApi.get(token, id),
        championshipsApi.getStandings(token, id),
        championshipsApi.getDriverStandings(token, id),
        championshipsApi.getStandingsBreakdown(token, id),
      ]);

      if (champResult.error) {
        setError(champResult.error);
      } else {
        setChampionship(champResult.data || null);
        setTeamStandings(standingsResult.data || []);
        setDriverStandings(driverResult.data || []);
        setBreakdown(breakdownResult.data || null);
        setError(null);
      }
      setLoading(false);
    };

    fetchData();
  }, [session, id, token]);

  if (loading) {
    return <p className="text-gray-500">Loading... / Carregando...</p>;
  }

  if (error) {
    return <p className="text-red-600">{error}</p>;
  }

  if (!championship) {
    return <p className="text-gray-500">Championship not found. / Campeonato nao encontrado.</p>;
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          Standings / Classificacao — {championship.display_name}
        </h1>
        <p className="text-sm text-gray-500">{championship.name}</p>
      </div>

      {/* Tabs / Abas */}
      <div className="mb-4 flex items-center gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab("teams")}
          className={`px-4 py-2 text-sm font-medium ${
            activeTab === "teams"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Teams / Equipes
        </button>
        <button
          onClick={() => setActiveTab("drivers")}
          className={`px-4 py-2 text-sm font-medium ${
            activeTab === "drivers"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Drivers / Pilotos
        </button>

        {/* Breakdown toggle / Toggle de detalhamento */}
        {breakdown && breakdown.races.length > 0 && (
          <label className="ml-auto flex items-center gap-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={showBreakdown}
              onChange={(e) => setShowBreakdown(e.target.checked)}
              className="rounded border-gray-300"
            />
            Race-by-race / Corrida-a-corrida
          </label>
        )}
      </div>

      {/* Teams tab / Aba de equipes */}
      {activeTab === "teams" && (
        <>
          {teamStandings.length === 0 ? (
            <p className="text-gray-500">
              No standings yet. / Nenhuma classificacao ainda.
            </p>
          ) : showBreakdown && breakdown ? (
            <TeamBreakdownTable
              teams={breakdown.team_standings}
              races={breakdown.races}
            />
          ) : (
            <TeamStandingsTable standings={teamStandings} />
          )}
        </>
      )}

      {/* Drivers tab / Aba de pilotos */}
      {activeTab === "drivers" && (
        <>
          {driverStandings.length === 0 ? (
            <p className="text-gray-500">
              No driver standings yet. / Nenhuma classificacao de pilotos ainda.
            </p>
          ) : showBreakdown && breakdown ? (
            <DriverBreakdownTable
              drivers={breakdown.driver_standings}
              races={breakdown.races}
            />
          ) : (
            <DriverStandingsTable standings={driverStandings} />
          )}
        </>
      )}

      <div className="mt-6 flex gap-4">
        <Link href="/standings" className="text-blue-600 hover:underline">
          &larr; All Standings / Todas as Classificacoes
        </Link>
        <Link href={`/championships/${id}`} className="text-blue-600 hover:underline">
          &larr; Back to Championship / Voltar ao Campeonato
        </Link>
      </div>
    </div>
  );
}

/* ──────── Team Standings Table / Tabela de classificacao de equipes ──────── */

function TeamStandingsTable({ standings }: { standings: ChampionshipStanding[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Pos</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Team / Equipe</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Points / Pontos</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Races / Corridas</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Wins / Vitorias</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {standings.map((s) => (
            <tr key={s.team_id} className={PODIUM_BORDER[s.position] || "hover:bg-gray-50"}>
              <td className="px-6 py-4 text-sm font-medium text-gray-900">{s.position}</td>
              <td className="px-6 py-4">
                <p className="font-medium text-gray-900">{s.team_display_name}</p>
                <p className="text-sm text-gray-500">{s.team_name}</p>
              </td>
              <td className="px-6 py-4 text-sm font-semibold text-gray-900">{s.total_points}</td>
              <td className="px-6 py-4 text-sm text-gray-500">{s.races_scored}</td>
              <td className="px-6 py-4 text-sm text-gray-500">{s.wins}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ──────── Driver Standings Table / Tabela de classificacao de pilotos ──────── */

function DriverStandingsTable({ standings }: { standings: DriverStanding[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Pos</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Driver / Piloto</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Team / Equipe</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Points / Pontos</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Races / Corridas</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Wins / Vitorias</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {standings.map((s) => (
            <tr key={s.driver_id} className={PODIUM_BORDER[s.position] || "hover:bg-gray-50"}>
              <td className="px-6 py-4 text-sm font-medium text-gray-900">{s.position}</td>
              <td className="px-6 py-4">
                <p className="font-medium text-gray-900">{s.driver_display_name}</p>
                <p className="text-sm text-gray-500">{s.driver_abbreviation}</p>
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">{s.team_display_name}</td>
              <td className="px-6 py-4 text-sm font-semibold text-gray-900">{s.total_points}</td>
              <td className="px-6 py-4 text-sm text-gray-500">{s.races_scored}</td>
              <td className="px-6 py-4 text-sm text-gray-500">{s.wins}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ──────── Team Breakdown Table / Tabela matricial de equipes ──────── */

function TeamBreakdownTable({
  teams,
  races,
}: {
  teams: TeamBreakdown[];
  races: StandingsBreakdown["races"];
}) {
  return (
    <>
      {/* Desktop: matrix table / Desktop: tabela matricial */}
      <div className="hidden overflow-x-auto md:block">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Pos</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Team / Equipe</th>
              {races.map((r) => (
                <th key={r.race_id} className="px-3 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">
                  R{r.round_number}
                </th>
              ))}
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">Total</th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">Wins</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {teams.map((t) => (
              <tr key={t.team_id} className={PODIUM_BORDER[t.position] || "hover:bg-gray-50"}>
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{t.position}</td>
                <td className="px-4 py-3">
                  <p className="font-medium text-gray-900">{t.team_display_name}</p>
                </td>
                {races.map((r) => {
                  const rp = getRacePointsForRace(t.race_points, r.race_id);
                  return (
                    <td key={r.race_id} className="px-3 py-3 text-center text-sm">
                      {rp ? (
                        <span className={rp.dsq ? "text-red-500 line-through" : "text-gray-700"}>
                          {rp.points}
                        </span>
                      ) : (
                        <span className="text-gray-300">—</span>
                      )}
                    </td>
                  );
                })}
                <td className="px-4 py-3 text-right text-sm font-bold text-gray-900">{t.total_points}</td>
                <td className="px-4 py-3 text-right text-sm text-gray-500">{t.wins}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile: cards with race points grid / Mobile: cards com grid de pontos */}
      <div className="space-y-3 md:hidden">
        {teams.map((t) => (
          <div
            key={t.team_id}
            className={`rounded-lg border p-4 ${PODIUM_BORDER[t.position] || "border-gray-200 bg-white"}`}
          >
            <div className="mb-2 flex items-center justify-between">
              <div>
                <span className="mr-2 text-lg font-bold text-gray-900">#{t.position}</span>
                <span className="font-medium text-gray-900">{t.team_display_name}</span>
              </div>
              <span className="text-lg font-bold text-gray-900">{t.total_points} pts</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {races.map((r) => {
                const rp = getRacePointsForRace(t.race_points, r.race_id);
                return (
                  <div key={r.race_id} className="rounded bg-gray-100 px-2 py-1 text-xs">
                    <span className="font-medium text-gray-500">R{r.round_number}: </span>
                    {rp ? (
                      <span className={rp.dsq ? "text-red-500 line-through" : "text-gray-700"}>
                        {rp.points}
                      </span>
                    ) : (
                      <span className="text-gray-300">—</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

/* ──────── Driver Breakdown Table / Tabela matricial de pilotos ──────── */

function DriverBreakdownTable({
  drivers,
  races,
}: {
  drivers: DriverBreakdown[];
  races: StandingsBreakdown["races"];
}) {
  return (
    <>
      {/* Desktop: matrix table / Desktop: tabela matricial */}
      <div className="hidden overflow-x-auto md:block">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Pos</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Driver / Piloto</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Team / Equipe</th>
              {races.map((r) => (
                <th key={r.race_id} className="px-3 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">
                  R{r.round_number}
                </th>
              ))}
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">Total</th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">Wins</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {drivers.map((d) => (
              <tr key={d.driver_id} className={PODIUM_BORDER[d.position] || "hover:bg-gray-50"}>
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{d.position}</td>
                <td className="px-4 py-3">
                  <p className="font-medium text-gray-900">{d.driver_display_name}</p>
                  <p className="text-xs text-gray-500">{d.driver_abbreviation}</p>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{d.team_display_name}</td>
                {races.map((r) => {
                  const rp = getRacePointsForRace(d.race_points, r.race_id);
                  return (
                    <td key={r.race_id} className="px-3 py-3 text-center text-sm">
                      {rp ? (
                        <span className={rp.dsq ? "text-red-500 line-through" : "text-gray-700"}>
                          {rp.points}
                        </span>
                      ) : (
                        <span className="text-gray-300">—</span>
                      )}
                    </td>
                  );
                })}
                <td className="px-4 py-3 text-right text-sm font-bold text-gray-900">{d.total_points}</td>
                <td className="px-4 py-3 text-right text-sm text-gray-500">{d.wins}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile: cards with race points grid / Mobile: cards com grid de pontos */}
      <div className="space-y-3 md:hidden">
        {drivers.map((d) => (
          <div
            key={d.driver_id}
            className={`rounded-lg border p-4 ${PODIUM_BORDER[d.position] || "border-gray-200 bg-white"}`}
          >
            <div className="mb-1 flex items-center justify-between">
              <div>
                <span className="mr-2 text-lg font-bold text-gray-900">#{d.position}</span>
                <span className="font-medium text-gray-900">{d.driver_display_name}</span>
                <span className="ml-1 text-xs text-gray-500">({d.driver_abbreviation})</span>
              </div>
              <span className="text-lg font-bold text-gray-900">{d.total_points} pts</span>
            </div>
            <p className="mb-2 text-sm text-gray-500">{d.team_display_name}</p>
            <div className="flex flex-wrap gap-2">
              {races.map((r) => {
                const rp = getRacePointsForRace(d.race_points, r.race_id);
                return (
                  <div key={r.race_id} className="rounded bg-gray-100 px-2 py-1 text-xs">
                    <span className="font-medium text-gray-500">R{r.round_number}: </span>
                    {rp ? (
                      <span className={rp.dsq ? "text-red-500 line-through" : "text-gray-700"}>
                        {rp.points}
                      </span>
                    ) : (
                      <span className="text-gray-300">—</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
