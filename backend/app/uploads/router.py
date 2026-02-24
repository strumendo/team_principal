"""
Upload API router for avatars, logos, and photos.
Router da API de upload para avatares, logos e fotos.
"""

import uuid

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, require_permissions
from app.core.exceptions import ForbiddenException
from app.db.session import get_db
from app.drivers.service import get_driver_by_id
from app.teams.service import get_team_by_id
from app.uploads.schemas import UploadResponse
from app.uploads.storage import delete_upload, save_upload
from app.users.models import User
from app.users.service import get_user_by_id

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])


def _has_permission(user: User, codename: str) -> bool:
    """
    Check if user has a specific permission (or is superuser).
    Verifica se o usuario tem uma permissao especifica (ou e superusuario).
    """
    if user.is_superuser:
        return True
    for role in user.roles:
        for perm in role.permissions:
            if perm.codename == codename:
                return True
    return False


@router.post("/users/{user_id}/avatar", response_model=UploadResponse)
async def upload_user_avatar(
    user_id: uuid.UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """
    Upload a user avatar. Allowed for own user or with users:update permission.
    Upload de avatar de usuario. Permitido para o proprio usuario ou com permissao users:update.
    """
    # Permission check: own user OR users:update
    # Verificacao de permissao: proprio usuario OU users:update
    if current_user.id != user_id and not _has_permission(current_user, "users:update"):
        raise ForbiddenException("Missing permissions: users:update")

    user = await get_user_by_id(db, user_id)

    # Delete old avatar if exists / Excluir avatar antigo se existir
    if user.avatar_url:
        delete_upload(user.avatar_url)

    # Save new avatar / Salvar novo avatar
    url = await save_upload(file, "avatars")
    user.avatar_url = url
    await db.commit()
    await db.refresh(user)

    return UploadResponse(url=url)


@router.post("/teams/{team_id}/logo", response_model=UploadResponse)
async def upload_team_logo(
    team_id: uuid.UUID,
    file: UploadFile,
    _current_user: User = Depends(require_permissions("teams:update")),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """
    Upload a team logo. Requires teams:update permission.
    Upload de logo de equipe. Requer permissao teams:update.
    """
    team = await get_team_by_id(db, team_id)

    # Delete old logo if exists / Excluir logo antigo se existir
    if team.logo_url:
        delete_upload(team.logo_url)

    # Save new logo / Salvar novo logo
    url = await save_upload(file, "logos")
    team.logo_url = url
    await db.commit()
    await db.refresh(team)

    return UploadResponse(url=url)


@router.post("/drivers/{driver_id}/photo", response_model=UploadResponse)
async def upload_driver_photo(
    driver_id: uuid.UUID,
    file: UploadFile,
    _current_user: User = Depends(require_permissions("drivers:update")),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """
    Upload a driver photo. Requires drivers:update permission.
    Upload de foto de piloto. Requer permissao drivers:update.
    """
    driver = await get_driver_by_id(db, driver_id)

    # Delete old photo if exists / Excluir foto antiga se existir
    if driver.photo_url:
        delete_upload(driver.photo_url)

    # Save new photo / Salvar nova foto
    url = await save_upload(file, "photos")
    driver.photo_url = url
    await db.commit()
    await db.refresh(driver)

    return UploadResponse(url=url)
