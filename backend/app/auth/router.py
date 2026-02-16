"""
Auth API router: login, register, refresh.
Router da API de autenticacao: login, registro, atualizacao.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.auth.service import authenticate_user, create_tokens, refresh_access_token, register_user
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """
    Authenticate user and return JWT tokens.
    Autentica usuario e retorna tokens JWT.
    """
    user = await authenticate_user(db, body.email, body.password)
    return create_tokens(str(user.id))


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """
    Register a new user and return JWT tokens.
    Registra um novo usuario e retorna tokens JWT.
    """
    user = await register_user(db, body.email, body.password, body.full_name)
    return create_tokens(str(user.id))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """
    Refresh access token using a valid refresh token.
    Atualiza o token de acesso usando um token de atualizacao valido.
    """
    return await refresh_access_token(db, body.refresh_token)
