"""Create lap_positions and race_events tables.

Revision ID: 012
Revises: 011
Create Date: 2026-03-04

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lap_positions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("race_id", sa.Uuid(), sa.ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("driver_id", sa.Uuid(), sa.ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("team_id", sa.Uuid(), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lap_number", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("gap_to_leader_ms", sa.Integer(), nullable=True),
        sa.Column("interval_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("race_id", "driver_id", "lap_number", name="uq_lapposition_race_driver_lap"),
    )

    op.create_table(
        "race_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("race_id", sa.Uuid(), sa.ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("lap_number", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("driver_id", sa.Uuid(), sa.ForeignKey("drivers.id", ondelete="CASCADE"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("race_events")
    op.drop_table("lap_positions")
