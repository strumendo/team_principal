# Drivers API Reference / Referencia da API de Pilotos

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [Data Model / Modelo de Dados](#data-model--modelo-de-dados)
3. [Business Rules / Regras de Negocio](#business-rules--regras-de-negocio)
4. [Permissions / Permissoes](#permissions--permissoes)
5. [Pydantic Schemas / Schemas Pydantic](#pydantic-schemas--schemas-pydantic)
6. [API Endpoints](#api-endpoints)
7. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
8. [Service Layer / Camada de Servico](#service-layer--camada-de-servico)
9. [Test Coverage / Cobertura de Testes](#test-coverage--cobertura-de-testes)

---

## Overview / Visao Geral

The Drivers module manages individual racing drivers linked to teams. A driver is an independent entity (not tied to a User) with a mandatory team association. Drivers can be optionally linked to race results for individual tracking and driver championship standings.

O modulo de Pilotos gerencia pilotos de corrida individuais vinculados a equipes. Um piloto e uma entidade independente (sem vinculo com User) com associacao obrigatoria a uma equipe. Pilotos podem ser opcionalmente vinculados a resultados de corrida para rastreamento individual e classificacao de pilotos no campeonato.

### Key Files / Arquivos Chave

| File / Arquivo | Purpose / Proposito |
|---|---|
| `app/drivers/models.py` | ORM model: `Driver` |
| `app/drivers/schemas.py` | 7 Pydantic schemas (request/response) |
| `app/drivers/service.py` | Business logic: CRUD with validation |
| `app/drivers/router.py` | API endpoint definitions (5 endpoints) |

---

## Data Model / Modelo de Dados

### Entity Relationship Diagram / Diagrama de Entidade-Relacionamento

```
┌──────────────────────────────┐
│          teams                │
├──────────────────────────────┤
│ id              UUID PK       │
│ name            VARCHAR(64)   │
│ ...                           │
└──────────┬───────────────────┘
           │
           │ teams.id (FK, CASCADE)
           │
┌──────────┴───────────────────┐
│          drivers              │
├──────────────────────────────┤
│ id              UUID PK       │
│ name            VARCHAR(64)   │ UNIQUE INDEX
│ display_name    VARCHAR(128)  │
│ abbreviation    VARCHAR(3)    │ UNIQUE
│ number          INTEGER       │
│ nationality     VARCHAR(64)   │ nullable
│ date_of_birth   DATE          │ nullable
│ photo_url       VARCHAR(512)  │ nullable
│ team_id         UUID FK       │ NOT NULL, CASCADE
│ is_active       BOOLEAN       │ default: true
│ created_at      DATETIME(tz)  │
│ updated_at      DATETIME(tz)  │
├──────────────────────────────┤
│ UQ(team_id, number)          │ number unique within team
└──────────────────────────────┘
```

---

## Business Rules / Regras de Negocio

| Rule / Regra | Details / Detalhes |
|---|---|
| **name** | Globally unique, immutable after creation / Unico globalmente, imutavel apos criacao |
| **abbreviation** | Globally unique, exactly 3 characters, always stored uppercase / Unico globalmente, exatamente 3 caracteres, sempre armazenado em maiusculas |
| **number** | Unique within same team (different teams can share numbers) / Unico dentro da mesma equipe (equipes diferentes podem compartilhar numeros) |
| **team_id** | Required — team must exist / Obrigatorio — equipe deve existir |
| **Driver x User** | Independent entity — no FK to users / Entidade independente — sem FK para users |
| **Driver x Team** | Mandatory FK (`NOT NULL`, `CASCADE`) / FK obrigatoria |
| **Delete cascade** | Deleting a team deletes all its drivers / Excluir uma equipe exclui todos os seus pilotos |

---

## Permissions / Permissoes

| Codename | Description / Descricao |
|---|---|
| `drivers:read` | List and get drivers / Listar e buscar pilotos |
| `drivers:create` | Create new drivers / Criar novos pilotos |
| `drivers:update` | Update existing drivers / Atualizar pilotos existentes |
| `drivers:delete` | Delete drivers / Excluir pilotos |

**Seed defaults:** `admin` role gets all 4 permissions. `pilot` role gets `drivers:read`.

---

## Pydantic Schemas / Schemas Pydantic

| Schema | Usage / Uso |
|---|---|
| `DriverTeamResponse` | Team summary nested in driver detail |
| `DriverResponse` | Full driver (create/update response) |
| `DriverListResponse` | List item (excludes date_of_birth, photo_url) |
| `DriverDetailResponse` | Detail with nested team |
| `DriverCreateRequest` | Create request body |
| `DriverUpdateRequest` | Partial update request body |

---

## API Endpoints

### GET `/api/v1/drivers/`

List all drivers with optional filters.

**Query Parameters:**
- `is_active` (bool, optional) — filter by active status
- `team_id` (UUID, optional) — filter by team

**Permission:** `drivers:read`

**Response:** `200 OK` — `DriverListResponse[]`

```json
[
  {
    "id": "uuid",
    "name": "verstappen",
    "display_name": "Max Verstappen",
    "abbreviation": "VER",
    "number": 1,
    "nationality": "Dutch",
    "team_id": "uuid",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
  }
]
```

### GET `/api/v1/drivers/{id}`

Get driver detail with team info.

**Permission:** `drivers:read`

**Response:** `200 OK` — `DriverDetailResponse`

### POST `/api/v1/drivers/`

Create a new driver.

**Permission:** `drivers:create`

**Request Body:**
```json
{
  "name": "verstappen",
  "display_name": "Max Verstappen",
  "abbreviation": "VER",
  "number": 1,
  "team_id": "uuid",
  "nationality": "Dutch",
  "date_of_birth": "1997-09-30",
  "photo_url": "https://example.com/ver.png"
}
```

**Response:** `201 Created` — `DriverResponse`

### PATCH `/api/v1/drivers/{id}`

Update driver fields. `name` and `team_id` are immutable.

**Permission:** `drivers:update`

**Request Body (all optional):**
```json
{
  "display_name": "Max Emilian Verstappen",
  "abbreviation": "MVR",
  "number": 33,
  "nationality": "Dutch",
  "date_of_birth": "1997-09-30",
  "photo_url": "https://example.com/ver2.png",
  "is_active": false
}
```

**Response:** `200 OK` — `DriverResponse`

### DELETE `/api/v1/drivers/{id}`

Delete a driver.

**Permission:** `drivers:delete`

**Response:** `204 No Content`

---

## Error Responses / Respostas de Erro

| Status | Condition / Condicao |
|---|---|
| `401 Unauthorized` | Missing or invalid JWT token |
| `403 Forbidden` | User lacks required permission |
| `404 Not Found` | Driver or team not found |
| `409 Conflict` | Duplicate name, abbreviation, or number within team |
| `422 Validation Error` | Invalid abbreviation length (must be exactly 3 chars) |

---

## Service Layer / Camada de Servico

| Function | Description / Descricao |
|---|---|
| `list_drivers(db, is_active, team_id)` | List with optional filters, ordered by name |
| `get_driver_by_id(db, driver_id)` | Get by ID, raises `NotFoundException` |
| `create_driver(db, ...)` | Validates team + name/abbr/number uniqueness |
| `update_driver(db, driver, ...)` | Validates abbr/number uniqueness on change |
| `delete_driver(db, driver)` | Deletes driver record |

---

## Test Coverage / Cobertura de Testes

**File:** `tests/test_drivers.py` — **30 tests**

| Category / Categoria | Count / Qtd |
|---|---|
| List (empty, with data, filters) | 6 |
| Get by ID (found, not found) | 2 |
| Create (full, minimal, uppercase, conflicts, team not found, invalid abbr) | 8 |
| Update (fields, conflicts, not found) | 7 |
| Delete (success, not found) | 2 |
| Auth (401, 403 x3) | 5 |
| **Total** | **30** |
