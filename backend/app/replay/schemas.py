"""
Race replay request/response schemas.
Schemas de requisicao/resposta de replay de corrida.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.replay.models import RaceEventType

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


# --- LapPosition schemas / Schemas de posicao por volta ---


class LapPositionCreateRequest(BaseModel):
    """Lap position creation / Criacao de posicao por volta."""

    driver_id: uuid.UUID
    team_id: uuid.UUID
    lap_number: int
    position: int
    gap_to_leader_ms: int | None = None
    interval_ms: int | None = None


class LapPositionBulkCreateRequest(BaseModel):
    """Bulk lap position creation / Criacao em massa de posicoes por volta."""

    positions: list[LapPositionCreateRequest]


class LapPositionUpdateRequest(BaseModel):
    """Lap position update / Atualizacao de posicao por volta."""

    position: int | None = None
    gap_to_leader_ms: int | None = None
    interval_ms: int | None = None


class LapPositionResponse(BaseModel):
    """Lap position response / Resposta de posicao por volta."""

    id: uuid.UUID
    race_id: uuid.UUID
    driver_id: uuid.UUID
    team_id: uuid.UUID
    lap_number: int
    position: int
    gap_to_leader_ms: int | None
    interval_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LapPositionDetailResponse(LapPositionResponse):
    """Lap position detail with driver and team / Detalhe de posicao com piloto e equipe."""

    driver: DriverInfo
    team: TeamInfo


# --- RaceEvent schemas / Schemas de evento de corrida ---


class RaceEventCreateRequest(BaseModel):
    """Race event creation / Criacao de evento de corrida."""

    lap_number: int
    event_type: RaceEventType
    description: str | None = None
    driver_id: uuid.UUID | None = None


class RaceEventUpdateRequest(BaseModel):
    """Race event update / Atualizacao de evento de corrida."""

    lap_number: int | None = None
    event_type: RaceEventType | None = None
    description: str | None = None
    driver_id: uuid.UUID | None = None


class RaceEventResponse(BaseModel):
    """Race event response / Resposta de evento de corrida."""

    id: uuid.UUID
    race_id: uuid.UUID
    lap_number: int
    event_type: RaceEventType
    description: str | None
    driver_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RaceEventDetailResponse(RaceEventResponse):
    """Race event detail with optional driver / Detalhe de evento com piloto opcional."""

    driver: DriverInfo | None = None


# --- Analysis schemas / Schemas de analise ---


class ReplayPositionData(BaseModel):
    """Position data for a single driver on a lap / Dados de posicao de um piloto numa volta."""

    driver_id: uuid.UUID
    driver_name: str
    team_id: uuid.UUID
    position: int
    gap_to_leader_ms: int | None
    interval_ms: int | None


class ReplayEventData(BaseModel):
    """Event data for a lap / Dados de evento de uma volta."""

    event_type: RaceEventType
    description: str | None
    driver_id: uuid.UUID | None
    driver_name: str | None


class ReplayPitStopData(BaseModel):
    """Pit stop data for a lap / Dados de pit stop de uma volta."""

    driver_id: uuid.UUID
    driver_name: str
    duration_ms: int
    tire_from: str | None
    tire_to: str | None


class ReplayLapData(BaseModel):
    """Full data for a single lap / Dados completos de uma volta."""

    lap_number: int
    positions: list[ReplayPositionData]
    events: list[ReplayEventData]
    pit_stops: list[ReplayPitStopData]


class FullReplayResponse(BaseModel):
    """Full race replay response / Resposta completa de replay de corrida."""

    race_id: uuid.UUID
    total_laps: int
    laps: list[ReplayLapData]


class StintData(BaseModel):
    """Stint performance data / Dados de desempenho de stint."""

    driver_id: uuid.UUID
    driver_name: str
    stint_number: int
    compound: str | None
    start_lap: int
    end_lap: int
    total_laps: int
    avg_pace_ms: int | None
    best_lap_ms: int | None
    degradation_ms: int | None


class DriverStintData(BaseModel):
    """Driver stint breakdown / Detalhamento de stints de um piloto."""

    driver_id: uuid.UUID
    driver_name: str
    stints: list[StintData]


class StintAnalysisResponse(BaseModel):
    """Stint analysis response / Resposta de analise de stints."""

    race_id: uuid.UUID
    drivers: list[DriverStintData]


class OvertakeData(BaseModel):
    """Overtake detection data / Dados de deteccao de ultrapassagem."""

    lap_number: int
    driver_id: uuid.UUID
    driver_name: str
    from_position: int
    to_position: int
    positions_gained: int


class OvertakesResponse(BaseModel):
    """Overtakes analysis response / Resposta de analise de ultrapassagens."""

    race_id: uuid.UUID
    total_overtakes: int
    overtakes: list[OvertakeData]


class FastestLapData(BaseModel):
    """Fastest lap info / Informacao de volta mais rapida."""

    driver_id: uuid.UUID
    driver_name: str
    lap_number: int
    lap_time_ms: int


class RaceSummaryResponse(BaseModel):
    """Race summary response / Resposta de resumo da corrida."""

    race_id: uuid.UUID
    total_laps: int
    total_overtakes: int
    leader_changes: int
    safety_car_laps: int
    dnf_count: int
    fastest_lap: FastestLapData | None
