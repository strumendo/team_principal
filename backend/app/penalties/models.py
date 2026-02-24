"""
Penalty model.
Modelo de penalidade.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Penalty types / Tipos de penalidade
PENALTY_TYPES = (
    "warning",
    "time_penalty",
    "points_deduction",
    "disqualification",
    "grid_penalty",
)


class Penalty(Base):
    """
    Race penalty/incident model.
    Modelo de penalidade/incidente de corrida.
    """

    __tablename__ = "penalties"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    race_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True
    )
    result_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("race_results.id", ondelete="SET NULL"), nullable=True, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    penalty_type: Mapped[str] = mapped_column(
        Enum(*PENALTY_TYPES, name="penalty_type", native_enum=False),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(512), nullable=False)
    points_deducted: Mapped[float] = mapped_column(Float, default=0.0, server_default="0.0", nullable=False)
    time_penalty_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lap_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships / Relacionamentos
    race: Mapped["Race"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Race", lazy="selectin"
    )
    result: Mapped["RaceResult | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "RaceResult", back_populates="penalties", lazy="selectin"
    )
    team: Mapped["Team"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Team", lazy="selectin"
    )
    driver: Mapped["Driver | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Driver", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Penalty(id={self.id}, type={self.penalty_type}, race_id={self.race_id})>"
