"""
Dashboard response schemas.
Schemas de resposta do dashboard.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel


class DashboardChampionshipResponse(BaseModel):
    """Active championship summary / Resumo de campeonato ativo."""

    id: uuid.UUID
    name: str
    display_name: str
    season_year: int
    status: str
    start_date: date | None
    end_date: date | None
    total_races: int
    completed_races: int
    team_count: int

    model_config = {"from_attributes": True}


class DashboardNextRaceResponse(BaseModel):
    """Upcoming race summary / Resumo de proxima corrida."""

    id: uuid.UUID
    name: str
    display_name: str
    championship_id: uuid.UUID
    championship_display_name: str
    round_number: int
    scheduled_at: datetime
    track_name: str | None
    track_country: str | None

    model_config = {"from_attributes": True}


class DashboardStandingEntryResponse(BaseModel):
    """Standing entry within a championship / Entrada de classificacao em um campeonato."""

    position: int
    team_id: uuid.UUID
    team_name: str
    team_display_name: str
    total_points: float
    races_scored: int
    wins: int

    model_config = {"from_attributes": True}


class DashboardChampionshipStandingsResponse(BaseModel):
    """Standings for a single championship / Classificacao de um campeonato."""

    championship_id: uuid.UUID
    championship_display_name: str
    standings: list[DashboardStandingEntryResponse]

    model_config = {"from_attributes": True}


class DashboardSummaryResponse(BaseModel):
    """Full dashboard summary / Resumo completo do dashboard."""

    active_championships: list[DashboardChampionshipResponse]
    next_races: list[DashboardNextRaceResponse]
    championship_standings: list[DashboardChampionshipStandingsResponse]

    model_config = {"from_attributes": True}
