# Teams API Reference / Referencia da API de Equipes

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [Data Model / Modelo de Dados](#data-model--modelo-de-dados)
3. [Business Rules / Regras de Negocio](#business-rules--regras-de-negocio)
4. [Permissions / Permissoes](#permissions--permissoes)
5. [Pydantic Schemas / Schemas Pydantic](#pydantic-schemas--schemas-pydantic)
6. [API Endpoints — Teams CRUD](#api-endpoints--teams-crud)
7. [API Endpoints — Team Membership](#api-endpoints--team-membership)
8. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
9. [Service Layer / Camada de Servico](#service-layer--camada-de-servico)
10. [Database Migrations / Migracoes de Banco](#database-migrations--migracoes-de-banco)
11. [Test Coverage / Cobertura de Testes](#test-coverage--cobertura-de-testes)

---

## Overview / Visao Geral

The Teams module provides racing team management with full CRUD operations and membership control. Each user can belong to at most **one team** (1:N relationship via `team_id` FK on `users`). Team roles are managed through the existing RBAC system — there are no separate roles within a team.

O modulo de Equipes fornece gerenciamento de equipes de corrida com operacoes CRUD completas e controle de membros. Cada usuario pode pertencer a no maximo **uma equipe** (relacionamento 1:N via FK `team_id` em `users`). Os papeis dentro da equipe sao gerenciados pelo sistema RBAC existente — nao ha papeis separados dentro da equipe.

### Key Files / Arquivos Chave

| File / Arquivo | Purpose / Proposito |
|---|---|
| `app/teams/models.py` | ORM model: `Team` with `members` relationship |
| `app/teams/schemas.py` | 7 Pydantic schemas (request/response) |
| `app/teams/service.py` | Business logic: CRUD + membership management |
| `app/teams/router.py` | API endpoint definitions (8 endpoints) |
| `alembic/versions/002_create_teams_table.py` | Migration: `teams` table |
| `alembic/versions/003_add_team_id_to_users.py` | Migration: `team_id` FK on `users` |

---

## Data Model / Modelo de Dados

### Entity Relationship Diagram / Diagrama de Entidade-Relacionamento

```
┌──────────────────────────┐
│          teams            │
├──────────────────────────┤
│ id           UUID PK      │
│ name         VARCHAR(64)  │ UNIQUE, INDEXED
│ display_name VARCHAR(128) │
│ description  VARCHAR(512) │ nullable
│ logo_url     VARCHAR(2048)│ nullable
│ is_active    BOOLEAN      │ default: true
│ created_at   TIMESTAMPTZ  │
│ updated_at   TIMESTAMPTZ  │
└──────────┬───────────────┘
           │
           │ teams.id (PK)
           │
┌──────────┴───────────────┐
│          users            │
├──────────────────────────┤
│ ...                       │
│ team_id    UUID FK        │──→ teams.id (SET NULL)
│ ...                       │    nullable, INDEXED
└──────────────────────────┘
```

### Relationship / Relacionamento

The relationship is **1:N** — one team has many users, each user belongs to at most one team.

O relacionamento e **1:N** — uma equipe tem muitos usuarios, cada usuario pertence a no maximo uma equipe.

```python
# Team → User (one-to-many)
Team.members ←→ User.team    # via users.team_id FK
```

Both sides use `lazy="selectin"` for eager loading.

Ambos os lados usam `lazy="selectin"` para carregamento antecipado.

### Foreign Key Behavior / Comportamento da FK

| Event / Evento | Behavior / Comportamento |
|---|---|
| Team deleted | `team_id` set to `NULL` on all members (service-level + `ondelete=SET NULL`) |
| User deleted | No cascade needed (user row is removed) |

**Defense in depth / Defesa em profundidade:** The `delete_team` service explicitly nullifies `team_id` for all members before deleting the team, even though the DB-level `ondelete=SET NULL` would handle it. This ensures consistent behavior across all database backends (including SQLite in tests).

O servico `delete_team` anula explicitamente o `team_id` de todos os membros antes de excluir a equipe, mesmo que o `ondelete=SET NULL` do banco trate isso. Garante comportamento consistente em todos os backends (incluindo SQLite nos testes).

---

## Business Rules / Regras de Negocio

### 1. One Team Per User / Uma Equipe por Usuario

A user can belong to at most one team. The `add_member` service enforces this:

Um usuario pode pertencer a no maximo uma equipe. O servico `add_member` garante isso:

| Condition / Condicao | Result / Resultado |
|---|---|
| `user.team_id is None` | User is added to the team |
| `user.team_id == team_id` | **409** — "User is already a member of this team" |
| `user.team_id != team_id` | **409** — "User already belongs to another team" |

### 2. Team Name Immutability / Imutabilidade do Nome

The `name` field (unique slug) is set at creation and **cannot be updated**. Only `display_name`, `description`, `logo_url`, and `is_active` are updatable via PATCH.

O campo `name` (slug unico) e definido na criacao e **nao pode ser atualizado**. Apenas `display_name`, `description`, `logo_url` e `is_active` sao atualizaveis via PATCH.

### 3. Team Deletion Cascading / Cascata na Exclusao

When a team is deleted:
1. All members have their `team_id` set to `NULL` (service-level)
2. The team row is deleted

Quando uma equipe e excluida:
1. Todos os membros tem seu `team_id` definido como `NULL` (nivel de servico)
2. A linha da equipe e excluida

---

## Permissions / Permissoes

5 permissions in the `teams` module, seeded by `app/db/seed.py`:

5 permissoes no modulo `teams`, populadas por `app/db/seed.py`:

| Codename | Description / Descricao | Used By / Usado Por |
|---|---|---|
| `teams:read` | Read teams and members / Ler equipes e membros | GET endpoints |
| `teams:create` | Create teams / Criar equipes | POST `/api/v1/teams/` |
| `teams:update` | Update teams / Atualizar equipes | PATCH `/api/v1/teams/{id}` |
| `teams:delete` | Delete teams / Excluir equipes | DELETE `/api/v1/teams/{id}` |
| `teams:manage_members` | Add/remove members / Adicionar/remover membros | POST/DELETE `.../members` |

### Default Role Assignments / Atribuicoes Padrao

| Role / Papel | Teams Permissions / Permissoes de Equipes |
|---|---|
| `admin` | All 5 (`teams:read`, `teams:create`, `teams:update`, `teams:delete`, `teams:manage_members`) |
| `pilot` | `teams:read` |
| Others / Outros | None (configure as needed / configure conforme necessario) |

---

## Pydantic Schemas / Schemas Pydantic

Defined in `app/teams/schemas.py`. All response schemas use `model_config = {"from_attributes": True}`.

### Request Schemas / Schemas de Requisicao

**`TeamCreateRequest`**
```json
{
    "name": "red_bull_racing",
    "display_name": "Oracle Red Bull Racing",
    "description": "Milton Keynes-based team",
    "logo_url": "https://example.com/redbull.png"
}
```
- `name` and `display_name` are required / `name` e `display_name` sao obrigatorios
- `description` and `logo_url` are optional (default `null`) / `description` e `logo_url` sao opcionais

**`TeamUpdateRequest`** (all fields optional / todos os campos opcionais)
```json
{
    "display_name": "Oracle Red Bull Racing",
    "description": "Updated description",
    "logo_url": "https://example.com/new-logo.png",
    "is_active": false
}
```
- `name` is **not updatable** / `name` **nao e atualizavel**

**`TeamAddMemberRequest`**
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Response Schemas / Schemas de Resposta

**`TeamListResponse`** (used in list endpoint — lightweight, no `logo_url` or `members`)
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "red_bull_racing",
    "display_name": "Oracle Red Bull Racing",
    "description": "Milton Keynes-based team",
    "is_active": true,
    "created_at": "2026-02-18T00:00:00Z",
    "updated_at": "2026-02-18T00:00:00Z"
}
```

**`TeamResponse`** (used in create/update — includes `logo_url`, no `members`)
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "red_bull_racing",
    "display_name": "Oracle Red Bull Racing",
    "description": "Milton Keynes-based team",
    "logo_url": "https://example.com/redbull.png",
    "is_active": true,
    "created_at": "2026-02-18T00:00:00Z",
    "updated_at": "2026-02-18T00:00:00Z"
}
```

**`TeamDetailResponse`** (used in GET by ID — includes `logo_url` + `members`)
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "red_bull_racing",
    "display_name": "Oracle Red Bull Racing",
    "description": "Milton Keynes-based team",
    "logo_url": "https://example.com/redbull.png",
    "is_active": true,
    "members": [
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "email": "max@example.com",
            "full_name": "Max Verstappen",
            "is_active": true,
            "avatar_url": null
        }
    ],
    "created_at": "2026-02-18T00:00:00Z",
    "updated_at": "2026-02-18T00:00:00Z"
}
```

**`TeamMemberResponse`** (used in membership endpoints)
```json
{
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "email": "max@example.com",
    "full_name": "Max Verstappen",
    "is_active": true,
    "avatar_url": null
}
```

---

## API Endpoints — Teams CRUD

### `GET /api/v1/teams/`

List all teams. Supports optional filtering by active status.

Lista todas as equipes. Suporta filtragem opcional por status ativo.

| Parameter | Type | Description |
|---|---|---|
| `is_active` | `bool` (query, optional) | Filter by active status / Filtrar por status ativo |

**Permission:** `teams:read`
**Response:** `200` — `list[TeamListResponse]`

```bash
# List all teams / Listar todas as equipes
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/teams/

# Filter active only / Filtrar apenas ativas
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/teams/?is_active=true
```

### `GET /api/v1/teams/{team_id}`

Get a team by ID with its members list.

Busca uma equipe por ID com lista de membros.

**Permission:** `teams:read`
**Response:** `200` — `TeamDetailResponse` (includes `members[]`)
**Error:** `404` — Team not found

### `POST /api/v1/teams/`

Create a new team.

Cria uma nova equipe.

**Permission:** `teams:create`
**Request Body:** `TeamCreateRequest`
**Response:** `201` — `TeamResponse`
**Error:** `409` — Team name already exists

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "mclaren", "display_name": "McLaren Racing"}' \
  http://localhost:8000/api/v1/teams/
```

### `PATCH /api/v1/teams/{team_id}`

Update a team's fields. Only provided fields are updated.

Atualiza campos de uma equipe. Apenas campos fornecidos sao atualizados.

**Permission:** `teams:update`
**Request Body:** `TeamUpdateRequest`
**Response:** `200` — `TeamResponse`
**Error:** `404` — Team not found

```bash
curl -X PATCH -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Oracle Red Bull Racing", "is_active": false}' \
  http://localhost:8000/api/v1/teams/{team_id}
```

### `DELETE /api/v1/teams/{team_id}`

Delete a team. All members have their `team_id` set to `NULL`.

Exclui uma equipe. Todos os membros tem seu `team_id` definido como `NULL`.

**Permission:** `teams:delete`
**Response:** `204` — No content
**Error:** `404` — Team not found

---

## API Endpoints — Team Membership

### `GET /api/v1/teams/{team_id}/members`

List all members of a team.

Lista todos os membros de uma equipe.

**Permission:** `teams:read`
**Response:** `200` — `list[TeamMemberResponse]`
**Error:** `404` — Team not found

### `POST /api/v1/teams/{team_id}/members`

Add a user to a team.

Adiciona um usuario a uma equipe.

**Permission:** `teams:manage_members`
**Request Body:** `TeamAddMemberRequest`
**Response:** `200` — `list[TeamMemberResponse]` (updated members list)
**Errors:**
- `404` — Team not found / User not found
- `409` — User is already a member of this team
- `409` — User already belongs to another team

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "550e8400-e29b-41d4-a716-446655440000"}' \
  http://localhost:8000/api/v1/teams/{team_id}/members
```

### `DELETE /api/v1/teams/{team_id}/members/{user_id}`

Remove a user from a team.

Remove um usuario de uma equipe.

**Permission:** `teams:manage_members`
**Response:** `200` — `list[TeamMemberResponse]` (updated members list)
**Errors:**
- `404` — Team not found / User not found
- `404` — User is not a member of this team

---

## Error Responses / Respostas de Erro

All errors follow the standard FastAPI format. All error responses use the same HTTP exception classes from `app/core/exceptions.py`.

Todos os erros seguem o formato padrao do FastAPI.

| Status | Exception | Description / Descricao |
|---|---|---|
| `401` | `CredentialsException` | Missing or invalid JWT token / Token JWT ausente ou invalido |
| `403` | `ForbiddenException` | Missing required permission / Permissao necessaria ausente |
| `404` | `NotFoundException` | Team or user not found / Equipe ou usuario nao encontrado |
| `409` | `ConflictException` | Duplicate team name or membership conflict / Nome duplicado ou conflito de membro |

### Example Error Responses / Exemplos de Erro

**404 — Team not found**
```json
{"detail": "Team not found"}
```

**409 — Duplicate name**
```json
{"detail": "Team name already exists"}
```

**409 — Already a member**
```json
{"detail": "User is already a member of this team"}
```

**409 — Belongs to another team**
```json
{"detail": "User already belongs to another team"}
```

**403 — Missing permission**
```json
{"detail": "Missing permissions: teams:manage_members"}
```

---

## Service Layer / Camada de Servico

All business logic is in `app/teams/service.py`. Functions follow the same async pattern as other modules.

Toda a logica de negocios esta em `app/teams/service.py`. As funcoes seguem o mesmo padrao async dos outros modulos.

### CRUD Functions / Funcoes CRUD

| Function | Description / Descricao |
|---|---|
| `list_teams(db, is_active?)` | List teams, optionally filtered by active status |
| `get_team_by_id(db, team_id)` | Get team by ID; raises `404` if not found |
| `create_team(db, name, display_name, description?, logo_url?)` | Create team; raises `409` if name exists |
| `update_team(db, team, display_name?, description?, logo_url?, is_active?)` | Update provided fields only |
| `delete_team(db, team)` | Nullify members' `team_id`, then delete team |

### Membership Functions / Funcoes de Membros

| Function | Description / Descricao |
|---|---|
| `list_team_members(db, team_id)` | List team members via `team.members` relationship |
| `add_member(db, team_id, user_id)` | Add user; raises `404` (user/team) or `409` (already in a team) |
| `remove_member(db, team_id, user_id)` | Remove user; raises `404` if not a member |

---

## Database Migrations / Migracoes de Banco

### 002 — Create Teams Table

**File:** `alembic/versions/002_create_teams_table.py`
**Revision:** `002` (depends on `001`)

Creates the `teams` table with:
- UUID PK with `gen_random_uuid()` server default
- `name` — `VARCHAR(64)`, unique, indexed
- `display_name` — `VARCHAR(128)`
- `description` — `VARCHAR(512)`, nullable
- `logo_url` — `VARCHAR(2048)`, nullable
- `is_active` — `BOOLEAN`, default `true`
- `created_at`, `updated_at` — `TIMESTAMPTZ`

Constraints: `pk_teams`, `uq_teams_name`, `ix_teams_name`

### 003 — Add team_id to Users

**File:** `alembic/versions/003_add_team_id_to_users.py`
**Revision:** `003` (depends on `002`)

Adds to the `users` table:
- `team_id` — `UUID FK` → `teams.id`, nullable, `ondelete=SET NULL`
- Index: `ix_users_team_id`

---

## Test Coverage / Cobertura de Testes

33 tests total across 2 test files.

33 testes no total em 2 arquivos de teste.

### `tests/test_teams.py` — 19 tests

| Test | Status | Description |
|---|---|---|
| `test_list_teams_empty` | 200 | Empty list when no teams |
| `test_list_teams_with_data` | 200 | Returns teams without `logo_url` |
| `test_list_teams_filter_active` | 200 | Filters active teams only |
| `test_list_teams_filter_inactive` | 200 | Filters inactive teams only |
| `test_get_team_by_id` | 200 | Returns team with all fields |
| `test_get_team_not_found` | 404 | Invalid ID returns 404 |
| `test_create_team_full` | 201 | Creates with all fields |
| `test_create_team_minimal` | 201 | Creates with required fields only |
| `test_create_team_duplicate` | 409 | Duplicate name returns 409 |
| `test_update_team_display_name` | 200 | Updates display_name |
| `test_update_team_description` | 200 | Updates description |
| `test_update_team_deactivate` | 200 | Deactivates team |
| `test_update_team_not_found` | 404 | Invalid ID returns 404 |
| `test_delete_team` | 204 | Deletes team, confirms 404 after |
| `test_delete_team_not_found` | 404 | Invalid ID returns 404 |
| `test_list_teams_unauthorized` | 401 | No token returns 401 |
| `test_create_team_forbidden` | 403 | No permission returns 403 |
| `test_admin_can_list` | 200 | Admin with `teams:read` can list |
| `test_admin_can_create` | 201 | Admin with `teams:create` can create |

### `tests/test_team_members.py` — 14 tests

| Test | Status | Description |
|---|---|---|
| `test_list_members_empty` | 200 | Empty members list |
| `test_list_members_team_not_found` | 404 | Invalid team ID |
| `test_add_member` | 200 | Adds member successfully |
| `test_add_member_duplicate_same_team` | 409 | Already a member of this team |
| `test_add_member_already_in_other_team` | 409 | Belongs to another team |
| `test_add_member_user_not_found` | 404 | Non-existent user |
| `test_add_member_team_not_found` | 404 | Non-existent team |
| `test_remove_member` | 200 | Removes member successfully |
| `test_remove_non_member` | 404 | User not in team |
| `test_remove_user_not_found` | 404 | Non-existent user |
| `test_delete_team_nullifies_members` | 204 | Deleting team nullifies `team_id` |
| `test_get_team_detail_includes_members` | 200 | GET detail includes members |
| `test_add_member_forbidden` | 403 | No `teams:manage_members` |
| `test_remove_member_forbidden` | 403 | No `teams:manage_members` |
