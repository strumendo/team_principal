"""
User request/response schemas.
Schemas de requisicao/resposta de usuario.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """User response body / Corpo da resposta de usuario."""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """User list response body / Corpo da resposta de listagem de usuarios."""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """User update request body / Corpo da requisicao de atualizacao de usuario."""

    full_name: str | None = None
    avatar_url: str | None = None


class AdminUserCreateRequest(BaseModel):
    """Admin user create request body / Corpo da requisicao de criacao de usuario pelo admin."""

    email: EmailStr
    password: str
    full_name: str
    is_active: bool = True


class AdminUserUpdate(BaseModel):
    """Admin user update request body / Corpo da requisicao de atualizacao de usuario pelo admin."""

    full_name: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
