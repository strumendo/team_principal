/**
 * LapTimeTable component tests.
 * Testes do componente LapTimeTable.
 */
import { render, screen } from "@testing-library/react";
import LapTimeTable from "@/components/telemetry/LapTimeTable";
import type { LapTime } from "@/types/telemetry";

const baseLap: LapTime = {
  id: "lap-1",
  race_id: "race-1",
  driver_id: "d1",
  team_id: "t1",
  lap_number: 1,
  lap_time_ms: 92450,
  sector_1_ms: 28100,
  sector_2_ms: 33200,
  sector_3_ms: 31150,
  is_valid: true,
  is_personal_best: false,
  created_at: "2026-01-01T00:00:00Z",
};

describe("LapTimeTable / Tabela de Tempos de Volta", () => {
  it("renders lap time data / renderiza dados de tempo de volta", () => {
    render(<LapTimeTable laps={[baseLap]} />);
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("1:32.450")).toBeInTheDocument();
  });

  it("formats sectors correctly / formata setores corretamente", () => {
    render(<LapTimeTable laps={[baseLap]} />);
    expect(screen.getByText("0:28.100")).toBeInTheDocument();
    expect(screen.getByText("0:33.200")).toBeInTheDocument();
    expect(screen.getByText("0:31.150")).toBeInTheDocument();
  });

  it("shows valid indicator / exibe indicador de valida", () => {
    render(<LapTimeTable laps={[baseLap]} />);
    expect(screen.getByText(/Yes/)).toBeInTheDocument();
  });

  it("highlights invalid laps / destaca voltas invalidas", () => {
    const invalidLap = { ...baseLap, is_valid: false };
    render(<LapTimeTable laps={[invalidLap]} />);
    expect(screen.getByText(/No/)).toBeInTheDocument();
  });

  it("shows PB badge / exibe badge PB", () => {
    const pbLap = { ...baseLap, is_personal_best: true };
    render(<LapTimeTable laps={[pbLap]} />);
    const pbElements = screen.getAllByText("PB");
    // One in header, one as badge
    expect(pbElements.length).toBeGreaterThanOrEqual(2);
  });

  it("shows empty state / exibe estado vazio", () => {
    render(<LapTimeTable laps={[]} />);
    expect(screen.getByText(/No lap times recorded/)).toBeInTheDocument();
  });

  it("handles null sectors / trata setores nulos", () => {
    const lap = { ...baseLap, sector_1_ms: null, sector_2_ms: null, sector_3_ms: null };
    render(<LapTimeTable laps={[lap]} />);
    const dashes = screen.getAllByText("-");
    expect(dashes.length).toBeGreaterThanOrEqual(3);
  });
});
