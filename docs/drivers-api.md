# Drivers API Reference / Referencia da API de Pilotos

## Table of Contents / Indice

1. [Overview / Visao Geral](#overview--visao-geral)
2. [Data Model / Modelo de Dados](#data-model--modelo-de-dados)
3. [Pydantic Schemas / Schemas Pydantic](#pydantic-schemas--schemas-pydantic)
4. [API Endpoints](#api-endpoints)
5. [Error Responses / Respostas de Erro](#error-responses--respostas-de-erro)
6. [Service Layer / Camada de Servico](#service-layer--camada-de-servico)
7. [Test Coverage / Cobertura de Testes](#test-coverage--cobertura-de-testes)

---

## Overview / Visao Geral

The Drivers module manages racing drivers. Each driver belongs to a team, has a unique name, unique 3-character abbreviation, and a number unique within their team. Drivers can be linked to race results for driver-level standings.

O modulo de Pilotos gerencia pilotos de corrida. Cada piloto pertence a uma equipe, tem um nome unico, abreviacao unica de 3 caracteres, e um numero unico dentro da equipe. Pilotos podem ser vinculados a resultados de corrida para classificacao individual.

### Key Files / Arquivos Chave

| File / Arquivo | Purpose / Proposito |
|---|---|
| `app/drivers/models.py` | Driver ORM model |
| `app/drivers/schemas.py` | 6 Pydantic schemas |
| `app/drivers/service.py` | CRUD business logic |
| `app/drivers/router.py` | 5 API endpoints |

---

## Data Model / Modelo de Dados

```
┌─────────────────────────┐
│        drivers           │
├─────────────────────────┤
│ id           UUID PK     │
│ name         VARCHAR(64) │ UNIQUE, INDEXED
│ display_name VARCHAR(128)│
│ abbreviation VARCHAR(3)  │ UNIQUE
│ number       INT         │
│ nationality  VARCHAR(64) │ nullable
│ date_of_birth DATE       │ nullable
│ photo_url    VARCHAR(512)│ nullable
│ team_id      UUID FK     │──→ teams.id (CASCADE), INDEXED
│ is_active    BOOLEAN     │ default true
│ created_at   TIMESTAMPTZ │
│ updated_at   TIMESTAMPTZ │
├─────────────────────────┤
│ UQ(team_id, number)     │
└─────────────────────────┘
```

### Constraints / Restricoes

- `name` is globally unique / `name` e globalmente unico
- `abbreviation` is globally unique, always 3 characters, stored uppercase / `abbreviation` e globalmente unico, sempre 3 caracteres, armazenado em maiusculo
- `number` is unique per team (via `UQ(team_id, number)`) / `number` e unico por equipe
- `team_id` CASCADE delete — deleting a team deletes its drivers / deletar equipe deleta seus pilotos

---

## Pydantic Schemas / Schemas Pydantic

### Request Schemas / Schemas de Requisicao

**`DriverCreateRequest`**
```json
{
    "name": "driver_alpha",
    "display_name": "Driver Alpha",
    "abbreviation": "ALP",
    "number": 7,
    "team_id": "uuid",
    "nationality": "Brazilian",
    "date_of_birth": "1995-06-15",
    "photo_url": "https://example.com/photo.jpg"
}
```
Required: `name`, `display_name`, `abbreviation` (3 chars), `number`, `team_id`. Optional: `nationality`, `date_of_birth`, `photo_url`.

**`DriverUpdateRequest`** (all fields optional / todos opcionais)
```json
{
    "display_name": "Updated Name",
    "abbreviation": "UPD",
    "number": 10,
    "nationality": "Portuguese",
    "date_of_birth": "1995-06-15",
    "photo_url": "https://example.com/new.jpg",
    "is_active": false
}
```

### Response Schemas / Schemas de Resposta

**`DriverListResponse`** — used in list endpoint (without team detail or date_of_birth/photo_url)

**`DriverResponse`** — used in create/update (full fields, team_id only)

**`DriverDetailResponse`** — used in get by ID (includes nested `team` object with `id`, `name`, `display_name`, `is_active`)

---

## API Endpoints

### GET `/api/v1/drivers/`

List all drivers with optional filters.

Lista todos os pilotos com filtros opcionais.

| Parameter | Type | In | Required | Description |
|---|---|---|---|---|
| `is_active` | `boolean` | query | No | Filter by active status / Filtrar por status ativo |
| `team_id` | `UUID` | query | No | Filter by team / Filtrar por equipe |

**Permission:** `drivers:read`
**Response:** `200 OK` — `list[DriverListResponse]`

### GET `/api/v1/drivers/{driver_id}`

Get a driver by ID with team details.

Busca um piloto por ID com detalhes da equipe.

**Permission:** `drivers:read`
**Response:** `200 OK` — `DriverDetailResponse`
**Errors:** `404` if not found

### POST `/api/v1/drivers/`

Create a new driver.

Cria um novo piloto.

**Permission:** `drivers:create`
**Request body:** `DriverCreateRequest`
**Response:** `201 Created` — `DriverResponse`
**Errors:** `404` if team not found, `409` if name/abbreviation exists or number taken in team

### PATCH `/api/v1/drivers/{driver_id}`

Update a driver's fields.

Atualiza campos de um piloto.

**Permission:** `drivers:update`
**Request body:** `DriverUpdateRequest`
**Response:** `200 OK` — `DriverResponse`
**Errors:** `404` if not found, `409` if abbreviation/number conflict

### DELETE `/api/v1/drivers/{driver_id}`

Delete a driver.

Exclui um piloto.

**Permission:** `drivers:delete`
**Response:** `204 No Content`
**Errors:** `404` if not found

---

## Error Responses / Respostas de Erro

| Status | Condition (EN) | Condicao (pt-BR) |
|---|---|---|
| 401 | Missing or invalid auth token | Token ausente ou invalido |
| 403 | Insufficient permissions | Permissoes insuficientes |
| 404 | Driver or team not found | Piloto ou equipe nao encontrado |
| 409 | Duplicate driver name | Nome de piloto duplicado |
| 409 | Duplicate abbreviation | Abreviacao duplicada |
| 409 | Number taken within team | Numero ja em uso na equipe |
| 422 | Abbreviation not 3 characters | Abreviacao sem 3 caracteres |

---

## Service Layer / Camada de Servico

| Function | Purpose (EN) | Proposito (pt-BR) |
|---|---|---|
| `list_drivers(db, is_active?, team_id?)` | List with optional filters | Lista com filtros opcionais |
| `get_driver_by_id(db, driver_id)` | Get or raise 404 | Busca ou lanca 404 |
| `create_driver(db, name, ...)` | Create with full validation | Cria com validacao completa |
| `update_driver(db, driver, ...)` | Partial update with uniqueness checks | Atualizacao parcial com validacao |
| `delete_driver(db, driver)` | Delete driver | Exclui piloto |

---

## Test Coverage / Cobertura de Testes

### Drivers Tests / Testes de Pilotos (`test_drivers.py` — 30 tests)

| Test | Category |
|---|---|
| `test_list_drivers_empty` | List |
| `test_list_drivers_with_data` | List |
| `test_list_drivers_filter_active` | List (filter) |
| `test_list_drivers_filter_inactive` | List (filter) |
| `test_list_drivers_filter_team` | List (filter) |
| `test_list_drivers_filter_active_and_team` | List (filter) |
| `test_get_driver_by_id` | Get |
| `test_get_driver_not_found` | Get (404) |
| `test_create_driver_full` | Create |
| `test_create_driver_minimal` | Create |
| `test_create_driver_abbreviation_uppercase` | Create (validation) |
| `test_create_driver_duplicate_name` | Create (409) |
| `test_create_driver_duplicate_abbreviation` | Create (409) |
| `test_create_driver_duplicate_number_same_team` | Create (409) |
| `test_create_driver_same_number_different_team` | Create |
| `test_create_driver_team_not_found` | Create (404) |
| `test_create_driver_invalid_abbreviation_length` | Create (422) |
| `test_update_driver_display_name` | Update |
| `test_update_driver_abbreviation` | Update |
| `test_update_driver_abbreviation_conflict` | Update (409) |
| `test_update_driver_number` | Update |
| `test_update_driver_number_conflict` | Update (409) |
| `test_update_driver_deactivate` | Update |
| `test_update_driver_not_found` | Update (404) |
| `test_delete_driver` | Delete |
| `test_delete_driver_not_found` | Delete (404) |
| `test_list_drivers_unauthorized` | Auth (401) |
| `test_create_driver_forbidden` | Auth (403) |
| `test_update_driver_forbidden` | Auth (403) |
| `test_delete_driver_forbidden` | Auth (403) |
