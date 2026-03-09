/**
 * PitStopForm component tests.
 * Testes do componente PitStopForm.
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PitStopForm from "@/components/pitstops/PitStopForm";

const mockDrivers = [
  { id: "d1", display_name: "Max Verstappen", team_id: "t1" },
  { id: "d2", display_name: "Lewis Hamilton", team_id: "t2" },
];

describe("PitStopForm / Formulario de Pit Stop", () => {
  const mockSubmit = jest.fn().mockResolvedValue(undefined);
  const mockCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders all form fields / renderiza todos os campos", () => {
    render(<PitStopForm drivers={mockDrivers} onSubmit={mockSubmit} onCancel={mockCancel} />);
    expect(screen.getByText(/Driver/)).toBeInTheDocument();
    expect(screen.getByText(/Lap Number/)).toBeInTheDocument();
    expect(screen.getByText(/Duration/)).toBeInTheDocument();
    expect(screen.getByText(/Tire From/)).toBeInTheDocument();
    expect(screen.getByText(/Tire To/)).toBeInTheDocument();
    expect(screen.getByText(/Notes/)).toBeInTheDocument();
  });

  it("shows driver options / exibe opcoes de pilotos", () => {
    render(<PitStopForm drivers={mockDrivers} onSubmit={mockSubmit} onCancel={mockCancel} />);
    expect(screen.getByText("Max Verstappen")).toBeInTheDocument();
    expect(screen.getByText("Lewis Hamilton")).toBeInTheDocument();
  });

  it("calls onCancel when cancel clicked / chama onCancel ao clicar cancelar", () => {
    render(<PitStopForm drivers={mockDrivers} onSubmit={mockSubmit} onCancel={mockCancel} />);
    fireEvent.click(screen.getByText(/Cancel/));
    expect(mockCancel).toHaveBeenCalled();
  });

  it("submits form with correct data / submete formulario com dados corretos", async () => {
    render(<PitStopForm drivers={mockDrivers} onSubmit={mockSubmit} onCancel={mockCancel} />);

    // Select the first combobox (Driver select) - no label association, use display value
    const selects = screen.getAllByRole("combobox");
    fireEvent.change(selects[0], { target: { value: "d1" } });
    fireEvent.change(screen.getByPlaceholderText("e.g. 15"), { target: { value: "15" } });
    fireEvent.change(screen.getByPlaceholderText("e.g. 2450"), { target: { value: "2450" } });

    fireEvent.click(screen.getByText(/Add Pit Stop/));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          driver_id: "d1",
          team_id: "t1",
          lap_number: 15,
          duration_ms: 2450,
        }),
      );
    });
  });

  it("shows saving state / exibe estado salvando", () => {
    render(<PitStopForm drivers={mockDrivers} onSubmit={mockSubmit} onCancel={mockCancel} saving />);
    expect(screen.getByText(/Saving/)).toBeInTheDocument();
  });
});
