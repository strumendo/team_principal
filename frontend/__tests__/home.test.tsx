/**
 * Tests for the landing page component.
 * Testes para o componente da pagina inicial.
 */
import { render, screen } from "@testing-library/react";
import Home from "@/app/page";

describe("Home Page / Pagina Inicial", () => {
  it("renders the main heading", () => {
    render(<Home />);
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toHaveTextContent("TeamPrincipal");
  });

  it("renders login and register links", () => {
    render(<Home />);
    const loginLink = screen.getByRole("link", { name: /login/i });
    const registerLink = screen.getByRole("link", { name: /register/i });
    expect(loginLink).toHaveAttribute("href", "/login");
    expect(registerLink).toHaveAttribute("href", "/register");
  });

  it("renders the platform description", () => {
    render(<Home />);
    expect(
      screen.getByText("E-Sports Racing Management Platform"),
    ).toBeInTheDocument();
  });
});
