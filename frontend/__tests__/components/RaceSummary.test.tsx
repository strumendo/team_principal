/**
 * RaceSummary component tests.
 * Testes do componente RaceSummary.
 */
import { render, screen } from "@testing-library/react";
import RaceSummary from "@/components/replay/RaceSummary";
import type { RaceSummaryResponse } from "@/types/race-replay";

const mockData: RaceSummaryResponse = {
  race_id: "race-1",
  total_laps: 57,
  total_overtakes: 23,
  leader_changes: 5,
  safety_car_laps: 3,
  dnf_count: 2,
  fastest_lap: {
    driver_id: "d1",
    driver_name: "Max Verstappen",
    lap_number: 42,
    lap_time_ms: 91234,
  },
};

describe("RaceSummary / Resumo da Corrida", () => {
  it("renders all stats cards / renderiza todos os cards de estatisticas", () => {
    render(<RaceSummary data={mockData} />);
    expect(screen.getByText("57")).toBeInTheDocument();
    expect(screen.getByText("23")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("shows stat labels / exibe labels das estatisticas", () => {
    render(<RaceSummary data={mockData} />);
    expect(screen.getByText(/Total Laps/)).toBeInTheDocument();
    expect(screen.getByText(/Overtakes/)).toBeInTheDocument();
    expect(screen.getByText(/Leader Changes/)).toBeInTheDocument();
    expect(screen.getByText(/Safety Car/)).toBeInTheDocument();
    expect(screen.getByText(/DNFs/)).toBeInTheDocument();
  });

  it("shows fastest lap details / exibe detalhes da volta mais rapida", () => {
    render(<RaceSummary data={mockData} />);
    expect(screen.getByText(/Fastest Lap/)).toBeInTheDocument();
    expect(screen.getByText("1:31.234")).toBeInTheDocument();
    expect(screen.getByText(/Max Verstappen/)).toBeInTheDocument();
    expect(screen.getByText(/42/)).toBeInTheDocument();
  });

  it("handles null fastest lap / trata volta mais rapida nula", () => {
    const noFastest = { ...mockData, fastest_lap: null };
    render(<RaceSummary data={noFastest} />);
    expect(screen.queryByText(/Fastest Lap/)).not.toBeInTheDocument();
  });
});
