"""
Auth request/response schemas.
Schemas de requisicao/resposta de autenticacao.
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request body / Corpo da requisicao de login."""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Register request body / Corpo da requisicao de registro."""

    email: EmailStr
    password: str
    full_name: str


class TokenResponse(BaseModel):
    """Token response body / Corpo da resposta de token."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Refresh token request body / Corpo da requisicao de atualizacao de token."""

    refresh_token: str
