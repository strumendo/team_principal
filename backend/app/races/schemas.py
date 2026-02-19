"""
Race request/response schemas.
Schemas de requisicao/resposta de corrida.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.races.models import RaceStatus


class RaceResponse(BaseModel):
    """Race response body / Corpo da resposta de corrida."""

    id: uuid.UUID
    championship_id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    round_number: int
    status: RaceStatus
    scheduled_at: datetime | None
    track_name: str | None
    track_country: str | None
    laps_total: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RaceListResponse(BaseModel):
    """Race list response body / Corpo da resposta de listagem de corridas."""

    id: uuid.UUID
    championship_id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    round_number: int
    status: RaceStatus
    scheduled_at: datetime | None
    track_name: str | None
    track_country: str | None
    laps_total: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RaceTeamResponse(BaseModel):
    """Team summary within a race / Resumo de equipe em uma corrida."""

    id: uuid.UUID
    name: str
    display_name: str
    is_active: bool

    model_config = {"from_attributes": True}


class RaceDetailResponse(BaseModel):
    """Race detail response body with teams / Corpo da resposta detalhada de corrida com equipes."""

    id: uuid.UUID
    championship_id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    round_number: int
    status: RaceStatus
    scheduled_at: datetime | None
    track_name: str | None
    track_country: str | None
    laps_total: int | None
    is_active: bool
    teams: list[RaceTeamResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RaceEntryResponse(BaseModel):
    """Race entry with registration date / Inscricao de corrida com data de registro."""

    team_id: uuid.UUID
    team_name: str
    team_display_name: str
    team_is_active: bool
    registered_at: datetime

    model_config = {"from_attributes": True}


class RaceEntryRequest(BaseModel):
    """Race entry request body / Corpo da requisicao de inscricao de corrida."""

    team_id: uuid.UUID


class RaceCreateRequest(BaseModel):
    """Race creation request body / Corpo da requisicao de criacao de corrida."""

    name: str
    display_name: str
    description: str | None = None
    round_number: int
    status: RaceStatus = RaceStatus.scheduled
    scheduled_at: datetime | None = None
    track_name: str | None = None
    track_country: str | None = None
    laps_total: int | None = None


class RaceUpdateRequest(BaseModel):
    """Race update request body / Corpo da requisicao de atualizacao de corrida."""

    display_name: str | None = None
    description: str | None = None
    round_number: int | None = None
    status: RaceStatus | None = None
    scheduled_at: datetime | None = None
    track_name: str | None = None
    track_country: str | None = None
    laps_total: int | None = None
    is_active: bool | None = None
