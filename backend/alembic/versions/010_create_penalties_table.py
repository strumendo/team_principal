"""Create penalties table.

Revision ID: 010
Revises: 009
Create Date: 2026-02-24

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
        "penalties",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("race_id", sa.Uuid(), sa.ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column(
            "result_id", sa.Uuid(), sa.ForeignKey("race_results.id", ondelete="SET NULL"), nullable=True, index=True
        ),
        sa.Column("team_id", sa.Uuid(), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column(
            "driver_id", sa.Uuid(), sa.ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True, index=True
        ),
        sa.Column(
            "penalty_type",
            sa.Enum(
                "warning",
                "time_penalty",
                "points_deduction",
                "disqualification",
                "grid_penalty",
                name="penalty_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("reason", sa.String(512), nullable=False),
        sa.Column("points_deducted", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("time_penalty_seconds", sa.Integer(), nullable=True),
        sa.Column("lap_number", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("penalties")
