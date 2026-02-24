"""
Upload response schemas.
Schemas de resposta de upload.
"""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """
    Response returned after a successful file upload.
    Resposta retornada apos um upload de arquivo bem-sucedido.
    """

    url: str
