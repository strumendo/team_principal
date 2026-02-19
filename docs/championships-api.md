# Championships API Reference / Referencia da API de Campeonatos

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [Data Model / Modelo de Dados](#data-model--modelo-de-dados)
3. [Business Rules / Regras de Negocio](#business-rules--regras-de-negocio)
4. [Permissions / Permissoes](#permissions--permissoes)
5. [Pydantic Schemas / Schemas Pydantic](#pydantic-schemas--schemas-pydantic)
6. [API Endpoints — Championships CRUD](#api-endpoints--championships-crud)
7. [API Endpoints — Championship Entries](#api-endpoints--championship-entries)
8. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
9. [Service Layer / Camada de Servico](#service-layer--camada-de-servico)
10. [Database Migrations / Migracoes de Banco](#database-migrations--migracoes-de-banco)
11. [Test Coverage / Cobertura de Testes](#test-coverage--cobertura-de-testes)

---

## Overview / Visao Geral

The Championships module provides racing championship / season management with full CRUD operations and team enrollment (M:N relationship via `championship_entries` association table). Championships track seasons with status lifecycle (planned → active → completed / cancelled).

O modulo de Campeonatos fornece gerenciamento de campeonatos / temporadas de corrida com operacoes CRUD completas e inscricao de equipes (relacionamento M:N via tabela associativa `championship_entries`). Os campeonatos rastreiam temporadas com ciclo de vida de status (planned → active → completed / cancelled).

### Key Files / Arquivos Chave

| File / Arquivo | Purpose / Proposito |
|---|---|
| `app/championships/models.py` | ORM model: `Championship`, `ChampionshipStatus` enum, `championship_entries` table |
| `app/championships/schemas.py` | 9 Pydantic schemas (request/response) |
| `app/championships/service.py` | Business logic: CRUD + entry management |
| `app/championships/router.py` | API endpoint definitions (8 endpoints) |
| `alembic/versions/004_create_championships_table.py` | Migration: `championships` table |
| `alembic/versions/005_create_championship_entries_table.py` | Migration: `championship_entries` table |

---

## Data Model / Modelo de Dados

### Entity Relationship Diagram / Diagrama de Entidade-Relacionamento

```
┌──────────────────────────────┐
│        championships          │
├──────────────────────────────┤
│ id            UUID PK         │
│ name          VARCHAR(64)     │ UNIQUE, INDEXED
│ display_name  VARCHAR(128)    │
│ description   VARCHAR(512)    │ nullable
│ season_year   INTEGER         │
│ status        VARCHAR(20)     │ planned/active/completed/cancelled
│ start_date    DATE            │ nullable
│ end_date      DATE            │ nullable
│ is_active     BOOLEAN         │ default: true
│ created_at    TIMESTAMPTZ     │
│ updated_at    TIMESTAMPTZ     │
└──────────┬───────────────────┘
           │
           │ championships.id (PK)
           │
┌──────────┴───────────────────┐
│    championship_entries       │
├──────────────────────────────┤
│ championship_id  UUID PK FK  │──→ championships.id (CASCADE)
│ team_id          UUID PK FK  │──→ teams.id (CASCADE)
│ registered_at    TIMESTAMPTZ │ server_default=now()
└──────────┬───────────────────┘
           │
           │ teams.id (PK)
           │
┌──────────┴───────────────────┐
│          teams                │
├──────────────────────────────┤
│ id            UUID PK         │
│ name          VARCHAR(64)     │
│ ...                           │
└──────────────────────────────┘
```

### Relationships / Relacionamentos

The relationship is **M:N** — one championship has many teams, one team can be enrolled in many championships.

O relacionamento e **M:N** — um campeonato tem muitas equipes, uma equipe pode estar inscrita em muitos campeonatos.

```python
# Championship ←→ Team (many-to-many via championship_entries)
Championship.teams ←→ Team.championships   # via championship_entries
```

Both sides use `lazy="selectin"` for eager loading.

Ambos os lados usam `lazy="selectin"` para carregamento antecipado.

### ChampionshipStatus Enum

```python
class ChampionshipStatus(str, enum.Enum):
    planned = "planned"      # Not yet started / Ainda nao iniciado
    active = "active"        # Currently running / Em andamento
    completed = "completed"  # Finished / Finalizado
    cancelled = "cancelled"  # Cancelled / Cancelado
```

Uses `native_enum=False` — stored as `VARCHAR(20)` for SQLite test compatibility.

Usa `native_enum=False` — armazenado como `VARCHAR(20)` para compatibilidade com SQLite nos testes.

### Foreign Key Behavior / Comportamento da FK

| Event / Evento | Behavior / Comportamento |
|---|---|
| Championship deleted | Entries cleared via ORM (`championship.teams.clear()`) before deletion |
| Team deleted | `ondelete=CASCADE` removes entries from `championship_entries` |

---

## Business Rules / Regras de Negocio

### 1. Championship Name Immutability / Imutabilidade do Nome

The `name` field (unique slug) is set at creation and **cannot be updated**. Only `display_name`, `description`, `season_year`, `status`, `start_date`, `end_date`, and `is_active` are updatable via PATCH.

O campo `name` (slug unico) e definido na criacao e **nao pode ser atualizado**. Apenas `display_name`, `description`, `season_year`, `status`, `start_date`, `end_date` e `is_active` sao atualizaveis via PATCH.

### 2. One Enrollment Per Team-Championship / Uma Inscricao por Equipe-Campeonato

A team can only be enrolled once per championship. The `add_championship_entry` service enforces this:

Uma equipe so pode ser inscrita uma vez por campeonato. O servico `add_championship_entry` garante isso:

| Condition / Condicao | Result / Resultado |
|---|---|
| No existing entry | Team is added to the championship |
| Entry already exists | **409** — "Team is already enrolled in this championship" |

### 3. Championship Deletion Cascading / Cascata na Exclusao

When a championship is deleted:
1. All entries are cleared via ORM (`championship.teams.clear()`)
2. The championship row is deleted

Quando um campeonato e excluido:
1. Todas as inscricoes sao limpas via ORM (`championship.teams.clear()`)
2. A linha do campeonato e excluida

---

## Permissions / Permissoes

5 permissions in the `championships` module, seeded by `app/db/seed.py`:

5 permissoes no modulo `championships`, populadas por `app/db/seed.py`:

| Codename | Description / Descricao | Used By / Usado Por |
|---|---|---|
| `championships:read` | Read championships and entries / Ler campeonatos e inscricoes | GET endpoints |
| `championships:create` | Create championships / Criar campeonatos | POST `/api/v1/championships/` |
| `championships:update` | Update championships / Atualizar campeonatos | PATCH `/api/v1/championships/{id}` |
| `championships:delete` | Delete championships / Excluir campeonatos | DELETE `/api/v1/championships/{id}` |
| `championships:manage_entries` | Add/remove entries / Adicionar/remover inscricoes | POST/DELETE `.../entries` |

### Default Role Assignments / Atribuicoes Padrao

| Role / Papel | Championships Permissions / Permissoes de Campeonatos |
|---|---|
| `admin` | All 5 (`championships:read/create/update/delete/manage_entries`) |
| `pilot` | `championships:read` |
| Others / Outros | None (configure as needed / configure conforme necessario) |

---

## Pydantic Schemas / Schemas Pydantic

Defined in `app/championships/schemas.py`. All response schemas use `model_config = {"from_attributes": True}`.

### Request Schemas / Schemas de Requisicao

**`ChampionshipCreateRequest`**
```json
{
    "name": "formula_e_2026",
    "display_name": "Formula E 2026",
    "description": "Electric racing championship",
    "season_year": 2026,
    "status": "planned",
    "start_date": "2026-03-01",
    "end_date": "2026-11-30"
}
```
- `name`, `display_name`, `season_year` are required / sao obrigatorios
- `description`, `status`, `start_date`, `end_date` are optional / sao opcionais
- `status` defaults to `"planned"` / padrao e `"planned"`

**`ChampionshipUpdateRequest`** (all fields optional / todos os campos opcionais)
```json
{
    "display_name": "Formula E Season 2026",
    "description": "Updated description",
    "season_year": 2026,
    "status": "active",
    "start_date": "2026-03-01",
    "end_date": "2026-11-30",
    "is_active": false
}
```
- `name` is **not updatable** / `name` **nao e atualizavel**

**`ChampionshipEntryRequest`**
```json
{
    "team_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Response Schemas / Schemas de Resposta

**`ChampionshipListResponse`** (used in list endpoint)
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "formula_e_2026",
    "display_name": "Formula E 2026",
    "description": "Electric racing championship",
    "season_year": 2026,
    "status": "planned",
    "start_date": "2026-03-01",
    "end_date": "2026-11-30",
    "is_active": true,
    "created_at": "2026-02-19T00:00:00Z",
    "updated_at": "2026-02-19T00:00:00Z"
}
```

**`ChampionshipDetailResponse`** (used in GET by ID — includes `teams`)
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "formula_e_2026",
    "display_name": "Formula E 2026",
    "description": "Electric racing championship",
    "season_year": 2026,
    "status": "active",
    "start_date": "2026-03-01",
    "end_date": "2026-11-30",
    "is_active": true,
    "teams": [
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "name": "red_bull_racing",
            "display_name": "Red Bull Racing",
            "is_active": true
        }
    ],
    "created_at": "2026-02-19T00:00:00Z",
    "updated_at": "2026-02-19T00:00:00Z"
}
```

**`ChampionshipEntryResponse`** (used in entry endpoints — includes `registered_at`)
```json
{
    "team_id": "660e8400-e29b-41d4-a716-446655440001",
    "team_name": "red_bull_racing",
    "team_display_name": "Red Bull Racing",
    "team_is_active": true,
    "registered_at": "2026-02-19T00:00:00Z"
}
```

---

## API Endpoints — Championships CRUD

### `GET /api/v1/championships/`

List all championships. Supports optional filtering by status, season year, and active status.

Lista todos os campeonatos. Suporta filtragem opcional por status, ano da temporada e status ativo.

| Parameter | Type | Description |
|---|---|---|
| `status` | `string` (query, optional) | Filter by status (planned/active/completed/cancelled) |
| `season_year` | `int` (query, optional) | Filter by season year |
| `is_active` | `bool` (query, optional) | Filter by active status |

**Permission:** `championships:read`
**Response:** `200` — `list[ChampionshipListResponse]`

```bash
# List all / Listar todos
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/championships/

# Filter by status / Filtrar por status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/championships/?status=active

# Filter by season / Filtrar por temporada
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/championships/?season_year=2026
```

### `GET /api/v1/championships/{championship_id}`

Get a championship by ID with its enrolled teams list.

Busca um campeonato por ID com lista de equipes inscritas.

**Permission:** `championships:read`
**Response:** `200` — `ChampionshipDetailResponse` (includes `teams[]`)
**Error:** `404` — Championship not found

### `POST /api/v1/championships/`

Create a new championship.

Cria um novo campeonato.

**Permission:** `championships:create`
**Request Body:** `ChampionshipCreateRequest`
**Response:** `201` — `ChampionshipResponse`
**Error:** `409` — Championship name already exists

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "formula_e_2026", "display_name": "Formula E 2026", "season_year": 2026}' \
  http://localhost:8000/api/v1/championships/
```

### `PATCH /api/v1/championships/{championship_id}`

Update a championship's fields. Only provided fields are updated.

Atualiza campos de um campeonato. Apenas campos fornecidos sao atualizados.

**Permission:** `championships:update`
**Request Body:** `ChampionshipUpdateRequest`
**Response:** `200` — `ChampionshipResponse`
**Error:** `404` — Championship not found

```bash
curl -X PATCH -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "active", "start_date": "2026-03-01"}' \
  http://localhost:8000/api/v1/championships/{championship_id}
```

### `DELETE /api/v1/championships/{championship_id}`

Delete a championship. All entries are cleared before deletion.

Exclui um campeonato. Todas as inscricoes sao limpas antes da exclusao.

**Permission:** `championships:delete`
**Response:** `204` — No content
**Error:** `404` — Championship not found

---

## API Endpoints — Championship Entries

### `GET /api/v1/championships/{championship_id}/entries`

List all entries of a championship with registration dates.

Lista todas as inscricoes de um campeonato com datas de registro.

**Permission:** `championships:read`
**Response:** `200` — `list[ChampionshipEntryResponse]`
**Error:** `404` — Championship not found

### `POST /api/v1/championships/{championship_id}/entries`

Add a team to a championship.

Adiciona uma equipe a um campeonato.

**Permission:** `championships:manage_entries`
**Request Body:** `ChampionshipEntryRequest`
**Response:** `200` — `list[ChampionshipEntryResponse]` (updated entries list)
**Errors:**
- `404` — Championship not found / Team not found
- `409` — Team is already enrolled in this championship

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"team_id": "550e8400-e29b-41d4-a716-446655440000"}' \
  http://localhost:8000/api/v1/championships/{championship_id}/entries
```

### `DELETE /api/v1/championships/{championship_id}/entries/{team_id}`

Remove a team from a championship.

Remove uma equipe de um campeonato.

**Permission:** `championships:manage_entries`
**Response:** `200` — `list[ChampionshipEntryResponse]` (updated entries list)
**Errors:**
- `404` — Championship not found
- `404` — Team is not enrolled in this championship

---

## Error Responses / Respostas de Erro

All errors follow the standard FastAPI format. All error responses use the same HTTP exception classes from `app/core/exceptions.py`.

Todos os erros seguem o formato padrao do FastAPI.

| Status | Exception | Description / Descricao |
|---|---|---|
| `401` | `CredentialsException` | Missing or invalid JWT token / Token JWT ausente ou invalido |
| `403` | `ForbiddenException` | Missing required permission / Permissao necessaria ausente |
| `404` | `NotFoundException` | Championship or team not found / Campeonato ou equipe nao encontrado |
| `409` | `ConflictException` | Duplicate name or enrollment conflict / Nome duplicado ou conflito de inscricao |

### Example Error Responses / Exemplos de Erro

**404 — Championship not found**
```json
{"detail": "Championship not found"}
```

**409 — Duplicate name**
```json
{"detail": "Championship name already exists"}
```

**409 — Already enrolled**
```json
{"detail": "Team is already enrolled in this championship"}
```

**404 — Not enrolled**
```json
{"detail": "Team is not enrolled in this championship"}
```

**403 — Missing permission**
```json
{"detail": "Missing permissions: championships:manage_entries"}
```

---

## Service Layer / Camada de Servico

All business logic is in `app/championships/service.py`. Functions follow the same async pattern as other modules.

Toda a logica de negocios esta em `app/championships/service.py`. As funcoes seguem o mesmo padrao async dos outros modulos.

### CRUD Functions / Funcoes CRUD

| Function | Description / Descricao |
|---|---|
| `list_championships(db, status?, season_year?, is_active?)` | List championships with optional filters |
| `get_championship_by_id(db, championship_id)` | Get by ID; raises `404` if not found |
| `create_championship(db, name, display_name, season_year, ...)` | Create championship; raises `409` if name exists |
| `update_championship(db, championship, ...)` | Update provided fields only |
| `delete_championship(db, championship)` | Clear entries, then delete championship |

### Entry Functions / Funcoes de Inscricao

| Function | Description / Descricao |
|---|---|
| `list_championship_entries(db, championship_id)` | List entries with `registered_at` via custom join query |
| `add_championship_entry(db, championship_id, team_id)` | Add team; raises `404` (team/champ) or `409` (already enrolled) |
| `remove_championship_entry(db, championship_id, team_id)` | Remove team; raises `404` if not enrolled |

### Design Note / Nota de Design

The `list_championship_entries` function uses a custom query joining `championship_entries` with `teams` to expose `registered_at` in the response. SQLAlchemy's `secondary=` relationship doesn't include association table columns on related objects, so a direct query is needed.

A funcao `list_championship_entries` usa uma query customizada juntando `championship_entries` com `teams` para expor `registered_at` na resposta. O `secondary=` do SQLAlchemy nao inclui colunas da tabela associativa nos objetos relacionados.

---

## Database Migrations / Migracoes de Banco

### 004 — Create Championships Table

**File:** `alembic/versions/004_create_championships_table.py`
**Revision:** `004` (depends on `003`)

Creates the `championships` table with:
- UUID PK
- `name` — `VARCHAR(64)`, unique, indexed
- `display_name` — `VARCHAR(128)`
- `description` — `VARCHAR(512)`, nullable
- `season_year` — `INTEGER`
- `status` — `VARCHAR(20)`, server_default `"planned"` (not native enum — SQLite compat)
- `start_date`, `end_date` — `DATE`, nullable
- `is_active` — `BOOLEAN`, default `true`
- `created_at`, `updated_at` — `TIMESTAMPTZ`

### 005 — Create Championship Entries Table

**File:** `alembic/versions/005_create_championship_entries_table.py`
**Revision:** `005` (depends on `004`)

Creates the `championship_entries` association table with:
- `championship_id` — `UUID PK FK` → `championships.id`, `ondelete=CASCADE`
- `team_id` — `UUID PK FK` → `teams.id`, `ondelete=CASCADE`
- `registered_at` — `TIMESTAMPTZ`, server_default `now()`

---

## Test Coverage / Cobertura de Testes

33 tests total across 2 test files.

33 testes no total em 2 arquivos de teste.

### `tests/test_championships.py` — 20 tests

| Test | Status | Description |
|---|---|---|
| `test_list_championships_empty` | 200 | Empty list when no championships |
| `test_list_championships_with_data` | 200 | Returns championships |
| `test_list_championships_filter_by_status` | 200 | Filters by status |
| `test_list_championships_filter_by_season_year` | 200 | Filters by season year |
| `test_list_championships_filter_by_active` | 200 | Filters by active status |
| `test_get_championship_by_id` | 200 | Returns championship with all fields |
| `test_get_championship_not_found` | 404 | Invalid ID returns 404 |
| `test_create_championship_full` | 201 | Creates with all fields |
| `test_create_championship_minimal` | 201 | Creates with required fields only |
| `test_create_championship_duplicate` | 409 | Duplicate name returns 409 |
| `test_update_championship_display_name` | 200 | Updates display_name |
| `test_update_championship_status` | 200 | Updates status |
| `test_update_championship_deactivate` | 200 | Deactivates championship |
| `test_update_championship_not_found` | 404 | Invalid ID returns 404 |
| `test_delete_championship` | 204 | Deletes, confirms 404 after |
| `test_delete_championship_not_found` | 404 | Invalid ID returns 404 |
| `test_list_championships_unauthorized` | 401 | No token returns 401 |
| `test_create_championship_forbidden` | 403 | No permission returns 403 |
| `test_admin_can_list` | 200 | Admin with `championships:read` can list |
| `test_admin_can_create` | 201 | Admin with `championships:create` can create |

### `tests/test_championship_entries.py` — 13 tests

| Test | Status | Description |
|---|---|---|
| `test_list_entries_empty` | 200 | Empty entries list |
| `test_list_entries_championship_not_found` | 404 | Invalid championship ID |
| `test_add_entry` | 200 | Adds team successfully |
| `test_add_entry_duplicate` | 409 | Already enrolled |
| `test_add_entry_team_not_found` | 404 | Non-existent team |
| `test_add_entry_championship_not_found` | 404 | Non-existent championship |
| `test_add_multiple_entries` | 200 | Adds multiple teams |
| `test_remove_entry` | 200 | Removes team successfully |
| `test_remove_entry_not_enrolled` | 404 | Team not enrolled |
| `test_delete_championship_clears_entries` | 204 | Deleting championship clears entries |
| `test_get_championship_detail_includes_teams` | 200 | GET detail includes teams |
| `test_add_entry_forbidden` | 403 | No `championships:manage_entries` |
| `test_remove_entry_forbidden` | 403 | No `championships:manage_entries` |
