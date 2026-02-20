"""
Driver request/response schemas.
Schemas de requisicao/resposta de piloto.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, field_validator


class DriverTeamResponse(BaseModel):
    """Team summary within a driver / Resumo de equipe em um piloto."""

    id: uuid.UUID
    name: str
    display_name: str
    is_active: bool

    model_config = {"from_attributes": True}


class DriverResponse(BaseModel):
    """Driver response body / Corpo da resposta de piloto."""

    id: uuid.UUID
    name: str
    display_name: str
    abbreviation: str
    number: int
    nationality: str | None
    date_of_birth: date | None
    photo_url: str | None
    team_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DriverListResponse(BaseModel):
    """Driver list response body / Corpo da resposta de listagem de pilotos."""

    id: uuid.UUID
    name: str
    display_name: str
    abbreviation: str
    number: int
    nationality: str | None
    team_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DriverDetailResponse(BaseModel):
    """Driver detail response with team / Resposta detalhada de piloto com equipe."""

    id: uuid.UUID
    name: str
    display_name: str
    abbreviation: str
    number: int
    nationality: str | None
    date_of_birth: date | None
    photo_url: str | None
    team_id: uuid.UUID
    team: DriverTeamResponse
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DriverCreateRequest(BaseModel):
    """Driver creation request body / Corpo da requisicao de criacao de piloto."""

    name: str
    display_name: str
    abbreviation: str
    number: int
    nationality: str | None = None
    date_of_birth: date | None = None
    photo_url: str | None = None
    team_id: uuid.UUID

    @field_validator("abbreviation")
    @classmethod
    def validate_abbreviation(cls, v: str) -> str:
        """Validate abbreviation is exactly 3 chars / Valida que abreviacao tem exatamente 3 caracteres."""
        v = v.upper()
        if len(v) != 3:
            raise ValueError("Abbreviation must be exactly 3 characters")
        return v


class DriverUpdateRequest(BaseModel):
    """Driver update request body / Corpo da requisicao de atualizacao de piloto."""

    display_name: str | None = None
    abbreviation: str | None = None
    number: int | None = None
    nationality: str | None = None
    date_of_birth: date | None = None
    photo_url: str | None = None
    is_active: bool | None = None

    @field_validator("abbreviation")
    @classmethod
    def validate_abbreviation(cls, v: str | None) -> str | None:
        """Validate abbreviation is exactly 3 chars / Valida que abreviacao tem exatamente 3 caracteres."""
        if v is None:
            return v
        v = v.upper()
        if len(v) != 3:
            raise ValueError("Abbreviation must be exactly 3 characters")
        return v
