"""Create race_results table.

Revision ID: 008
Revises: 007
Create Date: 2026-02-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "race_results",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("race_id", sa.Uuid(), sa.ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("team_id", sa.Uuid(), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("points", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("laps_completed", sa.Integer(), nullable=True),
        sa.Column("fastest_lap", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("dnf", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("dsq", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("notes", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("race_id", "team_id", name="uq_race_result_team"),
    )


def downgrade() -> None:
    op.drop_table("race_results")
