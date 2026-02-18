"""Add team_id foreign key to users table.

Revision ID: 003
Revises: 002
Create Date: 2026-02-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "team_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teams.id", ondelete="SET NULL", name=op.f("fk_users_team_id_teams")),
            nullable=True,
        ),
    )
    op.create_index(op.f("ix_users_team_id"), "users", ["team_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_users_team_id"), table_name="users")
    op.drop_column("users", "team_id")
