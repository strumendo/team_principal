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


class ChampionshipDetailResponse(BaseModel):
    """Championship detail response body / Corpo da resposta detalhada de campeonato."""

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
