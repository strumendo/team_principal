"""
Team request/response schemas.
Schemas de requisicao/resposta de equipe.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class TeamResponse(BaseModel):
    """Team response body / Corpo da resposta de equipe."""

    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    logo_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TeamListResponse(BaseModel):
    """Team list response body (without logo_url) / Corpo da resposta de listagem de equipes (sem logo_url)."""

    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TeamCreateRequest(BaseModel):
    """Team creation request body / Corpo da requisicao de criacao de equipe."""

    name: str
    display_name: str
    description: str | None = None
    logo_url: str | None = None


class TeamUpdateRequest(BaseModel):
    """Team update request body / Corpo da requisicao de atualizacao de equipe."""

    display_name: str | None = None
    description: str | None = None
    logo_url: str | None = None
    is_active: bool | None = None
