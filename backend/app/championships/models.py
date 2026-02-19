"""
Championship model.
Modelo de campeonato.
"""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChampionshipStatus(str, enum.Enum):
    """
    Championship lifecycle status.
    Status do ciclo de vida do campeonato.
    """

    planned = "planned"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class Championship(Base):
    """
    Racing championship / season model.
    Modelo de campeonato / temporada de corrida.
    """

    __tablename__ = "championships"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ChampionshipStatus] = mapped_column(
        Enum(ChampionshipStatus, native_enum=False, length=20),
        default=ChampionshipStatus.planned,
        server_default="planned",
        nullable=False,
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Championship(id={self.id}, name={self.name})>"
