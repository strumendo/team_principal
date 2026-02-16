"""Initial schema — users, roles, permissions, association tables.

Revision ID: 001
Revises:
Create Date: 2026-02-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table / Tabela de usuarios
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(1024), nullable=False),
        sa.Column("full_name", sa.String(256), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_superuser", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("avatar_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # Roles table / Tabela de papeis
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("is_system", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roles")),
        sa.UniqueConstraint("name", name=op.f("uq_roles_name")),
    )
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=True)

    # Permissions table / Tabela de permissoes
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("codename", sa.String(128), nullable=False),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("module", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_permissions")),
        sa.UniqueConstraint("codename", name=op.f("uq_permissions_codename")),
    )
    op.create_index(op.f("ix_permissions_codename"), "permissions", ["codename"], unique=True)
    op.create_index(op.f("ix_permissions_module"), "permissions", ["module"])

    # Role-Permission association / Associacao Papel-Permissao
    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE", name=op.f("fk_role_permissions_role_id_roles")),
            nullable=False,
        ),
        sa.Column(
            "permission_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "permissions.id", ondelete="CASCADE", name=op.f("fk_role_permissions_permission_id_permissions")
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id", name=op.f("pk_role_permissions")),
    )

    # User-Role association / Associacao Usuario-Papel
    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE", name=op.f("fk_user_roles_user_id_users")),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE", name=op.f("fk_user_roles_role_id_roles")),
            nullable=False,
        ),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "assigned_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", name=op.f("fk_user_roles_assigned_by_users")),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("user_id", "role_id", name=op.f("pk_user_roles")),
    )


def downgrade() -> None:
    op.drop_table("user_roles")
    op.drop_table("role_permissions")
    op.drop_index(op.f("ix_permissions_module"), table_name="permissions")
    op.drop_index(op.f("ix_permissions_codename"), table_name="permissions")
    op.drop_table("permissions")
    op.drop_index(op.f("ix_roles_name"), table_name="roles")
    op.drop_table("roles")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
