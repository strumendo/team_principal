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


class RaceDetailResponse(BaseModel):
    """Race detail response body / Corpo da resposta detalhada de corrida."""

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
