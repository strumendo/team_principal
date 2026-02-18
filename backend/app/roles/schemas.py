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


class RoleResponse(BaseModel):
    """Role response body with permissions / Corpo da resposta de papel com permissoes."""

    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    is_system: bool
    permissions: list[PermissionResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoleListResponse(BaseModel):
    """Role list response body (without permissions) / Corpo da resposta de listagem de papeis (sem permissoes)."""

    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    is_system: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoleCreateRequest(BaseModel):
    """Role creation request body / Corpo da requisicao de criacao de papel."""

    name: str
    display_name: str
    description: str | None = None


class RoleUpdateRequest(BaseModel):
    """Role update request body / Corpo da requisicao de atualizacao de papel."""

    display_name: str | None = None
    description: str | None = None


class RolePermissionRequest(BaseModel):
    """Role-permission assignment request body / Corpo da requisicao de atribuicao de permissao a papel."""

    permission_id: uuid.UUID
