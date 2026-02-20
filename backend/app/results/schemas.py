"""
Race result request/response schemas.
Schemas de requisicao/resposta de resultado de corrida.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class RaceResultResponse(BaseModel):
    """Race result response body / Corpo da resposta de resultado de corrida."""

    id: uuid.UUID
    race_id: uuid.UUID
    team_id: uuid.UUID
    driver_id: uuid.UUID | None
    position: int
    points: float
    laps_completed: int | None
    fastest_lap: bool
    dnf: bool
    dsq: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RaceResultListResponse(BaseModel):
    """Race result list response body / Corpo da resposta de listagem de resultados."""

    id: uuid.UUID
    race_id: uuid.UUID
    team_id: uuid.UUID
    driver_id: uuid.UUID | None
    position: int
    points: float
    laps_completed: int | None
    fastest_lap: bool
    dnf: bool
    dsq: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RaceResultTeamResponse(BaseModel):
    """Team summary within a result / Resumo de equipe em um resultado."""

    id: uuid.UUID
    name: str
    display_name: str
    is_active: bool

    model_config = {"from_attributes": True}


class RaceResultDriverResponse(BaseModel):
    """Driver summary within a result / Resumo de piloto em um resultado."""

    id: uuid.UUID
    name: str
    display_name: str
    abbreviation: str
    number: int

    model_config = {"from_attributes": True}


class RaceResultDetailResponse(BaseModel):
    """Race result detail response with team and driver / Resposta detalhada de resultado com equipe e piloto."""

    id: uuid.UUID
    race_id: uuid.UUID
    team_id: uuid.UUID
    driver_id: uuid.UUID | None
    position: int
    points: float
    laps_completed: int | None
    fastest_lap: bool
    dnf: bool
    dsq: bool
    notes: str | None
    team: RaceResultTeamResponse
    driver: RaceResultDriverResponse | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RaceResultCreateRequest(BaseModel):
    """Race result creation request body / Corpo da requisicao de criacao de resultado."""

    team_id: uuid.UUID
    driver_id: uuid.UUID | None = None
    position: int
    points: float = 0.0
    laps_completed: int | None = None
    fastest_lap: bool = False
    dnf: bool = False
    dsq: bool = False
    notes: str | None = None


class RaceResultUpdateRequest(BaseModel):
    """Race result update request body / Corpo da requisicao de atualizacao de resultado."""

    driver_id: uuid.UUID | None = None
    position: int | None = None
    points: float | None = None
    laps_completed: int | None = None
    fastest_lap: bool | None = None
    dnf: bool | None = None
    dsq: bool | None = None
    notes: str | None = None


class ChampionshipStandingResponse(BaseModel):
    """Championship standing response body / Corpo da resposta de classificacao do campeonato."""

    position: int
    team_id: uuid.UUID
    team_name: str
    team_display_name: str
    total_points: float
    races_scored: int
    wins: int

    model_config = {"from_attributes": True}
