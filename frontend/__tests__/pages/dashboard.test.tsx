/**
 * Dashboard page tests.
 * Testes da pagina de dashboard.
 */
import { render, screen } from "@testing-library/react";
import DashboardPage from "@/app/(dashboard)/dashboard/page";
import { dashboardApi } from "@/lib/api-client";

jest.mock("next-auth/react", () => ({
  useSession: () => ({
    data: { accessToken: "test-token", user: { name: "Test" } },
    status: "authenticated",
  }),
}));

jest.mock("@/lib/api-client", () => ({
  dashboardApi: {
    getSummary: jest.fn(),
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

jest.mock("@/components/dashboard/StandingsChart", () => ({
  __esModule: true,
  default: () => null,
}));

jest.mock("@/components/dashboard/RaceDistributionChart", () => ({
  __esModule: true,
  default: () => null,
}));

const mockGetSummary = dashboardApi.getSummary as jest.Mock;

describe("DashboardPage / Pagina de Dashboard", () => {
  beforeEach(() => {
    mockGetSummary.mockReset();
  });

  it("shows loading state initially / exibe estado carregando inicialmente", () => {
    mockGetSummary.mockReturnValue(new Promise(() => {}));
    render(<DashboardPage />);
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  it("calls getSummary with auth token / chama getSummary com token de auth", () => {
    mockGetSummary.mockReturnValue(new Promise(() => {}));
    render(<DashboardPage />);
    expect(mockGetSummary).toHaveBeenCalledWith("test-token");
  });
});
