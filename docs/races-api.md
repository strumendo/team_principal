# Races API Reference / Referencia da API de Corridas

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [Data Model / Modelo de Dados](#data-model--modelo-de-dados)
3. [Business Rules / Regras de Negocio](#business-rules--regras-de-negocio)
4. [Permissions / Permissoes](#permissions--permissoes)
5. [Pydantic Schemas / Schemas Pydantic](#pydantic-schemas--schemas-pydantic)
6. [API Endpoints — Races CRUD](#api-endpoints--races-crud)
7. [API Endpoints — Race Entries](#api-endpoints--race-entries)
8. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
9. [Service Layer / Camada de Servico](#service-layer--camada-de-servico)
10. [Database Migrations / Migracoes de Banco](#database-migrations--migracoes-de-banco)
11. [Test Coverage / Cobertura de Testes](#test-coverage--cobertura-de-testes)

---

## Overview / Visao Geral

The Races module provides individual race event management within championships. Races belong to a championship (1:N) and support M:N team enrollment per race via the `race_entries` association table. Race enrollment validates that teams are first enrolled in the parent championship.

O modulo de Corridas fornece gerenciamento de eventos de corrida individuais dentro de campeonatos. Corridas pertencem a um campeonato (1:N) e suportam inscricao M:N de equipes por corrida via tabela associativa `race_entries`. A inscricao em corrida valida que equipes estejam primeiro inscritas no campeonato pai.

### Key Files / Arquivos Chave

| File / Arquivo | Purpose / Proposito |
|---|---|
| `app/races/models.py` | ORM model: `Race`, `RaceStatus` enum, `race_entries` table |
| `app/races/schemas.py` | 10 Pydantic schemas (request/response) |
| `app/races/service.py` | Business logic: CRUD + entry management |
| `app/races/router.py` | API endpoint definitions (8 endpoints) |
| `alembic/versions/006_create_races_table.py` | Migration: `races` table |
| `alembic/versions/007_create_race_entries_table.py` | Migration: `race_entries` table |

---

## Data Model / Modelo de Dados

### Entity Relationship Diagram / Diagrama de Entidade-Relacionamento

```
┌──────────────────────────────┐
│        championships          │
├──────────────────────────────┤
│ id            UUID PK         │
│ ...                           │
└──────────┬───────────────────┘
           │
           │ championships.id (FK)
           │
┌──────────┴───────────────────┐
│          races                │
├──────────────────────────────┤
│ id              UUID PK       │
│ championship_id UUID FK       │ INDEXED, CASCADE
│ name            VARCHAR(64)   │ INDEXED, unique per championship
│ display_name    VARCHAR(128)  │
│ description     VARCHAR(512)  │ nullable
│ round_number    INTEGER       │
│ status          VARCHAR(20)   │ scheduled/qualifying/active/finished/cancelled
│ scheduled_at    TIMESTAMPTZ   │ nullable
│ track_name      VARCHAR(128)  │ nullable
│ track_country   VARCHAR(64)   │ nullable
│ laps_total      INTEGER       │ nullable
│ is_active       BOOLEAN       │ default: true
│ created_at      TIMESTAMPTZ   │
│ updated_at      TIMESTAMPTZ   │
└──────────┬───────────────────┘
           │
           │ races.id (PK)
           │
┌──────────┴───────────────────┐
│       race_entries            │
├──────────────────────────────┤
│ race_id      UUID PK FK      │──→ races.id (CASCADE)
│ team_id      UUID PK FK      │──→ teams.id (CASCADE)
│ registered_at TIMESTAMPTZ    │ server_default=now()
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

- **Championship → Races** (1:N) — one championship has many races, cascade delete
- **Race → Teams** (M:N via `race_entries`) — one race enrolls many teams

```python
# Championship ←→ Race (one-to-many)
Championship.races ←→ Race.championship   # cascade="all, delete-orphan"

# Race ←→ Team (many-to-many via race_entries)
Race.teams ←→ Team.races                  # via race_entries
```

All sides use `lazy="selectin"` for eager loading.

Todos os lados usam `lazy="selectin"` para carregamento antecipado.

### RaceStatus Enum

```python
class RaceStatus(str, enum.Enum):
    scheduled = "scheduled"      # Not yet started / Ainda nao iniciada
    qualifying = "qualifying"    # Qualifying session / Sessao de classificacao
    active = "active"            # Currently running / Em andamento
    finished = "finished"        # Completed / Finalizada
    cancelled = "cancelled"      # Cancelled / Cancelada
```

Uses `native_enum=False` — stored as `VARCHAR(20)` for SQLite test compatibility.

Usa `native_enum=False` — armazenado como `VARCHAR(20)` para compatibilidade com SQLite nos testes.

### Unique Constraint / Restricao Unica

`name` is unique **per championship**, not globally. Enforced by composite unique constraint:

`name` e unico **por campeonato**, nao globalmente. Garantido por restricao unica composta:

```python
UniqueConstraint("championship_id", "name", name="uq_race_championship_name")
```

### Foreign Key Behavior / Comportamento da FK

| Event / Evento | Behavior / Comportamento |
|---|---|
| Championship deleted | Races cascade-deleted via `cascade="all, delete-orphan"` |
| Race deleted | Entries cleared via ORM (`race.teams.clear()`) before deletion |
| Team deleted | `ondelete=CASCADE` removes entries from `race_entries` |

---

## Business Rules / Regras de Negocio

### 1. Race Name Immutability / Imutabilidade do Nome

The `name` field is set at creation and **cannot be updated**. The `championship_id` is also immutable. Only `display_name`, `description`, `round_number`, `status`, `scheduled_at`, `track_name`, `track_country`, `laps_total`, and `is_active` are updatable via PATCH.

O campo `name` e definido na criacao e **nao pode ser atualizado**. O `championship_id` tambem e imutavel.

### 2. Championship Enrollment Prerequisite / Pre-requisito de Inscricao no Campeonato

A team can only be added to a race if it is **already enrolled in the race's championship** (via `championship_entries`). The `add_race_entry` service validates this:

Uma equipe so pode ser adicionada a uma corrida se ja estiver **inscrita no campeonato da corrida** (via `championship_entries`). O servico `add_race_entry` valida isso:

| Condition / Condicao | Result / Resultado |
|---|---|
| Team enrolled in championship | Team is added to the race |
| Team NOT in championship | **409** — "Team is not enrolled in this championship" |
| Entry already exists | **409** — "Team is already enrolled in this race" |

### 3. Race Deletion Cascading / Cascata na Exclusao

When a race is deleted:
1. All entries are cleared via ORM (`race.teams.clear()`)
2. The race row is deleted

Quando uma corrida e excluida:
1. Todas as inscricoes sao limpas via ORM (`race.teams.clear()`)
2. A linha da corrida e excluida

---

## Permissions / Permissoes

5 permissions in the `races` module, seeded by `app/db/seed.py`:

5 permissoes no modulo `races`, populadas por `app/db/seed.py`:

| Codename | Description / Descricao | Used By / Usado Por |
|---|---|---|
| `races:read` | Read races and entries / Ler corridas e inscricoes | GET endpoints |
| `races:create` | Create races / Criar corridas | POST `/api/v1/championships/{id}/races` |
| `races:update` | Update races / Atualizar corridas | PATCH `/api/v1/races/{id}` |
| `races:delete` | Delete races / Excluir corridas | DELETE `/api/v1/races/{id}` |
| `races:manage_entries` | Add/remove entries / Adicionar/remover inscricoes | POST/DELETE `.../entries` |

### Default Role Assignments / Atribuicoes Padrao

| Role / Papel | Races Permissions / Permissoes de Corridas |
|---|---|
| `admin` | All 5 (`races:read/create/update/delete/manage_entries`) |
| `pilot` | `races:read` |
| Others / Outros | None (configure as needed / configure conforme necessario) |

---

## Pydantic Schemas / Schemas Pydantic

Defined in `app/races/schemas.py`. All response schemas use `model_config = {"from_attributes": True}`.

### Request Schemas / Schemas de Requisicao

**`RaceCreateRequest`**
```json
{
    "name": "round_01_monza",
    "display_name": "Round 1 - Monza",
    "description": "Opening race at Monza",
    "round_number": 1,
    "status": "scheduled",
    "scheduled_at": "2026-03-15T14:00:00Z",
    "track_name": "Autodromo di Monza",
    "track_country": "Italy",
    "laps_total": 30
}
```
- `name`, `display_name`, `round_number` are required / sao obrigatorios
- `description`, `status`, `scheduled_at`, `track_name`, `track_country`, `laps_total` are optional / sao opcionais
- `status` defaults to `"scheduled"` / padrao e `"scheduled"`

**`RaceUpdateRequest`** (all fields optional / todos os campos opcionais)
```json
{
    "display_name": "Round 1 - Monza GP",
    "description": "Updated description",
    "round_number": 1,
    "status": "active",
    "scheduled_at": "2026-03-15T14:00:00Z",
    "track_name": "Autodromo di Monza",
    "track_country": "Italy",
    "laps_total": 30,
    "is_active": false
}
```
- `name` and `championship_id` are **not updatable** / **nao sao atualizaveis**

**`RaceEntryRequest`**
```json
{
    "team_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Response Schemas / Schemas de Resposta

**`RaceListResponse`** (used in list endpoint)
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "championship_id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "round_01_monza",
    "display_name": "Round 1 - Monza",
    "description": "Opening race at Monza",
    "round_number": 1,
    "status": "scheduled",
    "scheduled_at": "2026-03-15T14:00:00Z",
    "track_name": "Autodromo di Monza",
    "track_country": "Italy",
    "laps_total": 30,
    "is_active": true,
    "created_at": "2026-02-19T00:00:00Z",
    "updated_at": "2026-02-19T00:00:00Z"
}
```

**`RaceDetailResponse`** (used in GET by ID — includes `teams`)
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "championship_id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "round_01_monza",
    "display_name": "Round 1 - Monza",
    "description": "Opening race at Monza",
    "round_number": 1,
    "status": "scheduled",
    "scheduled_at": "2026-03-15T14:00:00Z",
    "track_name": "Autodromo di Monza",
    "track_country": "Italy",
    "laps_total": 30,
    "is_active": true,
    "teams": [
        {
            "id": "770e8400-e29b-41d4-a716-446655440002",
            "name": "red_bull_racing",
            "display_name": "Red Bull Racing",
            "is_active": true
        }
    ],
    "created_at": "2026-02-19T00:00:00Z",
    "updated_at": "2026-02-19T00:00:00Z"
}
```

**`RaceEntryResponse`** (used in entry endpoints — includes `registered_at`)
```json
{
    "team_id": "770e8400-e29b-41d4-a716-446655440002",
    "team_name": "red_bull_racing",
    "team_display_name": "Red Bull Racing",
    "team_is_active": true,
    "registered_at": "2026-02-19T00:00:00Z"
}
```

---

## API Endpoints — Races CRUD

### `GET /api/v1/championships/{championship_id}/races`

List all races of a championship. Supports optional filtering by status and active status. Results ordered by `round_number`.

Lista todas as corridas de um campeonato. Suporta filtragem opcional por status e status ativo. Resultados ordenados por `round_number`.

| Parameter | Type | Description |
|---|---|---|
| `status` | `string` (query, optional) | Filter by status (scheduled/qualifying/active/finished/cancelled) |
| `is_active` | `bool` (query, optional) | Filter by active status |

**Permission:** `races:read`
**Response:** `200` — `list[RaceListResponse]`
**Error:** `404` — Championship not found

```bash
# List all races in a championship / Listar todas as corridas de um campeonato
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/championships/{champ_id}/races

# Filter by status / Filtrar por status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/championships/{champ_id}/races?status=active
```

### `POST /api/v1/championships/{championship_id}/races`

Create a new race within a championship.

Cria uma nova corrida dentro de um campeonato.

**Permission:** `races:create`
**Request Body:** `RaceCreateRequest`
**Response:** `201` — `RaceResponse`
**Errors:**
- `404` — Championship not found
- `409` — Race name already exists in this championship

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "round_01_monza", "display_name": "Round 1 - Monza", "round_number": 1}' \
  http://localhost:8000/api/v1/championships/{champ_id}/races
```

### `GET /api/v1/races/{race_id}`

Get a race by ID with its enrolled teams list.

Busca uma corrida por ID com lista de equipes inscritas.

**Permission:** `races:read`
**Response:** `200` — `RaceDetailResponse` (includes `teams[]`)
**Error:** `404` — Race not found

### `PATCH /api/v1/races/{race_id}`

Update a race's fields. Only provided fields are updated.

Atualiza campos de uma corrida. Apenas campos fornecidos sao atualizados.

**Permission:** `races:update`
**Request Body:** `RaceUpdateRequest`
**Response:** `200` — `RaceResponse`
**Error:** `404` — Race not found

```bash
curl -X PATCH -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "active", "laps_total": 35}' \
  http://localhost:8000/api/v1/races/{race_id}
```

### `DELETE /api/v1/races/{race_id}`

Delete a race. All entries are cleared before deletion.

Exclui uma corrida. Todas as inscricoes sao limpas antes da exclusao.

**Permission:** `races:delete`
**Response:** `204` — No content
**Error:** `404` — Race not found

---

## API Endpoints — Race Entries

### `GET /api/v1/races/{race_id}/entries`

List all entries of a race with registration dates.

Lista todas as inscricoes de uma corrida com datas de registro.

**Permission:** `races:read`
**Response:** `200` — `list[RaceEntryResponse]`
**Error:** `404` — Race not found

### `POST /api/v1/races/{race_id}/entries`

Add a team to a race. The team must be enrolled in the race's championship.

Adiciona uma equipe a uma corrida. A equipe deve estar inscrita no campeonato da corrida.

**Permission:** `races:manage_entries`
**Request Body:** `RaceEntryRequest`
**Response:** `200` — `list[RaceEntryResponse]` (updated entries list)
**Errors:**
- `404` — Race not found / Team not found
- `409` — Team is not enrolled in this championship
- `409` — Team is already enrolled in this race

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"team_id": "550e8400-e29b-41d4-a716-446655440000"}' \
  http://localhost:8000/api/v1/races/{race_id}/entries
```

### `DELETE /api/v1/races/{race_id}/entries/{team_id}`

Remove a team from a race.

Remove uma equipe de uma corrida.

**Permission:** `races:manage_entries`
**Response:** `200` — `list[RaceEntryResponse]` (updated entries list)
**Errors:**
- `404` — Race not found
- `404` — Team is not enrolled in this race

---

## Error Responses / Respostas de Erro

All errors follow the standard FastAPI format.

Todos os erros seguem o formato padrao do FastAPI.

| Status | Exception | Description / Descricao |
|---|---|---|
| `401` | `CredentialsException` | Missing or invalid JWT token / Token JWT ausente ou invalido |
| `403` | `ForbiddenException` | Missing required permission / Permissao necessaria ausente |
| `404` | `NotFoundException` | Race, championship, or team not found / Corrida, campeonato ou equipe nao encontrado |
| `409` | `ConflictException` | Duplicate name, enrollment conflict, or championship prerequisite / Nome duplicado, conflito de inscricao ou pre-requisito de campeonato |

### Example Error Responses / Exemplos de Erro

**404 — Race not found**
```json
{"detail": "Race not found"}
```

**404 — Championship not found**
```json
{"detail": "Championship not found"}
```

**409 — Duplicate name**
```json
{"detail": "Race name already exists in this championship"}
```

**409 — Not in championship**
```json
{"detail": "Team is not enrolled in this championship"}
```

**409 — Already enrolled in race**
```json
{"detail": "Team is already enrolled in this race"}
```

**404 — Not enrolled in race**
```json
{"detail": "Team is not enrolled in this race"}
```

---

## Service Layer / Camada de Servico

All business logic is in `app/races/service.py`.

Toda a logica de negocios esta em `app/races/service.py`.

### CRUD Functions / Funcoes CRUD

| Function | Description / Descricao |
|---|---|
| `list_races(db, championship_id, status?, is_active?)` | List races with optional filters, ordered by round_number |
| `get_race_by_id(db, race_id)` | Get by ID; raises `404` if not found |
| `create_race(db, championship_id, name, display_name, round_number, ...)` | Create race; raises `404` (championship) or `409` (duplicate name) |
| `update_race(db, race, ...)` | Update provided fields only |
| `delete_race(db, race)` | Clear entries, then delete race |

### Entry Functions / Funcoes de Inscricao

| Function | Description / Descricao |
|---|---|
| `list_race_entries(db, race_id)` | List entries with `registered_at` via custom join query |
| `add_race_entry(db, race_id, team_id)` | Add team; validates championship enrollment; raises `404`/`409` |
| `remove_race_entry(db, race_id, team_id)` | Remove team; raises `404` if not enrolled |

---

## Database Migrations / Migracoes de Banco

### 006 — Create Races Table

**File:** `alembic/versions/006_create_races_table.py`
**Revision:** `006` (depends on `005`)

Creates the `races` table with:
- UUID PK
- `championship_id` — `UUID FK` → `championships.id`, `ondelete=CASCADE`, indexed
- `name` — `VARCHAR(64)`, indexed
- `display_name` — `VARCHAR(128)`
- `description` — `VARCHAR(512)`, nullable
- `round_number` — `INTEGER`
- `status` — `VARCHAR(20)`, server_default `"scheduled"` (not native enum — SQLite compat)
- `scheduled_at` — `TIMESTAMPTZ`, nullable
- `track_name` — `VARCHAR(128)`, nullable
- `track_country` — `VARCHAR(64)`, nullable
- `laps_total` — `INTEGER`, nullable
- `is_active` — `BOOLEAN`, default `true`
- `created_at`, `updated_at` — `TIMESTAMPTZ`
- Composite unique constraint: `uq_race_championship_name`

### 007 — Create Race Entries Table

**File:** `alembic/versions/007_create_race_entries_table.py`
**Revision:** `007` (depends on `006`)

Creates the `race_entries` association table with:
- `race_id` — `UUID PK FK` → `races.id`, `ondelete=CASCADE`
- `team_id` — `UUID PK FK` → `teams.id`, `ondelete=CASCADE`
- `registered_at` — `TIMESTAMPTZ`, server_default `now()`

---

## Test Coverage / Cobertura de Testes

35 tests total across 2 test files.

35 testes no total em 2 arquivos de teste.

### `tests/test_races.py` — 22 tests

| Test | Status | Description |
|---|---|---|
| `test_list_races_empty` | 200 | Empty list when no races |
| `test_list_races_with_data` | 200 | Returns races |
| `test_list_races_ordered_by_round` | 200 | Ordered by round_number |
| `test_list_races_filter_by_status` | 200 | Filters by status |
| `test_list_races_filter_by_active` | 200 | Filters by active status |
| `test_list_races_championship_not_found` | 404 | Invalid championship ID |
| `test_get_race_by_id` | 200 | Returns race with all fields |
| `test_get_race_not_found` | 404 | Invalid ID returns 404 |
| `test_create_race_full` | 201 | Creates with all fields |
| `test_create_race_minimal` | 201 | Creates with required fields only |
| `test_create_race_duplicate_name` | 409 | Duplicate name in championship returns 409 |
| `test_create_race_championship_not_found` | 404 | Invalid championship returns 404 |
| `test_update_race_display_name` | 200 | Updates display_name |
| `test_update_race_status` | 200 | Updates status |
| `test_update_race_deactivate` | 200 | Deactivates race |
| `test_update_race_not_found` | 404 | Invalid ID returns 404 |
| `test_delete_race` | 204 | Deletes, confirms 404 after |
| `test_delete_race_not_found` | 404 | Invalid ID returns 404 |
| `test_list_races_unauthorized` | 401 | No token returns 401 |
| `test_create_race_forbidden` | 403 | No permission returns 403 |
| `test_admin_can_list_races` | 200 | Admin with `races:read` can list |
| `test_admin_can_create_race` | 201 | Admin with `races:create` can create |

### `tests/test_race_entries.py` — 13 tests

| Test | Status | Description |
|---|---|---|
| `test_list_race_entries_empty` | 200 | Empty entries list |
| `test_list_race_entries_with_data` | 200 | Returns entries with registration date |
| `test_list_race_entries_not_found` | 404 | Invalid race ID |
| `test_add_race_entry` | 200 | Adds team successfully |
| `test_add_race_entry_team_not_in_championship` | 409 | Team not enrolled in championship |
| `test_add_race_entry_duplicate` | 409 | Already enrolled in race |
| `test_add_race_entry_race_not_found` | 404 | Non-existent race |
| `test_add_race_entry_team_not_found` | 404 | Non-existent team |
| `test_remove_race_entry` | 200 | Removes team successfully |
| `test_remove_race_entry_not_found` | 404 | Team not enrolled |
| `test_list_race_entries_unauthorized` | 401 | No token returns 401 |
| `test_add_race_entry_forbidden` | 403 | No `races:manage_entries` |
| `test_get_race_detail_includes_teams` | 200 | GET detail includes teams |
