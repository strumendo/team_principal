/**
 * Login page tests.
 * Testes da pagina de login.
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import LoginPage from "@/app/(auth)/login/page";

const mockPush = jest.fn();
const mockSignIn = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

jest.mock("next-auth/react", () => ({
  signIn: (...args: unknown[]) => mockSignIn(...args),
}));

jest.mock("next/link", () => {
  const React = require("react");
  return {
    __esModule: true,
    default: ({ children, href, ...props }: { children: React.ReactNode; href: string; [key: string]: unknown }) =>
      React.createElement("a", { href, ...props }, children),
  };
});

describe("LoginPage / Pagina de Login", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders login form / renderiza formulario de login", () => {
    render(<LoginPage />);
    expect(screen.getByText("Login")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Login/ })).toBeInTheDocument();
  });

  it("has link to register / tem link para registro", () => {
    render(<LoginPage />);
    const link = screen.getByText(/Register/);
    expect(link.closest("a")).toHaveAttribute("href", "/register");
  });

  it("calls signIn on form submission / chama signIn ao submeter formulario", async () => {
    mockSignIn.mockResolvedValueOnce({ error: null });
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "test@test.com" } });
    fireEvent.change(screen.getByLabelText(/Password/), { target: { value: "password123" } });
    fireEvent.click(screen.getByRole("button", { name: /Login/ }));

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith("credentials", {
        email: "test@test.com",
        password: "password123",
        redirect: false,
      });
    });
  });

  it("redirects to dashboard on success / redireciona ao dashboard em sucesso", async () => {
    mockSignIn.mockResolvedValueOnce({ error: null });
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "test@test.com" } });
    fireEvent.change(screen.getByLabelText(/Password/), { target: { value: "password123" } });
    fireEvent.click(screen.getByRole("button", { name: /Login/ }));

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("shows error on failed login / exibe erro em login falho", async () => {
    mockSignIn.mockResolvedValueOnce({ error: "CredentialsSignin" });
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "test@test.com" } });
    fireEvent.change(screen.getByLabelText(/Password/), { target: { value: "wrong" } });
    fireEvent.click(screen.getByRole("button", { name: /Login/ }));

    await waitFor(() => {
      expect(screen.getByText(/Invalid email or password/)).toBeInTheDocument();
    });
  });
});
