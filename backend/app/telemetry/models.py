"""
Telemetry models: lap times and car setups.
Modelos de telemetria: tempos de volta e setups de carro.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LapTime(Base):
    """
    Lap time record for a driver in a race.
    Registro de tempo de volta de um piloto em uma corrida.
    """

    __tablename__ = "lap_times"
    __table_args__ = (UniqueConstraint("race_id", "driver_id", "lap_number", name="uq_lap_race_driver_lap"),)

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
    lap_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    sector_1_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sector_2_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sector_3_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    is_personal_best: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
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
        return f"<LapTime(id={self.id}, race_id={self.race_id}, driver_id={self.driver_id}, lap={self.lap_number})>"


class CarSetup(Base):
    """
    Car setup configuration for a driver in a race.
    Configuracao de setup do carro de um piloto em uma corrida.
    """

    __tablename__ = "car_setups"

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
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    front_wing: Mapped[float | None] = mapped_column(Float, nullable=True)
    rear_wing: Mapped[float | None] = mapped_column(Float, nullable=True)
    differential: Mapped[float | None] = mapped_column(Float, nullable=True)
    brake_bias: Mapped[float | None] = mapped_column(Float, nullable=True)
    tire_pressure_fl: Mapped[float | None] = mapped_column(Float, nullable=True)
    tire_pressure_fr: Mapped[float | None] = mapped_column(Float, nullable=True)
    tire_pressure_rl: Mapped[float | None] = mapped_column(Float, nullable=True)
    tire_pressure_rr: Mapped[float | None] = mapped_column(Float, nullable=True)
    suspension_stiffness: Mapped[float | None] = mapped_column(Float, nullable=True)
    anti_roll_bar: Mapped[float | None] = mapped_column(Float, nullable=True)
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
        return f"<CarSetup(id={self.id}, name={self.name}, driver_id={self.driver_id})>"
