/**
 * RaceTimeline component tests.
 * Testes do componente RaceTimeline.
 */
import { render, screen } from "@testing-library/react";
import RaceTimeline from "@/components/replay/RaceTimeline";
import type { ReplayLapData } from "@/types/race-replay";

const mockLaps: ReplayLapData[] = [
  {
    lap_number: 1,
    positions: [],
    events: [
      { event_type: "race_start", description: "Race started", driver_id: null, driver_name: null },
    ],
    pit_stops: [],
  },
  {
    lap_number: 15,
    positions: [],
    events: [
      { event_type: "safety_car", description: "Debris on track", driver_id: null, driver_name: null },
    ],
    pit_stops: [],
  },
  {
    lap_number: 42,
    positions: [],
    events: [
      { event_type: "overtake", description: "Great move", driver_id: "d1", driver_name: "Max" },
    ],
    pit_stops: [],
  },
];

describe("RaceTimeline / Linha do Tempo da Corrida", () => {
  it("renders event markers / renderiza marcadores de eventos", () => {
    render(<RaceTimeline laps={mockLaps} totalLaps={57} />);
    // Each label appears in both marker and legend
    expect(screen.getAllByText("START").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("SC").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("OVT").length).toBeGreaterThanOrEqual(2);
  });

  it("shows legend / exibe legenda", () => {
    render(<RaceTimeline laps={mockLaps} totalLaps={57} />);
    // Labels that only appear in legend (not in markers)
    expect(screen.getByText("VSC")).toBeInTheDocument();
    expect(screen.getByText("RED")).toBeInTheDocument();
    expect(screen.getByText("INC")).toBeInTheDocument();
    expect(screen.getByText("PEN")).toBeInTheDocument();
    expect(screen.getByText("MF")).toBeInTheDocument();
    expect(screen.getByText("END")).toBeInTheDocument();
  });

  it("shows empty state / exibe estado vazio", () => {
    const emptyLaps: ReplayLapData[] = [{ lap_number: 1, positions: [], events: [], pit_stops: [] }];
    render(<RaceTimeline laps={emptyLaps} totalLaps={57} />);
    expect(screen.getByText(/No events recorded/)).toBeInTheDocument();
  });

  it("shows timeline header / exibe titulo da timeline", () => {
    render(<RaceTimeline laps={mockLaps} totalLaps={57} />);
    expect(screen.getByText(/Race Timeline/)).toBeInTheDocument();
  });
});
