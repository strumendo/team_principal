# Architecture / Arquitetura

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [High-Level Architecture / Arquitetura de Alto Nivel](#high-level-architecture--arquitetura-de-alto-nivel)
3. [Backend Architecture / Arquitetura do Backend](#backend-architecture--arquitetura-do-backend)
4. [Module Structure / Estrutura de Modulos](#module-structure--estrutura-de-modulos)
5. [Authentication & Authorization Flow / Fluxo de Autenticacao & Autorizacao](#authentication--authorization-flow--fluxo-de-autenticacao--autorizacao)
6. [Database Schema / Esquema do Banco de Dados](#database-schema--esquema-do-banco-de-dados)
7. [Frontend Architecture / Arquitetura do Frontend](#frontend-architecture--arquitetura-do-frontend)
8. [Key Technical Decisions / Decisoes Tecnicas Chave](#key-technical-decisions--decisoes-tecnicas-chave)
9. [Testing Strategy / Estrategia de Testes](#testing-strategy--estrategia-de-testes)
10. [Infrastructure / Infraestrutura](#infrastructure--infraestrutura)

---

## Overview / Visao Geral

TeamPrincipal follows a monorepo structure with a clear separation between backend and frontend. The backend is a RESTful API built with FastAPI, and the frontend is a Next.js application. Communication happens via HTTP/JSON over the `/api/v1/` prefix.

TeamPrincipal segue uma estrutura monorepo com separacao clara entre backend e frontend. O backend e uma API RESTful construida com FastAPI, e o frontend e uma aplicacao Next.js. A comunicacao acontece via HTTP/JSON pelo prefixo `/api/v1/`.

---

## High-Level Architecture / Arquitetura de Alto Nivel

```
┌─────────────────┐     ┌────────────────────────┐     ┌──────────────┐
│   Next.js 14    │────>│   FastAPI (Python 3.12) │────>│ PostgreSQL 16│
│  (Frontend)     │<────│   (Backend API)         │<────│  (Database)  │
│  NextAuth v5    │     │   SQLAlchemy 2.0 async  │     │  asyncpg     │
└─────────────────┘     └────────────────────────┘     └──────────────┘
     :3000                      :8000                       :5432
      │                          │
      │                          ├── JWT (python-jose)
      │                          ├── bcrypt (password hashing)
      │                          ├── Alembic (migrations)
      │                          └── Pydantic v2 (validation)
      │
      ├── TypeScript + Tailwind CSS
      ├── App Router (route groups)
      └── NextAuth.js v5 (session management)
```

---

## Backend Architecture / Arquitetura do Backend

The backend follows a **modular, layered architecture** organized by domain. Each module is self-contained with its own models, schemas, services, and router.

O backend segue uma **arquitetura modular em camadas** organizada por dominio. Cada modulo e autocontido com seus proprios models, schemas, services e router.

### Directory Structure / Estrutura de Diretorios

```
backend/
├── app/
│   ├── main.py              # App factory + lifespan + router registration
│   ├── config.py            # Pydantic BaseSettings (env-based config)
│   │
│   ├── db/                  # Database layer / Camada de banco de dados
│   │   ├── base.py          # SQLAlchemy DeclarativeBase
│   │   ├── session.py       # Async engine + session factory + get_db dependency
│   │   └── seed.py          # Idempotent data seeding (roles, permissions)
│   │
│   ├── core/                # Shared infrastructure / Infraestrutura compartilhada
│   │   ├── security.py      # JWT encode/decode + bcrypt hash/verify
│   │   ├── dependencies.py  # Auth chain + RBAC enforcement dependencies
│   │   └── exceptions.py    # Custom HTTP exceptions (401, 403, 404, 409)
│   │
│   ├── auth/                # Authentication module / Modulo de autenticacao
│   │   ├── router.py        # POST /login, POST /register, POST /refresh
│   │   ├── service.py       # authenticate_user, register_user, create_tokens
│   │   └── schemas.py       # LoginRequest, RegisterRequest, TokenResponse
│   │
│   ├── users/               # Users module / Modulo de usuarios
│   │   ├── router.py        # GET /me, PATCH /me, GET /{id}
│   │   ├── service.py       # get_user_by_id, update_user
│   │   ├── models.py        # User ORM model
│   │   └── schemas.py       # UserResponse, UserUpdateRequest
│   │
│   ├── roles/               # RBAC module / Modulo RBAC
│   │   ├── router.py        # 3 routers: permissions, roles, user-roles
│   │   ├── service.py       # CRUD + assignment + revocation business logic
│   │   ├── models.py        # Role, Permission, user_roles, role_permissions
│   │   └── schemas.py       # 8 Pydantic schemas
│   │
│   ├── teams/               # Teams module / Modulo de equipes
│   │   ├── router.py        # CRUD + membership endpoints (8 endpoints)
│   │   ├── service.py       # CRUD + membership business logic
│   │   ├── models.py        # Team ORM model (1:N with User, M:N with Championship)
│   │   └── schemas.py       # 7 Pydantic schemas
│   │
│   ├── championships/       # Championships module / Modulo de campeonatos
│   │   ├── router.py        # CRUD + entry endpoints (8 endpoints)
│   │   ├── service.py       # CRUD + entry management business logic
│   │   ├── models.py        # Championship model, ChampionshipStatus enum, championship_entries table
│   │   └── schemas.py       # 9 Pydantic schemas
│   │
│   ├── races/               # Races module / Modulo de corridas
│   │   ├── router.py        # CRUD + entry endpoints (8 endpoints)
│   │   ├── service.py       # CRUD + entry management business logic
│   │   ├── models.py        # Race model, RaceStatus enum, race_entries table
│   │   └── schemas.py       # 10 Pydantic schemas
│   │
│   ├── results/             # Results module / Modulo de resultados
│   │   ├── router.py        # CRUD + standings endpoints (6 endpoints)
│   │   ├── service.py       # CRUD + standings computation business logic
│   │   ├── models.py        # RaceResult model
│   │   └── schemas.py       # 8 Pydantic schemas
│   │
│   ├── dashboard/            # Dashboard module / Modulo do dashboard
│   │   ├── router.py        # GET /dashboard/summary
│   │   ├── service.py       # Aggregation queries + standings reuse
│   │   └── schemas.py       # 5 Pydantic schemas
│   │
│   ├── notifications/        # Notifications module / Modulo de notificacoes
│   │   ├── router.py        # 6 endpoints: list, unread-count, mark-read, mark-all, delete, create
│   │   ├── service.py       # CRUD + broadcast + helper functions
│   │   ├── models.py        # Notification model, NotificationType enum (native_enum=False)
│   │   └── schemas.py       # 4 Pydantic schemas
│   │
│   └── health/              # Health check module
│       └── router.py        # GET /health, GET /health/db
│
├── tests/                   # pytest test suite
│   ├── conftest.py          # Fixtures: db, client, users, auth headers
│   ├── test_auth.py         # 7 tests
│   ├── test_users.py        # 5 tests
│   ├── test_permissions.py  # 7 tests
│   ├── test_roles.py        # 13 tests
│   ├── test_rbac.py         # 12 tests
│   ├── test_user_roles.py   # 10 tests
│   ├── test_teams.py              # 19 tests
│   ├── test_team_members.py       # 14 tests
│   ├── test_championships.py      # 20 tests
│   ├── test_championship_entries.py # 13 tests
│   ├── test_races.py              # 22 tests
│   ├── test_race_entries.py       # 13 tests
│   ├── test_race_results.py       # 23 tests
│   ├── test_championship_standings.py # 9 tests
│   ├── test_drivers.py              # 30 tests
│   ├── test_dashboard.py            # 13 tests
│   ├── test_notifications.py        # 25 tests
│   └── test_health.py               # 2 tests
│
├── alembic/                 # Database migrations
│   ├── versions/            # Migration scripts
│   └── env.py               # Alembic configuration
│
└── pyproject.toml           # Poetry dependencies + tool config (ruff, mypy, pytest)
```

### Layer Responsibilities / Responsabilidades das Camadas

```
┌─────────────────────────────────────────────────────┐
│ Router (router.py)                                  │
│  - HTTP endpoint definitions                        │
│  - Request validation (Pydantic schemas)            │
│  - Dependency injection (auth, DB session)          │
│  - Response serialization (response_model)          │
├─────────────────────────────────────────────────────┤
│ Service (service.py)                                │
│  - Business logic and rules                         │
│  - Database queries (SQLAlchemy select/insert)      │
│  - Conflict/validation checks                       │
│  - Transaction management (commit/refresh)          │
├─────────────────────────────────────────────────────┤
│ Models (models.py)                                  │
│  - SQLAlchemy ORM models (Mapped[] types)           │
│  - Table definitions and constraints                │
│  - Relationships (lazy="selectin")                  │
├─────────────────────────────────────────────────────┤
│ Schemas (schemas.py)                                │
│  - Pydantic v2 BaseModel classes                    │
│  - Request body validation                          │
│  - Response serialization (from_attributes=True)    │
├─────────────────────────────────────────────────────┤
│ Core (core/)                                        │
│  - Security utilities (JWT, bcrypt)                 │
│  - FastAPI dependency factories                     │
│  - Custom exception classes                         │
├─────────────────────────────────────────────────────┤
│ Database (db/)                                      │
│  - Async engine and session management              │
│  - DeclarativeBase                                  │
│  - Seed scripts                                     │
└─────────────────────────────────────────────────────┘
```

---

## Module Structure / Estrutura de Modulos

### Router Registration / Registro de Routers

All routers are registered in `app/main.py` via `app.include_router()`:

| Router | Prefix | Source File |
|---|---|---|
| `health_router` | `/api/v1/health` | `app/health/router.py` |
| `auth_router` | `/api/v1/auth` | `app/auth/router.py` |
| `users_router` | `/api/v1/users` | `app/users/router.py` |
| `permissions_router` | `/api/v1/permissions` | `app/roles/router.py` |
| `roles_router` | `/api/v1/roles` | `app/roles/router.py` |
| `user_roles_router` | `/api/v1/users` | `app/roles/router.py` |
| `teams_router` | `/api/v1/teams` | `app/teams/router.py` |
| `championships_router` | `/api/v1/championships` | `app/championships/router.py` |
| `races_router` | `/api/v1/championships/.../races`, `/api/v1/races` | `app/races/router.py` |
| `results_router` | `/api/v1/races/.../results`, `/api/v1/results`, `/api/v1/championships/.../standings` | `app/results/router.py` |
| `drivers_router` | `/api/v1/drivers` | `app/drivers/router.py` |
| `dashboard_router` | `/api/v1/dashboard` | `app/dashboard/router.py` |
| `notifications_router` | `/api/v1/notifications` | `app/notifications/router.py` |

### Complete Endpoint Map / Mapa Completo de Endpoints

| Method | Path | Auth | Module |
|---|---|---|---|
| GET | `/api/v1/health` | None | health |
| GET | `/api/v1/health/db` | None | health |
| POST | `/api/v1/auth/register` | None | auth |
| POST | `/api/v1/auth/login` | None | auth |
| POST | `/api/v1/auth/refresh` | None | auth |
| GET | `/api/v1/users/me` | Bearer token | users |
| PATCH | `/api/v1/users/me` | Bearer token | users |
| GET | `/api/v1/users/{id}` | `users:read` | users |
| GET | `/api/v1/permissions/` | `permissions:read` | roles |
| GET | `/api/v1/permissions/{id}` | `permissions:read` | roles |
| POST | `/api/v1/permissions/` | `permissions:create` | roles |
| GET | `/api/v1/roles/` | `roles:read` | roles |
| GET | `/api/v1/roles/{id}` | `roles:read` | roles |
| POST | `/api/v1/roles/` | `roles:create` | roles |
| PATCH | `/api/v1/roles/{id}` | `roles:update` | roles |
| DELETE | `/api/v1/roles/{id}` | `roles:delete` | roles |
| POST | `/api/v1/roles/{id}/permissions` | `permissions:assign` | roles |
| DELETE | `/api/v1/roles/{id}/permissions/{pid}` | `permissions:revoke` | roles |
| GET | `/api/v1/users/{id}/roles` | `roles:read` | roles |
| POST | `/api/v1/users/{id}/roles` | `roles:assign` | roles |
| DELETE | `/api/v1/users/{id}/roles/{rid}` | `roles:revoke` | roles |
| GET | `/api/v1/teams/` | `teams:read` | teams |
| GET | `/api/v1/teams/{id}` | `teams:read` | teams |
| POST | `/api/v1/teams/` | `teams:create` | teams |
| PATCH | `/api/v1/teams/{id}` | `teams:update` | teams |
| DELETE | `/api/v1/teams/{id}` | `teams:delete` | teams |
| GET | `/api/v1/teams/{id}/members` | `teams:read` | teams |
| POST | `/api/v1/teams/{id}/members` | `teams:manage_members` | teams |
| DELETE | `/api/v1/teams/{id}/members/{uid}` | `teams:manage_members` | teams |
| GET | `/api/v1/championships/` | `championships:read` | championships |
| GET | `/api/v1/championships/{id}` | `championships:read` | championships |
| POST | `/api/v1/championships/` | `championships:create` | championships |
| PATCH | `/api/v1/championships/{id}` | `championships:update` | championships |
| DELETE | `/api/v1/championships/{id}` | `championships:delete` | championships |
| GET | `/api/v1/championships/{id}/entries` | `championships:read` | championships |
| POST | `/api/v1/championships/{id}/entries` | `championships:manage_entries` | championships |
| DELETE | `/api/v1/championships/{id}/entries/{tid}` | `championships:manage_entries` | championships |
| GET | `/api/v1/championships/{id}/races` | `races:read` | races |
| POST | `/api/v1/championships/{id}/races` | `races:create` | races |
| GET | `/api/v1/races/{id}` | `races:read` | races |
| PATCH | `/api/v1/races/{id}` | `races:update` | races |
| DELETE | `/api/v1/races/{id}` | `races:delete` | races |
| GET | `/api/v1/races/{id}/entries` | `races:read` | races |
| POST | `/api/v1/races/{id}/entries` | `races:manage_entries` | races |
| DELETE | `/api/v1/races/{id}/entries/{tid}` | `races:manage_entries` | races |
| GET | `/api/v1/races/{id}/results` | `results:read` | results |
| POST | `/api/v1/races/{id}/results` | `results:create` | results |
| GET | `/api/v1/results/{id}` | `results:read` | results |
| PATCH | `/api/v1/results/{id}` | `results:update` | results |
| DELETE | `/api/v1/results/{id}` | `results:delete` | results |
| GET | `/api/v1/championships/{id}/standings` | `results:read` | results |
| GET | `/api/v1/drivers/` | `drivers:read` | drivers |
| GET | `/api/v1/drivers/{id}` | `drivers:read` | drivers |
| POST | `/api/v1/drivers/` | `drivers:create` | drivers |
| PATCH | `/api/v1/drivers/{id}` | `drivers:update` | drivers |
| DELETE | `/api/v1/drivers/{id}` | `drivers:delete` | drivers |
| GET | `/api/v1/dashboard/summary` | `championships:read` + `results:read` | dashboard |
| GET | `/api/v1/notifications/` | Authenticated | notifications |
| GET | `/api/v1/notifications/unread-count` | Authenticated | notifications |
| PATCH | `/api/v1/notifications/{id}/read` | Authenticated | notifications |
| POST | `/api/v1/notifications/mark-all-read` | Authenticated | notifications |
| DELETE | `/api/v1/notifications/{id}` | Authenticated | notifications |
| POST | `/api/v1/notifications/` | `notifications:create` | notifications |

---

## Authentication & Authorization Flow / Fluxo de Autenticacao & Autorizacao

### JWT Token Flow / Fluxo de Tokens JWT

```
1. POST /api/v1/auth/login (email + password)
   │
   ▼
2. Server validates credentials (bcrypt.checkpw)
   │
   ▼
3. Server returns:
   ├── access_token  (JWT, exp: 30 min, type: "access")
   └── refresh_token (JWT, exp: 7 days, type: "refresh")
   │
   ▼
4. Client sends: Authorization: Bearer <access_token>
   │
   ▼
5. Server decodes JWT (python-jose)
   ├── Extracts "sub" (user UUID as string)
   ├── Validates "type" == "access"
   └── Queries User from DB by UUID
   │
   ▼
6. RBAC enforcement:
   ├── get_current_active_user (checks is_active)
   └── require_permissions/require_role (checks permissions/roles)
```

### Token Payload / Payload do Token

**Access Token:**
```json
{
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "exp": 1700000000,
    "type": "access"
}
```

**Refresh Token:**
```json
{
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "exp": 1700604800,
    "type": "refresh"
}
```

### RBAC Dependency Chain / Cadeia de Dependencias RBAC

```python
# Simplified dependency chain:
OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
  → get_current_user(token, db)          # Decodes JWT, queries User
    → get_current_active_user(user)      # Checks is_active
      → require_permissions(*codenames)  # AND logic, superuser bypass
      → require_role(*role_names)        # OR logic, superuser bypass
```

---

## Database Schema / Esquema do Banco de Dados

### Core Tables / Tabelas Principais

```
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│     users        │        │      roles       │        │   permissions    │
├─────────────────┤        ├─────────────────┤        ├─────────────────┤
│ id          PK  │◄──┐    │ id          PK  │◄──┐    │ id          PK  │
│ email       UQ  │   │    │ name        UQ  │   │    │ codename    UQ  │
│ hashed_pw       │   │    │ display_name    │   │    │ description     │
│ full_name       │   │    │ description     │   │    │ module      IDX │
│ is_active       │   │    │ is_system       │   │    │ created_at      │
│ is_superuser    │   │    │ created_at      │   │    │ updated_at      │
│ avatar_url      │   │    │ updated_at      │   │    └────────┬────────┘
│ team_id FK  IDX │───┐    └────────┬────────┘   │             │
│ created_at      │   │             │             │             │
│ updated_at      │   │             │             │             │
└────────┬────────┘   │    ┌────────┴────────┐   │    ┌────────┴────────┐
         │            │    │   user_roles     │   │    │role_permissions │
         │            │    ├─────────────────┤   │    ├─────────────────┤
         └────────────┼───>│ user_id     PK  │   │    │ role_id     PK  │
                      │    │ role_id     PK  │───┘    │ permission_id PK│
                      │    │ assigned_at     │        └─────────────────┘
                      └────│ assigned_by FK  │
                           └─────────────────┘

┌─────────────────┐
│      teams       │
├─────────────────┤
│ id          PK  │◄── users.team_id (SET NULL)
│ name        UQ  │
│ display_name    │
│ description     │
│ logo_url        │
│ is_active       │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ teams.id (PK)
         │
┌────────┴────────────────┐
│  championship_entries    │
├─────────────────────────┤
│ championship_id  PK FK  │──→ championships.id (CASCADE)
│ team_id          PK FK  │──→ teams.id (CASCADE)
│ registered_at           │
└────────┬────────────────┘
         │
         │ championships.id (PK)
         │
┌────────┴────────┐
│  championships   │
├─────────────────┤
│ id          PK  │
│ name        UQ  │
│ display_name    │
│ description     │
│ season_year     │
│ status          │ planned/active/completed/cancelled
│ start_date      │
│ end_date        │
│ is_active       │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ championships.id (FK)
         │
┌────────┴────────┐
│     races        │
├─────────────────┤
│ id          PK  │
│ champ_id    FK  │ UQ(championship_id, name)
│ name        IDX │
│ display_name    │
│ description     │
│ round_number    │
│ status          │ scheduled/qualifying/active/finished/cancelled
│ scheduled_at    │
│ track_name      │
│ track_country   │
│ laps_total      │
│ is_active       │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ races.id (PK)
         │
┌────────┴────────────────┐
│     race_entries         │
├─────────────────────────┤
│ race_id      PK FK      │──→ races.id (CASCADE)
│ team_id      PK FK      │──→ teams.id (CASCADE)
│ registered_at           │
└─────────────────────────┘

┌─────────────────────────┐
│     race_results         │
├─────────────────────────┤
│ id           PK          │
│ race_id      FK IDX      │──→ races.id (CASCADE)
│ team_id      FK IDX      │──→ teams.id (CASCADE)
│ position     INT         │
│ points       FLOAT       │ default 0.0
│ laps_completed INT       │ nullable
│ fastest_lap  BOOL        │ default false
│ dnf          BOOL        │ default false
│ dsq          BOOL        │ default false
│ notes        VARCHAR(512)│ nullable
│ created_at               │
│ updated_at               │
├─────────────────────────┤
│ UQ(race_id, team_id)    │
└─────────────────────────┘

┌─────────────────────────┐
│     notifications        │
├─────────────────────────┤
│ id           PK          │
│ user_id      FK IDX      │──→ users.id (CASCADE)
│ type         ENUM        │ race_scheduled/result_published/team_invite/championship_update/general
│ title        VARCHAR(256)│
│ message      TEXT         │
│ entity_type  VARCHAR(64) │ nullable (race/championship/team)
│ entity_id    UUID        │ nullable
│ is_read      BOOL        │ default false
│ created_at               │
│ updated_at               │
└─────────────────────────┘
```

### Conventions / Convencoes

- **Primary keys:** UUID (`sqlalchemy.Uuid` — generic, not PostgreSQL-specific)
- **Timestamps:** `DateTime(timezone=True)` with `server_default=func.now()`
- **Naming:** snake_case for all tables and columns
- **Cascading:** `ondelete="CASCADE"` on association table FKs, `ondelete="SET NULL"` on optional FKs (e.g., `users.team_id`)
- **Lazy loading:** `lazy="selectin"` for all relationships (eager loading)
- **String limits:** email(320), name(64/128/256), description(512), codename(128)

---

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
│   │   ├── dashboard/
│   │   ├── championships/  # List, detail, create, edit pages
│   │   ├── races/          # Detail, edit pages (list/create under championships)
│   │   └── notifications/  # Notifications list with filters and actions
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

---

## Key Technical Decisions / Decisoes Tecnicas Chave

| Decision / Decisao | Choice / Escolha | Rationale / Justificativa |
|---|---|---|
| ORM | SQLAlchemy 2.0 async | Full async support, complex RBAC relationships, Mapped[] type hints |
| Migrations | Alembic | Standard for SQLAlchemy, version-controlled schema changes |
| Auth | JWT (python-jose) | Stateless, standard for API-based auth, refresh token rotation |
| Password hashing | bcrypt (direct) | passlib is incompatible with bcrypt >= 4.x. See [troubleshooting](troubleshooting.md#5-bcrypt--passlib-incompatibility) |
| Primary Keys | UUID (generic `Uuid`) | Distributed-friendly, avoids PostgreSQL dialect lock-in for tests |
| API Versioning | URL prefix `/api/v1/` | Simple, explicit, easy to evolve |
| RBAC model | Permissions AND, Roles OR | AND ensures all required permissions; OR provides flexible role matching |
| Test DB | SQLite in-memory | Fast tests, no external dependencies, generic `Uuid` type compatibility |
| Lazy loading | `selectin` | Prevents N+1 queries for relationships |
| Linting | Ruff (lint + format) | Fast, replaces flake8 + isort + black |
| Type checking | mypy strict | Maximum type safety with Pydantic plugin |

---

## Testing Strategy / Estrategia de Testes

### Test Pyramid / Piramide de Testes

```
┌───────────────────┐
│ Integration (257) │  ← httpx AsyncClient against test app
│  (API-level)      │    Tests full request/response cycle
├───────────────────┤
│  Unit (implicit)  │  ← Service functions tested via API
│                   │    No separate unit test layer yet
└───────────────────┘
```

### Test Infrastructure / Infraestrutura de Testes

- **Framework:** pytest 8 + pytest-asyncio 0.24
- **HTTP Client:** httpx AsyncClient (async-native)
- **Database:** In-memory SQLite (`sqlite+aiosqlite://`) — fresh schema per test via `Base.metadata.create_all()`
- **Async mode:** `asyncio_mode = "auto"` (no need for `@pytest.mark.asyncio`)

### Fixture Hierarchy / Hierarquia de Fixtures

```
db (AsyncSession)
  └── client (AsyncClient)
        ├── test_user + auth_headers      (regular user)
        ├── admin_user + admin_headers    (user with admin role + all permissions)
        └── superuser + superuser_headers (is_superuser=True, bypasses all)
```

---

## Infrastructure / Infraestrutura

### Development / Desenvolvimento

- **Docker Compose:** PostgreSQL + Backend + Frontend
- **Hot-reload:** Enabled for both backend (`uvicorn --reload`) and frontend (`next dev`)
- **API docs:** Swagger UI at `http://localhost:8000/docs`

### CI/CD

- **GitHub Actions:** Separate workflows for backend and frontend
- **Backend CI:** `ruff check` → `mypy --strict` → `pytest`
- **Frontend CI:** `npm run lint` → `npm run build`

### Production / Producao (future / futuro)

- AWS ECS/EC2 for compute
- AWS S3 for file storage
- AWS RDS for managed PostgreSQL
