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


class TeamMemberResponse(BaseModel):
    """Team member response body / Corpo da resposta de membro da equipe."""

    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    avatar_url: str | None

    model_config = {"from_attributes": True}


class TeamDetailResponse(BaseModel):
    """Team detail response body with members / Corpo da resposta detalhada de equipe com membros."""

    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    logo_url: str | None
    is_active: bool
    members: list[TeamMemberResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TeamUpdateRequest(BaseModel):
    """Team update request body / Corpo da requisicao de atualizacao de equipe."""

    display_name: str | None = None
    description: str | None = None
    logo_url: str | None = None
    is_active: bool | None = None


class TeamAddMemberRequest(BaseModel):
    """Team add member request body / Corpo da requisicao de adicao de membro."""

    user_id: uuid.UUID
