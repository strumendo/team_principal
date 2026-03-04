"""
Race replay models: lap positions and race events.
Modelos de replay de corrida: posicoes por volta e eventos de corrida.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RaceEventType(str, enum.Enum):
    """
    Race event types.
    Tipos de eventos de corrida.
    """

    safety_car = "safety_car"
    virtual_safety_car = "virtual_safety_car"
    red_flag = "red_flag"
    incident = "incident"
    penalty = "penalty"
    overtake = "overtake"
    mechanical_failure = "mechanical_failure"
    race_start = "race_start"
    race_end = "race_end"


class LapPosition(Base):
    """
    Position of a driver on a specific lap of a race.
    Posicao de um piloto em uma volta especifica da corrida.
    """

    __tablename__ = "lap_positions"
    __table_args__ = (UniqueConstraint("race_id", "driver_id", "lap_number", name="uq_lapposition_race_driver_lap"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    race_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    gap_to_leader_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    interval_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
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
        return (
            f"<LapPosition(id={self.id}, race_id={self.race_id}, "
            f"driver_id={self.driver_id}, lap={self.lap_number}, pos={self.position})>"
        )


class RaceEvent(Base):
    """
    Event during a race (safety car, incidents, flags, etc.).
    Evento durante uma corrida (safety car, incidentes, bandeiras, etc.).
    """

    __tablename__ = "race_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    race_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[RaceEventType] = mapped_column(Enum(RaceEventType, native_enum=False, length=30), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships / Relacionamentos
    race: Mapped["Race"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Race", lazy="selectin"
    )
    driver: Mapped["Driver | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Driver", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<RaceEvent(id={self.id}, race_id={self.race_id}, " f"lap={self.lap_number}, type={self.event_type})>"
