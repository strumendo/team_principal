"""Create races table.

Revision ID: 006
Revises: 005
Create Date: 2026-02-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "races",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "championship_id",
            sa.Uuid(),
            sa.ForeignKey("championships.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(64), nullable=False, index=True),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="scheduled"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("track_name", sa.String(128), nullable=True),
        sa.Column("track_country", sa.String(64), nullable=True),
        sa.Column("laps_total", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("championship_id", "name", name="uq_race_championship_name"),
    )


def downgrade() -> None:
    op.drop_table("races")
