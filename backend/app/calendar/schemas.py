"""
Calendar response schemas.
Schemas de resposta do calendario.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.races.models import RaceStatus


class CalendarRaceResponse(BaseModel):
    """Race entry for calendar view / Entrada de corrida para visualizacao de calendario."""

    id: uuid.UUID
    display_name: str
    round_number: int
    status: RaceStatus
    scheduled_at: datetime
    track_name: str | None
    track_country: str | None
    championship_id: uuid.UUID
    championship_display_name: str
    championship_status: str

    model_config = {"from_attributes": True}
