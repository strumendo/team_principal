/**
 * API client wrapper for the FastAPI backend.
 * Wrapper do cliente API para o backend FastAPI.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

/**
 * Make an authenticated API request.
 * Faz uma requisicao autenticada para a API.
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string,
): Promise<ApiResponse<T>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      return {
        error: errorData?.detail || `Request failed with status ${response.status}`,
      };
    }

    const data = await response.json();
    return { data };
  } catch {
    return { error: "Network error. Please try again." };
  }
}

/**
 * Auth API calls / Chamadas da API de autenticacao.
 */
export const authApi = {
  login: (email: string, password: string) =>
    apiRequest<{ access_token: string; refresh_token: string }>(
      "/auth/login",
      {
        method: "POST",
        body: JSON.stringify({ email, password }),
      },
    ),

  register: (email: string, password: string, fullName: string) =>
    apiRequest<{ access_token: string; refresh_token: string }>(
      "/auth/register",
      {
        method: "POST",
        body: JSON.stringify({ email, password, full_name: fullName }),
      },
    ),

  refresh: (refreshToken: string) =>
    apiRequest<{ access_token: string; refresh_token: string }>(
      "/auth/refresh",
      {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      },
    ),
};

/**
 * Users API calls / Chamadas da API de usuarios.
 */
export const usersApi = {
  getMe: (token: string) => apiRequest<{ id: string; email: string; full_name: string }>("/users/me", {}, token),
};

/**
 * Championships API calls / Chamadas da API de campeonatos.
 */
import type {
  ChampionshipListItem,
  ChampionshipDetail,
  ChampionshipEntry,
} from "@/types/championship";

import type { ChampionshipStanding } from "@/types/result";
import type { DriverStanding } from "@/types/driver";

export const championshipsApi = {
  list: (token: string, params?: { status?: string; season_year?: number; is_active?: boolean }) => {
    const query = new URLSearchParams();
    if (params?.status) query.set("status", params.status);
    if (params?.season_year) query.set("season_year", String(params.season_year));
    if (params?.is_active !== undefined) query.set("is_active", String(params.is_active));
    const qs = query.toString();
    return apiRequest<ChampionshipListItem[]>(`/championships/${qs ? `?${qs}` : ""}`, {}, token);
  },

  get: (token: string, id: string) =>
    apiRequest<ChampionshipDetail>(`/championships/${id}`, {}, token),

  create: (
    token: string,
    data: {
      name: string;
      display_name: string;
      season_year: number;
      description?: string;
      status?: string;
      start_date?: string;
      end_date?: string;
    },
  ) =>
    apiRequest<ChampionshipListItem>("/championships/", {
      method: "POST",
      body: JSON.stringify(data),
    }, token),

  update: (
    token: string,
    id: string,
    data: {
      display_name?: string;
      description?: string;
      season_year?: number;
      status?: string;
      start_date?: string;
      end_date?: string;
      is_active?: boolean;
    },
  ) =>
    apiRequest<ChampionshipListItem>(`/championships/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }, token),

  delete: (token: string, id: string) =>
    apiRequest<void>(`/championships/${id}`, { method: "DELETE" }, token),

  listEntries: (token: string, id: string) =>
    apiRequest<ChampionshipEntry[]>(`/championships/${id}/entries`, {}, token),

  addEntry: (token: string, id: string, teamId: string) =>
    apiRequest<ChampionshipEntry[]>(`/championships/${id}/entries`, {
      method: "POST",
      body: JSON.stringify({ team_id: teamId }),
    }, token),

  removeEntry: (token: string, id: string, teamId: string) =>
    apiRequest<ChampionshipEntry[]>(`/championships/${id}/entries/${teamId}`, {
      method: "DELETE",
    }, token),

  getStandings: (token: string, id: string) =>
    apiRequest<ChampionshipStanding[]>(`/championships/${id}/standings`, {}, token),

  getDriverStandings: (token: string, id: string) =>
    apiRequest<DriverStanding[]>(`/championships/${id}/driver-standings`, {}, token),
};

/**
 * Races API calls / Chamadas da API de corridas.
 */
import type {
  RaceListItem,
  RaceDetail,
  RaceEntry,
} from "@/types/race";

import type {
  RaceResult,
  RaceResultDetail,
} from "@/types/result";

export const racesApi = {
  listByChampionship: (token: string, championshipId: string, params?: { status?: string; is_active?: boolean }) => {
    const query = new URLSearchParams();
    if (params?.status) query.set("status", params.status);
    if (params?.is_active !== undefined) query.set("is_active", String(params.is_active));
    const qs = query.toString();
    return apiRequest<RaceListItem[]>(`/championships/${championshipId}/races${qs ? `?${qs}` : ""}`, {}, token);
  },

  get: (token: string, id: string) =>
    apiRequest<RaceDetail>(`/races/${id}`, {}, token),

  create: (
    token: string,
    championshipId: string,
    data: {
      name: string;
      display_name: string;
      round_number: number;
      description?: string;
      status?: string;
      scheduled_at?: string;
      track_name?: string;
      track_country?: string;
      laps_total?: number;
    },
  ) =>
    apiRequest<RaceListItem>(`/championships/${championshipId}/races`, {
      method: "POST",
      body: JSON.stringify(data),
    }, token),

  update: (
    token: string,
    id: string,
    data: {
      display_name?: string;
      description?: string;
      round_number?: number;
      status?: string;
      scheduled_at?: string;
      track_name?: string;
      track_country?: string;
      laps_total?: number;
      is_active?: boolean;
    },
  ) =>
    apiRequest<RaceListItem>(`/races/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }, token),

  delete: (token: string, id: string) =>
    apiRequest<void>(`/races/${id}`, { method: "DELETE" }, token),

  listEntries: (token: string, id: string) =>
    apiRequest<RaceEntry[]>(`/races/${id}/entries`, {}, token),

  addEntry: (token: string, id: string, teamId: string) =>
    apiRequest<RaceEntry[]>(`/races/${id}/entries`, {
      method: "POST",
      body: JSON.stringify({ team_id: teamId }),
    }, token),

  removeEntry: (token: string, id: string, teamId: string) =>
    apiRequest<RaceEntry[]>(`/races/${id}/entries/${teamId}`, {
      method: "DELETE",
    }, token),
};

/**
 * Drivers API calls / Chamadas da API de pilotos.
 */
import type {
  DriverListItem,
  DriverDetail,
} from "@/types/driver";

export const driversApi = {
  list: (token: string, params?: { is_active?: boolean; team_id?: string }) => {
    const query = new URLSearchParams();
    if (params?.is_active !== undefined) query.set("is_active", String(params.is_active));
    if (params?.team_id) query.set("team_id", params.team_id);
    const qs = query.toString();
    return apiRequest<DriverListItem[]>(`/drivers/${qs ? `?${qs}` : ""}`, {}, token);
  },

  get: (token: string, id: string) =>
    apiRequest<DriverDetail>(`/drivers/${id}`, {}, token),
};

/**
 * Results API calls / Chamadas da API de resultados.
 */
export const resultsApi = {
  listByRace: (token: string, raceId: string) =>
    apiRequest<RaceResult[]>(`/races/${raceId}/results`, {}, token),

  get: (token: string, id: string) =>
    apiRequest<RaceResultDetail>(`/results/${id}`, {}, token),

  create: (
    token: string,
    raceId: string,
    data: {
      team_id: string;
      driver_id?: string;
      position: number;
      points?: number;
      laps_completed?: number;
      fastest_lap?: boolean;
      dnf?: boolean;
      dsq?: boolean;
      notes?: string;
    },
  ) =>
    apiRequest<RaceResult>(`/races/${raceId}/results`, {
      method: "POST",
      body: JSON.stringify(data),
    }, token),

  update: (
    token: string,
    id: string,
    data: {
      driver_id?: string;
      position?: number;
      points?: number;
      laps_completed?: number;
      fastest_lap?: boolean;
      dnf?: boolean;
      dsq?: boolean;
      notes?: string;
    },
  ) =>
    apiRequest<RaceResult>(`/results/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }, token),

  delete: (token: string, id: string) =>
    apiRequest<void>(`/results/${id}`, { method: "DELETE" }, token),
};
