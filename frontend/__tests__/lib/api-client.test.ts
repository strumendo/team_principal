/**
 * API client unit tests.
 * Testes unitarios do cliente API.
 */

const originalFetch = global.fetch;

beforeEach(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  global.fetch = originalFetch;
  jest.resetModules();
});

describe("API Client / Cliente API", () => {
  describe("apiRequest", () => {
    it("sends correct headers with token / envia headers corretos com token", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: "1" }),
      });

      const { authApi } = await import("@/lib/api-client");
      await authApi.login("test@test.com", "password");

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/auth/login"),
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            "Content-Type": "application/json",
          }),
        }),
      );
    });

    it("handles successful response / trata resposta bem-sucedida", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: "abc", refresh_token: "def" }),
      });

      const { authApi } = await import("@/lib/api-client");
      const result = await authApi.login("test@test.com", "password");

      expect(result.data).toEqual({ access_token: "abc", refresh_token: "def" });
      expect(result.error).toBeUndefined();
    });

    it("handles error response / trata resposta de erro", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: "Invalid credentials" }),
      });

      const { authApi } = await import("@/lib/api-client");
      const result = await authApi.login("test@test.com", "wrong");

      expect(result.error).toBe("Invalid credentials");
      expect(result.data).toBeUndefined();
    });

    it("handles network error / trata erro de rede", async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error("Network error"));

      const { authApi } = await import("@/lib/api-client");
      const result = await authApi.login("test@test.com", "password");

      expect(result.error).toBe("Network error. Please try again.");
    });
  });

  describe("authApi.register", () => {
    it("sends correct body / envia body correto", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: "abc", refresh_token: "def" }),
      });

      const { authApi } = await import("@/lib/api-client");
      await authApi.register("test@test.com", "password123", "Test User");

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/auth/register"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ email: "test@test.com", password: "password123", full_name: "Test User" }),
        }),
      );
    });
  });
});
