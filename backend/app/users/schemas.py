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


class UserUpdate(BaseModel):
    """User update request body / Corpo da requisicao de atualizacao de usuario."""

    full_name: str | None = None
    avatar_url: str | None = None
