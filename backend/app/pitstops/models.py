"""
Pit stop and race strategy models.
Modelos de pit stop e estrategia de corrida.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TireCompound(str, enum.Enum):
    """
    Tire compound types.
    Tipos de compostos de pneu.
    """

    soft = "soft"
    medium = "medium"
    hard = "hard"
    intermediate = "intermediate"
    wet = "wet"


class PitStop(Base):
    """
    Pit stop event for a driver in a race.
    Evento de pit stop de um piloto em uma corrida.
    """

    __tablename__ = "pit_stops"
    __table_args__ = (UniqueConstraint("race_id", "driver_id", "lap_number", name="uq_pitstop_race_driver_lap"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    race_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    tire_from: Mapped[TireCompound | None] = mapped_column(
        Enum(TireCompound, native_enum=False, length=20), nullable=True
    )
    tire_to: Mapped[TireCompound | None] = mapped_column(
        Enum(TireCompound, native_enum=False, length=20), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships / Relacionamentos
    race: Mapped["Race"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Race", lazy="selectin"
    )
    driver: Mapped["Driver"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Driver", lazy="selectin"
    )
    team: Mapped["Team"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Team", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<PitStop(id={self.id}, race_id={self.race_id}, driver_id={self.driver_id}, lap={self.lap_number})>"


class RaceStrategy(Base):
    """
    Race strategy plan for a driver.
    Plano de estrategia de corrida para um piloto.
    """

    __tablename__ = "race_strategies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    race_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_stops: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_laps: Mapped[str | None] = mapped_column(String(256), nullable=True)
    starting_compound: Mapped[TireCompound | None] = mapped_column(
        Enum(TireCompound, native_enum=False, length=20), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships / Relacionamentos
    race: Mapped["Race"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Race", lazy="selectin"
    )
    driver: Mapped["Driver"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Driver", lazy="selectin"
    )
    team: Mapped["Team"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Team", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<RaceStrategy(id={self.id}, name={self.name}, driver_id={self.driver_id})>"
