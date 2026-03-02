"""
Telemetry request/response schemas.
Schemas de requisicao/resposta de telemetria.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


# --- Lap Time schemas / Schemas de tempo de volta ---


class LapTimeCreateRequest(BaseModel):
    """Single lap time creation / Criacao de tempo de volta."""

    driver_id: uuid.UUID
    team_id: uuid.UUID
    lap_number: int
    lap_time_ms: int
    sector_1_ms: int | None = None
    sector_2_ms: int | None = None
    sector_3_ms: int | None = None
    is_valid: bool = True
    is_personal_best: bool = False


class LapTimeBulkCreateRequest(BaseModel):
    """Bulk lap time creation / Criacao em lote de tempos de volta."""

    laps: list[LapTimeCreateRequest]


class LapTimeResponse(BaseModel):
    """Lap time response / Resposta de tempo de volta."""

    id: uuid.UUID
    race_id: uuid.UUID
    driver_id: uuid.UUID
    team_id: uuid.UUID
    lap_number: int
    lap_time_ms: int
    sector_1_ms: int | None
    sector_2_ms: int | None
    sector_3_ms: int | None
    is_valid: bool
    is_personal_best: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LapTimeSummaryDriver(BaseModel):
    """Per-driver lap time summary / Resumo de tempos de volta por piloto."""

    driver_id: uuid.UUID
    driver_display_name: str
    fastest_lap_ms: int
    avg_lap_ms: int
    total_laps: int
    personal_best_lap: int | None


class LapTimeSummaryResponse(BaseModel):
    """Lap time summary for a race / Resumo de tempos de volta de uma corrida."""

    drivers: list[LapTimeSummaryDriver]
    overall_fastest: LapTimeResponse | None


# --- Car Setup schemas / Schemas de setup de carro ---


class CarSetupCreateRequest(BaseModel):
    """Car setup creation / Criacao de setup de carro."""

    driver_id: uuid.UUID
    team_id: uuid.UUID
    name: str
    notes: str | None = None
    front_wing: float | None = None
    rear_wing: float | None = None
    differential: float | None = None
    brake_bias: float | None = None
    tire_pressure_fl: float | None = None
    tire_pressure_fr: float | None = None
    tire_pressure_rl: float | None = None
    tire_pressure_rr: float | None = None
    suspension_stiffness: float | None = None
    anti_roll_bar: float | None = None


class CarSetupUpdateRequest(BaseModel):
    """Car setup update / Atualizacao de setup de carro."""

    name: str | None = None
    notes: str | None = None
    front_wing: float | None = None
    rear_wing: float | None = None
    differential: float | None = None
    brake_bias: float | None = None
    tire_pressure_fl: float | None = None
    tire_pressure_fr: float | None = None
    tire_pressure_rl: float | None = None
    tire_pressure_rr: float | None = None
    suspension_stiffness: float | None = None
    anti_roll_bar: float | None = None
    is_active: bool | None = None


class CarSetupResponse(BaseModel):
    """Car setup response / Resposta de setup de carro."""

    id: uuid.UUID
    race_id: uuid.UUID
    driver_id: uuid.UUID
    team_id: uuid.UUID
    name: str
    notes: str | None
    front_wing: float | None
    rear_wing: float | None
    differential: float | None
    brake_bias: float | None
    tire_pressure_fl: float | None
    tire_pressure_fr: float | None
    tire_pressure_rl: float | None
    tire_pressure_rr: float | None
    suspension_stiffness: float | None
    anti_roll_bar: float | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


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


class CarSetupDetailResponse(CarSetupResponse):
    """Car setup detail with driver and team / Detalhe de setup com piloto e equipe."""

    driver: DriverInfo
    team: TeamInfo


# --- Compare schemas / Schemas de comparacao ---


class DriverComparison(BaseModel):
    """Driver comparison data / Dados de comparacao entre pilotos."""

    driver_id: uuid.UUID
    driver_display_name: str
    laps: list[LapTimeResponse]
