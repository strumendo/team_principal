"""
Championship request/response schemas.
Schemas de requisicao/resposta de campeonato.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.championships.models import ChampionshipStatus


class ChampionshipResponse(BaseModel):
    """Championship response body / Corpo da resposta de campeonato."""

    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    season_year: int
    status: ChampionshipStatus
    start_date: date | None
    end_date: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChampionshipListResponse(BaseModel):
    """Championship list response body / Corpo da resposta de listagem de campeonatos."""

    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    season_year: int
    status: ChampionshipStatus
    start_date: date | None
    end_date: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChampionshipTeamResponse(BaseModel):
    """Team summary within a championship / Resumo de equipe em um campeonato."""

    id: uuid.UUID
    name: str
    display_name: str
    is_active: bool

    model_config = {"from_attributes": True}


class ChampionshipDetailResponse(BaseModel):
    """Championship detail response body with teams / Corpo da resposta detalhada de campeonato com equipes."""

    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    season_year: int
    status: ChampionshipStatus
    start_date: date | None
    end_date: date | None
    is_active: bool
    teams: list[ChampionshipTeamResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChampionshipEntryResponse(BaseModel):
    """Championship entry with registration date / Inscricao com data de registro."""

    team_id: uuid.UUID
    team_name: str
    team_display_name: str
    team_is_active: bool
    registered_at: datetime

    model_config = {"from_attributes": True}


class ChampionshipEntryRequest(BaseModel):
    """Championship entry request body / Corpo da requisicao de inscricao."""

    team_id: uuid.UUID


class ChampionshipCreateRequest(BaseModel):
    """Championship creation request body / Corpo da requisicao de criacao de campeonato."""

    name: str
    display_name: str
    description: str | None = None
    season_year: int
    status: ChampionshipStatus = ChampionshipStatus.planned
    start_date: date | None = None
    end_date: date | None = None


class ChampionshipUpdateRequest(BaseModel):
    """Championship update request body / Corpo da requisicao de atualizacao de campeonato."""

    display_name: str | None = None
    description: str | None = None
    season_year: int | None = None
    status: ChampionshipStatus | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None
