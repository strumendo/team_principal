# Architecture / Arquitetura

## Overview / Visao Geral

TeamPrincipal follows a monorepo structure with a clear separation between backend and frontend.

TeamPrincipal segue uma estrutura monorepo com uma separacao clara entre backend e frontend.

## High-Level Architecture / Arquitetura de Alto Nivel

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Next.js   │────>│   FastAPI        │────>│  PostgreSQL  │
│  (Frontend) │<────│   (Backend API)  │<────│  (Database)  │
└─────────────┘     └─────────────────┘     └──────────────┘
     :3000               :8000                   :5432
```

## Backend Architecture / Arquitetura do Backend

The backend follows a modular structure organized by domain:

O backend segue uma estrutura modular organizada por dominio:

```
backend/app/
├── main.py          # App factory + lifespan
├── config.py        # Settings (Pydantic BaseSettings)
├── db/              # Database layer / Camada de banco de dados
│   ├── base.py      # DeclarativeBase
│   ├── session.py   # Engine + session management
│   └── seed.py      # Initial data seeding
├── core/            # Shared core / Nucleo compartilhado
│   ├── security.py  # JWT + password hashing
│   ├── dependencies.py  # FastAPI dependencies
│   └── exceptions.py    # Custom exceptions
├── auth/            # Authentication module / Modulo de autenticacao
├── users/           # Users module / Modulo de usuarios
├── roles/           # Roles module / Modulo de papeis (RBAC)
└── health/          # Health check endpoints
```

### Key Decisions / Decisoes Chave

| Decision / Decisao | Choice / Escolha | Rationale / Justificativa |
|---|---|---|
| ORM | SQLAlchemy 2.0 (async) | Full async support, complex RBAC relationships / Suporte async completo, relacionamentos RBAC complexos |
| Migrations | Alembic | Standard for SQLAlchemy / Padrao para SQLAlchemy |
| Auth | JWT (python-jose) | Standard for API-based auth / Padrao para auth baseada em API |
| Primary Keys | UUID | Better for distributed systems / Melhor para sistemas distribuidos |
| API Versioning | URL prefix `/api/v1/` | Simple and explicit / Simples e explicito |

## Frontend Architecture / Arquitetura do Frontend

The frontend uses Next.js App Router with route groups:

O frontend usa Next.js App Router com grupos de rotas:

```
frontend/src/
├── app/
│   ├── (auth)/          # Public auth pages / Paginas publicas de auth
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/     # Protected pages / Paginas protegidas
│   │   └── dashboard/
│   └── api/auth/        # NextAuth.js API routes
├── components/
│   ├── ui/              # Reusable UI components / Componentes UI reutilizaveis
│   ├── auth/            # Auth-specific components
│   └── layout/          # Layout components
├── lib/                 # Utilities / Utilitarios
│   ├── auth.ts          # NextAuth config
│   └── api-client.ts    # API wrapper
└── middleware.ts        # Route protection / Protecao de rotas
```

## Database Schema / Esquema do Banco de Dados

### Phase 1 — Core RBAC / Fase 1 — RBAC Central

```
users ──< user_roles >── roles ──< role_permissions >── permissions
```

- **users**: Platform users / Usuarios da plataforma
- **roles**: System roles (Admin, Tech Lead, etc.) / Papeis do sistema
- **permissions**: Granular permissions by module / Permissoes granulares por modulo
- **user_roles**: N:N relationship (user-role) / Relacionamento N:N
- **role_permissions**: N:N relationship (role-permission) / Relacionamento N:N

## Infrastructure / Infraestrutura

### Development / Desenvolvimento

- Docker Compose: PostgreSQL + Backend + Frontend
- Hot-reload enabled for both backend and frontend

### Production / Producao (future / futuro)

- AWS ECS/EC2 for compute
- AWS S3 for file storage
- AWS RDS for managed PostgreSQL
