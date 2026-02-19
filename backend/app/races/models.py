"""
Race model.
Modelo de corrida.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RaceStatus(str, enum.Enum):
    """
    Race lifecycle status.
    Status do ciclo de vida da corrida.
    """

    scheduled = "scheduled"
    qualifying = "qualifying"
    active = "active"
    finished = "finished"
    cancelled = "cancelled"


class Race(Base):
    """
    Individual race event within a championship.
    Evento de corrida individual dentro de um campeonato.
    """

    __tablename__ = "races"
    __table_args__ = (UniqueConstraint("championship_id", "name", name="uq_race_championship_name"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    championship_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("championships.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[RaceStatus] = mapped_column(
        Enum(RaceStatus, native_enum=False, length=20),
        default=RaceStatus.scheduled,
        server_default="scheduled",
        nullable=False,
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    track_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    track_country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    laps_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships / Relacionamentos
    championship: Mapped["Championship"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Championship", back_populates="races", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Race(id={self.id}, name={self.name})>"
