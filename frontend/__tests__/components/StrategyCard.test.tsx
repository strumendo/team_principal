/**
 * StrategyCard component tests.
 * Testes do componente StrategyCard.
 */
import { render, screen, fireEvent } from "@testing-library/react";
import StrategyCard from "@/components/pitstops/StrategyCard";
import type { RaceStrategy } from "@/types/pitstops";

const mockStrategy: RaceStrategy = {
  id: "s1",
  race_id: "race-1",
  driver_id: "d1",
  team_id: "t1",
  name: "Aggressive Strategy",
  description: "Two-stop with soft tires",
  target_stops: 2,
  planned_laps: "1-20, 21-40",
  starting_compound: "soft",
  is_active: true,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("StrategyCard / Card de Estrategia", () => {
  it("renders strategy name and description / renderiza nome e descricao", () => {
    render(<StrategyCard strategy={mockStrategy} />);
    expect(screen.getByText("Aggressive Strategy")).toBeInTheDocument();
    expect(screen.getByText("Two-stop with soft tires")).toBeInTheDocument();
  });

  it("shows active badge / exibe badge ativo", () => {
    render(<StrategyCard strategy={mockStrategy} />);
    expect(screen.getByText(/Active/)).toBeInTheDocument();
  });

  it("shows inactive badge / exibe badge inativo", () => {
    const inactive = { ...mockStrategy, is_active: false };
    render(<StrategyCard strategy={inactive} />);
    expect(screen.getByText(/Inactive/)).toBeInTheDocument();
  });

  it("shows compound badge / exibe badge do composto", () => {
    render(<StrategyCard strategy={mockStrategy} />);
    expect(screen.getByText("Soft")).toBeInTheDocument();
  });

  it("shows target stops / exibe paradas planejadas", () => {
    render(<StrategyCard strategy={mockStrategy} />);
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("shows action buttons when provided / exibe botoes de acao quando fornecidos", () => {
    const onEdit = jest.fn();
    const onDelete = jest.fn();
    render(<StrategyCard strategy={mockStrategy} onEdit={onEdit} onDelete={onDelete} />);

    fireEvent.click(screen.getByText(/Edit/));
    expect(onEdit).toHaveBeenCalledWith(mockStrategy);

    fireEvent.click(screen.getByText(/Delete/));
    expect(onDelete).toHaveBeenCalledWith("s1");
  });

  it("hides action buttons when not provided / esconde botoes sem callbacks", () => {
    render(<StrategyCard strategy={mockStrategy} />);
    expect(screen.queryByText(/Edit/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Delete/)).not.toBeInTheDocument();
  });
});
