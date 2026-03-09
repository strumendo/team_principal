/**
 * StintTable component tests.
 * Testes do componente StintTable.
 */
import { render, screen } from "@testing-library/react";
import StintTable from "@/components/replay/StintTable";
import type { StintAnalysisResponse } from "@/types/race-replay";

const mockData: StintAnalysisResponse = {
  race_id: "race-1",
  drivers: [
    {
      driver_id: "d1",
      driver_name: "Max Verstappen",
      stints: [
        {
          driver_id: "d1",
          driver_name: "Max Verstappen",
          stint_number: 1,
          compound: "soft",
          start_lap: 1,
          end_lap: 20,
          total_laps: 20,
          avg_pace_ms: 92000,
          best_lap_ms: 91000,
          degradation_ms: 500,
        },
        {
          driver_id: "d1",
          driver_name: "Max Verstappen",
          stint_number: 2,
          compound: "hard",
          start_lap: 21,
          end_lap: 57,
          total_laps: 37,
          avg_pace_ms: 93000,
          best_lap_ms: 91500,
          degradation_ms: 800,
        },
      ],
    },
  ],
};

describe("StintTable / Tabela de Stints", () => {
  it("renders driver name / renderiza nome do piloto", () => {
    render(<StintTable data={mockData} />);
    expect(screen.getByText("Max Verstappen")).toBeInTheDocument();
  });

  it("renders stint data / renderiza dados dos stints", () => {
    render(<StintTable data={mockData} />);
    expect(screen.getByText("soft")).toBeInTheDocument();
    expect(screen.getByText("hard")).toBeInTheDocument();
    expect(screen.getByText("1–20 (20)")).toBeInTheDocument();
    expect(screen.getByText("21–57 (37)")).toBeInTheDocument();
  });

  it("shows empty state / exibe estado vazio", () => {
    const empty = { race_id: "race-1", drivers: [] };
    render(<StintTable data={empty} />);
    expect(screen.getByText(/No stint data/)).toBeInTheDocument();
  });

  it("shows degradation values / exibe valores de degradacao", () => {
    render(<StintTable data={mockData} />);
    expect(screen.getByText("+0.5s")).toBeInTheDocument();
    expect(screen.getByText("+0.8s")).toBeInTheDocument();
  });
});
