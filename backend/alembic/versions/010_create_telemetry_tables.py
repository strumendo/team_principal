"""Create telemetry tables (lap_times, car_setups).

Revision ID: 010
Revises: 009
Create Date: 2026-03-02

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lap_times",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("race_id", sa.Uuid(), sa.ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("driver_id", sa.Uuid(), sa.ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("team_id", sa.Uuid(), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lap_number", sa.Integer(), nullable=False),
        sa.Column("lap_time_ms", sa.Integer(), nullable=False),
        sa.Column("sector_1_ms", sa.Integer(), nullable=True),
        sa.Column("sector_2_ms", sa.Integer(), nullable=True),
        sa.Column("sector_3_ms", sa.Integer(), nullable=True),
        sa.Column("is_valid", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_personal_best", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("race_id", "driver_id", "lap_number", name="uq_lap_race_driver_lap"),
    )

    op.create_table(
        "car_setups",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("race_id", sa.Uuid(), sa.ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("driver_id", sa.Uuid(), sa.ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("team_id", sa.Uuid(), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("front_wing", sa.Float(), nullable=True),
        sa.Column("rear_wing", sa.Float(), nullable=True),
        sa.Column("differential", sa.Float(), nullable=True),
        sa.Column("brake_bias", sa.Float(), nullable=True),
        sa.Column("tire_pressure_fl", sa.Float(), nullable=True),
        sa.Column("tire_pressure_fr", sa.Float(), nullable=True),
        sa.Column("tire_pressure_rl", sa.Float(), nullable=True),
        sa.Column("tire_pressure_rr", sa.Float(), nullable=True),
        sa.Column("suspension_stiffness", sa.Float(), nullable=True),
        sa.Column("anti_roll_bar", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("car_setups")
    op.drop_table("lap_times")
