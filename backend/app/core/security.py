"""
Security utilities: JWT token management and password hashing.
Utilitarios de seguranca: gerenciamento de tokens JWT e hashing de senha.
"""

from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.config import settings


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    Gera o hash de uma senha em texto puro usando bcrypt.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    Verifica uma senha em texto puro contra um hash bcrypt.
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    Cria um token de acesso JWT.
    """
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire, "type": "access"}
    encoded: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded


def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT refresh token.
    Cria um token de atualizacao JWT.
    """
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode = {"sub": subject, "exp": expire, "type": "refresh"}
    encoded: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded


def decode_token(token: str) -> dict[str, object] | None:
    """
    Decode and validate a JWT token. Returns payload or None if invalid.
    Decodifica e valida um token JWT. Retorna payload ou None se invalido.
    """
    try:
        payload: dict[str, object] = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
