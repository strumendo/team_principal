/**
 * PitStopTable component tests.
 * Testes do componente PitStopTable.
 */
import { render, screen, fireEvent } from "@testing-library/react";
import PitStopTable from "@/components/pitstops/PitStopTable";
import type { PitStop } from "@/types/pitstops";

const mockPitStop: PitStop = {
  id: "ps-1",
  race_id: "race-1",
  driver_id: "driver-1",
  team_id: "team-1",
  lap_number: 15,
  duration_ms: 2450,
  tire_from: "soft",
  tire_to: "medium",
  notes: "Good stop",
  created_at: "2026-01-01T00:00:00Z",
};

describe("PitStopTable / Tabela de Pit Stops", () => {
  it("renders table with pit stop data / renderiza tabela com dados", () => {
    render(<PitStopTable pitStops={[mockPitStop]} />);
    expect(screen.getByText("15")).toBeInTheDocument();
    expect(screen.getByText("2.450s")).toBeInTheDocument();
    expect(screen.getByText("Good stop")).toBeInTheDocument();
  });

  it("shows compound badges / exibe badges de compostos", () => {
    render(<PitStopTable pitStops={[mockPitStop]} />);
    expect(screen.getByText("Soft")).toBeInTheDocument();
    expect(screen.getByText("Medium")).toBeInTheDocument();
  });

  it("shows empty state / exibe estado vazio", () => {
    render(<PitStopTable pitStops={[]} />);
    expect(screen.getByText(/No pit stops recorded/)).toBeInTheDocument();
  });

  it("shows delete button when onDelete provided / exibe botao excluir quando onDelete fornecido", () => {
    const onDelete = jest.fn();
    render(<PitStopTable pitStops={[mockPitStop]} onDelete={onDelete} />);
    const deleteBtn = screen.getByText(/Delete/);
    fireEvent.click(deleteBtn);
    expect(onDelete).toHaveBeenCalledWith("ps-1");
  });

  it("hides delete column when no onDelete / esconde coluna excluir sem onDelete", () => {
    render(<PitStopTable pitStops={[mockPitStop]} />);
    expect(screen.queryByText(/Delete/)).not.toBeInTheDocument();
  });

  it("shows dash for null compounds / exibe traço para compostos nulos", () => {
    const ps = { ...mockPitStop, tire_from: null, tire_to: null };
    render(<PitStopTable pitStops={[ps]} />);
    const dashes = screen.getAllByText("-");
    expect(dashes.length).toBeGreaterThanOrEqual(2);
  });
});
