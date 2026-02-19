"""
Race result model.
Modelo de resultado de corrida.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RaceResult(Base):
    """
    Race finishing result for a team.
    Resultado de chegada da corrida para uma equipe.
    """

    __tablename__ = "race_results"
    __table_args__ = (UniqueConstraint("race_id", "team_id", name="uq_race_result_team"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    race_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    laps_completed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fastest_lap: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    dnf: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    dsq: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships / Relacionamentos
    race: Mapped["Race"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Race", back_populates="results", lazy="selectin"
    )
    team: Mapped["Team"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Team", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<RaceResult(id={self.id}, race_id={self.race_id}, team_id={self.team_id}, position={self.position})>"
