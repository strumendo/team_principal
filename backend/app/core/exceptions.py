"""
Custom HTTP exceptions.
Excecoes HTTP customizadas.
"""

from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    """
    Raised when authentication credentials are invalid.
    Lancada quando credenciais de autenticacao sao invalidas.
    """

    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotFoundException(HTTPException):
    """
    Raised when a resource is not found.
    Lancada quando um recurso nao e encontrado.
    """

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictException(HTTPException):
    """
    Raised when a resource already exists.
    Lancada quando um recurso ja existe.
    """

    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ForbiddenException(HTTPException):
    """
    Raised when the user lacks permission.
    Lancada quando o usuario nao tem permissao.
    """

    def __init__(self, detail: str = "Not enough permissions") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
