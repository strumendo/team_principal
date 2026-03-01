"""
Database seeding script for initial system roles and permissions.
Script de seed do banco de dados para papeis e permissoes iniciais do sistema.

Usage / Uso: python -m app.db.seed
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.base import Base  # noqa: F401
from app.roles.models import Permission, Role

# System roles / Papeis do sistema
SYSTEM_ROLES = [
    {
        "name": "admin",
        "display_name": "Admin",
        "description": "Full system access / Acesso total ao sistema",
        "is_system": True,
    },
    {
        "name": "tech_lead",
        "display_name": "Tech Lead",
        "description": "Technical leadership and setup management / Lideranca tecnica e gerenciamento de setup",
        "is_system": True,
    },
    {
        "name": "performance_lead",
        "display_name": "Performance Lead",
        "description": "Performance analysis and telemetry / Analise de desempenho e telemetria",
        "is_system": True,
    },
    {
        "name": "radio_support",
        "display_name": "Radio/Support",
        "description": "Communication and race support / Comunicacao e suporte de corrida",
        "is_system": True,
    },
    {
        "name": "pilot",
        "display_name": "Pilot",
        "description": "Driver with access to own data / Piloto com acesso aos proprios dados",
        "is_system": True,
    },
    {
        "name": "media",
        "display_name": "Media",
        "description": "Content creation and media management / Criacao de conteudo e gerenciamento de midia",
        "is_system": True,
    },
]

# System permissions / Permissoes do sistema
SYSTEM_PERMISSIONS = [
    {"codename": "auth:register", "module": "auth", "description": "Register new users / Registrar novos usuarios"},
    {"codename": "users:read", "module": "users", "description": "Read any user / Ler qualquer usuario"},
    {"codename": "users:read_self", "module": "users", "description": "Read own profile / Ler perfil proprio"},
    {"codename": "users:update", "module": "users", "description": "Update any user / Atualizar qualquer usuario"},
    {
        "codename": "users:update_self",
        "module": "users",
        "description": "Update own profile / Atualizar perfil proprio",
    },
    {"codename": "users:list", "module": "users", "description": "List all users / Listar todos os usuarios"},
    {"codename": "users:create", "module": "users", "description": "Create users / Criar usuarios"},
    {"codename": "users:delete", "module": "users", "description": "Delete users / Excluir usuarios"},
    {"codename": "roles:read", "module": "roles", "description": "Read roles / Ler papeis"},
    {"codename": "roles:create", "module": "roles", "description": "Create roles / Criar papeis"},
    {"codename": "roles:update", "module": "roles", "description": "Update roles / Atualizar papeis"},
    {"codename": "roles:delete", "module": "roles", "description": "Delete roles / Excluir papeis"},
    {
        "codename": "roles:assign",
        "module": "roles",
        "description": "Assign roles to users / Atribuir papeis a usuarios",
    },
    {
        "codename": "roles:revoke",
        "module": "roles",
        "description": "Revoke roles from users / Revogar papeis de usuarios",
    },
    {"codename": "permissions:read", "module": "permissions", "description": "Read permissions / Ler permissoes"},
    {
        "codename": "permissions:create",
        "module": "permissions",
        "description": "Create permissions / Criar permissoes",
    },
    {
        "codename": "permissions:assign",
        "module": "permissions",
        "description": "Assign permissions to roles / Atribuir permissoes a papeis",
    },
    {
        "codename": "permissions:revoke",
        "module": "permissions",
        "description": "Revoke permissions from roles / Revogar permissoes de papeis",
    },
    {"codename": "teams:read", "module": "teams", "description": "Read teams / Ler equipes"},
    {"codename": "teams:create", "module": "teams", "description": "Create teams / Criar equipes"},
    {"codename": "teams:update", "module": "teams", "description": "Update teams / Atualizar equipes"},
    {"codename": "teams:delete", "module": "teams", "description": "Delete teams / Excluir equipes"},
    {
        "codename": "teams:manage_members",
        "module": "teams",
        "description": "Manage team members / Gerenciar membros da equipe",
    },
    {
        "codename": "championships:read",
        "module": "championships",
        "description": "Read championships / Ler campeonatos",
    },
    {
        "codename": "championships:create",
        "module": "championships",
        "description": "Create championships / Criar campeonatos",
    },
    {
        "codename": "championships:update",
        "module": "championships",
        "description": "Update championships / Atualizar campeonatos",
    },
    {
        "codename": "championships:delete",
        "module": "championships",
        "description": "Delete championships / Excluir campeonatos",
    },
    {
        "codename": "championships:manage_entries",
        "module": "championships",
        "description": "Manage championship entries / Gerenciar inscricoes de campeonato",
    },
    {"codename": "races:read", "module": "races", "description": "Read races / Ler corridas"},
    {"codename": "races:create", "module": "races", "description": "Create races / Criar corridas"},
    {"codename": "races:update", "module": "races", "description": "Update races / Atualizar corridas"},
    {"codename": "races:delete", "module": "races", "description": "Delete races / Excluir corridas"},
    {
        "codename": "races:manage_entries",
        "module": "races",
        "description": "Manage race entries / Gerenciar inscricoes de corrida",
    },
    {"codename": "results:read", "module": "results", "description": "Read race results / Ler resultados de corrida"},
    {
        "codename": "results:create",
        "module": "results",
        "description": "Create race results / Criar resultados de corrida",
    },
    {
        "codename": "results:update",
        "module": "results",
        "description": "Update race results / Atualizar resultados de corrida",
    },
    {
        "codename": "results:delete",
        "module": "results",
        "description": "Delete race results / Excluir resultados de corrida",
    },
    {"codename": "drivers:read", "module": "drivers", "description": "Read drivers / Ler pilotos"},
    {"codename": "drivers:create", "module": "drivers", "description": "Create drivers / Criar pilotos"},
    {"codename": "drivers:update", "module": "drivers", "description": "Update drivers / Atualizar pilotos"},
    {"codename": "drivers:delete", "module": "drivers", "description": "Delete drivers / Excluir pilotos"},
    {
        "codename": "notifications:read",
        "module": "notifications",
        "description": "Read notifications / Ler notificacoes",
    },
    {
        "codename": "notifications:create",
        "module": "notifications",
        "description": "Create notifications / Criar notificacoes",
    },
    {
        "codename": "notifications:delete",
        "module": "notifications",
        "description": "Delete notifications / Excluir notificacoes",
    },
]


async def seed_roles(session: AsyncSession) -> None:
    """
    Seed system roles if they don't exist.
    Popula papeis do sistema se nao existirem.
    """
    for role_data in SYSTEM_ROLES:
        result = await session.execute(select(Role).where(Role.name == role_data["name"]))
        existing = result.scalar_one_or_none()
        if existing is None:
            session.add(Role(**role_data))
            print(f"  Created role / Papel criado: {role_data['display_name']}")
        else:
            print(f"  Role already exists / Papel ja existe: {role_data['display_name']}")
    await session.commit()


async def seed_permissions(session: AsyncSession) -> None:
    """
    Seed system permissions if they don't exist.
    Popula permissoes do sistema se nao existirem.
    """
    for perm_data in SYSTEM_PERMISSIONS:
        result = await session.execute(select(Permission).where(Permission.codename == perm_data["codename"]))
        existing = result.scalar_one_or_none()
        if existing is None:
            session.add(Permission(**perm_data))
            print(f"  Created permission / Permissao criada: {perm_data['codename']}")
        else:
            print(f"  Permission already exists / Permissao ja existe: {perm_data['codename']}")
    await session.commit()


# Role-permission assignments / Atribuicoes de permissao a papel
# admin gets all permissions, pilot gets self-access permissions
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": [p["codename"] for p in SYSTEM_PERMISSIONS],
    "pilot": [
        "users:read_self",
        "users:update_self",
        "teams:read",
        "championships:read",
        "races:read",
        "results:read",
        "drivers:read",
        "notifications:read",
    ],
}


async def seed_role_permissions(session: AsyncSession) -> None:
    """
    Seed role-permission assignments if they don't exist.
    Popula atribuicoes de permissao a papel se nao existirem.
    """
    for role_name, codenames in ROLE_PERMISSIONS.items():
        result = await session.execute(select(Role).where(Role.name == role_name))
        role = result.scalar_one_or_none()
        if role is None:
            print(f"  Role not found, skipping / Papel nao encontrado: {role_name}")
            continue

        existing_codenames = {p.codename for p in role.permissions}
        for codename in codenames:
            if codename in existing_codenames:
                continue
            perm_result = await session.execute(select(Permission).where(Permission.codename == codename))
            perm = perm_result.scalar_one_or_none()
            if perm is None:
                print(f"  Permission not found / Permissao nao encontrada: {codename}")
                continue
            role.permissions.append(perm)
            print(f"  Assigned {codename} -> {role_name}")

    await session.commit()


async def main() -> None:
    """
    Main seed function.
    Funcao principal de seed.
    """
    print("Seeding database... / Populando banco de dados...")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        await seed_roles(session)
        await seed_permissions(session)
        await seed_role_permissions(session)

    await engine.dispose()
    print("Done! / Concluido!")


if __name__ == "__main__":
    asyncio.run(main())
