"""
Permission and Role request/response schemas.
Schemas de requisicao/resposta de permissao e papel.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class PermissionResponse(BaseModel):
    """Permission response body / Corpo da resposta de permissao."""

    id: uuid.UUID
    codename: str
    description: str | None
    module: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PermissionCreateRequest(BaseModel):
    """Permission creation request body / Corpo da requisicao de criacao de permissao."""

    codename: str
    description: str | None = None
    module: str
