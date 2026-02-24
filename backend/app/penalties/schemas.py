"""
Penalty request/response schemas.
Schemas de requisicao/resposta de penalidade.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

PenaltyType = Literal[
    "warning",
    "time_penalty",
    "points_deduction",
    "disqualification",
    "grid_penalty",
]

VALID_PENALTY_TYPES = {"warning", "time_penalty", "points_deduction", "disqualification", "grid_penalty"}


class PenaltyCreateRequest(BaseModel):
    """Penalty creation request body / Corpo da requisicao de criacao de penalidade."""

    team_id: uuid.UUID
    driver_id: uuid.UUID | None = None
    result_id: uuid.UUID | None = None
    penalty_type: str
    reason: str
    points_deducted: float = 0.0
    time_penalty_seconds: int | None = None
    lap_number: int | None = None

    @field_validator("penalty_type")
    @classmethod
    def validate_penalty_type(cls, v: str) -> str:
        if v not in VALID_PENALTY_TYPES:
            raise ValueError(f"Invalid penalty type. Must be one of: {', '.join(sorted(VALID_PENALTY_TYPES))}")
        return v

    @field_validator("points_deducted")
    @classmethod
    def validate_points_deducted(cls, v: float) -> float:
        if v < 0:
            raise ValueError("points_deducted must be >= 0")
        return v


class PenaltyUpdateRequest(BaseModel):
    """Penalty update request body / Corpo da requisicao de atualizacao de penalidade."""

    penalty_type: str | None = None
    reason: str | None = None
    points_deducted: float | None = None
    time_penalty_seconds: int | None = None
    lap_number: int | None = None
    result_id: uuid.UUID | None = None
    driver_id: uuid.UUID | None = None
    is_active: bool | None = None

    @field_validator("penalty_type")
    @classmethod
    def validate_penalty_type(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_PENALTY_TYPES:
            raise ValueError(f"Invalid penalty type. Must be one of: {', '.join(sorted(VALID_PENALTY_TYPES))}")
        return v

    @field_validator("points_deducted")
    @classmethod
    def validate_points_deducted(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("points_deducted must be >= 0")
        return v


class PenaltyResponse(BaseModel):
    """Penalty response body / Corpo da resposta de penalidade."""

    id: uuid.UUID
    race_id: uuid.UUID
    result_id: uuid.UUID | None
    team_id: uuid.UUID
    driver_id: uuid.UUID | None
    penalty_type: str
    reason: str
    points_deducted: float
    time_penalty_seconds: int | None
    lap_number: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PenaltyListResponse(BaseModel):
    """Penalty list item / Item de listagem de penalidade."""

    id: uuid.UUID
    race_id: uuid.UUID
    result_id: uuid.UUID | None
    team_id: uuid.UUID
    driver_id: uuid.UUID | None
    penalty_type: str
    reason: str
    points_deducted: float
    time_penalty_seconds: int | None
    lap_number: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PenaltyDetailResponse(BaseModel):
    """Penalty detail with nested team/driver info / Detalhe de penalidade com info de equipe/piloto."""

    id: uuid.UUID
    race_id: uuid.UUID
    result_id: uuid.UUID | None
    team_id: uuid.UUID
    driver_id: uuid.UUID | None
    penalty_type: str
    reason: str
    points_deducted: float
    time_penalty_seconds: int | None
    lap_number: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    team: dict | None = None
    driver: dict | None = None

    model_config = {"from_attributes": True}
