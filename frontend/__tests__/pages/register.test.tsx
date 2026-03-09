/**
 * Register page tests.
 * Testes da pagina de registro.
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import RegisterPage from "@/app/(auth)/register/page";

const mockPush = jest.fn();
const mockSignIn = jest.fn();
const mockRegister = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

jest.mock("next-auth/react", () => ({
  signIn: (...args: unknown[]) => mockSignIn(...args),
}));

jest.mock("@/lib/api-client", () => ({
  authApi: {
    register: (...args: unknown[]) => mockRegister(...args),
  },
}));

jest.mock("next/link", () => {
  const React = require("react");
  return {
    __esModule: true,
    default: ({ children, href, ...props }: { children: React.ReactNode; href: string; [key: string]: unknown }) =>
      React.createElement("a", { href, ...props }, children),
  };
});

describe("RegisterPage / Pagina de Registro", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders registration form / renderiza formulario de registro", () => {
    render(<RegisterPage />);
    expect(screen.getByRole("heading", { name: /Register/ })).toBeInTheDocument();
    expect(screen.getByLabelText(/Full Name/)).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/)).toBeInTheDocument();
  });

  it("has link to login / tem link para login", () => {
    render(<RegisterPage />);
    const link = screen.getByText(/Already have an account/);
    expect(link.closest("a")).toHaveAttribute("href", "/login");
  });

  it("calls register API then signIn on success / chama API de registro e depois signIn", async () => {
    mockRegister.mockResolvedValueOnce({ data: { access_token: "abc" } });
    mockSignIn.mockResolvedValueOnce({ error: null });

    render(<RegisterPage />);

    fireEvent.change(screen.getByLabelText(/Full Name/), { target: { value: "John Doe" } });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "john@test.com" } });
    fireEvent.change(screen.getByLabelText(/Password/), { target: { value: "password123" } });
    fireEvent.click(screen.getByRole("button", { name: /Register/ }));

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith("john@test.com", "password123", "John Doe");
    });

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith("credentials", {
        email: "john@test.com",
        password: "password123",
        redirect: false,
      });
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("shows error on registration failure / exibe erro em falha de registro", async () => {
    mockRegister.mockResolvedValueOnce({ error: "Email already exists" });

    render(<RegisterPage />);

    fireEvent.change(screen.getByLabelText(/Full Name/), { target: { value: "John" } });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "john@test.com" } });
    fireEvent.change(screen.getByLabelText(/Password/), { target: { value: "password123" } });
    fireEvent.click(screen.getByRole("button", { name: /Register/ }));

    await waitFor(() => {
      expect(screen.getByText("Email already exists")).toBeInTheDocument();
    });
  });

  it("shows error when registration succeeds but login fails / exibe erro quando registro ok mas login falha", async () => {
    mockRegister.mockResolvedValueOnce({ data: { access_token: "abc" } });
    mockSignIn.mockResolvedValueOnce({ error: "LoginFailed" });

    render(<RegisterPage />);

    fireEvent.change(screen.getByLabelText(/Full Name/), { target: { value: "John" } });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "john@test.com" } });
    fireEvent.change(screen.getByLabelText(/Password/), { target: { value: "password123" } });
    fireEvent.click(screen.getByRole("button", { name: /Register/ }));

    await waitFor(() => {
      expect(screen.getByText(/Registration succeeded but login failed/)).toBeInTheDocument();
    });
  });
});
