"""
Local filesystem storage for file uploads.
Armazenamento em sistema de arquivos local para uploads de arquivos.
"""

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import settings
from app.core.exceptions import ValidationException

# Map content-type to file extension / Mapa de content-type para extensao de arquivo
CONTENT_TYPE_EXTENSIONS: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


async def save_upload(file: UploadFile, category: str) -> str:
    """
    Validate and save an uploaded file to the local filesystem.
    Returns the URL path (e.g. /uploads/avatars/{uuid}.jpg).

    Valida e salva um arquivo enviado no sistema de arquivos local.
    Retorna o caminho URL (ex: /uploads/avatars/{uuid}.jpg).
    """
    # Validate content type / Validar tipo de conteudo
    if file.content_type not in settings.UPLOAD_ALLOWED_TYPES:
        raise ValidationException(
            f"Invalid file type: {file.content_type}. " f"Allowed: {', '.join(settings.UPLOAD_ALLOWED_TYPES)}"
        )

    # Read file bytes and validate size / Ler bytes do arquivo e validar tamanho
    data = await file.read()
    if len(data) > settings.UPLOAD_MAX_SIZE_BYTES:
        max_mb = settings.UPLOAD_MAX_SIZE_BYTES / (1024 * 1024)
        raise ValidationException(f"File too large. Maximum size: {max_mb:.0f} MB")

    # Generate unique filename / Gerar nome de arquivo unico
    ext = CONTENT_TYPE_EXTENSIONS[file.content_type]
    filename = f"{uuid.uuid4()}{ext}"

    # Create directory if needed / Criar diretorio se necessario
    upload_dir = Path(settings.UPLOAD_DIR) / category
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file / Salvar arquivo
    file_path = upload_dir / filename
    file_path.write_bytes(data)

    return f"/uploads/{category}/{filename}"


def delete_upload(url_path: str) -> None:
    """
    Delete a previously uploaded file by its URL path.
    Silent if the file does not exist.

    Exclui um arquivo previamente enviado pelo seu caminho URL.
    Silencioso se o arquivo nao existir.
    """
    # Convert URL path to filesystem path / Converter caminho URL para caminho do sistema
    # URL: /uploads/avatars/uuid.jpg -> filesystem: uploads/avatars/uuid.jpg
    relative = url_path.lstrip("/")
    file_path = Path(relative)
    if file_path.exists():
        file_path.unlink()
