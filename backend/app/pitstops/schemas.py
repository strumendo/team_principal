"""
Pit stop and race strategy request/response schemas.
Schemas de requisicao/resposta de pit stop e estrategia de corrida.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.pitstops.models import TireCompound

# --- Shared helpers / Schemas auxiliares compartilhados ---


class DriverInfo(BaseModel):
    """Nested driver info / Informacao de piloto aninhada."""

    id: uuid.UUID
    name: str
    display_name: str
    abbreviation: str

    model_config = {"from_attributes": True}


class TeamInfo(BaseModel):
    """Nested team info / Informacao de equipe aninhada."""

    id: uuid.UUID
    name: str
    display_name: str

    model_config = {"from_attributes": True}


# --- Pit Stop schemas / Schemas de pit stop ---


class PitStopCreateRequest(BaseModel):
    """Pit stop creation / Criacao de pit stop."""

    driver_id: uuid.UUID
    team_id: uuid.UUID
    lap_number: int
    duration_ms: int
    tire_from: TireCompound | None = None
    tire_to: TireCompound | None = None
    notes: str | None = None


class PitStopUpdateRequest(BaseModel):
    """Pit stop update / Atualizacao de pit stop."""

    duration_ms: int | None = None
    tire_from: TireCompound | None = None
    tire_to: TireCompound | None = None
    notes: str | None = None


class PitStopResponse(BaseModel):
    """Pit stop response / Resposta de pit stop."""

    id: uuid.UUID
    race_id: uuid.UUID
    driver_id: uuid.UUID
    team_id: uuid.UUID
    lap_number: int
    duration_ms: int
    tire_from: TireCompound | None
    tire_to: TireCompound | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PitStopDetailResponse(PitStopResponse):
    """Pit stop detail with driver and team / Detalhe de pit stop com piloto e equipe."""

    driver: DriverInfo
    team: TeamInfo


class PitStopSummaryDriver(BaseModel):
    """Per-driver pit stop summary / Resumo de pit stops por piloto."""

    driver_id: uuid.UUID
    driver_display_name: str
    total_stops: int
    avg_duration_ms: int
    fastest_pit_ms: int


class PitStopSummaryResponse(BaseModel):
    """Pit stop summary for a race / Resumo de pit stops de uma corrida."""

    drivers: list[PitStopSummaryDriver]


# --- Race Strategy schemas / Schemas de estrategia de corrida ---


class RaceStrategyCreateRequest(BaseModel):
    """Race strategy creation / Criacao de estrategia de corrida."""

    driver_id: uuid.UUID
    team_id: uuid.UUID
    name: str
    description: str | None = None
    target_stops: int
    planned_laps: str | None = None
    starting_compound: TireCompound | None = None


class RaceStrategyUpdateRequest(BaseModel):
    """Race strategy update / Atualizacao de estrategia de corrida."""

    name: str | None = None
    description: str | None = None
    target_stops: int | None = None
    planned_laps: str | None = None
    starting_compound: TireCompound | None = None
    is_active: bool | None = None


class RaceStrategyResponse(BaseModel):
    """Race strategy response / Resposta de estrategia de corrida."""

    id: uuid.UUID
    race_id: uuid.UUID
    driver_id: uuid.UUID
    team_id: uuid.UUID
    name: str
    description: str | None
    target_stops: int
    planned_laps: str | None
    starting_compound: TireCompound | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RaceStrategyDetailResponse(RaceStrategyResponse):
    """Race strategy detail with driver and team / Detalhe de estrategia com piloto e equipe."""

    driver: DriverInfo
    team: TeamInfo
